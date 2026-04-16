/**
 * 应用全局状态管理
 * 
 * 这个 Store 用于管理应用级别的全局状态，与用户无关的状态。
 * 
 * 对于新手：
 * - Pinia 是 Vue 3 推荐的状态管理库
 * - defineStore 定义一个状态存储，第一个参数是 store 的唯一 id
 * - ref() 定义的变量是响应式的（状态）
 * - function 是 actions（修改状态的方法）
 * - 最后 return 出去的内容就是外部可以访问的
 */

import { defineStore } from 'pinia'
import { ref, reactive, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  const refreshTermTrigger = ref(0)
  
  const triggerTermRefresh = () => {
    refreshTermTrigger.value++
  }

  const listRefreshTriggers = reactive({})

  const triggerListRefresh = (listType) => {
    if (!listRefreshTriggers[listType]) {
      listRefreshTriggers[listType] = 0
    }
    listRefreshTriggers[listType]++
  }

  const getListRefreshTrigger = (listType) => {
    return listRefreshTriggers[listType] || 0
  }

  const dataVersions = reactive({
    schedules: 0,
    laboratories: 0,
    labs: 0,
    equipment: 0,
    devices: 0,
    users: 0,
    semesters: 0,
    departments: 0,
    records: 0,
    maintenances: 0,
    statistics: 0,
    dashboard: 0
  })

  const resourceDependencies = {
    schedules: ['laboratories', 'statistics', 'dashboard'],
    laboratories: ['statistics', 'dashboard'],
    equipment: ['laboratories', 'statistics', 'dashboard'],
    users: ['statistics', 'dashboard'],
    semesters: ['schedules', 'statistics', 'dashboard'],
    departments: ['users', 'statistics', 'dashboard'],
    records: ['statistics', 'dashboard'],
    maintenances: ['statistics', 'dashboard']
  }

  const listTypeMapping = {
    schedules: 'schedules',
    laboratories: 'labs',
    labs: 'labs',
    equipment: 'devices',
    devices: 'devices',
    users: 'users',
    semesters: 'semesters',
    departments: 'departments',
    records: 'records',
    maintenances: 'maintenances',
    statistics: 'statistics',
    dashboard: 'dashboard'
  }

  const resourceAliases = {
    laboratories: ['labs'],
    labs: ['laboratories'],
    equipment: ['devices'],
    devices: ['equipment']
  }

  const incrementDataVersion = (resourceType) => {
    if (dataVersions[resourceType] !== undefined) {
      dataVersions[resourceType]++
    }

    const aliases = resourceAliases[resourceType] || []
    aliases.forEach(alias => {
      if (dataVersions[alias] !== undefined) {
        dataVersions[alias]++
      }
    })

    const dependencies = resourceDependencies[resourceType] || []
    dependencies.forEach(dep => {
      if (dataVersions[dep] !== undefined) {
        dataVersions[dep]++
      }
    })
  }

  const getDataVersion = (resourceType) => {
    return dataVersions[resourceType] || 0
  }

  const notifyDataChange = (resourceType) => {
    incrementDataVersion(resourceType)

    const listType = listTypeMapping[resourceType]
    if (listType) {
      triggerListRefresh(listType)
    }

    const dependencies = resourceDependencies[resourceType] || []
    dependencies.forEach(dep => {
      const depListType = listTypeMapping[dep]
      if (depListType && depListType !== listType) {
        triggerListRefresh(depListType)
      }
    })
  }

  const notifyMultipleChanges = (resourceTypes) => {
    const processedTypes = new Set()
    
    resourceTypes.forEach(type => {
      if (!processedTypes.has(type)) {
        processedTypes.add(type)
        incrementDataVersion(type)
      }
    })

    resourceTypes.forEach(type => {
      const listType = listTypeMapping[type]
      if (listType) {
        triggerListRefresh(listType)
      }
    })
  }

  const lastUpdateTime = reactive({})

  const recordUpdateTime = (resourceType) => {
    lastUpdateTime[resourceType] = Date.now()
  }

  const getLastUpdateTime = (resourceType) => {
    return lastUpdateTime[resourceType] || 0
  }

  const isDataStale = (resourceType, maxAge = 30000) => {
    const lastUpdate = getLastUpdateTime(resourceType)
    if (!lastUpdate) return true
    return Date.now() - lastUpdate > maxAge
  }

  const globalLoading = ref(false)
  const globalError = ref(null)

  const setGlobalLoading = (loading) => {
    globalLoading.value = loading
  }

  const setGlobalError = (error) => {
    globalError.value = error
  }

  const clearGlobalError = () => {
    globalError.value = null
  }

  return {
    refreshTermTrigger,
    triggerTermRefresh,
    listRefreshTriggers,
    triggerListRefresh,
    getListRefreshTrigger,
    
    dataVersions,
    getDataVersion,
    incrementDataVersion,
    
    notifyDataChange,
    notifyMultipleChanges,
    
    lastUpdateTime,
    recordUpdateTime,
    getLastUpdateTime,
    isDataStale,
    
    globalLoading,
    globalError,
    setGlobalLoading,
    setGlobalError,
    clearGlobalError
  }
})
