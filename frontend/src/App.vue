<template>
  <div id="progress"></div>

  <!-- 首页是纯功能入口门户，登录页是整屏两栏布局，均不叠顶栏和页脚 -->
  <AppHeader v-if="!hideChrome" />

  <main :class="hideChrome ? '' : 'wrap'">
    <RouterView />
  </main>

  <footer v-if="!hideChrome">
    HerbMind v2 · 视觉基线沿用 <span class="mono">prototype/assets/theme.css</span> ·
    <RouterLink to="/me">我的</RouterLink> ·
    <RouterLink to="/me/favorites">收藏笔记</RouterLink> ·
    <RouterLink to="/admin">治理后台</RouterLink>
  </footer>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from '@/components/AppHeader.vue'

const route = useRoute()
// 首页去掉导航栏与页脚：入口全部走功能模块卡片；其余页面保留原导航以便返回
const hideChrome = computed(() => route.path === '/' || route.path === '/login')

// 原型用 body.loaded 触发入场动画
onMounted(() => document.body.classList.add('loaded'))
</script>
