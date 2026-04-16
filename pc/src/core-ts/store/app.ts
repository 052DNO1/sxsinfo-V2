/**
 * 应用全局状态管理
 */

import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import { setAppStore } from '../services/cacheManager'

export const useAppStore = defineStore('app', () => {
  const refreshTermTrigger = ref(0)

  const triggerTermRefresh = (): void => {
    refreshTermTrigger.value++
  }

  const listRefreshTriggers = reactive<Record<string, number>>({})

  const triggerListRefresh = (listType: string): void => {
    if (!listRefreshTriggers[listType]) {
      listRefreshTriggers[listType] = 0
    }
    listRefreshTriggers[listType]++
  }

  const getListRefreshTrigger = (listType: string): number => {
    return listRefreshTriggers[listType] || 0
  }

  const store = {
    refreshTermTrigger,
    triggerTermRefresh,
    listRefreshTriggers,
    triggerListRefresh,
    getListRefreshTrigger
  }

  setAppStore(store)

  return store
})
