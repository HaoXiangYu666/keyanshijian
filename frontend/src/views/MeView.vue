<template>
  <div class="crumb"><RouterLink to="/">首页</RouterLink> / 我的</div>

  <div class="me-wrap">
    <section class="me-hero">
      <div class="avatar">{{ initial }}</div>
      <div class="me-hero-copy">
        <h1 class="serif">{{ nickname }}</h1>
        <p class="muted">{{ loggedIn ? '继续你的中医经典学习' : '登录后可同步你的学习记录' }}</p>
      </div>
      <RouterLink v-if="!loggedIn" class="btn primary" to="/login">登录 / 注册</RouterLink>
      <button v-else class="btn ghost" type="button" @click="logout">退出登录</button>
    </section>

    <div class="section-title">
      <span class="bar"></span>
      <h2>我的学习</h2>
      <p>从这些入口继续</p>
    </div>

    <section class="entry-grid">
      <RouterLink class="entry-card" to="/ask/history">
        <span class="entry-ic ic-purple">
          <svg viewBox="0 0 24 24"><path d="M4 5h16v11H9l-5 4V5Z"/><path d="M8 9h8M8 12h5"/></svg>
        </span>
        <div class="entry-body">
          <b>问答记录</b>
          <span class="muted">回看问过的问题与典籍出处</span>
        </div>
        <span class="entry-arrow">→</span>
      </RouterLink>

      <RouterLink class="entry-card" to="/train">
        <span class="entry-ic ic-orange">
          <svg viewBox="0 0 24 24"><path d="M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18Z"/><path d="M12 7v5l3.5 2"/></svg>
        </span>
        <div class="entry-body">
          <b>章节练习</b>
          <span class="muted">按章节做题，含解析与汇总</span>
        </div>
        <span class="entry-arrow">→</span>
      </RouterLink>

      <RouterLink class="entry-card" to="/library">
        <span class="entry-ic ic-blue">
          <svg viewBox="0 0 24 24"><path d="M12 6c-2-1.5-5-2-9-1v13c4-1 7-.5 9 1 2-1.5 5-2 9-1V5c-4-1-7-.5-9 1Z"/><path d="M12 6v13"/></svg>
        </span>
        <div class="entry-body">
          <b>典籍浏览</b>
          <span class="muted">按章节阅读经典原文</span>
        </div>
        <span class="entry-arrow">→</span>
      </RouterLink>
    </section>

    <p class="tip">提示：问答与练习记录保存在服务端，登录后可跨设备查看。</p>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from '@/utils/toast'
import { me, type UserDto } from '@/api/user'

const router = useRouter()
const user = ref<UserDto | null>(null)
const loggedIn = computed(() => !!user.value)
const nickname = computed(() => user.value?.nickname || user.value?.username || '学习者')
const initial = computed(() => nickname.value.slice(0, 1))

async function loadUser() {
  if (!localStorage.getItem('token')) {
    user.value = null
    return
  }
  try {
    user.value = await me()
  } catch {
    user.value = null
  }
}
loadUser()

function logout() {
  localStorage.removeItem('token')
  user.value = null
  toast('已退出登录')
  router.push('/')
}
</script>

<style scoped>
.me-wrap { max-width:1040px;margin:0 auto;padding:6px 0 60px }
.me-hero{display:flex;align-items:center;gap:18px;padding:28px 30px;border-radius:24px;
  background:rgba(255,255,255,.72);border:1px solid rgba(255,255,255,.9);
  box-shadow:0 16px 40px rgba(10,110,220,.14),inset 0 1px 0 rgba(255,255,255,.95)}
.avatar{width:70px;height:70px;border-radius:22px;flex:none;display:grid;place-items:center;
  font-size:30px;font-weight:700;color:#fff;background:linear-gradient(135deg,#4FA8FF,#0A6FE8);
  box-shadow:0 12px 26px rgba(10,110,220,.3)}
.me-hero-copy{flex:1;min-width:0}
.me-hero-copy h1{margin:0 0 6px;font-size:24px;color:var(--primary-deep)}
.me-hero-copy p{margin:0;font-size:14px}
.section-title{display:flex;align-items:center;gap:12px;margin:34px 4px 18px;flex-wrap:wrap}
.section-title .bar{width:5px;height:24px;border-radius:3px;background:linear-gradient(180deg,#3AA0FF,#0A6FE8)}
.section-title h2{margin:0;font-size:21px;color:var(--primary-deep);letter-spacing:1px}
.section-title p{margin:0;color:var(--text-3);font-size:14px}
.entry-grid{display:grid;gap:14px}
.entry-card{display:flex;align-items:center;gap:16px;padding:20px 22px;border-radius:18px;text-decoration:none;
  background:rgba(255,255,255,.72);border:1px solid rgba(255,255,255,.9);
  box-shadow:0 10px 26px rgba(10,110,220,.1);transition:transform .18s var(--ease),box-shadow .18s var(--ease)}
.entry-card:hover{transform:translateY(-3px);box-shadow:0 18px 38px rgba(10,110,220,.18)}
.entry-ic{width:52px;height:52px;border-radius:15px;flex:none;display:grid;place-items:center}
.entry-ic svg{width:28px;height:28px;fill:none;stroke:#fff;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round}
.ic-purple{background:linear-gradient(135deg,#7D7AFF,#5E5CE6)}
.ic-orange{background:linear-gradient(135deg,#FFB340,#FF7A00)}
.ic-blue{background:linear-gradient(135deg,#4FA8FF,#0A6FE8)}
.entry-body{flex:1;display:flex;flex-direction:column;gap:4px;min-width:0}
.entry-body b{font-size:16px;color:var(--text)}
.entry-body .muted{font-size:13px}
.entry-arrow{font-size:20px;color:var(--primary);opacity:.6}
.tip{margin-top:22px;font-size:13px;color:var(--text-3);text-align:center}
@media(max-width:620px){.me-hero{padding:20px;gap:12px}.avatar{width:56px;height:56px;font-size:24px}.me-hero-copy h1{font-size:20px}}
</style>
