import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.mobile.vue'
import router from './router/mobile'

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

import Vant from 'vant'
import 'vant/lib/index.css'
import { Locale } from 'vant'
import zhCN from 'vant/es/locale/lang/zh-CN'

Locale.use('zh-CN', zhCN)

import '@/assets/css/vant-theme.css'
import '@/assets/css/main.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(Vant)

app.mount('#app')
