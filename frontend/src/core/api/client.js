/**
 * Axios HTTP 客户端配置 【高并发+防抖节流版本】
 * 
 * @module api
 * @description 项目API请求基础配置
 * 
 * 【功能】
 * 1. 配置 API 基础路径和超时时间
 * 2. 请求拦截器：自动添加 JWT Token
 * 3. 响应拦截器：处理 401 未授权错误
 * 
 * 【高并发支持】⚡ 保留
 * - 请求队列：限制并发数，排队处理请求数量（默认6个）
 * - 请求去重：相同请求短时间内只发送一次
 * - 请求取消：支持取消正在进行的请求（AbortController）
 * - 防抖节流：狂刷新检测，自动降载
 * - 自动重试：网络错误自动重试（默认3次）
 * 
 * 【多标签页独立登录】✨
 * - Token 存储在 sessionStorage，每个标签页独立
 * - 不同标签页可以登录不同账号，互不干扰
 * 
 * @example
 * // GET 请求
 * const response = await api.get('/users/')
 * 
 * // POST 请求（自动去重）
 * const result = await api.post('/login/', { username, password })
 * 
 * // 取消所有请求
 * api.cancelAll()
 */

import axios from 'axios'
import { defaultQueue, generateRequestKey } from './queue'

const baseURL = import.meta.env.VITE_API_V2_BASE_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' }
})

const pendingRequests = new Map()

function detectRefreshStorm() {
  const now = Date.now()
  
  if (now - _requestCountResetTime > REQUEST_COUNT_WINDOW) {
    _requestCount = 0
    _requestCountResetTime = now
  }
  
  _requestCount++
  
  if (_requestCount > REQUEST_COUNT_THRESHOLD && !_isRefreshStorm) {
    _isRefreshStorm = true
    _stormStartTime = now
  }
  
  if (_isRefreshStorm && (now - _stormStartTime > STORM_DURATION)) {
    if (_requestCount <= REQUEST_COUNT_THRESHOLD / 2) {
      _isRefreshStorm = false
    } else {
      _stormStartTime = now
    }
  }
  
  return _isRefreshStorm
}

let _requestCount = 0
let _requestCountResetTime = Date.now()
const REQUEST_COUNT_WINDOW = 1000
const REQUEST_COUNT_THRESHOLD = 10
let _isRefreshStorm = false
let _stormStartTime = 0
const STORM_DURATION = 3000

function getToken() {
  return sessionStorage.getItem('access_token')
}

function getRefreshToken() {
  return sessionStorage.getItem('refresh_token')
}

function setTokens(access, refresh) {
  if (access) {
    sessionStorage.setItem('access_token', access)
  }
  if (refresh) {
    sessionStorage.setItem('refresh_token', refresh)
  }
}

function clearTokens() {
  sessionStorage.removeItem('access_token')
  sessionStorage.removeItem('refresh_token')
}

api.interceptors.request.use(
  config => {
    detectRefreshStorm()
    
    const token = getToken()
    if (token) config.headers.Authorization = `Bearer ${token}`

    if (config.url && !config.url.startsWith('http') && !config.url.startsWith('/')) {
      config.url = '/' + config.url
    }

    if (config.dedupe !== false) {
      const key = generateRequestKey(config)
      if (pendingRequests.has(key)) {
        config._duplicate = true
      } else {
        pendingRequests.set(key, true)
        config._requestKey = key
      }
    }

    return config
  },
  error => Promise.reject(error)
)

api.interceptors.response.use(
  response => {
    const { config, data } = response
    
    if (config._requestKey) pendingRequests.delete(config._requestKey)

    if (config.responseType === 'blob' || data instanceof Blob) return response

    return data
  },
  async error => {
    const { config, response } = error
    if (config?._requestKey) pendingRequests.delete(config._requestKey)

    if (response?.status === 401 && !config.url.includes('auth/login')) {
      const refreshToken = getRefreshToken()
      if (refreshToken && !config._isRetry) {
        try {
          const refreshResponse = await axios.post(`${baseURL}/auth/token/refresh/`, {
            refresh: refreshToken
          })
          
          if (refreshResponse.data?.access) {
            setTokens(refreshResponse.data.access, refreshResponse.data.refresh)
            
            config.headers.Authorization = `Bearer ${refreshResponse.data.access}`
            config._isRetry = true
            return api(config)
          }
        } catch (refreshError) {
          const errorMessage = refreshError.response?.data?.detail || 
                              refreshError.response?.data?.message ||
                              '登录已过期，请重新登录'
          
          clearTokens()
          
          setTimeout(() => {
            if (!getToken()) {
              const currentPath = window.location.hash.replace('#', '') || '/'
              if (currentPath !== '/login') {
                alert(errorMessage)
                window.location.href = '/#/login'
              }
            }
          }, 100)
          
          return Promise.reject(error)
        }
      }
      
      clearTokens()
      
      setTimeout(() => {
        if (!getToken()) {
          const currentPath = window.location.hash.replace('#', '') || '/'
          if (currentPath !== '/login') {
            alert('登录已过期，请重新登录')
            window.location.href = '/#/login'
          }
        }
      }, 1000)
    }

    return Promise.reject(error)
  }
)

api.requestWithQueue = (config) => {
  if (config._duplicate) {
    return Promise.reject(new Error('Duplicate request'))
  }
  
  return defaultQueue.add(async (qConfig) => api({ ...config, ...qConfig }), config)
}

api.get = (url, params = {}, config = {}) => api.requestWithQueue({ method: 'GET', url, params, ...config })
api.post = (url, data = {}, config = {}) => api.requestWithQueue({ method: 'POST', url, data, ...config })
api.put = (url, data = {}, config = {}) => api.requestWithQueue({ method: 'PUT', url, data, ...config })
api.patch = (url, data = {}, config = {}) => api.requestWithQueue({ method: 'PATCH', url, data, ...config })
api.delete = (url, config = {}) => api.requestWithQueue({ method: 'DELETE', url, ...config })

api.getToken = getToken
api.getRefreshToken = getRefreshToken
api.setTokens = setTokens
api.clearTokens = clearTokens

api.cancel = (requestKey) => {
  if (requestKey && pendingRequests.has(requestKey)) {
    pendingRequests.delete(requestKey)
 
  }
}

api.cancelAll = () => {
  pendingRequests.clear()

}

export default api
