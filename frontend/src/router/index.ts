import { createRouter, createWebHashHistory, type RouteRecordRaw } from 'vue-router'

/**
 * 精简后的页面清单：只保留真实有数据、面向学习者的核心功能。
 * 学习主线：找方证(检索/条文) → 读典籍 → 看关系(图谱) → 练题目 → 问疑惑
 * 已移除：书架/导入、收藏/笔记/错题/档案/学习路径、讨论、盲盒/背诵/旧答题流程、
 *         科研工作台/导出、治理后台、相似度地图（均为空壳或非学习者面向）。
 */
const routes: RouteRecordRaw[] = [
  // ---- 首页 / 账号 ----
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { title: '登录 / 注册' }
  },
  {
    path: '/me',
    name: 'me',
    component: () => import('@/views/MeView.vue'),
    meta: { title: '我的' }
  },

  // ---- 读：典籍与详情 ----
  {
    path: '/library',
    name: 'library',
    component: () => import('@/views/LibraryView.vue'),
    meta: { title: '典籍浏览' }
  },
  {
    path: '/node/:id',
    name: 'node',
    component: () => import('@/views/NodeView.vue'),
    meta: { title: '目录节点' }
  },
  {
    path: '/formula/:id',
    name: 'formula',
    component: () => import('@/views/FormulaView.vue'),
    meta: { title: '方剂详情' }
  },
  {
    path: '/case/:id',
    name: 'case',
    component: () => import('@/views/CaseView.vue'),
    meta: { title: '医案详情' }
  },
  {
    path: '/quote/:id',
    name: 'quote',
    component: () => import('@/views/QuoteView.vue'),
    meta: { title: '条文详情' }
  },

  // ---- 找：检索 ----
  {
    path: '/search',
    name: 'search',
    component: () => import('@/views/SearchView.vue'),
    meta: { title: '检索' }
  },
  {
    path: '/search/result',
    name: 'search-result',
    component: () => import('@/views/SearchResultView.vue'),
    meta: { title: '检索结果' }
  },
  {
    path: '/search/quote-index',
    name: 'quote-index',
    component: () => import('@/views/QuoteIndexView.vue'),
    meta: { title: '条文速查' }
  },

  // ---- 看：图谱 ----
  {
    path: '/graph',
    name: 'graph',
    component: () => import('@/views/GraphView.vue'),
    meta: { title: '方证图谱' }
  },
  {
    path: '/graph/formula/:id',
    name: 'graph-formula',
    component: () => import('@/views/GraphFormulaView.vue'),
    meta: { title: '方剂关系' }
  },

  // ---- 练 ----
  {
    path: '/train',
    name: 'train',
    component: () => import('@/views/TrainView.vue'),
    meta: { title: '章节练习' }
  },

  // ---- 问 ----
  {
    path: '/ask',
    name: 'ask',
    component: () => import('@/views/AskView.vue'),
    meta: { title: '智能问答' }
  },
  {
    path: '/ask/history',
    name: 'ask-history',
    component: () => import('@/views/AskHistoryView.vue'),
    meta: { title: '问答记录' }
  },

  { path: '/:pathMatch(.*)*', redirect: '/' }
]

// hash 路由：构建产物双击 file:// 打开时也能正常跳转，不依赖服务端重写
const router = createRouter({ history: createWebHashHistory(), routes })

router.afterEach(() => {
  document.title = 'HerbMind 本草心智'
  document.body.classList.add('loaded')
})

export default router
