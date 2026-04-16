/**
 * 自动刷新列表组合函数
 */

import { watch, computed, onUnmounted, type ComputedRef, type WatchStopHandle } from 'vue'
import { useAppStore } from '../../store/app'

interface UseAutoRefreshReturn {
  refreshTrigger: ComputedRef<number>
  setupAutoRefresh: (callback: () => void, options?: { immediate?: boolean; deep?: boolean }) => WatchStopHandle
  triggerRefresh: () => void
}

export function useAutoRefresh(listType: string): UseAutoRefreshReturn {
  const appStore = useAppStore()

  const refreshTrigger = computed(() => {
    return appStore.getListRefreshTrigger(listType)
  })

  const setupAutoRefresh = (callback: () => void, options: { immediate?: boolean; deep?: boolean } = {}): WatchStopHandle => {
    const { immediate = false, deep = false } = options

    const stopWatch = watch(
      refreshTrigger,
      (newVal, oldVal) => {
        if (newVal !== oldVal && typeof callback === 'function') {
          callback()
        }
      },
      { immediate }
    )

    onUnmounted(() => {
      stopWatch()
    })

    return stopWatch
  }

  const triggerRefresh = (): void => {
    appStore.triggerListRefresh(listType)
  }

  return {
    refreshTrigger,
    setupAutoRefresh,
    triggerRefresh
  }
}

interface UseListAutoRefreshReturn {
  triggerRefresh: () => void
  stopAutoRefresh: WatchStopHandle
}

export function useListAutoRefresh(listType: string, loadData: () => void, options: { immediate?: boolean } = {}): UseListAutoRefreshReturn {
  const { immediate = false } = options
  const { setupAutoRefresh, triggerRefresh } = useAutoRefresh(listType)

  const stopAutoRefresh = setupAutoRefresh(loadData, { immediate })

  return {
    triggerRefresh,
    stopAutoRefresh
  }
}

interface UseMultiListAutoRefreshReturn {
  triggerRefresh: (listType: string) => void
  triggerAllRefresh: () => void
}

export function useMultiListAutoRefresh(listTypes: string[], loadDataMap: Record<string, () => void>, options: { immediate?: boolean } = {}): UseMultiListAutoRefreshReturn {
  const { immediate = false } = options
  const appStore = useAppStore()
  const stopWatches: WatchStopHandle[] = []

  listTypes.forEach(listType => {
    const trigger = computed(() => appStore.getListRefreshTrigger(listType))
    const callback = loadDataMap[listType]

    if (callback) {
      const stopWatch = watch(
        trigger,
        (newVal, oldVal) => {
          if (newVal !== oldVal && typeof callback === 'function') {
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

  const triggerRefresh = (listType: string): void => {
    appStore.triggerListRefresh(listType)
  }

  const triggerAllRefresh = (): void => {
    listTypes.forEach(listType => {
      appStore.triggerListRefresh(listType)
    })
  }

  return {
    triggerRefresh,
    triggerAllRefresh
  }
}

export default useAutoRefresh
