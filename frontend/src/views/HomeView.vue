<template>
  <div class="portal">
    <!-- 简洁品牌头：无导航栏，只留品牌与标语 -->
    <header class="portal-head">
      <div class="portal-brand">
        <span class="portal-mark">本</span>
        <div>
          <h1>本草心智</h1>
          <p>HerMind · 中医方证知识平台</p>
        </div>
      </div>
      <p class="portal-motto">可查 · 可练 · 可问 · 可推演 · 可看见</p>
    </header>

    <!-- 功能模块入口：参考学习通 / 知网的大图标门户 -->
    <section class="portal-grid" aria-label="功能模块">
      <RouterLink
        v-for="m in modules"
        :key="m.label"
        class="portal-card"
        :to="m.to"
      >
        <span class="portal-icon" :style="{ background: m.color }">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
              v-for="(d, i) in m.paths"
              :key="i"
              :d="d"
            />
          </svg>
        </span>
        <b>{{ m.label }}</b>
        <small>{{ m.desc }}</small>
        <span class="portal-arrow">→</span>
      </RouterLink>
    </section>
  </div>
</template>

<script setup lang="ts">
/**
 * 首页 = 纯功能入口门户。
 * 不请求后端：即使服务未启动，首页也能秒开；进入各功能模块后才依赖接口。
 * 视觉参考学习通 / 知网：大图标、大卡片、大间距，彩色区分模块。
 */
const modules: Array<{
  label: string
  to: string
  desc: string
  color: string
  paths: string[]
}> = [
  {
    label: '典籍浏览',
    to: '/library',
    desc: '经典原著 · 目录章节',
    color: 'linear-gradient(135deg,#3b82f6,#1d4ed8)',
    paths: ['M12 6c-2-1.5-5-2-9-1v13c4-1 7-.5 9 1 2-1.5 5-2 9-1V5c-4-1-7-.5-9 1Z', 'M12 6v13']
  },
  {
    label: '多维检索',
    to: '/search',
    desc: '方 · 药 · 证 · 条文',
    color: 'linear-gradient(135deg,#14b8a6,#0f766e)',
    paths: ['M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14Z', 'M16 16l5 5']
  },
  {
    label: '智能问答',
    to: '/ask',
    desc: '语义提问 · 知识应答',
    color: 'linear-gradient(135deg,#8b5cf6,#6d28d9)',
    paths: ['M4 5h16v11H9l-5 4V5Z', 'M8 9h8', 'M8 12h5']
  },
  {
    label: '知识图谱',
    to: '/graph',
    desc: '方药证关系网络',
    color: 'linear-gradient(135deg,#22c55e,#15803d)',
    paths: ['M12 3a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5Z', 'M5 16a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5Z', 'M19 16a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5Z', 'm10.3 7.5-4 6.8', 'm13.7 7.5 4 6.8']
  },
  {
    label: '练习台',
    to: '/train',
    desc: '方证辨识 · 打卡',
    color: 'linear-gradient(135deg,#f59e0b,#b45309)',
    paths: ['M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18Z', 'M12 7v5l3.5 2']
  },
  {
    label: '科研统计',
    to: '/research',
    desc: '数据挖掘 · 导出',
    color: 'linear-gradient(135deg,#ef4444,#b91c1c)',
    paths: ['M3 20h18', 'M6 20V10', 'M12 20V4', 'M18 20v-7']
  },
  {
    label: '条文索引',
    to: '/search/quote-index',
    desc: '原文逐条速查',
    color: 'linear-gradient(135deg,#0ea5e9,#0369a1)',
    paths: ['M6 3h9l4 4v14H6z', 'M15 3v5h4', 'M9 12h6', 'M9 16h6']
  },
  {
    label: '我的方证库',
    to: '/me/collection',
    desc: '收藏 · 笔记 · 错题',
    color: 'linear-gradient(135deg,#ec4899,#be185d)',
    paths: ['M12 20s-7-4.5-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.5-7 10-7 10Z']
  }
]
</script>

<style scoped>
.portal {
  min-height: calc(100vh - 64px);
  padding: 56px clamp(20px, 6vw, 80px) 72px;
  background:
    radial-gradient(1000px 460px at 50% -120px, rgba(29, 132, 235, .10), transparent 70%),
    var(--bg, #f6f9fc);
}

.portal-head {
  max-width: 1240px;
  margin: 0 auto 44px;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
  flex-wrap: wrap;
}

.portal-brand {
  display: flex;
  align-items: center;
  gap: 18px;
}

.portal-mark {
  width: 64px;
  height: 64px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #38bdf8, #1d4ed8);
  color: #fff;
  font-size: 34px;
  font-weight: 700;
  box-shadow: 0 12px 26px rgba(29, 110, 216, .28);
}

.portal-brand h1 {
  margin: 0;
  font-size: 30px;
  letter-spacing: 2px;
  color: var(--text, #123);
}

.portal-brand p {
  margin: 4px 0 0;
  font-size: 14px;
  color: var(--muted, #6b7c8f);
  letter-spacing: 1px;
}

.portal-motto {
  margin: 0;
  font-size: 15px;
  color: var(--muted, #6b7c8f);
  letter-spacing: 2px;
}

.portal-grid {
  max-width: 1240px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 30px;
}

.portal-card {
  position: relative;
  min-height: 210px;
  padding: 30px 22px 26px;
  border-radius: 22px;
  background: #fff;
  border: 1px solid rgba(15, 84, 160, .08);
  box-shadow: 0 10px 30px rgba(22, 70, 130, .08);
  text-decoration: none;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
  transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease;
}

.portal-card:hover {
  transform: translateY(-8px);
  border-color: rgba(29, 132, 235, .38);
  box-shadow: 0 22px 44px rgba(22, 70, 130, .18);
}

.portal-icon {
  width: 68px;
  height: 68px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  margin-bottom: 10px;
  box-shadow: 0 10px 20px rgba(20, 80, 160, .18);
}

.portal-icon svg {
  width: 36px;
  height: 36px;
  fill: none;
  stroke: #fff;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.portal-card b {
  font-size: 21px;
  letter-spacing: 1px;
  color: var(--text, #14263a);
}

.portal-card small {
  font-size: 13.5px;
  color: var(--muted, #7a8b9c);
}

.portal-arrow {
  position: absolute;
  right: 22px;
  bottom: 24px;
  font-size: 20px;
  color: #9ab2c9;
  transition: transform .2s ease, color .2s ease;
}

.portal-card:hover .portal-arrow {
  transform: translateX(5px);
  color: #1d84eb;
}

@media (max-width: 1000px) {
  .portal-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 22px; }
}

@media (max-width: 560px) {
  .portal { padding: 32px 16px 48px; }
  .portal-grid { grid-template-columns: 1fr 1fr; gap: 14px; }
  .portal-card { min-height: 168px; padding: 20px 16px; }
  .portal-icon { width: 52px; height: 52px; }
  .portal-icon svg { width: 28px; height: 28px; }
  .portal-card b { font-size: 17px; }
  .portal-card small { font-size: 12px; }
}
</style>
