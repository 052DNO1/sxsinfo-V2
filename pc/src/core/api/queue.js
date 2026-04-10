/**
 * 请求队列管理 【高并发支持核心模块】
 * 
 * @module requestQueue
 * @description 用于控制并发请求数量，防止大量请求同时发送导致：
 * - 浏览器连接数限制
 * - 服务器压力过?
 * - 网络拥塞
 * 
 * 【高并发功能】
 * - 并发控制：限制同时进行的请求数量（默认6个）
 * - 请求去重：相同请求在短时间内只发送一次（默认500ms）
 * - 请求取消：支持取消正在进行的请求（AbortController）
 * - 自动重试：网络错误时自动重试（默?次）
 * 
 * @example
 * // 获取队列状态
 * import { defaultQueue } from '@/core/api/queue'
 * console.log(defaultQueue.getStatus())
 */

function generateRequestKey(config) {
  const { method, url, params, data } = config || {}
  const sortedParams = params ? JSON.stringify(Object.keys(params).sort().map(k => [k, params[k]])) : ''
  let sortedData = ''
  if (data) {
    if (data instanceof FormData) {
      const formDataKeys = []
      for (const key of data.keys()) {
        const value = data.get(key)
        if (value instanceof File || value instanceof Blob) {
          formDataKeys.push([key, `file:${value.name}:${value.size}`])
        } else {
          formDataKeys.push([key, value])
        }
      }
      sortedData = 'FormData:' + JSON.stringify(formDataKeys.sort())
    } else if (typeof data === 'object') {
      sortedData = JSON.stringify(Object.keys(data).sort().map(k => [k, data[k]]))
    }
  }
  return `${method?.toUpperCase() || 'GET'}:${url || ''}:${sortedParams}:${sortedData}`
}

class RequestQueue {
  constructor(options = {}) {
    this.maxConcurrent = options.maxConcurrent || 6
    this.dedupeWindow = options.dedupeWindow || 500
    this.retryTimes = options.retryTimes || 2
    this.retryDelay = options.retryDelay || 1000
    
    this.pending = new Map()
    this.queue = []
    this.activeCount = 0
    this.dedupeMap = new Map()
    this.abortControllers = new Map()
  }

  isDuplicate(key) {
    const now = Date.now()
    const lastTime = this.dedupeMap.get(key)
    
    if (lastTime && now - lastTime < this.dedupeWindow) {
      return true
    }
    
    this.dedupeMap.set(key, now)
    return false
  }

  cleanupDedupeMap() {
    const now = Date.now()
    for (const [key, time] of this.dedupeMap.entries()) {
      if (now - time > this.dedupeWindow * 2) {
        this.dedupeMap.delete(key)
      }
    }
  }

  async add(requestFn, config = {}) {
    const key = generateRequestKey(config)
    
    if (config.dedupe !== false && this.isDuplicate(key)) {
      const pendingRequest = this.pending.get(key)
      if (pendingRequest) {
        return pendingRequest
      }
      return Promise.reject(new Error('重复请求已被拦截'))
    }
    
    const abortController = new AbortController()
    this.abortControllers.set(key, abortController)
    
    const requestPromise = new Promise((resolve, reject) => {
      this.queue.push({
        key,
        requestFn,
        config,
        abortController,
        resolve,
        reject,
        retryCount: 0
      })
      
      this.process()
    })
    
    this.pending.set(key, requestPromise)
    
    requestPromise
      .finally(() => {
        this.pending.delete(key)
        this.abortControllers.delete(key)
      })
    
    return requestPromise
  }

  async process() {
    while (this.activeCount < this.maxConcurrent && this.queue.length > 0) {
      const task = this.queue.shift()
      if (!task) break
      
      this.activeCount++
      
      this.executeTask(task)
        .finally(() => {
          this.activeCount--
          this.process()
        })
    }
    
    if (this.dedupeMap.size > 100) {
      this.cleanupDedupeMap()
    }
  }

  async executeTask(task) {
    const { key, requestFn, config, abortController, resolve, reject, retryCount } = task
    
    try {
      const signal = abortController.signal
      const result = await requestFn({ signal, ...config })
      resolve(result)
    } catch (error) {
      if (error.name === 'AbortError' || error.name === 'CanceledError') {
        reject(new Error('请求已取消'))
        return
      }
      
      const shouldRetry = this.shouldRetry(error, retryCount, config)
      
      if (shouldRetry) {
        task.retryCount++
        await this.delay(this.retryDelay)
        
        if (!abortController.signal.aborted) {
          this.queue.unshift(task)
          this.process()
          return
        }
      }
      
      reject(error)
    }
  }

  shouldRetry(error, retryCount, config) {
    if (config.retry === false) return false
    if (retryCount >= (config.retryTimes ?? this.retryTimes)) return false
    
    const status = error.response?.status
    if (status && status >= 400 && status < 500) return false
    
    if (error.code === 'ECONNABORTED') return true
    if (error.code === 'ERR_NETWORK') return true
    if (error.code === 'ETIMEDOUT') return true
    if (!error.response && error.message?.includes('Network Error')) return true
    
    if (status >= 500) return true
    
    return false
  }

  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  cancel(key) {
    const controller = this.abortControllers.get(key)
    if (controller) {
      controller.abort()
      this.abortControllers.delete(key)
    }
    
    const queueIndex = this.queue.findIndex(task => task.key === key)
    if (queueIndex !== -1) {
      const task = this.queue.splice(queueIndex, 1)[0]
      task.reject(new Error('请求已取消'))
    }
  }

  cancelAll() {
    for (const controller of this.abortControllers.values()) {
      controller.abort()
    }
    this.abortControllers.clear()
    
    while (this.queue.length > 0) {
      const task = this.queue.shift()
      task.reject(new Error('请求已取消'))
    }
  }

  getStatus() {
    return {
      activeCount: this.activeCount,
      queueLength: this.queue.length,
      pendingCount: this.pending.size,
      maxConcurrent: this.maxConcurrent
    }
  }
}

const defaultQueue = new RequestQueue()

export { RequestQueue, generateRequestKey, defaultQueue }

export default RequestQueue
