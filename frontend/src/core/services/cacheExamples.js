/**
 * 缓存清理使用示例
 * 
 * 本文件展示如何在项目中使用缓存清理机制
 */

// ==================== 示例1: 在API调用中使用 ====================

import { useApi } from '@/core/hooks'

// 方式1: 通过resourceType自动清理
const { post } = useApi('/api/schedules/', { 
  resourceType: 'schedules'  // 操作成功后自动清理课表相关缓存并刷新列表
})

const createSchedule = async (data) => {
  const result = await post(data)
  // 成功后自动清理缓存并触发刷新，无需手动操作
  return result
}

// 方式2: 临时指定资源类型
const { put } = useApi()
const updateSchedule = async (id, data) => {
  const result = await put(data, { 
    url: `/api/schedules/${id}/`,
    resourceType: 'schedules'  // 临时指定
  })
  return result
}

// 方式3: 禁用自动刷新
const { del } = useApi('/api/schedules/', { 
  resourceType: 'schedules',
  autoRefresh: false  // 只清理缓存，不触发刷新
})

// ==================== 示例2: 在列表组件中使用 ====================

import { useBaseCRUD, useAutoRefresh } from '@/core/hooks'

export function useScheduleList() {
  const { 
    tableData, 
    loading, 
    loadData,
    execDelete,
    execBatchDelete 
  } = useBaseCRUD({
    service: scheduleService,
    listType: 'schedules',  // 指定列表类型，删除操作会自动触发刷新
    immediate: true
  })

  // 监听其他组件触发的刷新（支持数据版本监听）
  const { setupAutoRefresh, dataVersion, isStale } = useAutoRefresh('schedules')
  setupAutoRefresh(loadData)

  // 可选：检查数据是否过期
  const refreshIfStale = () => {
    if (isStale(30000)) {  // 30秒没更新
      loadData()
    }
  }

  return {
    tableData,
    loading,
    loadData,
    execDelete,
    execBatchDelete,
    dataVersion,
    refreshIfStale
  }
}

// ==================== 示例3: 在表单组件中使用 ====================

import { useApi } from '@/core/hooks'
import { useRouter } from 'vue-router'

export function useScheduleForm() {
  const router = useRouter()
  const { post, put, loading } = useApi()

  const createSchedule = async (data) => {
    const result = await post(data, {
      url: '/api/schedules/',
      resourceType: 'schedules'  // 创建成功后自动刷新列表
    })
    
    if (result.success) {
      router.back()  // 返回列表页，列表会自动刷新
    }
    return result
  }

  const updateSchedule = async (id, data) => {
    const result = await put(data, {
      url: `/api/schedules/${id}/`,
      resourceType: 'schedules'  // 更新成功后自动刷新列表
    })
    
    if (result.success) {
      router.back()
    }
    return result
  }

  return {
    createSchedule,
    updateSchedule,
    loading
  }
}

// ==================== 示例4: 手动控制缓存清理 ====================

import { cacheManager, clearCacheAndRefresh } from '@/core/services/cacheManager'

// 手动清理指定资源的缓存
const handleBatchOperation = async () => {
  // 执行批量操作...
  const result = await batchUpdateSchedules()
  
  if (result.success) {
    // 手动清理缓存并刷新（会自动更新数据版本和时间戳）
    clearCacheAndRefresh('schedules')
  }
}

// 使用事务控制
const handleComplexOperation = async () => {
  cacheManager.enterTransaction()
  
  try {
    await operation1()
    cacheManager.clearByResourceType('schedules')
    
    await operation2()
    cacheManager.notifyChange('schedules')
    
    // 所有操作成功，提交事务
    cacheManager.commitTransaction()
  } catch (error) {
    // 操作失败，回滚事务（不清理缓存）
    cacheManager.rollbackTransaction()
    throw error
  }
}

// ==================== 示例5: 多资源操作 ====================

import { useApi } from '@/core/hooks'
import { useAppStore } from '@/core/store/app'

export function useArchiveOperation() {
  const { post } = useApi()
  const appStore = useAppStore()

  const archiveSemester = async (semesterId) => {
    const result = await post({}, {
      url: `/api/semesters/${semesterId}/archive/`,
      resourceType: 'semesters'  // 会清理学期、课表、统计等多个相关缓存
    })
    return result
  }

  // 手动通知多个资源变更
  const batchNotifyChanges = () => {
    appStore.notifyMultipleChanges(['schedules', 'laboratories', 'users'])
  }
}

// ==================== 示例6: 数据同步 ====================

import { useDataSync } from '@/core/hooks'

export function useRealtimeData() {
  const { dataVersion, startSync, stopSync, isStale } = useDataSync('schedules', {
    autoSync: false,
    syncInterval: 30000  // 30秒检查一次
  })

  const loadData = async () => {
    // 加载数据...
  }

  // 启动自动同步
  const enableAutoSync = () => {
    startSync(loadData)
  }

  // 停止自动同步
  const disableAutoSync = () => {
    stopSync()
  }

  return {
    dataVersion,
    enableAutoSync,
    disableAutoSync,
    isStale
  }
}

// ==================== 示例7: 监听数据版本变化 ====================

import { watch } from 'vue'
import { useAutoRefresh } from '@/core/hooks'

export function useVersionWatch() {
  const { dataVersion, lastUpdate } = useAutoRefresh('schedules')

  // 监听数据版本变化
  watch(dataVersion, (newVersion, oldVersion) => {
    console.log(`数据版本从 ${oldVersion} 更新到 ${newVersion}`)
    // 可以在这里执行额外的逻辑
  })

  // 监听最后更新时间
  watch(lastUpdate, (newTime) => {
    console.log('数据最后更新时间:', new Date(newTime).toLocaleString())
  })
}

// ==================== 资源类型映射 ====================

/**
 * 支持的资源类型:
 * 
 * - 'schedules'     -> 课表
 * - 'laboratories'  -> 实训室
 * - 'equipment'     -> 设备
 * - 'users'         -> 用户
 * - 'semesters'     -> 学期
 * - 'departments'   -> 部门
 * - 'records'       -> 使用记录
 * - 'maintenances'  -> 维护记录
 * 
 * 每种资源类型会自动清理相关的API缓存并触发对应的列表刷新
 * 
 * 资源依赖关系（自动级联更新）：
 * - schedules  -> statistics, dashboard
 * - laboratories -> statistics, dashboard
 * - equipment -> laboratories, statistics, dashboard
 * - users -> statistics, dashboard
 * - semesters -> schedules, statistics, dashboard
 * - departments -> users, statistics, dashboard
 * - records -> statistics, dashboard
 * - maintenances -> statistics, dashboard
 */

export default {
  useApi,
  useBaseCRUD,
  useAutoRefresh,
  useDataSync,
  cacheManager,
  clearCacheAndRefresh
}
