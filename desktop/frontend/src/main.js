/**
 * 应用入口文件
 * 
 * 这是 Vue 应用的主入口，负责：
 * 1. 创建 Vue 应用实例
 * 2. 注册全局插件（Pinia状态管理、Vue Router路由、ElLoading 指令）
 * 
 * Element Plus 采用按需导入，由 unplugin-vue-components 自动处理；
 * 函数式 API（ElMessage/ElMessageBox/ElNotification）与 v-loading 指令需手动注册
 * 
 * 【多标签页独立登录】
 * - Token 存储在 sessionStorage，每个标签页独立
 * - 不同标签页可以登录不同账号，互不干扰
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from '@/App.vue'
import router from '@/core/router'
import tokenManager from '@/core/utils/tokenManager'
import { checkConnection } from '@/core/config/connection'
import { ElLoading } from 'element-plus'

function getToken() {
  return sessionStorage.getItem('access_token')
}

function clearAuthData() {
  sessionStorage.removeItem('access_token')
  sessionStorage.removeItem('refresh_token')
  sessionStorage.removeItem('user')
}

function cleanupInvalidAuthData() {
  const token = getToken()
  const userStr = sessionStorage.getItem('user')
  
  let userData = null
  if (userStr) {
    try {
      userData = JSON.parse(userStr)
    } catch {
      userData = null
    }
  }
  
  const hasValidToken = !!token
  const hasValidUser = !!(userData && userData.id)
  
  if (!hasValidToken || !hasValidUser) {
    clearAuthData()
  }
}

cleanupInvalidAuthData()

const IDLE_TIMEOUT = 30 * 60 * 1000
let idleTimer = null

function resetIdleTimer() {
  if (idleTimer) clearTimeout(idleTimer)
  
  const token = getToken()
  if (!token) return
  
  idleTimer = setTimeout(() => {
    clearAuthData()
    
    alert('由于长时间未操作，您已自动退出登录')
    router.push('/login')
  }, IDLE_TIMEOUT)
}

function setupIdleDetection() {
  const events = ['mousedown', 'mousemove', 'keydown', 'scroll', 'touchstart', 'click']
  
  events.forEach(event => {
    document.addEventListener(event, resetIdleTimer, { passive: true })
  })
  
  resetIdleTimer()
}

function hideLoading() {
  const el = document.getElementById('app-loading')
  if (!el || el.classList.contains('lims-hiding')) return
  // 淡出后再移除：占位现在是 #app 的兄弟节点（见 index.pc.html），
  // 直接 remove 会"啪"地闪一下白，桌面端看起来很不专业
  el.classList.add('lims-hiding')
  setTimeout(() => el.remove(), 220)
}

// 跟随系统暗色：Element Plus 的暗色变量挂在 html.dark 上。
// 这里先用系统媒体查询落地一次（Rust 侧还会在系统主题变化时推 lims:theme 事件）。
if (typeof window !== 'undefined' && window.matchMedia) {
  const darkQuery = window.matchMedia('(prefers-color-scheme: dark)')
  const applyTheme = (isDark) => {
    document.documentElement.classList.toggle('dark', isDark)
  }
  applyTheme(darkQuery.matches)
  if (typeof darkQuery.addEventListener === 'function') {
    darkQuery.addEventListener('change', (event) => applyTheme(event.matches))
  }
}

window.addEventListener('error', function(e) {
  console.error('[PC] JS Error:', e.message, e.filename, e.lineno)
  hideLoading()
}, true)

window.addEventListener('unhandledrejection', function(e) {
  console.error('[PC] Promise Error:', e.reason)
  hideLoading()
})

setTimeout(hideLoading, 8000)

// 函数式 API（ElMessage/ElMessageBox/ElNotification）动态挂载到 body，
// unplugin-vue-components 无法自动注入其样式，需手动全局引入
import 'element-plus/es/components/message/style/css'
import 'element-plus/es/components/message-box/style/css'
import 'element-plus/es/components/notification/style/css'
import 'element-plus/es/components/loading/style/css'
import '@/assets/css/main.css'

// ── 桌面外壳样式（只在桌面端这份前端里引入；Web 端那份 frontend/ 不含它）──
// 系统字体栈 / 8pt 网格 / 明暗变量 / 自绘标题栏 / 禁用浏览器默认行为 / 页面切换动效
import '@/assets/css/desktop-shell.css'
// Element Plus 暗色变量：配合上面的 html.dark，整套 UI 跟随系统暗色模式
import 'element-plus/theme-chalk/dark/css-vars.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElLoading)

app.mount('#app')

hideLoading()

setupIdleDetection()

function startTokenManager() {
  const token = getToken()
  if (token) {
    tokenManager.start({
      onTokenExpired: (message) => {
        clearAuthData()
        
        if (idleTimer) clearTimeout(idleTimer)
        
        const currentPath = window.location.hash.replace('#', '') || '/'
        if (currentPath !== '/login') {
          alert(message)
          router.push('/login')
        }
      },
      onTokenRefreshed: (newAccessToken, newRefreshToken) => {
      }
    })
  }
}

startTokenManager()

// 启动即探测一次后端可达性：服务器没起时立刻给出可操作的提示界面，
// 而不是让用户看着一堆失败的请求提示猜发生了什么
checkConnection({ silent: true })

window.addEventListener('storage', (e) => {
  if (e.key === 'access_token' && !e.newValue) {
    tokenManager.stop()
    clearAuthData()
    router.push('/login')
  }
})
