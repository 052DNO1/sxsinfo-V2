/**
 * 请求队列管理 【高并发支持核心模块】
 * 
 * @module requestQueue
 * @description 用于控制并发请求数量，防止大量请求同时发送导致：
 * - 浏览器连接数限制
 * - 服务器压力过大
 * - 网络拥塞
 */

import type { RequestQueueStatus, HttpMethod } from '../types'

interface RequestTask {
  key: string
  requestFn: (config: any) => Promise<any>
  config: any
  abortController: AbortController
  resolve: (value: any) => void
  reject: (reason: any) => void
  retryCount: number
}

interface RequestQueueOptions {
  maxConcurrent?: number
  dedupeWindow?: number
  retryTimes?: number
  retryDelay?: number
}

function generateRequestKey(config: any): string {
  const { method, url, params, data } = config || {}
  const sortedParams = params ? JSON.stringify(Object.keys(params).sort().map(k => [k, params[k]])) : ''
  let sortedData = ''
  if (data) {
    if (data instanceof FormData) {
      const formDataKeys: [string, any][] = []
      for (const key of data.keys()) {
        const value = data.get(key)
        if (value instanceof File || value instanceof Blob) {
          formDataKeys.push([key, `file:${(value as File | Blob).name}:${(value as File | Blob).size}`])
        } else {
          formDataKeys.push([key, value])
        }
      }
      sortedData = 'FormData:' + JSON.stringify(formDataKeys.sort())
    } else if (typeof data === 'object') {
      sortedData = JSON.stringify(Object.keys(data).sort().map(k => [k, data[k]]))
    }
  }
  return `${(method as string)?.toUpperCase() || 'GET'}:${url || ''}:${sortedParams}:${sortedData}`
}

class RequestQueue {
  private maxConcurrent: number
  private dedupeWindow: number
  private retryTimes: number
  private retryDelay: number
  
  private pending: Map<string, Promise<any>>
  private queue: RequestTask[]
  private activeCount: number
  private dedupeMap: Map<string, number>
  private abortControllers: Map<string, AbortController>

  constructor(options: RequestQueueOptions = {}) {
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

  private isDuplicate(key: string): boolean {
    const now = Date.now()
    const lastTime = this.dedupeMap.get(key)
    
    if (lastTime && now - lastTime < this.dedupeWindow) {
      return true
    }
    
    this.dedupeMap.set(key, now)
    return false
  }

  private cleanupDedupeMap(): void {
    const now = Date.now()
    for (const [key, time] of this.dedupeMap.entries()) {
      if (now - time > this.dedupeWindow * 2) {
        this.dedupeMap.delete(key)
      }
    }
  }

  async add<T = any>(requestFn: (config: any) => Promise<T>, config: any = {}): Promise<T> {
    const key = generateRequestKey(config)
    
    if (config.dedupe !== false && this.isDuplicate(key)) {
      const pendingRequest = this.pending.get(key)
      if (pendingRequest) {
        return pendingRequest as Promise<T>
      }
      return Promise.reject(new Error('重复请求已被拦截'))
    }
    
    const abortController = new AbortController()
    this.abortControllers.set(key, abortController)
    
    const requestPromise = new Promise<T>((resolve, reject) => {
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

  private async process(): Promise<void> {
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

  private async executeTask(task: RequestTask): Promise<void> {
    const { key, requestFn, config, abortController, resolve, reject, retryCount } = task
    
    try {
      const signal = abortController.signal
      const result = await requestFn({ signal, ...config })
      resolve(result)
    } catch (error: any) {
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

  private shouldRetry(error: any, retryCount: number, config: any): boolean {
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

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  cancel(key: string): void {
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

  cancelAll(): void {
    for (const controller of this.abortControllers.values()) {
      controller.abort()
    }
    this.abortControllers.clear()
    
    while (this.queue.length > 0) {
      const task = this.queue.shift()
      if (task) {
        task.reject(new Error('请求已取消'))
      }
    }
  }

  getStatus(): RequestQueueStatus {
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
export type { RequestQueueOptions }
export default RequestQueue
