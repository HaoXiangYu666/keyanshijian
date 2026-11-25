<template>
  <div class="portal">
    <!-- 读书横幅：搜索是最高频动作，放在最显眼处 -->
    <section class="banner">
      <div class="banner-copy">
        <div class="banner-kicker">HERBMIND · 本草心智</div>
        <h1>正是读书<span>好时节</span></h1>
        <p>搜方剂、查条文、读典籍，一搜即得</p>
        <form class="banner-search" @submit.prevent="goSearch">
          <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M16 16l5 5"/></svg>
          <input
            v-model="keyword"
            placeholder="试试：桂枝汤、无汗而喘、白虎汤"
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
          <path d="M254 138c-17 9-30 24-36 41l17 8c8-15 18-25 30-30M304 138c17 9 30 24 36 41l-17 8c8-15 18-25 30-30" fill="#F6CBA9"/>
          <path d="M214 178c15-13 32-19 51-19v27c-17 0-34 6-51 15v-23ZM336 159c19 0 36 6 51 19v23c-17-9-34-15-51-15v-27Z" fill="#FBE0CC"/>
          <path d="M38 62c19-23 47-30 71-19-19 23-47 30-71 19Z" fill="rgba(255,255,255,.28)"/>
          <path d="M362 32c19-15 42-15 59 0-19 15-42 15 59 0Z" fill="rgba(255,255,255,.22)"/>
        </svg>
      </div>
    </section>

    <!-- 六个模块：上三下三，卡片放大 -->
    <div class="section-title">
      <span class="bar"></span>
      <h2>开始学习</h2>
      <p>找方证 → 读典籍 → 看关系 → 练题目 → 问疑惑 → 我的</p>
    </div>
    <section class="portal-grid" aria-label="核心功能">
      <RouterLink
        v-for="m in modules"
        :key="m.name"
        class="portal-card"
        :to="m.to"
      >
        <span class="card-step">{{ m.step }}</span>
        <span class="portal-icon" :style="{ background: m.color }">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path v-for="(d, i) in m.paths" :key="i" :d="d" />
          </svg>
        </span>
        <b>{{ m.name }}</b>
        <span class="card-desc">{{ m.desc }}</span>
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

/**
 * 六个模块：上三下三大卡片布局。检索/典籍/图谱/练习/问答/我的，全部有真实数据支撑。
 */
const modules: Array<{
  name: string; to: string; color: string; paths: string[]; step: string; desc: string
}> = [
  { name: '检索', to: '/search', step: '01 找', color: 'linear-gradient(135deg,#2E9BF0,#0058C9)',
    paths: ['M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14Z', 'M16 16l5 5'],
    desc: '按方名、症状、原文快速找方剂与医案' },
  { name: '典籍', to: '/library', step: '02 读', color: 'linear-gradient(135deg,#4FA8FF,#0A6FE8)',
    paths: ['M12 6c-2-1.5-5-2-9-1v13c4-1 7-.5 9 1 2-1.5 5-2 9-1V5c-4-1-7-.5-9 1Z', 'M12 6v13'],
    desc: '按章节阅读伤寒论、金匮要略原文' },
  { name: '图谱', to: '/graph', step: '03 看', color: 'linear-gradient(135deg,#34C759,#1E8E3E)',
    paths: ['M12 3a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5Z', 'M5 16a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5Z', 'M19 16a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5Z', 'm10.3 7.5-4 6.8', 'm13.7 7.5 4 6.8'],
    desc: '可视化方剂与药味的关联关系' },
  { name: '练习', to: '/train', step: '04 练', color: 'linear-gradient(135deg,#FFB340,#FF7A00)',
    paths: ['M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18Z', 'M12 7v5l3.5 2'],
    desc: '按章节做题，附解析与错题汇总' },
  { name: '问答', to: '/ask', step: '05 问', color: 'linear-gradient(135deg,#7D7AFF,#5E5CE6)',
    paths: ['M4 5h16v11H9l-5 4V5Z', 'M8 9h8', 'M8 12h5'],
    desc: '用自然语言提问，答案附典籍出处' },
  { name: '我的', to: '/me', step: '06 我', color: 'linear-gradient(135deg,#5AC8D8,#0E8FA8)',
    paths: ['M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8Z', 'M4 21c0-4 3.6-7 8-7s8 3 8 7'],
    desc: '登录状态、问答记录与个人设置' }
]
</script>

<style scoped>
.portal { max-width:1320px;margin:0 auto;padding:clamp(20px,3vw,36px) clamp(16px,4vw,44px) 64px; }

/* 读书横幅 */
.banner{
  position:relative;overflow:hidden;
  min-height:268px;display:flex;align-items:center;
  padding:44px clamp(28px,4.5vw,64px);
  border-radius:28px;color:#fff;
  background:linear-gradient(120deg,#1E9BF0 0%,#0A84FF 52%,#0060DF 100%);
  box-shadow:0 22px 54px rgba(10,110,220,.32);
}
.banner::before{content:"";position:absolute;width:360px;height:360px;right:-70px;top:-170px;border-radius:50%;background:rgba(255,255,255,.10)}
.banner::after{content:"";position:absolute;width:240px;height:240px;right:230px;bottom:-160px;border-radius:50%;background:rgba(255,255,255,.08)}
.banner-copy{position:relative;z-index:2;max-width:680px}
.banner-kicker{font-size:13px;letter-spacing:3px;opacity:.88;margin-bottom:14px}
.banner h1{margin:0;font-size:clamp(34px,4.4vw,54px);letter-spacing:2px;color:#fff}
.banner h1 span{color:#FFE36E}
.banner p{margin:10px 0 0;font-size:17px;opacity:.94}
.banner-search{display:flex;align-items:center;gap:10px;margin-top:26px;max-width:660px;
  background:rgba(255,255,255,.98);border-radius:999px;padding:7px 7px 7px 22px;
  box-shadow:0 10px 28px rgba(4,48,110,.26)}
.banner-search svg{width:23px;height:23px;fill:none;stroke:#8AA0B8;stroke-width:2;stroke-linecap:round;flex:none}
.banner-search input{flex:1;min-width:0;border:0;outline:none;font-size:16px;color:var(--text);background:transparent}
.banner-search input::placeholder{color:#9AAEC2}
.banner-search button{border:0;border-radius:999px;padding:13px 34px;font-size:15px;font-weight:700;color:#fff;
  background:linear-gradient(180deg,#3AA0FF,#0A6FE8);cursor:pointer;white-space:nowrap}
.banner-search button:hover{filter:brightness(1.06)}
.banner-art{position:absolute;right:30px;bottom:10px;width:clamp(260px,32vw,420px);z-index:1}
.banner-art svg{width:100%;height:auto;display:block}

/* 分区标题 */
.section-title{display:flex;align-items:center;gap:12px;margin:clamp(28px,3.6vw,42px) 4px 20px;flex-wrap:wrap}
.section-title .bar{width:5px;height:24px;border-radius:3px;background:linear-gradient(180deg,#3AA0FF,#0A6FE8)}
.section-title h2{margin:0;font-size:22px;color:var(--primary-deep);letter-spacing:1px}
.section-title p{margin:0;color:var(--text-3);font-size:14px}

/* 六个核心功能卡：上三下三，卡片放大 */
.portal-grid{margin:0;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:clamp(18px,2vw,28px)}
.portal-card{
  position:relative;min-height:320px;padding:38px 24px 32px;border-radius:28px;
  background:rgba(255,255,255,.72);border:1px solid rgba(255,255,255,.9);
  -webkit-backdrop-filter:saturate(170%) blur(24px);backdrop-filter:saturate(170%) blur(24px);
  box-shadow:0 16px 40px rgba(10,110,220,.16),inset 0 1px 0 rgba(255,255,255,.95);
  text-decoration:none;display:flex;flex-direction:column;align-items:center;text-align:center;gap:18px;
  transition:transform .22s var(--ease),box-shadow .22s var(--ease),background .22s var(--ease);
}
.portal-card:hover{transform:translateY(-10px);background:rgba(255,255,255,.92);
  box-shadow:0 28px 56px rgba(10,110,220,.26),inset 0 1px 0 rgba(255,255,255,1)}
.card-step{position:absolute;top:22px;left:26px;font-size:15px;font-weight:700;color:var(--primary);opacity:.72;letter-spacing:1px}
.portal-icon{width:104px;height:104px;border-radius:30px;display:grid;place-items:center;margin-top:18px;
  box-shadow:0 14px 30px rgba(10,110,220,.3),inset 0 1px 0 rgba(255,255,255,.5)}
.portal-icon svg{width:54px;height:54px;fill:none;stroke:#fff;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round}
.portal-card b{font-size:28px;letter-spacing:6px;color:var(--primary-deep)}
.card-desc{font-size:15px;line-height:1.7;color:var(--text-3);max-width:260px}

@media(max-width:900px){.portal-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.banner-art{width:300px;opacity:.92}}
@media(max-width:560px){.portal-grid{grid-template-columns:repeat(1,minmax(0,1fr))}}
@media(max-width:620px){
  .banner{padding:28px 22px}.banner-art{display:none}.banner-search{padding-left:14px}
  .banner-search button{padding:11px 22px}
  .portal-grid{gap:14px}
  .portal-card{min-height:230px;padding:26px 14px;gap:12px}
  .portal-icon{width:76px;height:76px;border-radius:22px;margin-top:12px}.portal-icon svg{width:40px;height:40px}
  .portal-card b{font-size:21px;letter-spacing:4px}
  .card-step{font-size:13px;top:16px;left:18px}
  .card-desc{font-size:13px;max-width:180px}
}
</style>
