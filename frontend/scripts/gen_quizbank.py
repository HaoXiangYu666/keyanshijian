# -*- coding: utf-8 -*-
"""从本地 PostgreSQL 真实数据生成静态选择题库（不依赖后端接口）。"""
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


def make(cat, stem, answer, pool, hint='', need=3):
    """生成一题：answer 为正确答案，pool 为干扰项来源，need 为需要的干扰项数量。"""
    distract = []
    for x in random.sample(list(pool), min(len(pool), 40)):
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
        'stem': clean(stem),
        'answer': answer,
        'options': opts,
        'hint': clean(hint),
    }


bank = {'version': 1, 'questions': []}

# ---------- 1. 辨证选方：证候 -> 方剂 ----------
formulas = fetch("""
    SELECT name, syndrome_text FROM formula
    WHERE syndrome_text IS NOT NULL AND length(syndrome_text) BETWEEN 10 AND 120
      AND name ~ '^[一-龥]{2,12}$'
""")
all_names = [clean(r[0]) for r in fetch("SELECT name FROM formula WHERE name ~ '^[一-龥]{2,12}$'")]
items = [(clean(n), clean(s)) for n, s in formulas]
random.shuffle(items)
count = 0
for name, syn in items:
    if not name or not syn:
        continue
    stem = '患者见「%s」，最宜选用哪首方剂？' % shorten(syn, 60)
    q = make('辨证选方', stem, name, all_names, '依据方剂主治证候判断')
    if q:
        bank['questions'].append(q)
        count += 1
    if count >= 18:
        break

# ---------- 2. 条文选方：条文描述 -> 方剂 ----------
quotes = fetch("SELECT content, classic_id FROM classic_quote WHERE content IS NOT NULL")
# 抽取「…者，XX汤主之」结构
pairs = []
for content, cid in quotes:
    text = clean(content)
    for m in re.finditer(r'([^。；;]{6,90}?[者证]\s*[，,]?\s*)([\u4e00-\u9fa5]{2,8}(?:汤|散|丸|饮|膏))主之', text):
        desc, formula = m.group(1), m.group(2)
        desc = re.sub(r'^\d+[\.、]\s*', '', desc).strip('，, ')
        if len(desc) >= 8 and len(formula) >= 2:
            pairs.append((desc, formula))
random.shuffle(pairs)
used_desc = set()
count = 0
for desc, formula in pairs:
    if desc in used_desc:
        continue
    used_desc.add(desc)
    stem = '「%s」——此条文所述应当选用哪首方剂？' % shorten(desc, 62)
    q = make('条文选方', stem, formula, all_names, '出自《伤寒杂病论》条文')
    if q:
        bank['questions'].append(q)
        count += 1
    if count >= 16:
        break

# ---------- 3. 典籍归属：条文 -> 出自哪部经典 ----------
classic_name = dict((cid, clean(name)) for cid, name in fetch('SELECT id, name FROM classic'))
classic_names = list(classic_name.values())
qrows = fetch("""
    SELECT q.content, q.classic_id FROM classic_quote q
    WHERE q.content IS NOT NULL AND length(q.content) >= 40
""")
random.shuffle(qrows)
count = 0
for content, cid in qrows:
    name = classic_name.get(cid)
    if not name:
        continue
    text = clean(content)
    text = re.sub(r'^\d+[\.、]\s*', '', text)
    # 去掉选项标记和书名号前缀噪声，取一段连续正文
    text = re.sub(r'^[A-D][、.．]\s*', '', text)
    text = re.sub(r'^《[^》]{2,20}》\s*\d*\s*条?\s*', '', text)
    stem = '「%s」这段条文出自哪部经典？' % shorten(text, 76)
    q = make('典籍归属', stem, name, classic_names, '三部经典：伤寒论 / 金匮要略 / 温病学', need=2)
    if q:
        bank['questions'].append(q)
        count += 1
    if count >= 12:
        break

# ---------- 4. 方药对应：方剂 -> 组成药物 ----------
herbs = fetch("""
    SELECT f.name, fh.herb_name FROM formula_herb fh
    JOIN formula f ON f.id = fh.formula_id
    WHERE fh.seq = 1 AND f.name ~ '^[一-龥]{2,10}$'
""")
valid_herb = []
for name, herb in herbs:
    h = clean(herb)
    h = re.split(r'[（(\.。,，]', h)[0]
    if 2 <= len(h) <= 6 and re.fullmatch(r'[一-龥]+', h):
        valid_herb.append((clean(name), h))
all_herbs = sorted(set(h for _, h in valid_herb))
random.shuffle(valid_herb)
used_formula = set()
count = 0
for name, herb in valid_herb:
    if name in used_formula:
        continue
    used_formula.add(name)
    stem = '方剂「%s」的组成中，首先配伍的药物是？' % name
    q = make('方药对应', stem, herb, all_herbs, '考查方剂药物组成')
    if q:
        bank['questions'].append(q)
        count += 1
    if count >= 14:
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
conn.close()
