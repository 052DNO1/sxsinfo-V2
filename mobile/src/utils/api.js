/**
 * Axios HTTP 客户端配置 - 【高并发支持核心模块】
 * 
 * @module api
 * @description 这是项目中所有 API 请求的基础配置文件。
 * 使用 Axios 库进行 HTTP 请求，配置了请求/响应拦截器。
 * 
 * 【主要功能】
 * 1. 配置 API 基础路径和超时时间
 * 2. 请求拦截器：自动添加 JWT Token
 * 3. 响应拦截器：处理 401 未授权错误
 * 
 * 【高并发支持】
 * - 请求队列：限制并发数，排队处理请求
 * - 请求缓存：GET 请求自动缓存，减少重复请求
 * - 请求去重：相同请求短时间内只发送一次
 * - 请求取消：支持取消正在进行的请求
 * - 自动重试：网络错误自动重试
 * 
 * @example
 * // GET 请求（自动缓存）
 * const response = await api.get('/users/')
 * 
 * // POST 请求（自动去重）
 * const result = await api.post('/login/', { username, password })
 * 
 * // 取消所有请求
 * api.cancelAll()
 * 
 * // 清除缓存
 * api.clearCache()
 */
import axios from 'axios'
import { defaultQueue, generateRequestKey } from './requestQueue'
import { defaultCache } from './requestCache'

const baseURL = import.meta.env.VITE_API_BASE_URL || window.location.origin + '/api'

const api = axios.create({
  baseURL: baseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  },
})

const pendingRequests = new Map()

api.interceptors.request.use(
  config => {
    if (config.url && typeof config.url === 'string') {
      if (config.url.includes(':')) {
        console.error('❌ API路径包含路由参数格式:', config.url)
      }
      if (!config.url.startsWith('/')) {
        config.url = '/' + config.url
      }
    }

    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }

    const method = config.method?.toUpperCase() || 'GET'
    if (method === 'GET' && config.cache !== false) {
      const cachedData = defaultCache.get(config.url, config.params)
      if (cachedData) {
        config._fromCache = true
        config._cachedData = cachedData
        return config
      }
    }

    if (config.dedupe !== false) {
      const key = generateRequestKey(config)
      if (pendingRequests.has(key)) {
        config._duplicate = true
        config._duplicateKey = key
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
    const config = response.config
    
    if (config._fromCache) {
      return config._cachedData
    }

    if (config._requestKey) {
      pendingRequests.delete(config._requestKey)
    }

    if (response.config?.responseType === 'blob' || response.data instanceof Blob) {
      return response
    }

    const data = response.data
    const contentType = response.headers['content-type'] || ''

    if (typeof data === 'string' && (data.trim().startsWith('<!DOCTYPE html>') || data.trim().startsWith('<html'))) {
      console.error('❌ API返回了HTML而不是JSON')
      console.error('请求URL:', response.config?.url)
      console.error('响应状态:', response.status)

      return {
        error: 'API返回了HTML响应，请检查API路径和服务器状态',
        htmlResponse: true,
        status: response.status,
        url: response.config?.url
      }
    }

    const method = config?.method?.toUpperCase() || 'GET'
    if (method === 'GET' && config?.cache !== false && data) {
      const cacheTime = config.cacheTime || defaultCache.defaultTTL
      defaultCache.set(config.url, config?.params, data, cacheTime)
    }

    return data
  },
  
  error => {
    const config = error.config
    
    if (config?._requestKey) {
      pendingRequests.delete(config._requestKey)
    }

    if (error.response?.status === 401 && error.config?.responseType === 'blob') {
      return Promise.reject(error)
    }

    if (error.response?.status !== 401) {
      return Promise.reject(error)
    }

    const url = error.config?.url || ''
    const currentPath = window.location.pathname
    const method = error.config?.method?.toUpperCase() || ''
    const isLoginAPI = url.includes('/login')
    const isLoginPage = currentPath === '/login' || currentPath.startsWith('/login')
    const isLoginGetRequest = isLoginAPI && method === 'GET'

    if (isLoginGetRequest) {
      return Promise.resolve({ success: false, message: '未登录', data: { requires_login: true } })
    }

    if (isLoginAPI || isLoginPage) {
      return Promise.reject(error)
    }

    const redirectKey = 'auth_redirecting'
    const redirectTimestamp = sessionStorage.getItem(redirectKey)
    const now = Date.now()
    if (redirectTimestamp && (now - parseInt(redirectTimestamp)) < 10000) {
      return Promise.reject(error)
    }

    sessionStorage.setItem(redirectKey, now.toString())
    sessionStorage.removeItem('user')

    const isMobile = window.location.pathname.startsWith('/m')
    const loginPath = isMobile ? '/m/#/login' : '/login'
    window.location.href = loginPath

    setTimeout(() => sessionStorage.removeItem(redirectKey), 10000)

    return Promise.reject(error)
  }
)

api.requestWithQueue = async function(config) {
  if (config._fromCache) {
    return config._cachedData
  }

  if (config._duplicate) {
    return Promise.reject(new Error('重复请求已被拦截'))
  }

  return defaultQueue.add(
    async ({ signal, ...restConfig }) => {
      return api({
        ...config,
        ...restConfig,
        signal
      })
    },
    config
  )
}

api.get = async function(url, params = {}, config = {}) {
  const mergedConfig = {
    method: 'GET',
    url,
    params,
    ...config
  }
  
  const cachedData = defaultCache.get(url, params)
  if (cachedData && config.cache !== false) {
    return cachedData
  }
  
  return api.requestWithQueue(mergedConfig)
}

api.post = async function(url, data = {}, config = {}) {
  return api.requestWithQueue({
    method: 'POST',
    url,
    data,
    ...config
  })
}

api.put = async function(url, data = {}, config = {}) {
  return api.requestWithQueue({
    method: 'PUT',
    url,
    data,
    ...config
  })
}

api.delete = async function(url, config = {}) {
  return api.requestWithQueue({
    method: 'DELETE',
    url,
    ...config
  })
}

api.cancelAll = function() {
  defaultQueue.cancelAll()
}

api.cancel = function(key) {
  defaultQueue.cancel(key)
}

api.clearCache = function(pattern = null) {
  if (pattern) {
    defaultCache.clearPattern(pattern)
  } else {
    defaultCache.clear()
  }
}

api.getQueueStatus = function() {
  return defaultQueue.getStatus()
}

api.getCacheStatus = function() {
  return defaultCache.getStatus()
}

export default api
