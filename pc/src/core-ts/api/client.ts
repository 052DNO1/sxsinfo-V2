/**
 * Axios HTTP 客户端配置 【高并发支持核心模块】
 * 
 * @module api
 * @description 这是项目中所有 API 请求的基础配置文件
 * 使用 Axios 库进行HTTP 请求，配置了请求/响应拦截器
 */

import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse, type InternalAxiosRequestConfig } from 'axios'
import { defaultQueue, generateRequestKey } from './queue'
import { defaultCache } from './cache'
import type { ApiResponse, HttpMethod } from '../types'

interface ExtendedAxiosRequestConfig extends InternalAxiosRequestConfig {
  _fromCache?: boolean
  _cachedData?: any
  _duplicate?: boolean
  _requestKey?: string
  cache?: boolean
  dedupe?: boolean
}

const baseURL = import.meta.env.VITE_API_V2_BASE_URL || 'http://localhost:8000/api/v1'

const api: AxiosInstance = axios.create({
  baseURL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' }
})

const pendingRequests = new Map<string, boolean>()

const isStatisticsApi = (url: string): boolean => {
  const statisticsPatterns = [
    /\/statistics/i,
    /\/stats/i,
    /\/analytics/i,
    /\/reports/i,
    /\/dashboard/i,
    /\/metrics/i,
    /\/overview/i
  ]
  return statisticsPatterns.some(pattern => pattern.test(url))
}

api.interceptors.request.use(
  (config: ExtendedAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }

    if (config.url && !config.url.startsWith('http') && !config.url.startsWith('/')) {
      config.url = '/' + config.url
    }

    const method = config.method?.toUpperCase()
    if (method === 'GET' && config.cache !== false) {
      if (isStatisticsApi(config.url || '')) {
        config.cache = false
      } else {
        const cached = defaultCache.get(config.url || '', config.params)
        if (cached) {
          config._fromCache = true
          config._cachedData = cached
          return config
        }
      }
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
  (response: AxiosResponse) => {
    const { config, data } = response
    const extendedConfig = config as ExtendedAxiosRequestConfig
    
    if (extendedConfig._fromCache) return extendedConfig._cachedData
    if (extendedConfig._requestKey) pendingRequests.delete(extendedConfig._requestKey)

    if (config.responseType === 'blob' || data instanceof Blob) return response

    if (config.method?.toUpperCase() === 'GET' && extendedConfig.cache !== false && data) {
      defaultCache.set(config.url || '', config.params, data)
    }

    const method = config.method?.toUpperCase()
    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method || '')) {
      const baseUrl = (config.url || '').split('?')[0]
      const resourcePath = baseUrl.substring(0, baseUrl.lastIndexOf('/'))
      if (resourcePath) {
        defaultCache.clearPattern(new RegExp(`GET:${resourcePath}`, 'i'))
      }
      defaultCache.clearPattern(new RegExp(`GET:${baseUrl}`, 'i'))
    }

    return data
  },
  (error) => {
    const { config, response } = error
    const extendedConfig = config as ExtendedAxiosRequestConfig
    if (extendedConfig?._requestKey) pendingRequests.delete(extendedConfig._requestKey)

    if (response?.status === 401 && !config?.url?.includes('auth/login')) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }

    return Promise.reject(error)
  }
)

interface ApiInstance extends AxiosInstance {
  requestWithQueue<T = any>(config: AxiosRequestConfig): Promise<T>
  get<T = any>(url: string, params?: Record<string, any>, config?: AxiosRequestConfig): Promise<T>
  post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T>
  put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T>
  patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T>
  delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T>
  cancel(key: string): void
  cancelAll(): void
  clearCache(): void
}

const extendedApi = api as ApiInstance

extendedApi.requestWithQueue = function<T = any>(config: ExtendedAxiosRequestConfig): Promise<T> {
  if (config._fromCache) return Promise.resolve(config._cachedData)
  if (config._duplicate) return Promise.reject(new Error('Duplicate request'))
  
  return defaultQueue.add(async (qConfig) => api({ ...config, ...qConfig }), config)
}

extendedApi.get = function<T = any>(url: string, params: Record<string, any> = {}, config: AxiosRequestConfig = {}): Promise<T> {
  return extendedApi.requestWithQueue<T>({ method: 'GET', url, params, ...config })
}

extendedApi.post = function<T = any>(url: string, data: any = {}, config: AxiosRequestConfig = {}): Promise<T> {
  return extendedApi.requestWithQueue<T>({ method: 'POST', url, data, ...config })
}

extendedApi.put = function<T = any>(url: string, data: any = {}, config: AxiosRequestConfig = {}): Promise<T> {
  return extendedApi.requestWithQueue<T>({ method: 'PUT', url, data, ...config })
}

extendedApi.patch = function<T = any>(url: string, data: any = {}, config: AxiosRequestConfig = {}): Promise<T> {
  return extendedApi.requestWithQueue<T>({ method: 'PATCH', url, data, ...config })
}

extendedApi.delete = function<T = any>(url: string, config: AxiosRequestConfig = {}): Promise<T> {
  return extendedApi.requestWithQueue<T>({ method: 'DELETE', url, ...config })
}

extendedApi.cancel = function(key: string): void {
  defaultQueue.cancel(key)
}

extendedApi.cancelAll = function(): void {
  defaultQueue.cancelAll()
}

extendedApi.clearCache = function(): void {
  defaultCache.clear()
}

export default extendedApi
export type { ApiInstance, ExtendedAxiosRequestConfig }
