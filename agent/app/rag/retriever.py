"""向量检索：问题 → bge-m3 向量 → pgvector 余弦 Top-K。

几个关键事实（2026-10-22 实测）：
- content_unit 共 535 条，全部带 1024 维向量，索引 idx_cu_hnsw（HNSW + vector_cosine_ops）
- ref_type 只有 formula(245) 和 case(290) 两类；**568 条 classic_quote（条文）没有向量**，
  所以问条文类问题（"太阳病提纲是什么"）召回不到原文，这是已知缺口（数据侧待补）
- 相似度 = 1 - 余弦距离：1.0 完全相同，0 无关；实测相关结果多在 0.5~0.8，无关多在 0.2~0.35

⚠️ embedding 模型必须与建库时一致（BAAI/bge-m3），换模型 → 向量空间不同 → 相似度无意义。
"""

from __future__ import annotations

import asyncio
import logging
import math
from dataclasses import dataclass

from app.config import get_settings
from app.db import get_pg_pool
from app.llm import embed_query

logger = logging.getLogger("herbmind-agent")

# 引用卡片预览用的正文长度
SNIPPET_LEN = 160

# 不指定 ref_type 时，方剂占的配额比例（其余给医案）
# 0.6 → top_k=5 时方剂 3 条 + 医案 2 条
FORMULA_RATIO = 0.6


@dataclass(slots=True)
class RetrievedUnit:
    """一条召回结果。"""

    id: str
    ref_type: str
    ref_id: str
    title: str
    content: str
    score: float

    @property
    def kind_label(self) -> str:
        """给提示词用的中文类型名。"""
        return {"formula": "方剂", "case": "医案", "quote": "条文", "node": "理论"}.get(
            self.ref_type, self.ref_type
        )

    def snippet(self, limit: int = SNIPPET_LEN) -> str:
        """取正文前若干字做预览（去掉换行，前端好排版）。"""
        text = " ".join(self.content.split())
        return text if len(text) <= limit else text[:limit] + "…"


def _display_title(ref_type: str, title: str, content: str, ref_id: str) -> str:
    """给前端和提示词用的可读名称。

    数据现状（2026-10-22 实测）：
    - formula 的 title 是方名（245 条里 228 个 distinct，可用）
    - case 的 title 只有 3 个值（伤寒论 / 金匮要略 / 温病学，是书名），无法区分是哪则医案
      → 改取正文第一行，形如"医案：小承气汤" → "小承气汤"
    """
    if ref_type == "case":
        stripped = content.strip()
        first = stripped.splitlines()[0].strip() if stripped else ""
        first = first.removeprefix("医案：").removeprefix("医案:").strip()
        if first:
            return first[:30]
    return (title or ref_id).strip()


def _to_pgvector(vec: list[float]) -> str:
    """list[float] → pgvector 字面量 '[0.1,0.2,...]'（psycopg 传字符串，由 PG 侧 cast）。

    不依赖 psycopg 的 vector adapter，少一层环境依赖，也便于直接复制 SQL 到 psql 里调试。
    """
    return "[" + ",".join(f"{x:.7g}" for x in vec) + "]"


_SQL_TEMPLATE = """
SELECT id,
       ref_type,
       ref_id,
       coalesce(title, '') AS title,
       content,
       1 - (embedding <=> %(vec)s::vector) AS score
FROM content_unit
WHERE embedding IS NOT NULL
  {ref_filter}
ORDER BY embedding <=> %(vec)s::vector
LIMIT %(limit)s
"""


async def retrieve(
    question: str,
    top_k: int | None = None,
    ref_type: str | None = None,
    min_score: float | None = None,
) -> list[RetrievedUnit]:
    """按语义相似度召回内容单元。

    Args:
        question: 用户问题（中文原文，不需要预处理）
        top_k: 召回条数，默认取配置
        ref_type: 限定 'formula' / 'case'；None 表示按配额双路召回（方剂 60% + 医案 40%）
        min_score: 相似度下限，低于此丢弃（宁可少给，也不要塞不相关内容诱发幻觉）

    Returns:
        按相似度降序、且已过滤掉低分的列表（可能为空）
    """
    s = get_settings()
    limit = top_k or s.retrieval_top_k
    threshold = s.retrieval_min_score if min_score is None else min_score

    # ① 问题向量化（走硅基流动 bge-m3，约 100~300ms）——两类检索共用同一个向量，只调一次
    vec_literal = _to_pgvector(await embed_query(question))

    def _query(ref_type_filter: str, k: int) -> list[tuple]:
        """单路检索（走 HNSW 索引）。阻塞调用，调用方负责丢线程池。"""
        sql = _SQL_TEMPLATE.format(ref_filter="AND ref_type = %(ref_type)s")
        params = {"vec": vec_literal, "limit": k, "ref_type": ref_type_filter}
        with get_pg_pool().connection(timeout=5) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                return cur.fetchall()

    def _to_units(rows: list[tuple]) -> list[RetrievedUnit]:
        return [
            RetrievedUnit(
                id=row[0],
                ref_type=row[1],
                ref_id=row[2],
                title=_display_title(row[1], row[3], row[4], row[2]),
                content=row[4],
                score=float(row[5]),
            )
            for row in rows
        ]

    # ② 检索：指定类型就单路；不指定就按"类型配额"双路召回
    if ref_type:
        rows = await asyncio.to_thread(_query, ref_type, limit)
        units = _to_units(rows)
    else:
        # 为什么要配额：实测问"无汗而喘脉浮紧用什么方"时，Top5 全被医案占满，
        # 真正的"麻黄汤"方剂排在 6 名开外 → 问方不给方，用户体验很差。
        # 改成方剂 60% + 医案 40% 的配额，保证"问方必有方、问案必有案"。
        formula_k = max(1, math.ceil(limit * FORMULA_RATIO))
        # 注意用 0 兜底而不是 1：limit=1 时只应召回 1 条，不能强塞一条医案
        case_k = max(0, limit - formula_k)
        # 理论单元（章/节正文）走**独立的第三路**，在 formula+case 配额之外追加：
        # 混进原有比例会破坏"问方必有方"。它的篇幅远大于方剂/医案，条数由配置兜住。
        theory_k = max(0, min(s.retrieval_theory_top_k, limit))

        tasks = [asyncio.to_thread(_query, "formula", formula_k)]
        if case_k:
            tasks.append(asyncio.to_thread(_query, "case", case_k))
        if theory_k:
            tasks.append(asyncio.to_thread(_query, "node", theory_k))
        groups = await asyncio.gather(*tasks)
        units = [u for rows in groups for u in _to_units(rows)]
        units.sort(key=lambda u: u.score, reverse=True)

    kept = [u for u in units if u.score >= threshold]
    logger.info(
        "检索『%s』配额=%s 阈值=%.2f → 保留 %d/%d 条（方剂 %d、医案 %d、理论 %d，最高分 %.3f）",
        question[:24],
        "单路:" + ref_type if ref_type else "formula+case+node",
        threshold,
        len(kept),
        len(units),
        sum(1 for u in kept if u.ref_type == "formula"),
        sum(1 for u in kept if u.ref_type == "case"),
        sum(1 for u in kept if u.ref_type == "node"),
        units[0].score if units else 0.0,
    )
    return kept


# ==================== 无 LLM key 时的关键词检索降级 ====================
# bge-m3 embedding 与聊天模型共用同一个 LLM_API_KEY。本机未配置 key 时，
# 向量检索整条链会抛 RuntimeError，问答完全不可用。这里提供一条纯 PG 关键词
# 检索路径：中文 2-gram 拆词 + ILIKE 命中打分，不依赖任何外部模型，
# 配合 ask.py 的降级分支，让"没 key 也能问、且回答基于真实资料"。

# 提问里这些词对检索无意义，拆 gram 时忽略
_STOP = set(
    "了吗呢啊吧请问什么怎么哪些哪里可以是否的了我你他这那和与及在是有为将把被给对从到用什么方剂治疗"
    "怎样如何这个那个是否通过一下现在根据因为所以但是具有用于属于一种比较更加还是或者以及的话".split()
) | {"用什", "么方", "紧用", "而喘", "汗而", "紧用"}
# 单字词不拆，_len>=2 的中文串拆成 2-gram
_CJK = __import__("re").compile(r"[\u4e00-\u9fa5]{2,}")


def _keyword_grams(question: str) -> list[str]:
    """从问题里提取检索词：连续中文拆 2-gram，去掉停用词，保留方名类完整词。"""
    grams: list[str] = []
    for seg in _CJK.findall(question):
        if seg in _STOP or len(seg) <= 1:
            continue
        if len(seg) <= 4:
            grams.append(seg)
        for i in range(len(seg) - 1):
            g = seg[i:i + 2]
            if g not in _STOP:
                grams.append(g)
    # 去重保序，限制数量避免 SQL 过长
    seen: set[str] = set()
    out = []
    for g in grams:
        if g not in seen:
            seen.add(g)
            out.append(g)
    return out[:24]


async def retrieve_keyword(
    question: str,
    top_k: int | None = None,
    ref_type: str | None = None,
) -> list[RetrievedUnit]:
    """纯关键词检索（无 embedding、无 LLM key）。

    对每个内容单元，统计命中了多少个问题词（标题命中权重更高），按命中数降序。
    分数归一化到 0~1，便于复用下游 score 展示逻辑。
    """
    s = get_settings()
    limit = top_k or s.retrieval_top_k
    grams = _keyword_grams(question)
    if not grams:
        return []

    # 检索字段：标题、正文、证候(syndrome)、主方(formula)。
    # 症状类问题（"无汗而喘、脉浮紧"）的词主要落在 syndrome 元数据里，必须一起查。
    # 用 unnest(数组) 一次传所有词，避免逐个拼占位符（也绕开 f-string 里 %s 的转义坑）。
    patterns = [f"%{g}%" for g in grams]
    match_sql = """
        coalesce(cu.title,'') ILIKE p
        OR cu.content ILIKE p
        OR coalesce(cu.meta_jsonb->>'syndrome','') ILIKE p
        OR coalesce(cu.meta_jsonb->>'formula','') ILIKE p
    """
    type_filter = "AND cu.ref_type = %s" if ref_type else ""
    params: list = [patterns, patterns]
    if ref_type:
        params.append(ref_type)
    params.append(limit)
    sql = f"""
        SELECT cu.id, cu.ref_type, cu.ref_id, coalesce(cu.title,'') AS title, cu.content,
               (SELECT count(*) FROM unnest(%s::text[]) AS p WHERE {match_sql}) AS hits
        FROM content_unit cu
        WHERE EXISTS (SELECT 1 FROM unnest(%s::text[]) AS p WHERE {match_sql})
          {type_filter}
        ORDER BY hits DESC, length(cu.content) ASC
        LIMIT %s
    """

    def _query() -> list[tuple]:
        with get_pg_pool().connection(timeout=5) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                return cur.fetchall()

    rows = await asyncio.to_thread(_query)
    max_hits = max((int(r[5]) for r in rows), default=1) or 1
    units = [
        RetrievedUnit(
            id=r[0], ref_type=r[1], ref_id=r[2],
            title=_display_title(r[1], r[3], r[4], r[2]),
            content=r[4],
            score=round(min(1.0, 0.45 + 0.55 * int(r[5]) / max_hits), 4),
        )
        for r in rows
    ]
    logger.info(
        "关键词检索『%s』grams=%s → %d 条（最高命中 %d）",
        question[:24], grams[:8], len(units), max_hits,
    )
    return units
