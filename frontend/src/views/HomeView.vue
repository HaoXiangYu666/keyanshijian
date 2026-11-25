<template>
  <div class="portal">
    <!-- 极简欢迎区：只有品牌，无导航、无长文案 -->
    <header class="portal-head">
      <span class="portal-mark">本</span>
      <div class="portal-titles">
        <h1>本草心智</h1>
        <p>中医方证知识平台</p>
      </div>
    </header>

    <!-- 功能模块：大卡片、大间距、磨砂玻璃、只留图标 + 名称 -->
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
/**
 * 首页 = 纯功能入口门户（Apple 蓝毛玻璃）。
 * 不请求后端：服务未启动也能秒开；进入模块后才依赖接口。
 */
const modules: Array<{ name: string; to: string; color: string; paths: string[] }> = [
  { name: '典籍', to: '/library', color: 'linear-gradient(135deg,#5AC8FA,#0A84FF)',
    paths: ['M12 6c-2-1.5-5-2-9-1v13c4-1 7-.5 9 1 2-1.5 5-2 9-1V5c-4-1-7-.5-9 1Z', 'M12 6v13'] },
  { name: '检索', to: '/search', color: 'linear-gradient(135deg,#32ADE6,#0071E3)',
    paths: ['M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14Z', 'M16 16l5 5'] },
  { name: '问答', to: '/ask', color: 'linear-gradient(135deg,#7D7AFF,#5E5CE6)',
    paths: ['M4 5h16v11H9l-5 4V5Z', 'M8 9h8', 'M8 12h5'] },
  { name: '图谱', to: '/graph', color: 'linear-gradient(135deg,#30D158,#248A3D)',
    paths: ['M12 3a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5Z', 'M5 16a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5Z', 'M19 16a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5Z', 'm10.3 7.5-4 6.8', 'm13.7 7.5 4 6.8'] },
  { name: '练习', to: '/train', color: 'linear-gradient(135deg,#FF9F0A,#FF6A00)',
    paths: ['M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18Z', 'M12 7v5l3.5 2'] },
  { name: '科研', to: '/research', color: 'linear-gradient(135deg,#FF6B6B,#D7352E)',
    paths: ['M3 20h18', 'M6 20V10', 'M12 20V4', 'M18 20v-7'] },
  { name: '条文', to: '/search/quote-index', color: 'linear-gradient(135deg,#64D2FF,#0A84FF)',
    paths: ['M6 3h9l4 4v14H6z', 'M15 3v5h4', 'M9 12h6', 'M9 16h6'] },
  { name: '我的', to: '/me', color: 'linear-gradient(135deg,#FF9CCB,#C51E7A)',
    paths: ['M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z', 'M4 21a8 8 0 0 1 16 0'] }
]
</script>

<style scoped>
.portal {
  min-height: calc(100vh - 32px);
  padding: clamp(40px, 8vh, 92px) clamp(20px, 7vw, 96px) 80px;
  background: transparent;
}

.portal-head {
  max-width: 1180px;
  margin: 0 auto clamp(40px, 7vh, 72px);
  display: flex;
  align-items: center;
  gap: 20px;
}

.portal-mark {
  width: 62px;
  height: 62px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  background: rgba(255, 255, 255, .28);
  border: 1px solid rgba(255, 255, 255, .6);
  -webkit-backdrop-filter: saturate(160%) blur(16px);
  backdrop-filter: saturate(160%) blur(16px);
  box-shadow: 0 10px 26px rgba(4, 48, 110, .18);
  color: #fff;
  font-size: 32px;
  font-weight: 700;
}

.portal-titles h1 {
  margin: 0;
  font-size: 30px;
  letter-spacing: 3px;
  color: #fff;
  text-shadow: 0 2px 12px rgba(4, 48, 110, .25);
}

.portal-titles p {
  margin: 2px 0 0;
  font-size: 14px;
  letter-spacing: 2px;
  color: rgba(255, 255, 255, .88);
}

.portal-grid {
  max-width: 1180px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: clamp(20px, 2.6vw, 34px);
}

.portal-card {
  min-height: 208px;
  padding: 30px 20px;
  border-radius: 24px;
  background: rgba(255, 255, 255, .58);
  border: 1px solid rgba(255, 255, 255, .66);
  -webkit-backdrop-filter: saturate(170%) blur(22px);
  backdrop-filter: saturate(170%) blur(22px);
  box-shadow: 0 12px 34px rgba(4, 48, 110, .16), inset 0 1px 0 rgba(255, 255, 255, .6);
  text-decoration: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 18px;
  transition: transform .22s var(--ease), box-shadow .22s var(--ease), background .22s var(--ease);
}

.portal-card:hover {
  transform: translateY(-9px);
  background: rgba(255, 255, 255, .74);
  box-shadow: 0 24px 50px rgba(4, 48, 110, .28), inset 0 1px 0 rgba(255, 255, 255, .8);
}

.portal-icon {
  width: 76px;
  height: 76px;
  border-radius: 22px;
  display: grid;
  place-items: center;
  box-shadow: 0 12px 24px rgba(4, 48, 110, .22), inset 0 1px 0 rgba(255, 255, 255, .4);
}

.portal-icon svg {
  width: 40px;
  height: 40px;
  fill: none;
  stroke: #fff;
  stroke-width: 1.9;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.portal-card b {
  font-size: 20px;
  letter-spacing: 4px;
  color: var(--primary-deep);
}

@media (max-width: 1000px) {
  .portal-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 560px) {
  .portal { padding: 32px 16px 48px; }
  .portal-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
  .portal-card { min-height: 156px; padding: 20px 12px; gap: 14px; }
  .portal-icon { width: 60px; height: 60px; border-radius: 18px; }
  .portal-icon svg { width: 32px; height: 32px; }
  .portal-card b { font-size: 17px; letter-spacing: 3px; }
}
</style>
