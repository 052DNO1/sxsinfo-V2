/**
 * 移动端应用入口文件
 * 
 * 这是移动端 Vue 应用的主入口，负责：
 * 1. 创建 Vue 应用实例
 * 2. 注册全局插件（Pinia状态管理、Vue Router路由）
 * 3. 配置Vant UI组件库
 * 
 * 【多标签页独立登录】
 * - Token 存储在 sessionStorage，每个标签页独立
 * - 不同标签页可以登录不同账号，互不干扰
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from '@/App.vue'
import router from '@/core/router/mobile'
import tokenManager from '@/core/utils/tokenManager'

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
  if (el) el.remove()
}

window.addEventListener('error', function(e) {
  console.error('[Mobile] JS Error:', e.message, e.filename, e.lineno)
  hideLoading()
}, true)

window.addEventListener('unhandledrejection', function(e) {
  console.error('[Mobile] Promise Error:', e.reason)
  hideLoading()
})

setTimeout(hideLoading, 8000)

import 'vant/lib/index.css'
import '@/assets/css/main.css'
import '@/assets/css/mobile.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

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

window.addEventListener('storage', (e) => {
  if (e.key === 'access_token' && !e.newValue) {
    tokenManager.stop()
    clearAuthData()
    router.push('/login')
  }
})
