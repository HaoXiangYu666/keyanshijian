<template>
  <div class="portal">
    <!-- 读书横幅（图2 样式）：正是读书好时节 + 插画 + 搜索框 -->
    <section class="banner">
      <div class="banner-copy">
        <div class="banner-kicker">HERBMIND · 本草心智</div>
        <h1>正是读书<span>好时节</span></h1>
        <p>中医药知识，一搜即得</p>
        <form class="banner-search" @submit.prevent="goSearch">
          <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M16 16l5 5"/></svg>
          <input
            v-model="keyword"
            placeholder="搜方剂、医案、条文，如：桂枝汤"
            aria-label="搜索"
          />
          <button type="submit">搜索</button>
        </form>
      </div>
      <div class="banner-art" aria-hidden="true">
        <svg viewBox="0 0 420 260" fill="none">
          <ellipse cx="215" cy="238" rx="168" ry="11" fill="rgba(6,70,150,.16)"/>
          <path d="M56 158c46-28 100-28 146 0v66c-46-26-100-26-146 0v-66Z" fill="#fff"/>
          <path d="M202 158c46-28 100-28 146 0v66c-46-26-100-26-146 0v-66Z" fill="#EAF4FF"/>
          <path d="M56 158c46-28 100-28 146 0M202 158c46-28 100-28 146 0" stroke="#BBD9F5" stroke-width="2"/>
          <path d="M56 224c46-26 100-26 146 0 46-26 100-26 146 0" stroke="#CFE4F8" stroke-width="7" stroke-linecap="round"/>
          <path d="M254 96c0-18 14-32 32-32s32 14 32 32-14 32-32 32-32-14-32-32Z" fill="#F6CBA9"/>
          <path d="M250 92c-3-21 13-36 32-36 18 0 33 13 33 32-9-7-18-9-28-7-13 2-24 0-37-11Z" fill="#4A3428"/>
          <circle cx="316" cy="62" r="11" fill="#4A3428"/>
          <path d="M248 128c9-11 22-15 38-15s29 4 38 15l13 66h-102l13-66Z" fill="#FF5E57"/>
          <path d="M254 138c-17 9-30 24-36 41l17 8c8-15 18-25 30-30M304 138c17 9 30 24 36 41l-17 8c-8-15-18-25-30-30" fill="#F6CBA9"/>
          <path d="M214 178c15-13 32-19 51-19v27c-17 0-34 6-51 15v-23ZM336 159c19 0 36 6 51 19v23c-17-9-34-15-51-15v-27Z" fill="#FBE0CC"/>
          <path d="M38 62c19-23 47-30 71-19-19 23-47 30-71 19Z" fill="rgba(255,255,255,.28)"/>
          <path d="M362 32c19-15 42-15 59 0-19 15-42 15-59 0Z" fill="rgba(255,255,255,.22)"/>
        </svg>
      </div>
    </section>

    <!-- 功能模块：图标更蓝、卡片更大、间隔更大 -->
    <section class="portal-grid" aria-label="功能模块">
      <RouterLink
        v-for="m in modules"
        :key="m.name"
        class="portal-card"
        :to="m.to"
      >
        <span class="portal-icon" :style="{ background: m.color }">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path v-for="(d, i) in m.paths" :key="i" :d="d" />
          </svg>
        </span>
        <b>{{ m.name }}</b>
      </RouterLink>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const keyword = ref('')

function goSearch() {
  const q = keyword.value.trim()
  router.push({ path: '/search', query: q ? { q } : {} })
}

/** 首页 = 纯功能入口：不请求后端，服务未启动也能秒开 */
const modules: Array<{ name: string; to: string; color: string; paths: string[] }> = [
  { name: '典籍', to: '/library', color: 'linear-gradient(135deg,#4FA8FF,#0A6FE8)',
    paths: ['M12 6c-2-1.5-5-2-9-1v13c4-1 7-.5 9 1 2-1.5 5-2 9-1V5c-4-1-7-.5-9 1Z', 'M12 6v13'] },
  { name: '检索', to: '/search', color: 'linear-gradient(135deg,#2E9BF0,#0058C9)',
    paths: ['M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14Z', 'M16 16l5 5'] },
  { name: '问答', to: '/ask', color: 'linear-gradient(135deg,#7D7AFF,#5E5CE6)',
    paths: ['M4 5h16v11H9l-5 4V5Z', 'M8 9h8', 'M8 12h5'] },
  { name: '图谱', to: '/graph', color: 'linear-gradient(135deg,#34C759,#1E8E3E)',
    paths: ['M12 3a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5Z', 'M5 16a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5Z', 'M19 16a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5Z', 'm10.3 7.5-4 6.8', 'm13.7 7.5 4 6.8'] },
  { name: '练习', to: '/train', color: 'linear-gradient(135deg,#FFB340,#FF7A00)',
    paths: ['M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18Z', 'M12 7v5l3.5 2'] },
  { name: '科研', to: '/research', color: 'linear-gradient(135deg,#FF7B7B,#E03A32)',
    paths: ['M3 20h18', 'M6 20V10', 'M12 20V4', 'M18 20v-7'] },
  { name: '条文', to: '/search/quote-index', color: 'linear-gradient(135deg,#5FD2FF,#0A84FF)',
    paths: ['M6 3h9l4 4v14H6z', 'M15 3v5h4', 'M9 12h6', 'M9 16h6'] },
  { name: '我的', to: '/me', color: 'linear-gradient(135deg,#FF9ECC,#D81E80)',
    paths: ['M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z', 'M4 21a8 8 0 0 1 16 0'] }
]
</script>

<style scoped>
.portal { padding: clamp(20px, 3.4vw, 40px) clamp(16px, 5vw, 56px) 64px; }

/* 读书横幅 */
.banner{
  position:relative;overflow:hidden;
  min-height:230px;display:flex;align-items:center;
  padding:36px clamp(24px,4vw,52px);
  border-radius:26px;color:#fff;
  background:linear-gradient(120deg,#1E9BF0 0%,#0A84FF 52%,#0060DF 100%);
  box-shadow:0 18px 44px rgba(10,110,220,.28);
}
.banner::before{content:"";position:absolute;width:360px;height:360px;right:-70px;top:-170px;border-radius:50%;background:rgba(255,255,255,.10)}
.banner::after{content:"";position:absolute;width:240px;height:240px;right:230px;bottom:-160px;border-radius:50%;background:rgba(255,255,255,.08)}
.banner-copy{position:relative;z-index:2;max-width:620px}
.banner-kicker{font-size:12px;letter-spacing:3px;opacity:.85;margin-bottom:12px}
.banner h1{margin:0;font-size:clamp(30px,4vw,46px);letter-spacing:2px;color:#fff}
.banner h1 span{color:#FFE36E}
.banner p{margin:8px 0 0;font-size:15px;opacity:.92}
.banner-search{display:flex;align-items:center;gap:8px;margin-top:20px;max-width:540px;
  background:rgba(255,255,255,.97);border-radius:999px;padding:6px 6px 6px 18px;
  box-shadow:0 6px 20px rgba(4,48,110,.2)}
.banner-search svg{width:20px;height:20px;fill:none;stroke:#8AA0B8;stroke-width:2;stroke-linecap:round;flex:none}
.banner-search input{flex:1;min-width:0;border:0;outline:none;font-size:14px;color:var(--text);background:transparent}
.banner-search input::placeholder{color:#9AAEC2}
.banner-search button{border:0;border-radius:999px;padding:10px 24px;font-weight:700;color:#fff;
  background:linear-gradient(180deg,#3AA0FF,#0A6FE8);cursor:pointer;white-space:nowrap}
.banner-search button:hover{filter:brightness(1.06)}
.banner-art{position:absolute;right:24px;bottom:6px;width:clamp(240px,32vw,400px);z-index:1}
.banner-art svg{width:100%;height:auto;display:block}

/* 功能模块 */
.portal-grid{
  max-width:1180px;margin:clamp(26px,3.4vw,40px) auto 0;
  display:grid;grid-template-columns:repeat(4,minmax(0,1fr));
  gap:clamp(18px,2.4vw,32px);
}
.portal-card{
  min-height:200px;padding:28px 18px;border-radius:24px;
  background:rgba(255,255,255,.66);border:1px solid rgba(255,255,255,.85);
  -webkit-backdrop-filter:saturate(170%) blur(22px);backdrop-filter:saturate(170%) blur(22px);
  box-shadow:0 14px 36px rgba(10,110,220,.14),inset 0 1px 0 rgba(255,255,255,.9);
  text-decoration:none;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px;
  transition:transform .22s var(--ease),box-shadow .22s var(--ease),background .22s var(--ease);
}
.portal-card:hover{transform:translateY(-9px);background:rgba(255,255,255,.85);
  box-shadow:0 24px 50px rgba(10,110,220,.24),inset 0 1px 0 rgba(255,255,255,.95)}
.portal-icon{width:78px;height:78px;border-radius:22px;display:grid;place-items:center;
  box-shadow:0 12px 26px rgba(10,110,220,.28),inset 0 1px 0 rgba(255,255,255,.45)}
.portal-icon svg{width:40px;height:40px;fill:none;stroke:#fff;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round}
.portal-card b{font-size:20px;letter-spacing:4px;color:var(--primary-deep)}

@media(max-width:1000px){.portal-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.banner-art{width:280px;opacity:.9}}
@media(max-width:620px){
  .banner{padding:28px 22px}.banner-art{display:none}.banner-search{padding-left:14px}
  .portal-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
  .portal-card{min-height:150px;padding:18px 10px;gap:12px}
  .portal-icon{width:60px;height:60px;border-radius:18px}.portal-icon svg{width:32px;height:32px}
  .portal-card b{font-size:17px;letter-spacing:3px}
}
</style>
