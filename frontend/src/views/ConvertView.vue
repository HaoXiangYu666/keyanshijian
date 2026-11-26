<template>
  <div class="page-head">
    <span class="ph-bar"></span>
    <h1 class="serif">古今剂量换算</h1>
  </div>

  <!-- ===== 单值换算 ===== -->
  <div class="card">
    <h3 style="margin-bottom:16px">单值换算</h3>

    <div class="era-tabs">
      <button
        v-for="e in ERAS"
        :key="e.key"
        class="era-btn"
        :class="{ on: eraKey === e.key }"
        @click="eraKey = e.key"
      >
        <b>{{ e.label }}</b>
        <span>{{ e.period }}</span>
      </button>
    </div>

    <div class="conv-row">
      <div class="field">
        <label>数量</label>
        <input v-model.number="amount" type="number" min="0" step="0.1" />
      </div>
      <div class="field">
        <label>单位</label>
        <select v-model="unit">
          <option v-for="u in era.units" :key="u.unit" :value="u.unit">
            {{ u.unit }}{{ u.kind === 'volume' ? '（容量）' : u.kind === 'count' ? '（枚计）' : '' }}
          </option>
        </select>
      </div>
      <div class="arrow">→</div>
      <div class="field result">
        <label>折算结果</label>
        <div class="big-result">
          <b>{{ fmt(converted) }}</b>
          <span>{{ resultUnit }}</span>
        </div>
      </div>
    </div>

    <div class="quick">
      <span class="muted" style="font-size:12px">常用：</span>
      <button
        v-for="q in quickList"
        :key="q.label"
        class="btn ghost sm"
        @click="applyQuick(q.amount, q.unit)"
      >{{ q.label }}</button>
    </div>

    <p v-if="eraKey === 'han'" class="han-toggle">
      <span class="muted" style="font-size:12px">汉制一两取</span>
      <button class="btn ghost sm" :class="{ 'is-on': hanLiang === 15.625 }" @click="setHan(15.625)">
        15.6 g（1斤=250g）
      </button>
      <button class="btn ghost sm" :class="{ 'is-on': hanLiang === 13.8 }" @click="setHan(13.8)">
        13.8 g（柯雪帆考据）
      </button>
    </p>

    <details class="note">
      <summary>参考依据</summary>
      <p>{{ era.source }}</p>
    </details>
  </div>

  <!-- ===== 整方折算 ===== -->
  <div class="card" style="margin-top:16px">
    <div class="preset-head">
      <div>
        <h3>整方折算</h3>
      </div>
      <div class="preset-btns">
        <button v-for="p in PRESETS" :key="p.name" class="btn ghost sm" @click="loadPreset(p)">
          载入{{ p.name }}
        </button>
        <button class="btn ghost sm" @click="clearRows">清空</button>
      </div>
    </div>

    <table class="rx-table">
      <thead>
        <tr>
          <th style="width:34%">药味</th>
          <th style="width:20%">数量</th>
          <th style="width:24%">单位</th>
          <th style="width:14%">折合</th>
          <th style="width:8%"></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(r, i) in rows" :key="i">
          <td><input v-model="r.name" placeholder="如：桂枝" /></td>
          <td><input v-model.number="r.amount" type="number" min="0" step="0.1" /></td>
          <td>
            <select v-model="r.unit">
              <option v-for="u in era.units" :key="u.unit" :value="u.unit">{{ u.unit }}</option>
            </select>
          </td>
          <td class="cell-gram">{{ fmt(rowGram(r)) }} <span class="unit-s">g</span></td>
          <td>
            <button class="del" title="删除该行" @click="rows.splice(i, 1)">×</button>
          </td>
        </tr>
      </tbody>
    </table>

    <button class="btn ghost sm" style="margin-top:10px" @click="addRow">+ 加一味</button>

    <div v-if="totalGram > 0" class="summary">
      <div class="sum-head">
        <span>全方总重</span>
        <b>{{ fmt(totalGram) }} g</b>
      </div>
      <div class="bars">
        <div v-for="b in shares" :key="b.name + b.gram" class="bar-row">
          <span class="bar-name">{{ b.name || '未命名' }}</span>
          <div class="bar-track">
            <div class="bar-fill" :style="{ width: b.pct + '%' }"></div>
          </div>
          <span class="bar-val">{{ b.pct }}%</span>
        </div>
      </div>
    </div>
    <p v-else class="muted" style="margin-top:14px">录入药味与数量后，这里会显示总重与占比。</p>
  </div>

  <p class="disclaimer">
    折算依据历代度量衡考据整理，同一朝代不同学者结论略有出入，仅供读古籍时估算参考。
  </p>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

type UnitKind = 'weight' | 'volume' | 'count'

interface UnitDef {
  unit: string
  /** 折合克数（容量单位则折合毫升） */
  gram: number
  kind: UnitKind
}

interface Era {
  key: string
  label: string
  period: string
  source: string
  units: UnitDef[]
}

/** 各朝代度量衡（重量折克、容量折毫升）。数值取通行考据，页面已注明出处与不确定性。 */
const ERAS: Era[] = [
  {
    key: 'han',
    label: '汉制',
    period: '东汉 · 伤寒论',
    source:
      '依据：东汉一两约 13.8～15.6 g（1 斤 = 16 两 = 250 g，1 两 = 24 铢）；1 升 ≈ 200 ml，1 合 = 20 ml。张仲景方多用此制。',
    units: [
      { unit: '两', gram: 15.625, kind: 'weight' },
      { unit: '斤', gram: 250, kind: 'weight' },
      { unit: '铢', gram: 0.651, kind: 'weight' },
      { unit: '分', gram: 3.906, kind: 'weight' },
      { unit: '升', gram: 200, kind: 'volume' },
      { unit: '合', gram: 20, kind: 'volume' },
      { unit: '方寸匕', gram: 2.7, kind: 'weight' },
      { unit: '枚', gram: 3, kind: 'count' }
    ]
  },
  {
    key: 'song',
    label: '宋制',
    period: '宋 · 局方',
    source:
      '依据：宋代秤制增大，1 斤 ≈ 640 g，1 两 = 40 g，1 钱 = 4 g，1 分 = 0.4 g；1 升 ≈ 702 ml。宋代方书开始大量用「钱」。',
    units: [
      { unit: '两', gram: 40, kind: 'weight' },
      { unit: '斤', gram: 640, kind: 'weight' },
      { unit: '钱', gram: 4, kind: 'weight' },
      { unit: '分', gram: 0.4, kind: 'weight' },
      { unit: '字', gram: 1, kind: 'weight' },
      { unit: '升', gram: 702, kind: 'volume' },
      { unit: '合', gram: 70.2, kind: 'volume' },
      { unit: '枚', gram: 3, kind: 'count' }
    ]
  },
  {
    key: 'mingqing',
    label: '明清制',
    period: '明 · 清',
    source:
      '依据：明清库平制 1 斤 ≈ 596.8 g，1 两 = 37.3 g，1 钱 = 3.73 g，1 分 = 0.373 g，1 厘 = 0.037 g。',
    units: [
      { unit: '两', gram: 37.3, kind: 'weight' },
      { unit: '斤', gram: 596.8, kind: 'weight' },
      { unit: '钱', gram: 3.73, kind: 'weight' },
      { unit: '分', gram: 0.373, kind: 'weight' },
      { unit: '厘', gram: 0.0373, kind: 'weight' },
      { unit: '枚', gram: 3, kind: 'count' }
    ]
  },
  {
    key: 'modern',
    label: '现代',
    period: '市制 / 教材',
    source:
      '依据：现行市制 1 斤 = 500 g、1 两 = 50 g、1 钱 = 5 g（十两制）；1959 年前旧市制为 1 斤 = 16 两，1 两 = 31.25 g。',
    units: [
      { unit: '两', gram: 50, kind: 'weight' },
      { unit: '斤', gram: 500, kind: 'weight' },
      { unit: '钱', gram: 5, kind: 'weight' },
      { unit: '克', gram: 1, kind: 'weight' },
      { unit: '毫升', gram: 1, kind: 'volume' },
      { unit: '枚', gram: 3, kind: 'count' }
    ]
  }
]

const eraKey = ref('han')
const era = computed(() => ERAS.find((e) => e.key === eraKey.value) ?? ERAS[0])

/** 汉制一两的两种通行取值，切换后即时重算 */
const hanLiang = ref(15.625)
function setHan(v: number) {
  hanLiang.value = v
  // 同步改 era.units 里的「两」「铢」「分」，保持三者的 1:24:4 关系
  const han = ERAS[0]
  const liang = han.units.find((u) => u.unit === '两')
  const zhu = han.units.find((u) => u.unit === '铢')
  const fen = han.units.find((u) => u.unit === '分')
  if (liang) liang.gram = v
  if (zhu) zhu.gram = round(v / 24)
  if (fen) fen.gram = round(v / 4)
}

function round(n: number) {
  return Math.round(n * 1000) / 1000
}

const amount = ref(3)
const unit = ref('两')

const currentUnit = computed(() => era.value.units.find((u) => u.unit === unit.value))
const converted = computed(() => (Number(amount.value) || 0) * (currentUnit.value?.gram ?? 0))
const resultUnit = computed(() => (currentUnit.value?.kind === 'volume' ? 'ml' : 'g'))

const quickList = computed(() => {
  const u = era.value.units
  if (eraKey.value === 'han') {
    return [
      { label: '三两', amount: 3, unit: '两' },
      { label: '半斤', amount: 0.5, unit: '斤' },
      { label: '一升', amount: 1, unit: '升' },
      { label: '一方寸匕', amount: 1, unit: '方寸匕' }
    ].filter((q) => u.some((x) => x.unit === q.unit))
  }
  return [
    { label: '一钱', amount: 1, unit: '钱' },
    { label: '一两', amount: 1, unit: '两' },
    { label: '半两', amount: 0.5, unit: '两' }
  ].filter((q) => u.some((x) => x.unit === q.unit))
})

function applyQuick(a: number, u: string) {
  unit.value = u
  amount.value = a
}

function fmt(n: number): string {
  if (!Number.isFinite(n)) return '—'
  if (n === 0) return '0'
  if (n >= 100) return n.toFixed(0)
  if (n >= 10) return n.toFixed(1)
  return n.toFixed(2).replace(/\.?0+$/, '')
}

/** ===== 整方折算 ===== */
interface Row {
  name: string
  amount: number | string
  unit: string
}

const rows = ref<Row[]>([
  { name: '桂枝', amount: 3, unit: '两' },
  { name: '芍药', amount: 3, unit: '两' },
  { name: '甘草', amount: 2, unit: '两' },
  { name: '生姜', amount: 3, unit: '两' },
  { name: '大枣', amount: 12, unit: '枚' }
])

/** 经典方示例：只录原文剂量，折算交给上面的表 */
const PRESETS = [
  {
    name: '桂枝汤',
    rows: [
      { name: '桂枝', amount: 3, unit: '两' },
      { name: '芍药', amount: 3, unit: '两' },
      { name: '甘草', amount: 2, unit: '两' },
      { name: '生姜', amount: 3, unit: '两' },
      { name: '大枣', amount: 12, unit: '枚' }
    ] as Row[]
  },
  {
    name: '麻黄汤',
    rows: [
      { name: '麻黄', amount: 3, unit: '两' },
      { name: '桂枝', amount: 2, unit: '两' },
      { name: '杏仁', amount: 70, unit: '枚' },
      { name: '甘草', amount: 1, unit: '两' }
    ] as Row[]
  }
]

function loadPreset(p: { name: string; rows: Row[] }) {
  eraKey.value = 'han'
  unit.value = '两'
  rows.value = p.rows.map((r) => ({ ...r }))
}

function addRow() {
  rows.value.push({ name: '', amount: 1, unit: era.value.units[0]?.unit ?? '两' })
}

function clearRows() {
  rows.value = []
}

function rowGram(r: Row): number {
  const u = era.value.units.find((x) => x.unit === r.unit)
  return (Number(r.amount) || 0) * (u?.gram ?? 0)
}

const totalGram = computed(() => rows.value.reduce((s, r) => s + rowGram(r), 0))

const shares = computed(() => {
  const total = totalGram.value
  if (total <= 0) return []
  return rows.value
    .map((r) => {
      const g = rowGram(r)
      return { name: r.name, gram: g, pct: Math.round((g / total) * 1000) / 10 }
    })
    .filter((x) => x.gram > 0)
    .sort((a, b) => b.gram - a.gram)
})
</script>

<style scoped>
.era-tabs {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 20px;
}

.era-btn {
  display: flex;
  flex-direction: column;
  gap: 3px;
  padding: 12px 10px;
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  text-align: left;
  font: inherit;
  transition: all 0.18s var(--ease, ease);
}

.era-btn:hover {
  border-color: #9dc6b0;
}

.era-btn.on {
  border-color: #2f6a4f;
  background: rgba(47, 106, 79, 0.08);
  box-shadow: inset 0 0 0 1px #2f6a4f;
}

.era-btn b {
  font-size: 15px;
  color: var(--primary-deep, #1f4d38);
}

.era-btn span {
  font-size: 11.5px;
  color: #6b7280;
}

.conv-row {
  display: flex;
  align-items: flex-end;
  gap: 14px;
  flex-wrap: wrap;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field label {
  font-size: 12px;
  color: #6b7280;
}

.field input,
.field select,
.rx-table input,
.rx-table select {
  padding: 9px 12px;
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 8px;
  font: inherit;
  color: inherit;
  background: rgba(255, 255, 255, 0.7);
  min-width: 110px;
}

.field input:focus,
.field select:focus,
.rx-table input:focus,
.rx-table select:focus {
  outline: none;
  border-color: #2f6a4f;
}

.arrow {
  font-size: 20px;
  color: #9ca3af;
  padding-bottom: 8px;
}

.result {
  flex: 1;
  min-width: 180px;
}

.big-result {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.big-result b {
  font-size: 34px;
  line-height: 1;
  color: #2f6a4f;
  font-variant-numeric: tabular-nums;
}

.big-result span {
  font-size: 14px;
  color: #6b7280;
}

.quick {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 18px;
}

.han-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 12px;
}

.han-toggle .is-on {
  border-color: #2f6a4f;
  color: #2f6a4f;
  font-weight: 700;
}

.note {
  margin-top: 14px;
  padding: 0;
  border-radius: 8px;
  background: rgba(47, 106, 79, 0.06);
  font-size: 12.5px;
  line-height: 1.65;
  color: #4b5563;
}

.note summary {
  padding: 9px 12px;
  cursor: pointer;
  color: #6b7280;
  list-style: none;
  user-select: none;
}

.note summary::-webkit-details-marker {
  display: none;
}

.note summary::before {
  content: "＋";
  margin-right: 6px;
  font-size: 11px;
}

.note[open] summary::before {
  content: "－";
}

.note p {
  margin: 0;
  padding: 0 12px 10px;
}

.preset-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 14px;
}

.preset-btns {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.rx-table {
  width: 100%;
  border-collapse: collapse;
}

.rx-table th {
  text-align: left;
  font-size: 12px;
  font-weight: 500;
  color: #6b7280;
  padding: 0 6px 8px;
}

.rx-table td {
  padding: 4px 6px;
}

.rx-table input,
.rx-table select {
  width: 100%;
  min-width: 0;
}

.cell-gram {
  font-variant-numeric: tabular-nums;
  color: #2f6a4f;
  font-weight: 700;
  white-space: nowrap;
}

.unit-s {
  font-weight: 400;
  font-size: 12px;
  color: #9ca3af;
}

.del {
  border: 0;
  background: transparent;
  color: #b91c1c;
  font-size: 18px;
  line-height: 1;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
}

.del:hover {
  background: rgba(185, 28, 28, 0.08);
}

.summary {
  margin-top: 22px;
  padding-top: 18px;
  border-top: 1px dashed var(--border, #e5e7eb);
}

.sum-head {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 14px;
}

.sum-head span {
  font-size: 13px;
  color: #6b7280;
}

.sum-head b {
  font-size: 26px;
  color: #2f6a4f;
  font-variant-numeric: tabular-nums;
}

.bars {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.bar-row {
  display: grid;
  grid-template-columns: 88px 1fr 56px;
  align-items: center;
  gap: 10px;
}

.bar-name {
  font-size: 13px;
  color: #374151;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.bar-track {
  height: 10px;
  border-radius: 999px;
  background: rgba(47, 106, 79, 0.1);
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #4f9e78, #2f6a4f);
}

.bar-val {
  font-size: 12.5px;
  color: #6b7280;
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.disclaimer {
  margin-top: 22px;
  font-size: 12px;
  color: #9ca3af;
  line-height: 1.7;
}

@media (max-width: 720px) {
  .era-tabs {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .big-result b {
    font-size: 28px;
  }

  .bar-row {
    grid-template-columns: 64px 1fr 48px;
  }
}
</style>
