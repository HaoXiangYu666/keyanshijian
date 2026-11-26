import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

const frontendDir = fileURLToPath(new URL('.', import.meta.url))
const repoDir = path.resolve(frontendDir, '..')

/**
 * 把构建产物变成"双击 index.html 就能看"的离线站点：
 * 1. 去掉 crossorigin（file:// 下 CSS 会被 CORS 拦截）
 * 2. 脚本移到 body 末尾（普通脚本在 head 里执行时 #app 尚未创建，挂载会失败）
 * 3. 构建后自动复制到仓库根目录 D:/keyanshijian/，保证路径真实存在、每次构建都是最新
 */
const standalonePlugin = {
  name: 'standalone-file-site',
  // 只在 build 时生效：dev 模式若注入构建产物 app.js，会导致整页重复挂载、路由被重置回首页
  apply: 'build' as const,
  transformIndexHtml(html: string) {
    return html
      .replace(/ crossorigin/g, '')
      .replace(/<script[^>]*src="\.\/app\.js"[^>]*><\/script>/, '')
      .replace('</body>', '  <script src="./app.js"></script>\n</body>')
  },
  closeBundle() {
    for (const file of ['index.html', 'app.js', 'style.css', 'favicon.svg']) {
      const src = path.join(frontendDir, 'dist', file)
      const dest = path.join(repoDir, file)
      if (fs.existsSync(src)) fs.copyFileSync(src, dest)
    }
  }
}

// 开发期：/api → 网关 :8080（网关再把 /api/biz/** 转给 BFF :8090）
export default defineConfig({
  // 相对路径：构建产物可直接双击 index.html 用 file:// 打开
  base: './',
  plugins: [vue(), standalonePlugin],
  resolve: {
    // @ 别名必须在这里配（tsconfig 的 paths 只影响类型检查，不影响打包）
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    // 0.0.0.0：手机等局域网设备可用 http://<本机IP>:5173 直接访问
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true
      }
    }
  },
  build: {
    // 打成单个普通脚本（非 ES module），不被 file:// 的 CORS 拦截，双击 index.html 可直接看
    rollupOptions: {
      output: {
        format: 'iife',
        inlineDynamicImports: true,
        manualChunks: undefined,
        entryFileNames: 'app.js',
        assetFileNames: '[name][extname]'
      }
    },
    cssCodeSplit: false
  }
})
