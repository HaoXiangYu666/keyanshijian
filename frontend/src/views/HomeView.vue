<template>
  <div>
    <!-- 加载态 -->
    <section v-if="loading" class="card">
      <p class="muted">首页加载中…</p>
    </section>

    <!-- 请求失败态 -->
    <section v-else-if="error" class="card">
      <h3>首页加载失败</h3>
      <p class="muted" style="margin-top:6px">{{ error }}</p>
      <p class="muted" style="margin-top:10px">
        请确认后端已启动（BFF :8090 / svc-catalog :8082），且已导入数据快照。
      </p>
      <button class="btn ghost sm" style="margin-top:14px" @click="load">重试</button>
    </section>

    <!-- 空数据态 -->
    <section v-else-if="!home" class="card">
      <h3>暂无首页数据</h3>
      <p class="muted" style="margin-top:6px">
        后端已响应，但没有返回可展示的首页内容。请先导入语料，或稍后重试。
      </p>
      <div style="display:flex;gap:10px;margin-top:14px;flex-wrap:wrap">
        <RouterLink class="btn primary sm" to="/shelf/import">导入语料</RouterLink>
        <button class="btn ghost sm" @click="load">重试</button>
      </div>
    </section>

    <template v-else>
      <p v-if="degraded.length" class="muted" style="margin-bottom:12px">
        ⚠ 部分服务暂不可用：{{ degraded.join('、') }}
      </p>

      <!-- 蓝色横幅（图片样式）+ 语义检索 -->
      <section class="hb-hero">
        <div class="hb-hero-copy">
          <p class="hb-eyebrow">HERBMIND · 本草心智 · 多语料中医知识平台</p>
          <h1>正是读书<span>好时节</span></h1>
          <p class="hb-sub">
            经方检索 · 临床思维练习 · 科研挖掘，让方证知识可查、可练、可问、可推演、可看见。
          </p>
          <form class="hb-search" @submit.prevent="goSearch()">
            <input
              v-model="keyword"
              class="hb-input"
              placeholder="试试：无汗而喘、脉浮紧用什么方 / 桂枝汤的组成"
              aria-label="语义检索"
            >
            <button class="hb-search-btn" type="submit">智能检索</button>
          </form>
          <div v-if="hotKeywords.length" class="hb-hot">
            <button
              v-for="k in hotKeywords"
              :key="k"
              type="button"
              class="hb-chip"
              @click="goSearch(k)"
            >{{ k }}</button>
          </div>
        </div>
        <div class="hb-hero-art" aria-hidden="true">
          <svg viewBox="0 0 420 240" fill="none">
            <ellipse cx="215" cy="220" rx="160" ry="12" fill="rgba(4,60,110,.18)"/>
            <path d="M70 150c42-26 92-26 135 0v64c-43-24-93-24-135 0v-64Z" fill="#fff" opacity=".96"/>
            <path d="M205 150c43-26 93-26 135 0v64c-42-24-92-24-135 0v-64Z" fill="#eef6ff"/>
            <path d="M70 150c42-26 92-26 135 0M205 150c43-26 93-26 135 0" stroke="#bcd9f2" stroke-width="2"/>
            <path d="M70 214c43-24 93-24 135 0 42-24 92-24 135 0" stroke="#d8e9f8" stroke-width="6" stroke-linecap="round"/>
            <path d="M250 92c0-17 13-30 30-30s30 13 30 30-13 30-30 30-30-13-30-30Z" fill="#f4c7a4"/>
            <path d="M250 88c-3-20 12-34 30-34 17 0 31 12 31 30-8-6-17-8-26-6-12 2-22 0-35-10Z" fill="#4a3328"/>
            <circle cx="312" cy="58" r="10" fill="#4a3328"/>
            <path d="M246 122c8-10 20-14 34-14s26 4 34 14l12 62h-92l12-62Z" fill="#e95d57"/>
            <path d="M252 132c-16 8-28 22-34 38l16 8c8-14 17-23 28-28M298 132c16 8 28 22 34 38l-16 8c-8-14-17-23-28-28" fill="#f4c7a4"/>
            <path d="M214 170c14-12 30-18 48-18v26c-16 0-32 5-48 14v-22ZM330 152c18 0 34 6 48 18v22c-16-9-32-14-48-14v-26Z" fill="#f7d9c2"/>
            <path d="M40 60c18-22 45-28 68-18-18 22-45 28-68 18Z" fill="rgba(255,255,255,.25)"/>
            <path d="M360 30c18-14 40-14 56 0-18 14-40 14-56 0Z" fill="rgba(255,255,255,.2)"/>
          </svg>
        </div>
      </section>

      <!-- 8 宫格入口（图片样式，接真实功能） -->
      <section class="hb-grid" aria-label="快捷入口">
        <RouterLink v-for="f in features" :key="f.label" class="hb-tile" :to="f.to">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path v-for="(d, i) in f.paths" :key="i" :d="d" />
          </svg>
          <span>{{ f.label }}</span>
        </RouterLink>
      </section>

      <p v-if="isEmpty" class="muted" style="margin-bottom:12px">
        尚未接入语料：可先前往
        <RouterLink to="/shelf/import" style="color:var(--primary)">导入语料</RouterLink>，
        导入后统计、今日方证与图谱会自动出现。
      </p>

      <!-- 统计条 -->
      <section class="grid cols-4 stagger" style="margin-top:22px">
        <div class="stat">
          <div class="n">{{ num(stats?.vectors ?? stats?.nodes) }}</div>
          <div class="l">结构化内容单元（含向量）</div>
        </div>
        <div class="stat">
          <div class="n">{{ num(stats?.formulas) }}</div>
          <div class="l">方剂</div>
        </div>
        <div class="stat">
          <div class="n">{{ num(stats?.cases) }}</div>
          <div class="l">医案</div>
        </div>
        <div class="stat">
          <div class="n">{{ num(stats?.books) }}</div>
          <div class="l">已接入语料（可扩展）</div>
        </div>
      </section>

      <!-- 语料库（插拔式） -->
      <section class="card" style="margin-top:22px;display:flex;align-items:center;gap:16px;flex-wrap:wrap">
        <div>
          <b>语料库（插拔式）</b>
          <div class="muted">同一套骨架适配多类书籍 · 已接入 {{ books.length }} 部，可扩展</div>
        </div>
        <div v-if="books.length" style="display:flex;gap:8px;flex-wrap:wrap">
          <span v-for="b in books" :key="b.id" :class="bookChipClass(b)">{{ bookChipText(b) }}</span>
        </div>
        <span v-else class="muted">暂无已接入语料</span>
        <RouterLink class="btn ghost sm" style="margin-left:auto" to="/shelf">进入书架 →</RouterLink>
      </section>

      <!-- 今日方证 + 图谱预览 -->
      <section class="grid cols-2" style="margin-top:26px">
        <div class="card">
          <div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap">
            <h3>今日方证<template v-if="today"> · {{ today.name }}</template></h3>
            <span v-if="today?.nodeTitle" class="chip primary">{{ today.nodeTitle }}</span>
          </div>

          <template v-if="today">
            <p class="muted" style="margin:8px 0 14px">
              {{ today.efficacy || '功效未收录' }}。主治：{{ today.syndrome || '证候未收录' }}。
            </p>
            <div style="margin-bottom:14px">
              <HerbChips :herbs="today.herbs" />
            </div>

            <RouterLink
              v-if="firstQuote"
              class="cite"
              :to="`/quote/${firstQuote.id}`"
              style="margin-bottom:16px;display:flex"
            >
              <div>
                <div>{{ firstQuote.content || firstQuote.plainText || '原文未收录' }}</div>
                <div class="pg">
                  {{ firstQuote.label || firstQuote.classicName || '原典' }}<template v-if="firstQuote.articleNo"> · 第 {{ firstQuote.articleNo }} 条</template><template v-if="firstQuote.page"> · 第 {{ firstQuote.page }} 页</template>
                </div>
              </div>
            </RouterLink>
            <p v-else class="muted" style="margin-bottom:16px">暂无原文引用。</p>

            <div style="display:flex;gap:10px;flex-wrap:wrap">
              <RouterLink class="btn primary sm" :to="`/formula/${today.id}`">查看方剂详情</RouterLink>
              <RouterLink class="btn ghost sm" to="/train">开始练习</RouterLink>
            </div>
          </template>

          <p v-else class="muted" style="margin-top:8px">今日方证暂不可用</p>
        </div>

        <div class="card">
          <div style="display:flex;justify-content:space-between;align-items:center;gap:10px">
            <h3>知识图谱 · 预览</h3>
            <RouterLink class="chip clickable" to="/graph">进入图谱 ↗</RouterLink>
          </div>
          <MiniGraph :graph="graph" :w="480" :h="300" />
          <p class="muted">方-药-证 关系网络，可逐层展开、多跳探索。</p>
        </div>
      </section>

      <!-- 大家都在查（A4：catalog + search 聚合） -->
      <template v-if="hotHits.length">
        <h2 class="section-title"><span class="dot"></span>大家都在查</h2>
        <section class="grid cols-4 stagger">
          <RouterLink
            v-for="h in hotHits"
            :key="h.id"
            class="rowitem"
            :to="hitLink(h)"
            style="align-items:flex-start"
          >
            <span class="thumb">{{ typeThumb(h.refType) }}</span>
            <div style="min-width:0">
              <b style="display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">
                {{ h.title || '（无标题）' }}
              </b>
              <div class="muted" style="font-size:12.5px;margin-top:2px">
                {{ typeLabel(h.refType) }} · 相关度 {{ h.score.toFixed(2) }}
              </div>
            </div>
          </RouterLink>
        </section>
      </template>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import type { Book } from '@/api/catalog'
import { getHome, type Home } from '@/api/home'
import type { SearchHit } from '@/api/search'
import HerbChips from '@/components/HerbChips.vue'
import MiniGraph from '@/components/MiniGraph.vue'
import { num, typeLabel, typeThumb } from '@/utils/format'
import { toast } from '@/utils/toast'

const router = useRouter()

const home = ref<Home | null>(null)
const loading = ref(false)
const error = ref('')
const keyword = ref('')

/** 8 宫格入口：图标照图片样式，跳转全部指向项目真实功能路由 */
const features: Array<{ label: string; to: string; paths: string[] }> = [
  { label: '典籍浏览', to: '/library', paths: ['M12 6c-2-1.5-5-2-9-1v13c4-1 7-.5 9 1 2-1.5 5-2 9-1V5c-4-1-7-.5-9 1Z', 'M12 6v13'] },
  { label: '多维检索', to: '/search', paths: ['M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14Z', 'M16 16l5 5'] },
  { label: '智能问答', to: '/ask', paths: ['M4 5h16v11H9l-5 4V5Z', 'M8 9h8', 'M8 12h5'] },
  { label: '知识图谱', to: '/graph', paths: ['M12 3a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5Z', 'M5 16a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5Z', 'M19 16a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5Z', 'm10.3 7.5-4 6.8', 'm13.7 7.5 4 6.8'] },
  { label: '练习台', to: '/train', paths: ['M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18Z', 'M12 7v5l3.5 2'] },
  { label: '科研统计', to: '/research', paths: ['M3 20h18', 'M6 20V10', 'M12 20V4', 'M18 20v-7'] },
  { label: '条文索引', to: '/search/quote-index', paths: ['M6 3h9l4 4v14H6z', 'M15 3v5h4', 'M9 12h6', 'M9 16h6'] },
  { label: '我的收藏', to: '/me/collection', paths: ['M12 20s-7-4.5-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.5-7 10-7 10Z'] }
]

const stats = computed(() => home.value?.stats ?? null)
const books = computed(() => home.value?.books ?? [])
const today = computed(() => home.value?.today ?? null)
const graph = computed(() => home.value?.graph ?? null)
const hotKeywords = computed(() => home.value?.hotKeywords ?? [])
const hotHits = computed<SearchHit[]>(() => home.value?.hotHits ?? [])
const degraded = computed(() => home.value?.degraded ?? [])
const firstQuote = computed(() => today.value?.quotes?.[0] ?? null)
const isEmpty = computed(
  () => !!home.value && (stats.value?.nodes ?? 0) === 0 && !today.value && books.value.length === 0
)

const STATUS_LABEL: Record<string, string> = {
  draft: '待审核',
  已发布: '已发布',
  整理中: '整理中'
}

type BookStatusKind = 'published' | 'processing' | 'other'

function statusKind(book: Book): BookStatusKind {
  const raw = `${book.ingestStatus ?? ''} ${book.statusLabel ?? ''}`
  if (raw.includes('已发布') || raw.includes('published')) return 'published'
  if (raw.includes('整理') || raw.includes('processing')) return 'processing'
  return 'other'
}

function bookChipClass(book: Book): string {
  const kind = statusKind(book)
  if (kind === 'published') return 'chip primary'
  if (kind === 'processing') return 'chip gold'
  return 'chip'
}

function bookChipText(book: Book): string {
  if (statusKind(book) === 'published') return book.title
  const label = book.statusLabel || STATUS_LABEL[book.ingestStatus ?? ''] || '规划中'
  return `${book.title} · ${label}`
}

function hitLink(h: SearchHit): string {
  if (h.refType === 'formula') return `/formula/${h.refId}`
  if (h.refType === 'case') return `/case/${h.refId}`
  const no = (h.title || '').match(/第\s*(\d+)\s*条/)?.[1]
  return no ? `/quote/${h.refId}?no=${no}` : `/quote/${h.refId}`
}

function goSearch(q?: string) {
  const text = (q ?? keyword.value).trim()
  if (!text) {
    toast('请输入检索关键词')
    return
  }
  router.push({ path: '/search', query: { q: text } })
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    home.value = await getHome()
  } catch (e) {
    error.value = e instanceof Error ? e.message : '加载失败'
    home.value = null
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
/* 蓝色横幅 + 8 宫格：沿用参考图片的视觉样式，内容接入真实功能 */
.hb-hero{
  position:relative;
  overflow:hidden;
  min-height:272px;
  display:flex;
  align-items:center;
  padding:40px 48px;
  border-radius:var(--radius-lg);
  color:#fff;
  background:linear-gradient(120deg,#1da3ef 0%,#1281d8 55%,#0a6cc5 100%);
  box-shadow:0 16px 36px rgba(11,104,190,.22);
}
.hb-hero::before{
  content:"";position:absolute;width:320px;height:320px;right:-60px;top:-150px;
  border-radius:50%;background:rgba(255,255,255,.10);
}
.hb-hero::after{
  content:"";position:absolute;width:220px;height:220px;right:250px;bottom:-140px;
  border-radius:50%;background:rgba(255,255,255,.08);
}
.hb-hero-copy{position:relative;z-index:2;max-width:600px}
.hb-eyebrow{margin:0 0 12px;font-size:12px;letter-spacing:3px;opacity:.82}
.hb-hero h1{margin:0 0 12px;font-size:44px;line-height:1.2;letter-spacing:2px;color:#fff}
.hb-hero h1 span{color:#ffe36e}
.hb-sub{margin:0;font-size:15px;opacity:.92;line-height:1.7}
.hb-search{display:flex;gap:10px;margin-top:20px;max-width:520px}
.hb-input{
  flex:1;min-width:0;padding:10px 16px;border:0;border-radius:24px;outline:none;
  background:rgba(255,255,255,.97);color:var(--text);font-size:14px;
  box-shadow:0 4px 14px rgba(5,61,110,.15);
}
.hb-input::placeholder{color:#93a9bb}
.hb-search-btn{
  padding:10px 22px;border:0;border-radius:24px;background:#fff;color:#0a6cc5;
  font-size:14px;font-weight:700;white-space:nowrap;cursor:pointer;
  box-shadow:0 4px 14px rgba(5,61,110,.18);transition:transform .16s;
}
.hb-search-btn:hover{transform:translateY(-2px)}
.hb-hot{display:flex;gap:10px;margin-top:16px;flex-wrap:wrap}
.hb-chip{
  padding:3px 12px;border:1px solid rgba(255,255,255,.55);border-radius:999px;
  background:rgba(255,255,255,.12);color:#fff;font-size:12.5px;cursor:pointer;transition:.16s;
}
.hb-chip:hover{background:rgba(255,255,255,.26)}
.hb-hero-art{position:absolute;right:28px;bottom:8px;width:400px;z-index:1}
.hb-hero-art svg{width:100%;height:auto;display:block}

.hb-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:18px;margin-top:22px}
.hb-tile{
  min-height:150px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;
  border-radius:var(--radius);color:#fff;text-decoration:none;
  background:linear-gradient(160deg,#71b9ed 0%,#4a9fe1 100%);
  box-shadow:0 10px 22px rgba(24,118,195,.16);
  transition:transform .16s var(--ease),box-shadow .16s var(--ease),filter .16s;
}
.hb-tile:nth-child(even){background:linear-gradient(160deg,#68b0e8 0%,#438fd4 100%)}
.hb-tile:hover{transform:translateY(-5px);box-shadow:0 16px 30px rgba(24,118,195,.26);filter:brightness(1.04)}
.hb-tile svg{
  width:42px;height:42px;fill:none;stroke:#fff;stroke-width:1.7;
  stroke-linecap:round;stroke-linejoin:round;
}
.hb-tile span{font-size:16px;letter-spacing:1px}

@media(max-width:1000px){
  .hb-hero-art{width:320px;opacity:.85}
  .hb-hero h1{font-size:36px}
}
@media(max-width:760px){
  .hb-hero{padding:30px 22px;min-height:230px}
  .hb-hero-art{display:none}
  .hb-hero h1{font-size:30px}
  .hb-grid{grid-template-columns:repeat(2,1fr)}
}
</style>
