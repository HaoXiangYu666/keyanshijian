<template>
  <!-- 后端连不上时才出现：明确告诉用户"不是页面坏了"，并给一键重试 -->
  <Transition name="svc">
    <div v-if="down" class="svc-bar">
      <span class="svc-dot" aria-hidden="true"></span>
      <span class="svc-text">服务未连接，部分内容加载失败</span>
      <button class="svc-retry" :disabled="checking" @click="check">
        {{ checking ? '连接中…' : '重试' }}
      </button>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'

/**
 * 轻量健康检查：只打一个最便宜的接口（/api/biz/home），15s 一次。
 * 失败才显示提示条；成功立刻消失。不阻塞渲染、不参与路由。
 */
const down = ref(false)
const checking = ref(false)
let timer: number | undefined

async function ping(url: string, withToken = false) {
  const ctrl = new AbortController()
  const to = window.setTimeout(() => ctrl.abort(), 5000)
  try {
    const headers: Record<string, string> = {}
    if (withToken) {
      const t = localStorage.getItem('token')
      if (t) headers.Authorization = `Bearer ${t}`
    }
    const res = await fetch(url, { signal: ctrl.signal, headers })
    // 401 说明网关活着（只是没登录），同样算“连得上”
    return res.status < 500
  } catch {
    return false
  } finally {
    window.clearTimeout(to)
  }
}

async function check() {
  if (checking.value) return
  checking.value = true
  try {
    // /api/agent/health 免鉴权；/api/biz/home 走网关+BFF。任一能应答就算后端在。
    const [a, b] = await Promise.all([ping('/api/agent/health'), ping('/api/biz/home', true)])
    down.value = !a && !b
  } finally {
    checking.value = false
  }
}

onMounted(() => {
  check()
  timer = window.setInterval(check, 15000)
})

onBeforeUnmount(() => {
  if (timer) window.clearInterval(timer)
})
</script>

<style scoped>
.svc-bar {
  position: fixed;
  left: 50%;
  bottom: 22px;
  transform: translateX(-50%);
  z-index: 90;
  display: flex;
  align-items: center;
  gap: 10px;
  /* fixed + left:50% 时，auto 宽度会被限制成视口一半，导致文字碎成多行 */
  width: max-content;
  max-width: calc(100vw - 32px);
  padding: 10px 12px 10px 16px;
  border-radius: 999px;
  background: rgba(255, 250, 245, 0.96);
  border: 1px solid rgba(226, 138, 74, 0.32);
  box-shadow: 0 10px 30px rgba(180, 110, 40, 0.16);
  -webkit-backdrop-filter: blur(14px);
  backdrop-filter: blur(14px);
  font-size: 13px;
  color: #8a5424;
}

.svc-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #e08a3c;
  flex: none;
  box-shadow: 0 0 0 4px rgba(224, 138, 60, 0.16);
}

.svc-text {
  line-height: 1.4;
  flex: 1;
  min-width: 0;
  text-align: left;
}

.svc-retry {
  flex: none;
  border: 0;
  border-radius: 999px;
  padding: 6px 14px;
  background: #b9762f;
  color: #fff;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.16s var(--ease);
}

.svc-retry:hover:not(:disabled) {
  background: #9c5f22;
}

.svc-retry:disabled {
  opacity: 0.6;
  cursor: default;
}

.svc-enter-active,
.svc-leave-active {
  transition: opacity 0.22s var(--ease), transform 0.22s var(--ease);
}

.svc-enter-from,
.svc-leave-to {
  opacity: 0;
  transform: translate(-50%, 12px);
}

@media (max-width: 560px) {
  .svc-bar {
    font-size: 12px;
    gap: 8px;
    padding: 9px 10px 9px 13px;
    bottom: 14px;
  }
}
</style>
