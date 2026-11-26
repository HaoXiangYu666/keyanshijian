// 全链路体检：逐条路由打开，记录控制台报错、失败请求、关键内容是否渲染
const puppeteer = require('puppeteer-core')

const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'
const BASE = 'http://127.0.0.1:5173'
const TOKEN = process.argv[2] || ''

const routes = [
  { hash: '#/', name: '首页', expect: '开始学习' },
  { hash: '#/search', name: '检索', expect: '检索工作台' },
  { hash: '#/library', name: '典籍', expect: '典籍浏览' },
  { hash: '#/cases', name: '医案列表', expect: '医案研读' },
  { hash: '#/daily', name: '每日一方', expect: '每日一方' },
  { hash: '#/graph', name: '图谱', expect: '知识图谱探索' },
  { hash: '#/train', name: '练习', expect: '方证练习' },
  { hash: '#/ask', name: '问答', expect: '智能问答' },
  { hash: '#/me', name: '我的', expect: '我的学习' },
  { hash: '#/search/quote-index', name: '条文索引', expect: '条文反向索引' },
  { hash: '#/formula/f_5', name: '方剂详情', expect: '桂枝汤' },
  { hash: '#/case/cs_10', name: '医案详情', expect: '桂枝汤' },
  { hash: '#/node/n_h1', name: '目录节点', expect: '' },
  { hash: '#/ask/history', name: '问答历史', expect: '' }
]

;(async () => {
  const browser = await puppeteer.launch({
    executablePath: EDGE,
    headless: 'new',
    args: ['--no-sandbox', '--disable-gpu']
  })

  const bad = []

  for (const r of routes) {
    const page = await browser.newPage()
    await page.setViewport({ width: 1440, height: 1000 })
    const errors = []
    const fails = []

    page.on('console', (m) => {
      if (m.type() === 'error') errors.push(m.text().slice(0, 160))
    })
    page.on('pageerror', (e) => errors.push('JS: ' + String(e).slice(0, 160)))
    page.on('requestfailed', (req) => {
      if (!req.url().includes('favicon')) fails.push(req.url().replace(BASE, '') + ' ' + (req.failure()?.errorText || ''))
    })
    page.on('response', (res) => {
      const u = res.url()
      if (u.includes('/api/') && res.status() >= 400) fails.push(`HTTP ${res.status()} ${u.replace(BASE, '')}`)
    })

    if (TOKEN) {
      await page.evaluateOnNewDocument((t) => {
        try { localStorage.setItem('token', t) } catch (e) {}
      }, TOKEN)
    }

    try {
      await page.goto(BASE + '/' + r.hash, { waitUntil: 'networkidle2', timeout: 25000 })
      await new Promise((res) => setTimeout(res, 1200))

      const body = await page.evaluate(() => document.body.innerText || '')
      const html = await page.evaluate(() => document.body.innerHTML.length)
      const blank = html < 800
      const missing = r.expect && !body.includes(r.expect)

      const status = blank ? '空白' : missing ? '缺内容' : '正常'
      const line = `[${status}] ${r.name.padEnd(6)} ${r.hash}`
      console.log(line)
      if (errors.length) console.log('   控制台: ' + [...new Set(errors)].slice(0, 3).join(' | '))
      if (fails.length) console.log('   请求: ' + [...new Set(fails)].slice(0, 4).join(' | '))
      if (status !== '正常') {
        bad.push(r.name)
        console.log('   正文: ' + body.replace(/\s+/g, ' ').slice(0, 150))
      }
    } catch (e) {
      console.log(`[超时] ${r.name} ${r.hash} :: ${String(e).slice(0, 100)}`)
      bad.push(r.name)
    }
    await page.close()
  }

  await browser.close()
  console.log('\n=== 汇总 ===')
  console.log(bad.length ? '有问题的页面: ' + bad.join('、') : '全部正常')
})()
