/**
 * 应用入口文件
 * 
 * 这是 Vue 应用的主入口，负责：
 * 1. 创建 Vue 应用实例
 * 2. 注册全局插件（Pinia状态管理、Vue Router路由）
 * 3. 配置中文语言包
 * 
 * Element Plus 采用按需导入，由 unplugin-vue-components 自动处理
 * 
 * 【多标签页独立登录】
 * - Token 存储在 sessionStorage，每个标签页独立
 * - 不同标签页可以登录不同账号，互不干扰
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from '@/App.vue'
import router from '@/core/router'

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
  if (el) el.remove()
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

import 'element-plus/dist/index.css'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import '@/assets/css/main.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus, { locale: zhCn })

app.mount('#app')

hideLoading()

setupIdleDetection()
