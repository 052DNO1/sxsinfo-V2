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
import { ref, reactive } from 'vue'

export const useAppStore = defineStore('app', () => {
  /**
   * 学期刷新触发器
   * 
   * 用于通知其他组件学期数据已更新，需要重新加载。
   * 当学期相关操作（如设为当前学期）完成后，会调用 triggerTermRefresh()
   * 其他组件可以 watch 这个值的变化来刷新数据。
   * 
   * 使用示例：
   * // 在组件中监听
   * watch(() => appStore.refreshTermTrigger, () => {
   *   // 重新加载学期数据
   *   loadTermList()
   * })
   */
  const refreshTermTrigger = ref(0)
  
  /**
   * 触发学期刷新
   * 
   * 调用此方法会让 refreshTermTrigger 的值 +1
   * 监听该值的组件会收到通知并刷新数据
   */
  const triggerTermRefresh = () => {
    refreshTermTrigger.value++
  }

  /**
   * 通用列表刷新触发器
   * 
   * 用于通知列表组件数据已更新，需要重新加载。
   * 使用 Map 存储不同类型列表的刷新计数器。
   * 
   * 列表类型映射：
   * - 'users': 用户列表
   * - 'semesters': 学期列表
   * - 'departments': 部门列表
   * - 'labs': 实训室列表
   * - 'devices': 设备列表
   * - 'records': 使用记录列表
   * - 'maintenances': 维护记录列表
   * - 'classes': 班级列表
   */
  const listRefreshTriggers = reactive({})

  /**
   * 触发指定类型列表的刷新
   * 
   * @param {string} listType - 列表类型（如 'users', 'semesters' 等）
   */
  const triggerListRefresh = (listType) => {
    if (!listRefreshTriggers[listType]) {
      listRefreshTriggers[listType] = 0
    }
    listRefreshTriggers[listType]++
  }

  /**
   * 获取指定类型列表的刷新计数器
   * 
   * @param {string} listType - 列表类型
   * @returns {number} 刷新计数器值
   */
  const getListRefreshTrigger = (listType) => {
    return listRefreshTriggers[listType] || 0
  }

  return {
    refreshTermTrigger,
    triggerTermRefresh,
    listRefreshTriggers,
    triggerListRefresh,
    getListRefreshTrigger
  }
})
