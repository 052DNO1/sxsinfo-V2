/**
 * 缓存管理服务
 * 提供统一的缓存清理和列表刷新机制
 * 
 * @module cacheManager
 * @description 
 * - 操作成功后自动清理相关缓存并触发列表刷新
 * - 操作失败则不清理缓存
 * - 支持模式匹配批量清理
 */

import { defaultCache } from '@/core/api/cache'
import { useAppStore } from '@/core/store/app'

const LIST_TYPE_MAP = {
  schedules: 'schedules',
  laboratories: 'labs',
  labs: 'labs',
  equipment: 'devices',
  devices: 'devices',
  users: 'users',
  semesters: 'semesters',
  departments: 'departments',
  records: 'records',
  'usage-records': 'records',
  'work-orders': 'maintenances',
  maintenances: 'maintenances'
}

const API_PATTERN_MAP = {
  schedules: ['/api/schedules/', '/api/laboratories/', '/api/statistics/'],
  laboratories: ['/api/laboratories/', '/api/statistics/'],
  labs: ['/api/laboratories/', '/api/statistics/'],
  equipment: ['/api/equipment/', '/api/laboratories/', '/api/statistics/'],
  devices: ['/api/equipment/', '/api/laboratories/', '/api/statistics/'],
  users: ['/api/users/', '/api/statistics/'],
  semesters: ['/api/semesters/', '/api/schedules/', '/api/statistics/'],
  departments: ['/api/departments/', '/api/users/', '/api/statistics/'],
  records: ['/api/records/', '/api/statistics/'],
  'usage-records': ['/api/records/', '/api/statistics/'],
  'work-orders': ['/api/work-orders/', '/api/maintenance/', '/api/statistics/'],
  maintenances: ['/api/work-orders/', '/api/maintenance/', '/api/statistics/']
}

class CacheManager {
  constructor() {
    this._pendingClears = new Set()
    this._pendingRefreshes = new Set()
    this._inTransaction = false
  }

  clearCache(pattern) {
    if (this._inTransaction) {
      this._pendingClears.add(pattern)
    } else {
      if (pattern instanceof RegExp) {
        defaultCache.clearPattern(pattern)
      } else {
        const regex = new RegExp(pattern, 'i')
        defaultCache.clearPattern(regex)
      }
    }
  }

  clearByApiPath(apiPath) {
    const pattern = `GET:${apiPath}`
    this.clearCache(pattern)
  }

  clearByResourceType(resourceType) {
    const actualPatterns = {
      schedules: ['GET:/schedules', 'GET:/laboratories'],
      laboratories: ['GET:/laboratories'],
      labs: ['GET:/laboratories'],
      equipment: ['GET:/equipment', 'GET:/laboratories'],
      devices: ['GET:/equipment', 'GET:/laboratories'],
      users: ['GET:/users'],
      semesters: ['GET:/semesters', 'GET:/schedules'],
      departments: ['GET:/departments'],
      records: ['GET:/records'],
      maintenances: ['GET:/work-orders', 'GET:/maintenance']
    }
    const patterns = actualPatterns[resourceType] || []
    patterns.forEach(pattern => {
      this.clearCache(pattern)
    })
  }

  triggerRefresh(listType) {
    if (this._inTransaction) {
      this._pendingRefreshes.add(listType)
    } else {
      try {
        const appStore = useAppStore()
        appStore.triggerListRefresh(listType)
      } catch (e) {
        console.warn('Failed to trigger refresh:', e)
      }
    }
  }

  triggerRefreshByResource(resourceType) {
    const listType = LIST_TYPE_MAP[resourceType]
    if (listType) {
      this.triggerRefresh(listType)
    }
  }

  notifyChange(resourceType) {
    try {
      const appStore = useAppStore()
      appStore.notifyDataChange(resourceType)
      appStore.recordUpdateTime(resourceType)
    } catch (e) {
      console.warn('Failed to notify data change:', e)
    }
  }

  enterTransaction() {
    this._inTransaction = true
    this._pendingClears.clear()
    this._pendingRefreshes.clear()
  }

  commitTransaction() {
    this._pendingClears.forEach(pattern => {
      try {
        if (pattern instanceof RegExp) {
          defaultCache.clearPattern(pattern)
        } else {
          const regex = new RegExp(pattern, 'i')
          defaultCache.clearPattern(regex)
        }
      } catch (e) {
        console.warn('Failed to clear cache:', e)
      }
    })

    const appStore = useAppStore()
    this._pendingRefreshes.forEach(listType => {
      try {
        appStore.triggerListRefresh(listType)
      } catch (e) {
        console.warn('Failed to trigger refresh:', e)
      }
    })

    this._inTransaction = false
    this._pendingClears.clear()
    this._pendingRefreshes.clear()
  }

  rollbackTransaction() {
    this._inTransaction = false
    this._pendingClears.clear()
    this._pendingRefreshes.clear()
  }

  clearAll() {
    defaultCache.clear()
    const appStore = useAppStore()
    Object.keys(LIST_TYPE_MAP).forEach(key => {
      const listType = LIST_TYPE_MAP[key]
      if (listType) {
        appStore.triggerListRefresh(listType)
      }
    })
  }
}

const cacheManager = new CacheManager()

export function useCacheManager() {
  return cacheManager
}

export function withCacheClear(resourceType, options = {}) {
  const { 
    clearCache = true, 
    triggerRefresh = true,
    onSuccess,
    onError
  } = options

  return function(target, propertyKey, descriptor) {
    const originalMethod = descriptor.value

    descriptor.value = async function(...args) {
      try {
        const result = await originalMethod.apply(this, args)

        if (clearCache) {
          cacheManager.clearByResourceType(resourceType)
        }

        if (triggerRefresh) {
          cacheManager.notifyChange(resourceType)
        }

        if (onSuccess) {
          onSuccess(result, args)
        }

        return result
      } catch (error) {
        if (onError) {
          onError(error, args)
        }
        throw error
      }
    }

    return descriptor
  }
}

export function createCachedOperation(resourceType) {
  return {
    onSuccess: (result) => {
      cacheManager.clearByResourceType(resourceType)
      cacheManager.notifyChange(resourceType)
      return result
    },
    onError: (error) => {
      throw error
    }
  }
}

export function clearCacheAndRefresh(resourceType) {
  cacheManager.clearByResourceType(resourceType)
  cacheManager.notifyChange(resourceType)
}

export function clearAllCache() {
  defaultCache.clear()
}

export { cacheManager, LIST_TYPE_MAP, API_PATTERN_MAP }
