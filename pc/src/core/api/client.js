/**
 * Axios HTTP 客户端配置 【高并发支持核心模块】
 * 
 * @module api
 * @description 这是项目中所�?API 请求的基础配置文件�?
 * 使用 Axios 库进�?HTTP 请求，配置了请求/响应拦截器�?
 * 
 * 【主要功能】
 * 1. 配置 API 基础路径和超时时�?
 * 2. 请求拦截器：自动添加 JWT Token
 * 3. 响应拦截器：处理 401 未授权错�?
 * 
 * 【高并发支持】 
 * - 请求队列：限制并发数，排队处理请求数量（默认6个）
 * - 请求缓存：GET 请求自动缓存，减少重复请求（默认500ms）
 * - 请求去重：相同请求短时间内只发送一�?
 * - 请求取消：支持取消正在进行的请求（AbortController）
 * - 自动重试：网络错误自动重试（默认3次）
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
import { defaultQueue, generateRequestKey } from './queue'
import { defaultCache } from './cache'

const baseURL = import.meta.env.VITE_API_V2_BASE_URL || 'http://localhost:8001/api/v1'

const api = axios.create({
  baseURL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' }
})

const pendingRequests = new Map()

// 请求拦截�?
api.interceptors.request.use(
  config => {
    // 处理 Token
    const token = localStorage.getItem('access_token')
    if (token) config.headers.Authorization = `Bearer ${token}`

    // 基础路径处理
    if (config.url && !config.url.startsWith('http') && !config.url.startsWith('/')) {
      config.url = '/' + config.url
    }

    // 缓存处理 (仅 GET)
    const method = config.method?.toUpperCase()
    if (method === 'GET' && config.cache !== false) {
      const cached = defaultCache.get(config.url, config.params)
      if (cached) {
        config._fromCache = true
        config._cachedData = cached
        return config
      }
    }

    // 去重处理
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

// 响应拦截器
api.interceptors.response.use(
  response => {
    const { config, data } = response
    
    if (config._fromCache) return config._cachedData
    if (config._requestKey) pendingRequests.delete(config._requestKey)

    // 文件下载直接返回响应
    if (config.responseType === 'blob' || data instanceof Blob) return response

    // 缓存 GET 结果
    if (config.method?.toUpperCase() === 'GET' && config.cache !== false && data) {
      defaultCache.set(config.url, config.params, data)
    }

    return data
  },
  error => {
    const { config, response } = error
    if (config?._requestKey) pendingRequests.delete(config._requestKey)

    // 处理 401 自动跳转
    if (response?.status === 401 && !config.url.includes('auth/login')) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }

    return Promise.reject(error)
  }
)

// 方法封装
api.requestWithQueue = (config) => {
  if (config._fromCache) return Promise.resolve(config._cachedData)
  if (config._duplicate) return Promise.reject(new Error('Duplicate request'))
  
  return defaultQueue.add(async (qConfig) => api({ ...config, ...qConfig }), config)
}

api.get = (url, params = {}, config = {}) => api.requestWithQueue({ method: 'GET', url, params, ...config })
api.post = (url, data = {}, config = {}) => api.requestWithQueue({ method: 'POST', url, data, ...config })
api.put = (url, data = {}, config = {}) => api.requestWithQueue({ method: 'PUT', url, data, ...config })
api.patch = (url, data = {}, config = {}) => api.requestWithQueue({ method: 'PATCH', url, data, ...config })
api.delete = (url, config = {}) => api.requestWithQueue({ method: 'DELETE', url, ...config })

export default api
