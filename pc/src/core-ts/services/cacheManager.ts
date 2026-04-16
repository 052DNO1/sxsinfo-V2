/**
 * 缓存管理服务
 * 提供统一的缓存清理和列表刷新机制
 */

import { defaultCache } from '../api/cache'

const LIST_TYPE_MAP: Record<string, string> = {
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

const API_PATTERN_MAP: Record<string, string[]> = {
  schedules: ['/api/schedules/', '/api/statistics/'],
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

interface AppStore {
  triggerListRefresh: (listType: string) => void
}

let appStoreInstance: AppStore | null = null

export function setAppStore(store: AppStore): void {
  appStoreInstance = store
}

class CacheManager {
  private _pendingClears: Set<RegExp | string>
  private _pendingRefreshes: Set<string>
  private _inTransaction: boolean

  constructor() {
    this._pendingClears = new Set()
    this._pendingRefreshes = new Set()
    this._inTransaction = false
  }

  clearCache(pattern: RegExp | string): void {
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

  clearByApiPath(apiPath: string): void {
    const pattern = `GET:${apiPath}`
    this.clearCache(pattern)
  }

  clearByResourceType(resourceType: string): void {
    const patterns = API_PATTERN_MAP[resourceType] || []
    patterns.forEach(pattern => {
      this.clearCache(`GET:${pattern}`)
    })
  }

  triggerRefresh(listType: string): void {
    if (this._inTransaction) {
      this._pendingRefreshes.add(listType)
    } else {
      try {
        if (appStoreInstance) {
          appStoreInstance.triggerListRefresh(listType)
        }
      } catch (e) {
        console.warn('Failed to trigger refresh:', e)
      }
    }
  }

  triggerRefreshByResource(resourceType: string): void {
    const listType = LIST_TYPE_MAP[resourceType]
    if (listType) {
      this.triggerRefresh(listType)
    }
  }

  enterTransaction(): void {
    this._inTransaction = true
    this._pendingClears.clear()
    this._pendingRefreshes.clear()
  }

  commitTransaction(): void {
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

    this._pendingRefreshes.forEach(listType => {
      try {
        if (appStoreInstance) {
          appStoreInstance.triggerListRefresh(listType)
        }
      } catch (e) {
        console.warn('Failed to trigger refresh:', e)
      }
    })

    this._inTransaction = false
    this._pendingClears.clear()
    this._pendingRefreshes.clear()
  }

  rollbackTransaction(): void {
    this._inTransaction = false
    this._pendingClears.clear()
    this._pendingRefreshes.clear()
  }

  clearAll(): void {
    defaultCache.clear()
    if (appStoreInstance) {
      Object.keys(LIST_TYPE_MAP).forEach(key => {
        const listType = LIST_TYPE_MAP[key]
        if (listType) {
          appStoreInstance.triggerListRefresh(listType)
        }
      })
    }
  }
}

const cacheManager = new CacheManager()

export function useCacheManager(): CacheManager {
  return cacheManager
}

interface WithCacheClearOptions {
  clearCache?: boolean
  triggerRefresh?: boolean
  onSuccess?: (result: any, args: any[]) => void
  onError?: (error: any, args: any[]) => void
}

export function withCacheClear(resourceType: string, options: WithCacheClearOptions = {}) {
  const {
    clearCache = true,
    triggerRefresh = true,
    onSuccess,
    onError
  } = options

  return function(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value

    descriptor.value = async function(...args: any[]) {
      try {
        const result = await originalMethod.apply(this, args)

        if (clearCache) {
          cacheManager.clearByResourceType(resourceType)
        }

        if (triggerRefresh) {
          cacheManager.triggerRefreshByResource(resourceType)
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

export function createCachedOperation(resourceType: string) {
  return {
    onSuccess: (result: any) => {
      cacheManager.clearByResourceType(resourceType)
      cacheManager.triggerRefreshByResource(resourceType)
      return result
    },
    onError: (error: any) => {
      throw error
    }
  }
}

export function clearCacheAndRefresh(resourceType: string): void {
  cacheManager.clearByResourceType(resourceType)
  cacheManager.triggerRefreshByResource(resourceType)
}

export function clearAllCache(): void {
  defaultCache.clear()
}

export { cacheManager, LIST_TYPE_MAP, API_PATTERN_MAP }
