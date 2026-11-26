# -*- coding: utf-8 -*-
"""生成「每日一方」的本地数据（不依赖后端接口，离线也能看）。

筛选口径：
  1. 方名规范 —— 排除抽取残留（「某某证治」不是方名）与证候名（「气营两燔」「热入心包」
     这类只有证、没有方），只保留以剂型字结尾的：汤/散/丸/丹/煎/饮/膏/胶/酒/茶
  2. 主治非空
  3. 药味 >= 3 且药名干净（纯汉字，排除 "1"、"1." 这种解析碎片）
  4. 按方名去重，同名保留药味最全的那条

药味剂量在库里基本为空（931 行只有 67 行有），所以只输出药名，不编造剂量。

运行：D:/tools/venvs/herbmind/Scripts/python.exe scripts/gen_daily.py
"""
import json
import os
import random
import re

import psycopg

# 池子按方名排序相邻性太强（连日都是「桂枝xx汤」），
# 用固定种子打散一次写进 JSON —— 之后顺序不再变，所以同一天取到的永远是同一首。
random.seed(20261126)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'data', 'daily.json')


def clean(s):
    if not s:
        return ''
    s = re.sub(r'\s+', ' ', str(s))
    s = s.replace('【', '').replace('】', '').strip()
    return s


def clip(s, n):
    s = clean(s)
    return s if len(s) <= n else s[:n].rstrip('，。；、 ') + '…'


POOL_SQL = """
with pool as (
  select f.id, f.name, f.syndrome_text, count(fh.id) as herbs
  from formula f
  join formula_herb fh on fh.formula_id = f.id
  where f.syndrome_text is not null and f.syndrome_text <> ''
    and f.name !~ '(证治|证$|^见|、|节)'
    and f.name ~ '(汤|散|丸|丹|煎|饮|膏|胶|酒|茶)$'
    and fh.herb_name ~ '^[一-龥]{1,5}$'
  group by f.id, f.name, f.syndrome_text
  having count(fh.id) >= 3
), ranked as (
  select *, row_number() over (partition by name order by herbs desc, id) as rn
  from pool
)
select id, name, syndrome_text, herbs from ranked where rn = 1 order by name
"""

HERB_SQL = """
select herb_name from formula_herb
where formula_id = %s and herb_name ~ '^[一-龥]{1,5}$'
order by seq nulls last, herb_name
"""

# 医案按「方名」关联，而不是单个 id：同名方在库里可能有多条记录，
# 去重时保留下来的那条不一定是医案挂靠的那条。
CASE_SQL = """
select c.id, c.title, c.syndrome_text
from case_record c
join formula f on f.id = c.main_formula_id
where f.name = %s
order by c.id
limit 3
"""


def main():
    conn = psycopg.connect('host=127.0.0.1 dbname=herbmind user=postgres password=postgres')
    cur = conn.cursor()

    cur.execute(POOL_SQL)
    pool = cur.fetchall()

    items = []
    for fid, name, syndrome, _ in pool:
        cur.execute(HERB_SQL, (fid,))
        herbs = [r[0] for r in cur.fetchall()]
        if len(herbs) < 3:
            continue

        cur.execute(CASE_SQL, (name,))
        cases = [
            {'id': cid, 'title': clip(title, 40), 'syndrome': clip(syn, 56)}
            for cid, title, syn in cur.fetchall()
        ]

        # 每日一方要让人看见「这个方实际怎么用」，所以只收挂得住真实医案的方。
        # 没有医案的方在方剂详情里仍可查到，不必占每日名额。
        if not cases:
            continue

        items.append({
            'id': fid,
            'name': name,
            'syndrome': clip(syndrome, 300),
            'herbs': herbs,
            'cases': cases,
        })

    random.shuffle(items)

    data = {
        'version': 1,
        'generatedAt': '2026-11-26',
        'source': 'PostgreSQL herbmind：formula / formula_herb / case_record',
        'count': len(items),
        'items': items,
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

    size = os.path.getsize(OUT) / 1024
    with_case = sum(1 for i in items if i['cases'])
    print(f'已生成 {OUT}')
    print(f'方剂 {len(items)} 首（含医案 {with_case} 首），文件 {size:.1f} KB')


if __name__ == '__main__':
    main()
