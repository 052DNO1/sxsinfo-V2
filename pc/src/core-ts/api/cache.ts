/**
 * 请求缓存管理器 - 【高并发支持核心模块】
 * 
 * @module requestCache
 * @description 用于缓存 GET 请求的响应数据，减少重复请求，提升响应速度
 * 
 * 【缓存功能】
 * - 内存缓存：快速访问，页面刷新后清除
 * - 过期时间：支持设置缓存有效期（默认1分钟）
 * - 缓存键：基于 URL 和参数生成唯一标识
 * - LRU淘汰：缓存数量超过限制时淘汰最久未使用的
 * - 自动清理：每分钟自动清理过期缓存
 */

import type { CacheItem, CacheStatus } from '../types'

class CacheItemImpl<T = any> implements CacheItem<T> {
  data: T
  timestamp: number
  ttl: number

  constructor(data: T, timestamp: number, ttl: number) {
    this.data = data
    this.timestamp = timestamp
    this.ttl = ttl
  }

  isExpired(): boolean {
    if (this.ttl <= 0) return false
    return Date.now() - this.timestamp > this.ttl
  }
}

interface RequestCacheOptions {
  defaultTTL?: number
  maxSize?: number
}

class RequestCache {
  private defaultTTL: number
  private maxSize: number
  private cache: Map<string, CacheItemImpl>
  private accessOrder: string[]

  constructor(options: RequestCacheOptions = {}) {
    this.defaultTTL = options.defaultTTL || 1 * 60 * 1000
    this.maxSize = options.maxSize || 100
    this.cache = new Map()
    this.accessOrder = []
  }

  generateKey(url: string, params: Record<string, any> | null = null): string {
    if (!params || Object.keys(params).length === 0) {
      return `GET:${url}`
    }
    const sortedParams = Object.keys(params)
      .sort()
      .map(k => `${k}=${JSON.stringify(params[k])}`)
      .join('&')
    return `GET:${url}?${sortedParams}`
  }

  get<T = any>(url: string, params: Record<string, any> | null = null): T | null {
    const key = this.generateKey(url, params)
    const item = this.cache.get(key)
    
    if (!item) return null
    
    if (item.isExpired()) {
      this.cache.delete(key)
      const index = this.accessOrder.indexOf(key)
      if (index !== -1) {
        this.accessOrder.splice(index, 1)
      }
      return null
    }
    
    const keyIndex = this.accessOrder.indexOf(key)
    if (keyIndex !== -1) {
      this.accessOrder.splice(keyIndex, 1)
      this.accessOrder.push(key)
    }
    
    return item.data as T
  }

  set<T = any>(url: string, params: Record<string, any> | null, data: T, ttl: number = this.defaultTTL): void {
    const key = this.generateKey(url, params)
    
    if (this.cache.size >= this.maxSize && !this.cache.has(key)) {
      this.evict()
    }
    
    this.cache.set(key, new CacheItemImpl(data, Date.now(), ttl))
    
    const existingIndex = this.accessOrder.indexOf(key)
    if (existingIndex !== -1) {
      this.accessOrder.splice(existingIndex, 1)
    }
    this.accessOrder.push(key)
  }

  delete(url: string, params: Record<string, any> | null = null): boolean {
    const key = this.generateKey(url, params)
    const result = this.cache.delete(key)
    
    const index = this.accessOrder.indexOf(key)
    if (index !== -1) {
      this.accessOrder.splice(index, 1)
    }
    
    return result
  }

  clear(): void {
    this.cache.clear()
    this.accessOrder = []
  }

  clearPattern(pattern: RegExp | string): void {
    const regex = typeof pattern === 'string' ? new RegExp(pattern) : pattern
    
    for (const key of this.cache.keys()) {
      if (regex.test(key)) {
        this.cache.delete(key)
        const index = this.accessOrder.indexOf(key)
        if (index !== -1) {
          this.accessOrder.splice(index, 1)
        }
      }
    }
  }

  cleanup(): void {
    for (const [key, item] of this.cache.entries()) {
      if (item.isExpired()) {
        this.cache.delete(key)
        const index = this.accessOrder.indexOf(key)
        if (index !== -1) {
          this.accessOrder.splice(index, 1)
        }
      }
    }
  }

  private evict(): void {
    if (this.accessOrder.length === 0) return
    
    const oldestKey = this.accessOrder.shift()
    if (oldestKey) {
      this.cache.delete(oldestKey)
    }
  }

  getStatus(): CacheStatus {
    let expiredCount = 0
    for (const item of this.cache.values()) {
      if (item.isExpired()) expiredCount++
    }
    
    return {
      size: this.cache.size,
      maxSize: this.maxSize,
      expiredCount,
      defaultTTL: this.defaultTTL
    }
  }

  has(url: string, params: Record<string, any> | null = null): boolean {
    const key = this.generateKey(url, params)
    const item = this.cache.get(key)
    
    if (!item) return false
    if (item.isExpired()) {
      this.cache.delete(key)
      return false
    }
    
    return true
  }
}

const defaultCache = new RequestCache()

setInterval(() => {
  defaultCache.cleanup()
}, 60 * 1000)

export { RequestCache, defaultCache }
export type { RequestCacheOptions }
export default RequestCache
