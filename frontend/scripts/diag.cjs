const puppeteer = require('puppeteer-core')
const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'

;(async () => {
  const browser = await puppeteer.launch({
    executablePath: EDGE, headless: 'new',
    args: ['--no-sandbox', '--disable-gpu']
  })
  const page = await browser.newPage()
  page.on('console', (m) => console.log('[console.' + m.type() + ']', m.text().slice(0, 300)))
  page.on('pageerror', (e) => console.log('[pageerror]', e.message.slice(0, 400)))
  page.on('requestfailed', (r) => console.log('[reqfail]', r.url().slice(0, 160), r.failure() && r.failure().errorText))

  for (const h of ['#/library', '#/search', '#/graph']) {
    console.log('\n===== 打开 ' + h + ' =====')
    await page.goto('http://127.0.0.1:5173/' + h, { waitUntil: 'networkidle2', timeout: 25000 }).catch(e => console.log('goto err', e.message))
    await new Promise(r => setTimeout(r, 3000))
    const info = await page.evaluate(() => ({
      hash: location.hash,
      text: document.body.innerText.slice(0, 100).replace(/\s+/g, ' ')
    }))
    console.log('  hash:', info.hash, '\n  text:', info.text)
  }
  await browser.close()
})()
