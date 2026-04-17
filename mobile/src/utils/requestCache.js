/**
 * 请求缓存管理器 - 【高并发支持核心模块】
 * 
 * @module requestCache
 * @description 用于缓存 GET 请求的响应数据，减少重复请求，提升响应速度
 * 
 * 【缓存功能】
 * - 内存缓存：快速访问，页面刷新后清空
 * - 过期时间：支持设置缓存有效期（默认5分钟）
 * - 缓存键：基于 URL 和参数生成唯一标识
 * - LRU淘汰：缓存数量超过限制时淘汰最久未使用的
 * - 自动清理：每分钟自动清理过期缓存
 * 
 * @example
 * // 启用缓存
 * const { get } = useApi('/users/', { cache: true, cacheTime: 60000 })
 * 
 * // 清除缓存
 * import { defaultCache } from '@/utils/requestCache'
 * defaultCache.clear()
 */

/**
 * 缓存项类
 */
class CacheItem {
  constructor(data, timestamp, ttl) {
    this.data = data
    this.timestamp = timestamp
    this.ttl = ttl
  }

  isExpired() {
    if (this.ttl <= 0) return false
    return Date.now() - this.timestamp > this.ttl
  }
}

/**
 * 请求缓存类
 */
class RequestCache {
  /**
   * @param {Object} options - 配置选项
   * @param {number} options.defaultTTL - 默认缓存时间（毫秒，默认5分钟）
   * @param {number} options.maxSize - 最大缓存数量（默认100）
   */
  constructor(options = {}) {
    this.defaultTTL = options.defaultTTL || 5 * 60 * 1000
    this.maxSize = options.maxSize || 100
    this.cache = new Map()
    this.accessOrder = []
  }

  /**
   * 生成缓存键
   * @param {string} url - 请求URL
   * @param {Object} params - 请求参数
   * @returns {string} 缓存键
   */
  generateKey(url, params = null) {
    if (!params || Object.keys(params).length === 0) {
      return `GET:${url}`
    }
    const sortedParams = Object.keys(params)
      .sort()
      .map(k => `${k}=${JSON.stringify(params[k])}`)
      .join('&')
    return `GET:${url}?${sortedParams}`
  }

  /**
   * 获取缓存
   * @param {string} url - 请求URL
   * @param {Object} params - 请求参数
   * @returns {Object|null} 缓存数据或null
   */
  get(url, params = null) {
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
    
    return item.data
  }

  /**
   * 设置缓存
   * @param {string} url - 请求URL
   * @param {Object} params - 请求参数
   * @param {any} data - 缓存数据
   * @param {number} ttl - 缓存时间（毫秒）
   */
  set(url, params, data, ttl = this.defaultTTL) {
    const key = this.generateKey(url, params)
    
    if (this.cache.size >= this.maxSize && !this.cache.has(key)) {
      this.evict()
    }
    
    this.cache.set(key, new CacheItem(data, Date.now(), ttl))
    
    const existingIndex = this.accessOrder.indexOf(key)
    if (existingIndex !== -1) {
      this.accessOrder.splice(existingIndex, 1)
    }
    this.accessOrder.push(key)
  }

  /**
   * 删除缓存
   * @param {string} url - 请求URL
   * @param {Object} params - 请求参数
   * @returns {boolean} 是否删除成功
   */
  delete(url, params = null) {
    const key = this.generateKey(url, params)
    const result = this.cache.delete(key)
    
    const index = this.accessOrder.indexOf(key)
    if (index !== -1) {
      this.accessOrder.splice(index, 1)
    }
    
    return result
  }

  /**
   * 清除所有缓存
   */
  clear() {
    this.cache.clear()
    this.accessOrder = []
  }

  /**
   * 清除匹配的缓存
   * @param {string|RegExp} pattern - 匹配模式
   */
  clearPattern(pattern) {
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

  /**
   * 清除过期缓存
   */
  cleanup() {
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

  /**
   * 淘汰最久未使用的缓存
   */
  evict() {
    if (this.accessOrder.length === 0) return
    
    const oldestKey = this.accessOrder.shift()
    this.cache.delete(oldestKey)
  }

  /**
   * 获取缓存状态
   * @returns {Object} 缓存状态
   */
  getStatus() {
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

  /**
   * 检查是否有缓存
   * @param {string} url - 请求URL
   * @param {Object} params - 请求参数
   * @returns {boolean} 是否有缓存
   */
  has(url, params = null) {
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

export default RequestCache
