// 截图：页面加载前注入 token（evaluateOnNewDocument），再直接导航完整 hash 地址
const puppeteer = require('puppeteer-core')
const path = require('path')

const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'
const BASE = 'http://127.0.0.1:5173'
const OUT = 'D:/keyanshijian/mobile-view'
const TOKEN = process.argv[2] || ''
const STAMP = process.argv[3] || ''

const pages = [
  { name: 'home', hash: '#/', waitFor: '开始学习' },
  { name: 'search', hash: '#/search', waitFor: '检索工作台' },
  { name: 'library', hash: '#/library', waitFor: '典籍浏览' },
  { name: 'cases', hash: '#/cases', waitFor: '医案研读' },
  { name: 'daily', hash: '#/daily', waitFor: '每日一方' },
  { name: 'graph', hash: '#/graph', waitFor: '知识图谱探索' },
  { name: 'train', hash: '#/train', waitFor: '方证练习' },
  { name: 'ask', hash: '#/ask', waitFor: '智能问答' },
  { name: 'me', hash: '#/me', waitFor: '我的学习' }
]

;(async () => {
  const browser = await puppeteer.launch({
    executablePath: EDGE,
    headless: 'new',
    args: ['--no-sandbox', '--disable-gpu', '--hide-scrollbars']
  })

  for (const p of pages) {
    const page = await browser.newPage()
    await page.setViewport({ width: 1280, height: 1000, deviceScaleFactor: 1 })

    // 关键：在任何脚本执行前把 token 写进 localStorage
    if (TOKEN) {
      await page.evaluateOnNewDocument((t) => {
        try { localStorage.setItem('token', t) } catch (e) {}
      }, TOKEN)
    }

    // 直接导航到完整 hash 地址（全新页面上下文，hash 不会被覆盖）
    await page.goto(BASE + '/' + p.hash, { waitUntil: 'domcontentloaded', timeout: 30000 })

    try {
      await page.waitForFunction(
        (kw) => document.body && document.body.innerText.includes(kw),
        { timeout: 20000, polling: 300 },
        p.waitFor
      )
    } catch (e) {
      console.log(`  ! ${p.name} 等待「${p.waitFor}」超时`)
    }
    try { await page.waitForNetworkIdle({ idleTime: 800, timeout: 10000 }) } catch (e) {}
    await new Promise((r) => setTimeout(r, 1500))

    const file = path.join(OUT, `page-${p.name}${STAMP}.png`)
    await page.screenshot({ path: file })
    const txt = await page.evaluate(() => document.body.innerText.slice(0, 70).replace(/\s+/g, ' '))
    console.log(`${p.name.padEnd(9)} -> ${file}\n           ${txt}`)
    await page.close()
  }

  await browser.close()
  console.log('DONE')
})().catch((e) => { console.error('ERROR', e.message); process.exit(1) })
