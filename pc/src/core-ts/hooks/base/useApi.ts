/**
 * API 调用组合式函数
 */

import { ref, onUnmounted, getCurrentInstance, type Ref } from 'vue'
import api from '../../api/client'
import { handleApiError, normalizeError } from '../../utils/errorHandler'
import { defaultCache } from '../../api/cache'
import { generateRequestKey } from '../../api/queue'
import { cacheManager, LIST_TYPE_MAP } from '../../services/cacheManager'
import type { UseApiOptions, ApiResponse } from '../../types'

interface UseApiReturn<T> {
  loading: Ref<boolean>
  error: Ref<Error | null>
  data: Ref<T | null>
  execute: (config?: any) => Promise<T | null>
  get: (params?: Record<string, any>, config?: any) => Promise<T | null>
  post: (payload?: any, config?: any) => Promise<T | null>
  put: (payload?: any, config?: any) => Promise<T | null>
  delete: (config?: any) => Promise<T | null>
  reset: () => void
  cancel: () => void
  clearCache: () => void
  refresh: (config?: any) => Promise<T | null>
}

export function useApi<T = any>(endpoint?: string | (() => string), options: UseApiOptions = {}): UseApiReturn<T> {
  const {
    immediate = false,
    defaultData = null,
    autoHandleError = true,
    onError,
    cache = false,
    cacheTime,
    dedupe = true,
    dedupeWindow,
    retry = true,
    retryTimes,
    resourceType,
    autoRefresh = true
  } = options

  const loading = ref(false)
  const error = ref<Error | null>(null)
  const data = ref<T | null>(defaultData) as Ref<T | null>
  
  let currentRequestKey: string | null = null
  let isCancelled = false

  const parseError = (err: unknown): Error => {
    return normalizeError(err)
  }

  const execute = async (config: any = {}): Promise<T | null> => {
    loading.value = true
    error.value = null
    isCancelled = false

    const shouldHandleError = config.autoHandleError !== undefined ? config.autoHandleError : autoHandleError
    
    const { autoHandleError: _, ...axiosConfig } = config

    const mergedConfig = {
      cache: config.cache !== undefined ? config.cache : cache,
      cacheTime: config.cacheTime || cacheTime,
      dedupe: config.dedupe !== undefined ? config.dedupe : dedupe,
      dedupeWindow: config.dedupeWindow || dedupeWindow,
      retry: config.retry !== undefined ? config.retry : retry,
      retryTimes: config.retryTimes || retryTimes,
      ...axiosConfig
    }

    try {
      const url = typeof endpoint === 'function' ? endpoint() : endpoint
      
      currentRequestKey = generateRequestKey({ url, ...mergedConfig })

      const method = mergedConfig.method?.toUpperCase() || 'GET'
      
      if (method === 'GET' && mergedConfig.cache !== false && url) {
        const cachedData = defaultCache.get(url, mergedConfig.params)
        if (cachedData) {
          data.value = cachedData
          loading.value = false
          return cachedData
        }
      }

      const response = await api<T>({
        url,
        ...mergedConfig
      })

      if (isCancelled) {
        return null
      }

      if (response && typeof response === 'object') {
        if ((response as ApiResponse).success !== undefined) {
          data.value = (response as ApiResponse).data || response
        } else {
          data.value = response
        }
      } else {
        data.value = response
      }

      if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method) && url) {
        const baseUrl = url.split('?')[0]
        const resourcePath = baseUrl.substring(0, baseUrl.lastIndexOf('/'))
        if (resourcePath) {
          defaultCache.clearPattern(new RegExp(`GET:${resourcePath}`, 'i'))
        }
        defaultCache.clearPattern(new RegExp(`GET:${baseUrl}`, 'i'))

        const effectiveResourceType = config.resourceType || resourceType
        const shouldAutoRefresh = config.autoRefresh !== undefined ? config.autoRefresh : autoRefresh

        if (effectiveResourceType && shouldAutoRefresh) {
          cacheManager.clearByResourceType(effectiveResourceType)
          cacheManager.triggerRefreshByResource(effectiveResourceType)
        }
      }

      return response
    } catch (err) {
      if (isCancelled) {
        return null
      }

      const errorInfo = parseError(err)
      error.value = errorInfo

      if (shouldHandleError) {
        await handleApiError(err, {
          showError: true,
          onError
        })
      }

      throw err
    } finally {
      loading.value = false
      currentRequestKey = null
    }
  }

  const get = async (params: Record<string, any> = {}, config: any = {}): Promise<T | null> => {
    return execute({
      method: 'GET',
      params,
      ...config
    })
  }

  const post = async (payload: any = {}, config: any = {}): Promise<T | null> => {
    return execute({
      method: 'POST',
      data: payload,
      ...config
    })
  }

  const put = async (payload: any = {}, config: any = {}): Promise<T | null> => {
    return execute({
      method: 'PUT',
      data: payload,
      ...config
    })
  }

  const del = async (config: any = {}): Promise<T | null> => {
    return execute({
      method: 'DELETE',
      ...config
    })
  }

  const reset = (): void => {
    loading.value = false
    error.value = null
    data.value = defaultData
    isCancelled = false
  }

  const cancel = (): void => {
    isCancelled = true
    if (currentRequestKey) {
      api.cancel(currentRequestKey)
    }
  }

  const clearCache = (): void => {
    const url = typeof endpoint === 'function' ? endpoint() : endpoint
    if (url) {
      defaultCache.delete(url)
    }
  }

  const refresh = async (config: any = {}): Promise<T | null> => {
    const url = typeof endpoint === 'function' ? endpoint() : endpoint
    if (url) {
      defaultCache.delete(url)
    }
    return get({}, config)
  }

  if (getCurrentInstance()) {
    onUnmounted(() => {
      cancel()
    })
  }

  if (immediate) {
    execute()
  }

  return {
    loading,
    error,
    data,
    
    execute,
    get,
    post,
    put,
    delete: del,
    reset,
    cancel,
    clearCache,
    refresh
  }
}

export default useApi
