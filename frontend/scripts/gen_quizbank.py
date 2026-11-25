# -*- coding: utf-8 -*-
"""从本地 PostgreSQL 真实数据生成静态选择题库（不依赖后端接口）。

每题带 chapter（章节：伤寒论/温病学/金匮要略）与 explain（答对/答错都显示的实质解析）。
运行：D:/tools/venvs/herbmind/Scripts/python.exe scripts/gen_quizbank.py
"""
import json, os, re, random
import psycopg

random.seed(20261125)
conn = psycopg.connect('host=127.0.0.1 dbname=herbmind user=postgres')


def fetch(sql):
    return conn.execute(sql).fetchall()


def clean(s):
    if not s:
        return ''
    s = re.sub(r'\s+', ' ', str(s))
    s = s.replace('【', '').replace('】', '').replace('（', '(').replace('）', ')')
    s = re.sub(r'^\[原文\]\s*', '', s)
    return s.strip()


def shorten(s, n=70):
    s = clean(s)
    return s if len(s) <= n else s[:n].rstrip('，。、；,;') + '…'


def make(cat, chapter, stem, answer, pool, explain, need=3):
    """生成一题：answer 为正确答案，pool 为干扰项来源，explain 为实质解析。"""
    distract = []
    for x in random.sample(list(pool), min(len(pool), 60)):
        x = clean(x)
        if x and x != answer and x not in distract and len(x) <= 18:
            distract.append(x)
        if len(distract) >= need:
            break
    if len(distract) < need:
        return None
    opts = distract[:need] + [answer]
    random.shuffle(opts)
    return {
        'category': cat,
        'chapter': chapter,
        'stem': clean(stem),
        'answer': answer,
        'options': opts,
        'explain': clean(explain),
    }


# 章节名映射：classic 字段 -> 章节显示名
CHAPTER = {
    '伤寒论': '伤寒论',
    '温病学': '温病学',
    '金匮要略': '金匮要略',
}

bank = {'version': 2, 'questions': []}

# 方剂池（按章节分组）：name -> classic
formula_rows = fetch("""
    SELECT f.name, coalesce(cu.meta_jsonb->>'classic','') AS classic
    FROM formula f
    LEFT JOIN LATERAL (
        SELECT meta_jsonb FROM content_unit
        WHERE ref_type='formula' AND ref_id=f.id LIMIT 1
    ) cu ON true
    WHERE f.name ~ '^[一-龥]{2,12}$'
""")
formula_classic = {}
for name, classic in formula_rows:
    n = clean(name)
    if n and n not in formula_classic:
        formula_classic[n] = CHAPTER.get(classic, '')
all_names = list(formula_classic.keys())

# ---------- 1. 辨证选方：证候 -> 方剂 ----------
rows = fetch("""
    SELECT f.name, f.syndrome_text, coalesce(cu.meta_jsonb->>'classic','') AS classic
    FROM formula f
    JOIN content_unit cu ON cu.ref_type='formula' AND cu.ref_id=f.id
    WHERE f.syndrome_text IS NOT NULL AND length(f.syndrome_text) BETWEEN 10 AND 120
      AND f.name ~ '^[一-龥]{2,12}$'
""")
items = [(clean(n), clean(s), CHAPTER.get(c, '')) for n, s, c in rows]
random.shuffle(items)
count = 0
for name, syn, chapter in items:
    if not name or not syn or not chapter:
        continue
    stem = '患者见「%s」，最宜选用哪首方剂？' % shorten(syn, 58)
    explain = '「%s」是《%s》%s的主治证候，故选%s。' % (shorten(syn, 42), chapter, name, name)
    q = make('辨证选方', chapter, stem, name, all_names, explain)
    if q:
        bank['questions'].append(q)
        count += 1
    if count >= 18:  # 每章 6 题
        break
# 保证每章都有题：按章节配额重做
per_chapter = 6
bank['questions'] = [q for q in bank['questions'] if q['category'] == '辨证选方']
for ch in CHAPTER.values():
    have = sum(1 for q in bank['questions'] if q['chapter'] == ch)
    if have >= per_chapter:
        continue
    pool = [it for it in items if it[2] == ch]
    for name, syn, _ in pool:
        if have >= per_chapter:
            break
        if not name or not syn:
            continue
        stem = '患者见「%s」，最宜选用哪首方剂？' % shorten(syn, 58)
        explain = '「%s」是《%s》%s主治的证候，辨证属此方，故选%s。' % (shorten(syn, 42), ch, name, name)
        q = make('辨证选方', ch, stem, name, all_names, explain)
        if q:
            bank['questions'].append(q)
            have += 1

# ---------- 2. 条文选方：条文描述 -> 方剂 ----------
quotes = fetch("SELECT content, coalesce(meta_jsonb->>'classic','') AS classic FROM content_unit WHERE unit_type='quote' OR content LIKE '%主之%'")
pairs = []
for content, classic in quotes:
    text = clean(content)
    ch = CHAPTER.get(classic, '')
    if not ch:
        continue
    # 去掉"方剂：XX 组成：… 经典条文："这类 ETL 包装前缀，只留条文正文
    text = re.sub(r'^方剂：[^\n]{1,20}\s*(组成：[^\n]*)?\s*经典条文：', '', text)
    text = re.sub(r'^\[原文\]\s*', '', text)
    for m in re.finditer(r'([^。；;]{6,90}?[者证]\s*[，,]?\s*)([\u4e00-\u9fa5]{2,8}(?:汤|散|丸|饮|膏))主之', text):
        desc, formula = m.group(1), m.group(2)
        desc = re.sub(r'^\d+[\.、]\s*', '', desc).strip('，, ')
        if len(desc) >= 8 and len(formula) >= 2:
            pairs.append((desc, formula, ch))
random.shuffle(pairs)
used_desc = set()
count = 0
per_ch = 5
ch_count = {c: 0 for c in CHAPTER.values()}
for desc, formula, ch in pairs:
    if desc in used_desc or ch_count[ch] >= per_ch:
        continue
    used_desc.add(desc)
    stem = '「%s」——此条文所述应当选用哪首方剂？' % shorten(desc, 60)
    explain = '《%s》原文载「%s…%s主之」，故本证用%s。' % (ch, shorten(desc, 30), formula, formula)
    q = make('条文选方', ch, stem, formula, all_names, explain)
    if q:
        bank['questions'].append(q)
        ch_count[ch] += 1
        count += 1
    if count >= 15:
        break

# ---------- 3. 典籍归属：条文 -> 出自哪部经典 ----------
classic_names = list(CHAPTER.keys())
qrows = fetch("""
    SELECT q.content, coalesce(q.meta_jsonb->>'classic','') AS classic
    FROM content_unit q
    WHERE (q.unit_type='quote' OR q.content LIKE '%主之%')
      AND length(q.content) >= 40
      AND coalesce(q.meta_jsonb->>'classic','') IN ('伤寒论','温病学','金匮要略')
""")
random.shuffle(qrows)
count = 0
per_ch = 4
ch_count = {c: 0 for c in CHAPTER.values()}
for content, classic in qrows:
    name = CHAPTER.get(classic, '')
    if not name or ch_count[name] >= per_ch:
        continue
    text = clean(content)
    text = re.sub(r'^\d+[\.、]\s*', '', text)
    text = re.sub(r'^[A-D][、.．]\s*', '', text)
    text = re.sub(r'^《[^》]{2,20}》\s*\d*\s*条?\s*', '', text)
    stem = '「%s」这段条文出自哪部经典？' % shorten(text, 72)
    explain = '该条文的内容与病机论述出自《%s》，是%s的核心篇章。' % (name, name)
    q = make('典籍归属', name, stem, name, classic_names, explain, need=2)
    if q:
        bank['questions'].append(q)
        ch_count[name] += 1
        count += 1
    if count >= 12:
        break

# ---------- 4. 方药对应：方剂 -> 组成药物 ----------
herbs = fetch("""
    SELECT f.name, fh.herb_name, coalesce(cu.meta_jsonb->>'classic','') AS classic
    FROM formula_herb fh
    JOIN formula f ON f.id = fh.formula_id
    LEFT JOIN LATERAL (
        SELECT meta_jsonb FROM content_unit
        WHERE ref_type='formula' AND ref_id=f.id LIMIT 1
    ) cu ON true
    WHERE fh.seq = 1 AND f.name ~ '^[一-龥]{2,10}$'
""")
valid_herb = []
for name, herb, classic in herbs:
    h = clean(herb)
    h = re.split(r'[（(\.。,，]', h)[0]
    if 2 <= len(h) <= 6 and re.fullmatch(r'[一-龥]+', h) and clean(name) in formula_classic:
        valid_herb.append((clean(name), h, CHAPTER.get(classic, '')))
all_herbs = sorted(set(h for _, h, _ in valid_herb))
random.shuffle(valid_herb)
used_formula = set()
count = 0
per_ch = 4
ch_count = {c: 0 for c in CHAPTER.values()}
for name, herb, ch in valid_herb:
    if name in used_formula or not ch or ch_count[ch] >= per_ch:
        continue
    used_formula.add(name)
    stem = '《%s》方剂「%s」的组成中，首先配伍的药物是？' % (ch, name)
    explain = '%s以%s为君药/首选药，体现了该方的核心治法，故首味药为%s。' % (name, herb, herb)
    q = make('方药对应', ch, stem, herb, all_herbs, explain)
    if q:
        bank['questions'].append(q)
        ch_count[ch] += 1
        count += 1
    if count >= 12:
        break

random.shuffle(bank['questions'])
out = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', 'data', 'quizbank.json')
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, 'w', encoding='utf-8') as f:
    json.dump(bank, f, ensure_ascii=False, indent=1)

from collections import Counter
print('written:', out)
print('total:', len(bank['questions']))
print('by category:', dict(Counter(q['category'] for q in bank['questions'])))
print('by chapter:', dict(Counter(q['chapter'] for q in bank['questions'])))
missing = [i for i, q in enumerate(bank['questions']) if not q.get('explain') or not q.get('chapter')]
print('missing explain/chapter:', missing[:10], 'count', len(missing))
conn.close()
