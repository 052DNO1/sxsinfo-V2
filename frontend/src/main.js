/**
 * 应用入口文件
 * 
 * 这是 Vue 应用的主入口，负责：
 * 1. 创建 Vue 应用实例
 * 2. 注册全局插件（Pinia状态管理、Vue Router路由）
 * 3. 配置中文语言包
 * 
 * Element Plus 采用按需导入，由 unplugin-vue-components 自动处理
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from '@/App.vue'
import router from '@/core/router'

function cleanupInvalidAuthData() {
  const token = localStorage.getItem('access_token')
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
    if (token) localStorage.removeItem('access_token')
    if (localStorage.getItem('refresh_token')) localStorage.removeItem('refresh_token')
    if (userStr) sessionStorage.removeItem('user')
  }
}

cleanupInvalidAuthData()

const IDLE_TIMEOUT = 30 * 60 * 1000
let idleTimer = null

function resetIdleTimer() {
  if (idleTimer) clearTimeout(idleTimer)
  
  const token = localStorage.getItem('access_token')
  if (!token) return
  
  idleTimer = setTimeout(() => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    sessionStorage.removeItem('user')
    
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

// Element Plus 样式
import 'element-plus/dist/index.css'

// Element Plus 中文语言包
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

// 全局样式
import '@/assets/css/main.css'

// 创建 Vue 应用实例
const app = createApp(App)

// 注册 Pinia 状态管理
app.use(createPinia())

// 注册路由
app.use(router)

// 注册 Element Plus 并配置中文
app.use(ElementPlus, { locale: zhCn })

app.mount('#app')

setupIdleDetection()
