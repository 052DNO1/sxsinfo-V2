/**
 * 自动刷新列表组合函数
 * 
 * 提供列表数据的自动刷新能力，当其他组件修改数据后自动刷新列表
 * 
 * @module useAutoRefresh
 * @example
 * // 在列表组件中使用
 * const { refreshTrigger, setupAutoRefresh } = useAutoRefresh('schedules')
 * 
 * // 监听刷新触发器
 * watch(refreshTrigger, () => {
 *   loadData()
 * })
 * 
 * // 或者使用 setupAutoRefresh 自动设置监听
 * const { loadData } = useBaseList({ ... })
 * setupAutoRefresh(loadData)
 */

import { watch, computed, onUnmounted, onMounted } from 'vue'
import { useAppStore } from '@/core/store/app'

export function useAutoRefresh(listType) {
  const appStore = useAppStore()

  const refreshTrigger = computed(() => {
    return appStore.getListRefreshTrigger(listType)
  })

  const dataVersion = computed(() => {
    return appStore.getDataVersion(listType)
  })

  const lastUpdate = computed(() => {
    return appStore.getLastUpdateTime(listType)
  })

  const setupAutoRefresh = (callback, options = {}) => {
    const { immediate = false, deep = false, watchVersion = true } = options

    const stopWatchTrigger = watch(
      refreshTrigger,
      (newVal, oldVal) => {
        if (newVal !== oldVal && typeof callback === 'function') {
          callback()
        }
      },
      { immediate }
    )

    let stopWatchVersion = null
    if (watchVersion) {
      stopWatchVersion = watch(
        dataVersion,
        (newVal, oldVal) => {
          if (newVal !== oldVal && typeof callback === 'function') {
            callback()
          }
        }
      )
    }

    onUnmounted(() => {
      stopWatchTrigger()
      if (stopWatchVersion) {
        stopWatchVersion()
      }
    })

    return () => {
      stopWatchTrigger()
      if (stopWatchVersion) {
        stopWatchVersion()
      }
    }
  }

  const triggerRefresh = () => {
    appStore.triggerListRefresh(listType)
  }

  const isStale = (maxAge = 30000) => {
    return appStore.isDataStale(listType, maxAge)
  }

  return {
    refreshTrigger,
    dataVersion,
    lastUpdate,
    setupAutoRefresh,
    triggerRefresh,
    isStale
  }
}

export function useListAutoRefresh(listType, loadData, options = {}) {
  const { immediate = false, watchVersion = true } = options
  const { setupAutoRefresh, triggerRefresh, isStale, dataVersion } = useAutoRefresh(listType)

  const stopAutoRefresh = setupAutoRefresh(loadData, { immediate, watchVersion })

  const refreshIfStale = (maxAge = 30000) => {
    if (isStale(maxAge)) {
      loadData()
    }
  }

  return {
    triggerRefresh,
    stopAutoRefresh,
    isStale,
    dataVersion,
    refreshIfStale
  }
}

export function useMultiListAutoRefresh(listTypes, loadDataMap, options = {}) {
  const { immediate = false } = options
  const appStore = useAppStore()
  const stopWatches = []

  listTypes.forEach(listType => {
    const trigger = computed(() => appStore.getListRefreshTrigger(listType))
    const version = computed(() => appStore.getDataVersion(listType))
    const callback = loadDataMap[listType]

    if (callback) {
      const stopWatch = watch(
        [trigger, version],
        ([newTrigger, newVersion], [oldTrigger, oldVersion]) => {
          if ((newTrigger !== oldTrigger || newVersion !== oldVersion) && typeof callback === 'function') {
            callback()
          }
        },
        { immediate }
      )
      stopWatches.push(stopWatch)
    }
  })

  onUnmounted(() => {
    stopWatches.forEach(stop => stop())
  })

  const triggerRefresh = (listType) => {
    appStore.triggerListRefresh(listType)
  }

  const triggerAllRefresh = () => {
    listTypes.forEach(listType => {
      appStore.triggerListRefresh(listType)
    })
  }

  const notifyChange = (resourceType) => {
    appStore.notifyDataChange(resourceType)
  }

  return {
    triggerRefresh,
    triggerAllRefresh,
    notifyChange
  }
}

export function useDataSync(resourceType, options = {}) {
  const { autoSync = true, syncInterval = 60000 } = options
  const appStore = useAppStore()
  
  const dataVersion = computed(() => appStore.getDataVersion(resourceType))
  const lastUpdate = computed(() => appStore.getLastUpdateTime(resourceType))
  
  let syncTimer = null
  
  const startSync = (callback) => {
    if (syncTimer) return
    
    syncTimer = setInterval(() => {
      if (appStore.isDataStale(resourceType, syncInterval)) {
        if (typeof callback === 'function') {
          callback()
        }
      }
    }, syncInterval)
  }
  
  const stopSync = () => {
    if (syncTimer) {
      clearInterval(syncTimer)
      syncTimer = null
    }
  }
  
  const markUpdated = () => {
    appStore.recordUpdateTime(resourceType)
  }
  
  onUnmounted(() => {
    stopSync()
  })
  
  return {
    dataVersion,
    lastUpdate,
    startSync,
    stopSync,
    markUpdated,
    isStale: (maxAge) => appStore.isDataStale(resourceType, maxAge)
  }
}
