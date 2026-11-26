<template>
  <div class="wrap">
    <div class="page-head">
      <span class="ph-bar"></span>
      <h1>每日一方</h1>
      <div class="ph-extra">
        <span class="ph-date">{{ label }}</span>
      </div>
    </div>

    <div v-if="cur" class="card daily">
      <div class="d-top">
        <div class="d-title">
          <h2 class="d-name serif">{{ cur.name }}</h2>
          <p class="d-meta">
            {{ cur.herbs.length }} 味药<template v-if="cur.cases.length"> · {{ cur.cases.length }} 则医案</template>
          </p>
        </div>
        <span class="d-stamp">方</span>
      </div>

      <section class="d-sec">
        <h3 class="d-label">主治</h3>
        <p class="d-text">{{ cur.syndrome }}</p>
      </section>

      <section class="d-sec">
        <h3 class="d-label">组成</h3>
        <p class="d-herbs">
          <span v-for="(h, i) in cur.herbs" :key="h + i" class="herb">{{ h }}</span>
        </p>
      </section>

      <section v-if="cur.cases.length" class="d-sec">
        <h3 class="d-label">医案</h3>
        <RouterLink
          v-for="c in cur.cases"
          :key="c.id"
          :to="`/case/${c.id}`"
          class="case-row"
        >
          <span class="case-body">
            <span class="case-t">{{ c.title }}</span>
            <span class="case-s">{{ c.syndrome }}</span>
          </span>
          <span class="case-go">→</span>
        </RouterLink>
      </section>

      <div class="d-actions">
        <RouterLink class="btn primary" :to="`/formula/${cur.id}`">看方剂详情</RouterLink>
        <button class="btn ghost" @click="shuffle">换一首</button>
      </div>
    </div>

    <div class="past">
      <div class="past-head">
        <h3 class="past-t">往日</h3>
        <button class="past-today" @click="backToday">回到今天</button>
      </div>
      <div class="past-list">
        <button
          v-for="p in past"
          :key="p.key"
          :class="['past-item', { on: p.idx === curIdx }]"
          @click="pick(p.idx, p.full)"
        >
          <span class="pi-date">{{ p.date }}</span>
          <span class="pi-name">{{ p.name }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 每日一方 —— 打开就有内容，不用想搜什么。
 *
 * 数据来自 src/data/daily.json（由 scripts/gen_daily.py 从 PostgreSQL 真实数据生成）：
 * 90 首方名规范、主治完整、药味齐全的方剂，其中 85 首挂着真实医案。
 * 因为剂量字段在库里基本是空的，这里只列药名，不编造用量。
 *
 * 选方规则：以「距纪元的本地天数」对池子大小取模，同一天不论刷几次都是同一首；
 * 「往日」按同样规则回算前 6 天，所以历史不需要存，也不会和今天重复。
 */
import { computed, ref } from 'vue'
import daily from '@/data/daily.json'

interface DailyCase {
  id: string
  title: string
  syndrome: string
}
interface DailyItem {
  id: string
  name: string
  syndrome: string
  herbs: string[]
  cases: DailyCase[]
}

const items = (daily as { items: DailyItem[] }).items
const N = items.length

/** 距纪元的天数（按本地零点算，避免时区把「今天」算错一天） */
function seedOf(d: Date) {
  return Math.floor(new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime() / 86400000)
}
function idxOf(d: Date) {
  return ((seedOf(d) % N) + N) % N
}
const WEEK = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
function fullDate(d: Date) {
  return `${d.getMonth() + 1} 月 ${d.getDate()} 日 · ${WEEK[d.getDay()]}`
}

const todayIdx = idxOf(new Date())
const curIdx = ref(todayIdx)
const label = ref(fullDate(new Date()))

const cur = computed<DailyItem | undefined>(() => items[curIdx.value])

const past = computed(() => {
  const out: Array<{ key: number; idx: number; date: string; name: string; full: string }> = []
  for (let k = 1; k <= 6; k++) {
    const d = new Date()
    d.setDate(d.getDate() - k)
    const i = idxOf(d)
    out.push({
      key: k,
      idx: i,
      date: `${d.getMonth() + 1}-${d.getDate()}`,
      name: items[i].name,
      full: fullDate(d)
    })
  }
  return out
})

function pick(i: number, lb: string) {
  curIdx.value = i
  label.value = lb
}

function backToday() {
  pick(todayIdx, fullDate(new Date()))
}

function shuffle() {
  if (N < 2) return
  let next = curIdx.value
  while (next === curIdx.value) next = Math.floor(Math.random() * N)
  curIdx.value = next
  label.value = '随手一方'
}
</script>

<style scoped>
.ph-date {
  font-size: 13px;
  color: var(--text-3);
  letter-spacing: 0.5px;
}

/* ---------- 今日之方 ---------- */
.card.daily {
  padding: 26px 28px 24px;
}
.d-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
}
.d-name {
  font-size: clamp(26px, 3vw, 34px);
  font-weight: 700;
  letter-spacing: 3px;
  color: var(--text);
  line-height: 1.25;
}
.d-meta {
  margin-top: 6px;
  font-size: 13px;
  color: var(--text-3);
  letter-spacing: 0.5px;
}
/* 朱砂小印：整页唯一的一点暖色，不抢内容 */
.d-stamp {
  flex: none;
  width: 42px;
  height: 42px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  font-family: 'Noto Serif SC', 'Songti SC', Georgia, serif;
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  background: linear-gradient(150deg, #D9564A, #A8322A);
  box-shadow: 0 6px 16px rgba(178, 59, 46, 0.28);
}

.d-sec {
  padding: 16px 0;
  border-top: 1px solid rgba(10, 132, 255, 0.08);
}
.d-label {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--primary-deep);
  opacity: 0.72;
  margin-bottom: 8px;
}
.d-text {
  font-size: 15.5px;
  line-height: 1.95;
  color: var(--text-2);
}

.d-herbs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.herb {
  padding: 5px 14px;
  border-radius: 999px;
  background: rgba(10, 132, 255, 0.07);
  border: 1px solid rgba(10, 132, 255, 0.1);
  font-family: 'Noto Serif SC', 'Songti SC', Georgia, serif;
  font-size: 15px;
  letter-spacing: 1px;
  color: var(--text);
}

.case-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 11px 14px;
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.55);
  border: 1px solid rgba(10, 132, 255, 0.1);
  margin-bottom: 8px;
  transition: background 0.16s var(--ease), border-color 0.16s var(--ease);
}
.case-row:hover {
  background: rgba(255, 255, 255, 0.9);
  border-color: rgba(10, 132, 255, 0.3);
}
.case-body {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}
.case-t {
  font-size: 14.5px;
  font-weight: 700;
  color: var(--text);
}
.case-s {
  font-size: 13px;
  color: var(--text-3);
  line-height: 1.7;
}
.case-go {
  flex: none;
  margin-left: auto;
  font-size: 16px;
  color: var(--primary-deep);
  opacity: 0.55;
}

.d-actions {
  display: flex;
  gap: 12px;
  padding-top: 18px;
  border-top: 1px solid rgba(10, 132, 255, 0.08);
}

/* ---------- 往日 ---------- */
.past {
  margin-top: 20px;
}
.past-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 10px;
}
.past-t {
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--text-3);
}
.past-today {
  font-size: 12.5px;
  color: var(--primary-deep);
  opacity: 0.85;
}
.past-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.past-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.55);
  border: 1px solid var(--border);
  font-size: 13.5px;
  color: var(--text-2);
  transition: all 0.16s var(--ease);
}
.past-item:hover {
  background: #fff;
  box-shadow: var(--shadow-1);
}
.past-item.on {
  background: var(--primary);
  border-color: var(--primary);
  color: #fff;
}
.pi-date {
  font-size: 12px;
  opacity: 0.7;
  font-variant-numeric: tabular-nums;
}
.pi-name {
  font-family: 'Noto Serif SC', 'Songti SC', Georgia, serif;
  letter-spacing: 0.5px;
}

@media (max-width: 620px) {
  .card.daily { padding: 20px 16px 18px; }
  .d-name { font-size: 24px; letter-spacing: 2px; }
  .d-text { font-size: 14.8px; }
  .d-stamp { width: 36px; height: 36px; font-size: 17px; border-radius: 9px; }
  .past-item { padding: 7px 12px; font-size: 13px; }
}
</style>
