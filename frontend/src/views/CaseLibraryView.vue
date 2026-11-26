<template>
  <div class="crumb"><RouterLink to="/">首页</RouterLink> / 医案</div>
  <h1 class="serif" style="margin-bottom:6px">医案研读</h1>
  <p class="muted" style="margin-bottom:16px">
    方剂看的是「法」，医案看的是「用法」。按章节挑一节，右侧列出该节全部医案，点开读原案全文——起病、辨证、处方、转归一目了然。
  </p>

  <div class="pill-tabs" style="margin-bottom:16px">
    <button
      v-for="b in bookTabs"
      :key="b.id"
      :class="{ active: bookId === b.id }"
      @click="switchBook(b.id)"
    >{{ b.label }}</button>
  </div>

  <p v-if="error" class="muted" style="color:#A32D2D">{{ error }}</p>

  <button class="btn ghost sm toc-toggle" @click="tocOpen = !tocOpen">
    {{ tocOpen ? '收起章节' : '展开章节' }}
  </button>

  <div class="grid case-layout">
    <!-- 章节树 -->
    <aside class="card case-toc" :class="{ 'is-open': tocOpen }">
      <h3 style="margin-bottom:12px">
        章节 · <span class="muted" style="font-weight:400;font-size:13px">{{ curBookTitle }}</span>
      </h3>
      <div v-if="loadingTree" class="muted">加载中…</div>
      <template v-else>
        <div v-for="ch in tree" :key="ch.id" class="node-ch">
          <button class="node-btn lvl-1" :class="{ on: isOn(ch.id) }" @click="selectNode(ch.id)">
            {{ ch.title }}
          </button>
          <button
            v-for="s in ch.children ?? []"
            :key="s.id"
            class="node-btn lvl-2"
            :class="{ on: isOn(s.id) }"
            @click="selectNode(s.id)"
          >{{ s.title }}</button>
        </div>
        <p v-if="!tree.length" class="muted">该语料暂无章节数据。</p>
      </template>
    </aside>

    <!-- 医案列表 -->
    <section>
      <div class="card">
        <div class="list-head">
          <div>
            <h3 style="margin-bottom:4px">{{ curTitle || '医案列表' }}</h3>
            <p class="muted" style="margin:0;font-size:13px">
              共 {{ allCases.length }} 例
              <template v-if="kw.trim()">，筛选出 {{ shown.length }} 例</template>
            </p>
          </div>
          <input v-model="kw" class="filter" placeholder="按方名 / 证候 / 脉象筛选" />
        </div>

        <div v-if="loadingList" class="muted" style="padding:20px 0">加载中…</div>

        <template v-else>
          <div v-if="shown.length" class="case-grid">
            <RouterLink
              v-for="c in shown"
              :key="c.id"
              class="case-card"
              :to="`/case/${c.id}`"
            >
              <div class="case-top">
                <b>{{ c.title || '未命名医案' }}</b>
                <span v-if="c.page" class="page">{{ c.page }}</span>
              </div>
              <p class="case-syn">{{ cleanSyn(c.syndrome) }}</p>
              <span class="read">读原案 ↗</span>
            </RouterLink>
          </div>
          <p v-else class="muted" style="padding:18px 0">
            {{ allCases.length ? '没有匹配的医案，换个关键词试试。' : '这一节暂无医案，换一节看看。' }}
          </p>
        </template>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getLibraryTree, getNodeDetail, type BookTreeNode, type CaseBrief } from '@/api/catalog'
import { useBooks } from '@/composables/useBooks'

const route = useRoute()
const router = useRouter()
const { books, defaultBookId, titleOf, loadBooks } = useBooks()
const bookTabs = computed(() => books.value.map((b) => ({ id: b.id, label: b.title })))

const bookId = ref(String(route.query.bookId ?? ''))
const tree = ref<BookTreeNode[]>([])
const loadingTree = ref(false)
const error = ref('')

const selectedId = ref(String(route.query.node ?? ''))
const curTitle = ref('')
const allCases = ref<CaseBrief[]>([])
const loadingList = ref(false)
const kw = ref('')
const tocOpen = ref(false)

const curBookTitle = computed(() => titleOf(bookId.value))

/** 后端节点的 cases 已递归聚合了子节点，所以选「节」就能拿到该节全部医案 */
const shown = computed(() => {
  const k = kw.value.trim()
  if (!k) return allCases.value
  return allCases.value.filter((c) => {
    const text = [c.title, c.syndrome, c.mainFormulaName].filter(Boolean).join(' ')
    return text.includes(k)
  })
})

/** 证候串里常有半角/全角分号拼接，去掉首尾冗余分隔符再展示 */
function cleanSyn(s?: string): string {
  if (!s) return '原案未附证候摘要'
  const t = s.replace(/^[；;，,\s]+|[；;，,\s]+$/g, '').replace(/；/g, ' · ')
  return t.length > 62 ? t.slice(0, 62) + '…' : t
}

function isOn(id: string) {
  return selectedId.value === id
}

async function loadNode(id: string) {
  if (!id) return
  loadingList.value = true
  error.value = ''
  try {
    const d = await getNodeDetail(id)
    curTitle.value = d.node?.title ?? ''
    allCases.value = d.cases ?? []
  } catch (e) {
    allCases.value = []
    error.value = e instanceof Error ? e.message : '医案加载失败'
  } finally {
    loadingList.value = false
  }
}

function selectNode(id: string) {
  if (!id) return
  selectedId.value = id
  kw.value = ''
  void router.replace({ query: { ...route.query, bookId: bookId.value, node: id } })
  void loadNode(id)
  if (tocOpen.value) tocOpen.value = false
}

async function loadTree() {
  loadingTree.value = true
  error.value = ''
  try {
    tree.value = await getLibraryTree(bookId.value)
    // 默认落在第一节：章级节点聚合内容太多，节级刚好是一屏能读完的量
    const exists = flat().some((n) => n.id === selectedId.value)
    const firstSection = flat().find((n) => n.nodeType === 'section') ?? flat()[0]
    if (!exists && (firstSection || !selectedId.value)) {
      selectNode(firstSection?.id ?? '')
    } else if (selectedId.value) {
      void loadNode(selectedId.value)
    }
  } catch (e) {
    tree.value = []
    error.value = e instanceof Error ? e.message : '目录加载失败'
  } finally {
    loadingTree.value = false
  }
}

/** 章 + 节 展平（类级太细，医案都在节里已聚合） */
function flat(): BookTreeNode[] {
  const list: BookTreeNode[] = []
  for (const ch of tree.value) {
    list.push(ch)
    for (const s of ch.children ?? []) list.push(s)
  }
  return list
}

async function switchBook(id: string) {
  if (id === bookId.value) return
  bookId.value = id
  selectedId.value = ''
  allCases.value = []
  curTitle.value = ''
  await loadTree()
}

onMounted(async () => {
  await loadBooks()
  if (!bookId.value) bookId.value = defaultBookId.value || 'bk_1'
  await loadTree()
})
</script>

<style scoped>
.case-layout {
  grid-template-columns: 300px 1fr;
}

.case-toc {
  align-self: start;
  max-height: 74vh;
  overflow: auto;
}

.toc-toggle {
  display: none;
  margin-bottom: 12px;
}

.node-ch {
  margin-bottom: 10px;
}

.node-btn {
  display: block;
  width: 100%;
  text-align: left;
  border: 0;
  background: transparent;
  cursor: pointer;
  border-radius: 6px;
  line-height: 1.45;
  color: inherit;
  font: inherit;
}

.node-btn:hover {
  background: rgba(0, 0, 0, 0.045);
}

.node-btn.on {
  background: rgba(47, 106, 79, 0.12);
  color: #2f6a4f;
  font-weight: 700;
}

.lvl-1 {
  font-weight: 700;
  font-size: 14.5px;
  padding: 5px 6px;
}

.lvl-2 {
  font-size: 13.5px;
  padding: 4px 6px 4px 16px;
  color: #374151;
}

.list-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.filter {
  padding: 8px 12px;
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 8px;
  font: inherit;
  color: inherit;
  background: rgba(255, 255, 255, 0.7);
  min-width: 220px;
}

.filter:focus {
  outline: none;
  border-color: #2f6a4f;
}

.case-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 12px;
}

.case-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 14px 16px;
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.55);
  color: inherit;
  text-decoration: none;
  transition: all 0.18s var(--ease, ease);
}

.case-card:hover {
  border-color: #9dc6b0;
  background: rgba(255, 255, 255, 0.9);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(31, 77, 56, 0.1);
}

.case-top {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 8px;
}

.case-top b {
  font-size: 15.5px;
  color: var(--primary-deep, #1f4d38);
}

.page {
  font-size: 11.5px;
  color: #9ca3af;
  white-space: nowrap;
}

.case-syn {
  margin: 0;
  font-size: 13px;
  line-height: 1.65;
  color: #4b5563;
}

.read {
  margin-top: auto;
  font-size: 12.5px;
  color: #2f6a4f;
}

@media (max-width: 860px) {
  .case-layout {
    grid-template-columns: 1fr;
  }

  .toc-toggle {
    display: inline-flex;
  }

  .case-toc {
    display: none;
    max-height: 46vh;
  }

  .case-toc.is-open {
    display: block;
  }

  .filter {
    min-width: 0;
    width: 100%;
  }
}
</style>
