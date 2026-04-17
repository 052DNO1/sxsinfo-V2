/**
 * API 调用组合式函数
 * 
 * 这是项目中最基础的网络请求封装，所有 API 调用都应该通过它进行。
 * 
 * 主要功能：
 * 1. 统一管理 API 请求的 loading、error、data 状态
 * 2. 集成统一错误处理机制
 * 3. 提供 GET、POST、PUT、DELETE 等便捷方法
 * 4. 高并发支持：缓存、去重、取消
 * 
 * 对于新手：
 * - Composable（组合式函数）是 Vue 3 推荐的代码复用方式
 * - 使用时通过 const { loading, data, get, post } = useApi() 获取状态和方法
 * - loading 是响应式的，可以直接在模板中使用
 * 
 * 使用示例：
 * ```js
 * // 基础用法
 * const { loading, data, get } = useApi('/api/users/')
 * await get()  // 发起 GET 请求
 * 
 * // 带参数的请求
 * const { data, get } = useApi()
 * await get({ page: 1, size: 10 }, { url: '/api/users/' })
 * 
 * // POST 请求
 * const { post } = useApi()
 * await post({ name: '张三' }, { url: '/api/users/' })
 * 
 * // 启用缓存
 * const { data, get } = useApi('/api/users/', { cache: true, cacheTime: 60000 })
 * 
 * // 禁用去重
 * const { post } = useApi('/api/submit/', { dedupe: false })
 * ```
 */
import { ref, onUnmounted, getCurrentInstance } from 'vue'
import api from '@/utils/api'
import { handleApiError, normalizeError } from '@/utils/errorHandler'
import { defaultCache } from '@/utils/requestCache'
import { generateRequestKey } from '@/utils/requestQueue'

/**
 * API 调用组合式函数
 * @param {string|Function} endpoint - API 端点路径，或返回路径的函数
 * @param {Object} options - 配置选项
 * @param {boolean} options.immediate - 是否立即执行请求（默认 false）
 * @param {Object} options.defaultData - 默认数据值
 * @param {boolean} options.autoHandleError - 是否自动处理错误并弹窗（默认 true）
 * @param {Function} options.onError - 自定义错误处理回调
 * @param {boolean} options.cache - 是否启用缓存（仅 GET 请求，默认 false）
 * @param {number} options.cacheTime - 缓存时间（毫秒，默认 5分钟）
 * @param {boolean} options.dedupe - 是否启用去重（默认 true）
 * @param {number} options.dedupeWindow - 去重时间窗口（毫秒，默认 500）
 * @param {boolean} options.retry - 是否启用重试（默认 true）
 * @param {number} options.retryTimes - 重试次数（默认 2）
 * @returns {Object} { loading, error, data, execute, get, post, put, delete, reset, cancel, clearCache }
 */
export function useApi(endpoint, options = {}) {
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
    retryTimes
  } = options

  const loading = ref(false)
  const error = ref(null)
  const data = ref(defaultData)
  
  let currentRequestKey = null
  let isCancelled = false

  const parseError = (err) => {
    return normalizeError(err)
  }

  const execute = async (config = {}) => {
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
      
      if (method === 'GET' && mergedConfig.cache !== false) {
        const cachedData = defaultCache.get(url, mergedConfig.params)
        if (cachedData) {
          data.value = cachedData
          loading.value = false
          return cachedData
        }
      }

      const response = await api({
        url,
        ...mergedConfig
      })

      if (isCancelled) {
        return null
      }

      if (response && typeof response === 'object') {
        if (response.success !== undefined) {
          data.value = response.data || response
        } else {
          data.value = response
        }
      } else {
        data.value = response
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

  const get = async (params = {}, config = {}) => {
    return execute({
      method: 'GET',
      params,
      ...config
    })
  }

  const post = async (payload = {}, config = {}) => {
    return execute({
      method: 'POST',
      data: payload,
      ...config
    })
  }

  const put = async (payload = {}, config = {}) => {
    return execute({
      method: 'PUT',
      data: payload,
      ...config
    })
  }

  const del = async (config = {}) => {
    return execute({
      method: 'DELETE',
      ...config
    })
  }

  const reset = () => {
    loading.value = false
    error.value = null
    data.value = defaultData
    isCancelled = false
  }

  const cancel = () => {
    isCancelled = true
    if (currentRequestKey) {
      api.cancel(currentRequestKey)
    }
  }

  const clearCache = () => {
    const url = typeof endpoint === 'function' ? endpoint() : endpoint
    if (url) {
      defaultCache.delete(url)
    }
  }

  const refresh = async (config = {}) => {
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
