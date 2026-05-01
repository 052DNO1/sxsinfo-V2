/**
 * Token 管理器
 * 
 * 功能:
 * 1. 解析JWT token获取过期时间
 * 2. 定时检查token是否即将过期
 * 3. 在token过期前主动刷新
 * 4. 监听页面可见性变化,用户回到页面时检查token
 * 5. 提供友好的过期提示
 */

import axios from 'axios'

const baseURL = import.meta.env.VITE_API_V2_BASE_URL || 'http://localhost:8000/api/v1'

class TokenManager {
  constructor() {
    this.checkInterval = null
    this.refreshTimeout = null
    this.isRefreshing = false
    this.onTokenExpired = null
    this.onTokenRefreshed = null
    
    this.CHECK_INTERVAL = 60000
    this.REFRESH_THRESHOLD = 5 * 60 * 1000
    this.MIN_REFRESH_INTERVAL = 30 * 1000
  }

  parseJWT(token) {
    if (!token) return null
    
    try {
      const base64Url = token.split('.')[1]
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      )
      
      return JSON.parse(jsonPayload)
    } catch (error) {
      return null
    }
  }

  getTokenExpiration(token) {
    const payload = this.parseJWT(token)
    if (!payload || !payload.exp) return null
    
    return payload.exp * 1000
  }

  getTimeUntilExpiration(token) {
    const expiration = this.getTokenExpiration(token)
    if (!expiration) return 0
    
    return Math.max(0, expiration - Date.now())
  }

  isTokenExpired(token) {
    const timeUntilExpiration = this.getTimeUntilExpiration(token)
    return timeUntilExpiration <= 0
  }

  isTokenExpiringSoon(token, threshold = this.REFRESH_THRESHOLD) {
    const timeUntilExpiration = this.getTimeUntilExpiration(token)
    return timeUntilExpiration > 0 && timeUntilExpiration <= threshold
  }

  async refreshToken() {
    if (this.isRefreshing) {
      return false
    }
    
    const refreshToken = sessionStorage.getItem('refresh_token')
    const accessToken = sessionStorage.getItem('access_token')
    
    if (!refreshToken || !accessToken) {
      return false
    }
    
    if (this.isTokenExpired(refreshToken)) {
      this.handleTokenExpired('登录已过期,请重新登录')
      return false
    }
    
    this.isRefreshing = true
    
    try {
      
      const response = await axios.post(`${baseURL}/auth/token/refresh/`, {
        refresh: refreshToken
      }, {
        timeout: 10000
      })
      
      if (response.data?.access) {
        sessionStorage.setItem('access_token', response.data.access)
        
        if (response.data.refresh) {
          sessionStorage.setItem('refresh_token', response.data.refresh)
        }
        
        if (this.onTokenRefreshed) {
          this.onTokenRefreshed(response.data.access, response.data.refresh)
        }
        
        this.scheduleNextRefresh()
        
        return true
      } else {
        throw new Error('刷新响应中没有access token')
      }
    } catch (error) {
      if (error.response?.status === 401 || error.response?.data?.code === 'token_not_valid') {
        this.handleTokenExpired('登录已过期,请重新登录')
      }
      
      return false
    } finally {
      this.isRefreshing = false
    }
  }

  handleTokenExpired(message = 'JWT令牌认证信息丢失,请重新登录') {
    this.stop()
    
    sessionStorage.removeItem('access_token')
    sessionStorage.removeItem('refresh_token')
    sessionStorage.removeItem('user')
    sessionStorage.removeItem('first_login')
    
    if (this.onTokenExpired) {
      this.onTokenExpired(message)
    } else {
      this.showExpiredMessage(message)
    }
  }

  showExpiredMessage(message) {
    const currentPath = window.location.hash.replace('#', '') || '/'
    
    if (currentPath !== '/login') {
      setTimeout(() => {
        alert(message)
        window.location.href = '/#/login'
      }, 100)
    }
  }

  scheduleNextRefresh() {
    if (this.refreshTimeout) {
      clearTimeout(this.refreshTimeout)
      this.refreshTimeout = null
    }
    
    const accessToken = sessionStorage.getItem('access_token')
    if (!accessToken) return
    
    const timeUntilExpiration = this.getTimeUntilExpiration(accessToken)
    const refreshTime = Math.max(
      this.MIN_REFRESH_INTERVAL,
      timeUntilExpiration - this.REFRESH_THRESHOLD
    )
    
    if (refreshTime > 0 && refreshTime < timeUntilExpiration) {
      this.refreshTimeout = setTimeout(() => {
        this.refreshToken()
      }, refreshTime)
    }
  }

  checkAndRefreshToken() {
    const accessToken = sessionStorage.getItem('access_token')
    const refreshToken = sessionStorage.getItem('refresh_token')
    
    if (!accessToken || !refreshToken) {
      return
    }
    
    if (this.isTokenExpired(accessToken)) {
      if (this.isTokenExpired(refreshToken)) {
        this.handleTokenExpired('登录已过期,请重新登录')
      } else {
        this.refreshToken()
      }
    } else if (this.isTokenExpiringSoon(accessToken)) {
      this.refreshToken()
    }
  }

  handleVisibilityChange = () => {
    if (document.visibilityState === 'visible') {
      this.checkAndRefreshToken()
    }
  }

  start(options = {}) {
    if (options.onTokenExpired) {
      this.onTokenExpired = options.onTokenExpired
    }
    
    if (options.onTokenRefreshed) {
      this.onTokenRefreshed = options.onTokenRefreshed
    }
    
    this.checkAndRefreshToken()
    
    this.scheduleNextRefresh()
    
    if (this.checkInterval) {
      clearInterval(this.checkInterval)
    }
    this.checkInterval = setInterval(() => {
      this.checkAndRefreshToken()
    }, this.CHECK_INTERVAL)
    
    document.addEventListener('visibilitychange', this.handleVisibilityChange)
  }

  stop() {
    if (this.checkInterval) {
      clearInterval(this.checkInterval)
      this.checkInterval = null
    }
    
    if (this.refreshTimeout) {
      clearTimeout(this.refreshTimeout)
      this.refreshTimeout = null
    }
    
    document.removeEventListener('visibilitychange', this.handleVisibilityChange)
    
    this.isRefreshing = false
  }

  getStatus() {
    const accessToken = sessionStorage.getItem('access_token')
    const refreshToken = sessionStorage.getItem('refresh_token')
    
    return {
      hasAccessToken: !!accessToken,
      hasRefreshToken: !!refreshToken,
      accessTokenExpiringSoon: accessToken ? this.isTokenExpiringSoon(accessToken) : false,
      accessTokenExpired: accessToken ? this.isTokenExpired(accessToken) : true,
      refreshTokenExpired: refreshToken ? this.isTokenExpired(refreshToken) : true,
      timeUntilAccessExpiration: accessToken ? this.getTimeUntilExpiration(accessToken) : 0,
      timeUntilRefreshExpiration: refreshToken ? this.getTimeUntilExpiration(refreshToken) : 0
    }
  }
}

const tokenManager = new TokenManager()

export default tokenManager
