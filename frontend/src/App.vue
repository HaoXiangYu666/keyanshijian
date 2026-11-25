<template>
  <div id="progress"></div>

  <!-- 首页 / 登录页：整屏门户，无返回栏；其余页面统一顶部返回键回首页 -->
  <template v-if="showBack">
    <div class="backbar">
      <RouterLink class="back" to="/"><span aria-hidden="true">←</span> 返回首页</RouterLink>
      <span class="brandmini">本草心智</span>
    </div>
    <main class="subpage">
      <RouterView />
    </main>
  </template>

  <main v-else>
    <RouterView />
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
// 首页与登录页用整屏布局，其余页面统一显示返回键
const showBack = computed(() => route.path !== '/' && route.path !== '/login')

onMounted(() => document.body.classList.add('loaded'))
</script>
