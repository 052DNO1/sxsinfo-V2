/**
 * 通用数据格式化工具函数
 */

/**
 * 格式化数字（保留一位小数）
 * @param {number} num - 要格式化的数字
 * @returns {number} 格式化后的数字
 */
export const formatNumber = (num) => {
  if (!num && num !== 0) return 0
  return Math.round(num * 10) / 10
}

/**
 * 格式化日期为本地字符串
 * @param {Date|string} date - 日期对象或日期字符串，默认为当前时间
 * @returns {string} 格式化后的日期字符串
 */
export const formatDate = (date = new Date()) => {
  const dateObj = typeof date === 'string' ? new Date(date) : date
  return dateObj.toLocaleString('zh-CN')
}

/**
 * 格式化日期为中文格式（YYYY年MM月DD日）
 * @param {Date|string} date - 日期对象或日期字符串
 * @returns {string} 格式化后的日期字符串，如：2024年12月25日
 */
export const formatDateChinese = (date) => {
  if (!date) return ''
  const dateObj = typeof date === 'string' ? new Date(date) : date
  if (isNaN(dateObj.getTime())) return ''
  const year = dateObj.getFullYear()
  const month = String(dateObj.getMonth() + 1).padStart(2, '0')
  const day = String(dateObj.getDate()).padStart(2, '0')
  return `${year}年${month}月${day}日`
}

/**
 * 格式化日期时间为中文格式（YYYY年MM月DD日 HH:mm）
 * @param {Date|string} date - 日期对象或日期字符串
 * @returns {string} 格式化后的日期时间字符串
 */
export const formatDateTimeChinese = (date) => {
  if (!date) return ''
  const dateObj = typeof date === 'string' ? new Date(date) : date
  if (isNaN(dateObj.getTime())) return ''
  const year = dateObj.getFullYear()
  const month = String(dateObj.getMonth() + 1).padStart(2, '0')
  const day = String(dateObj.getDate()).padStart(2, '0')
  const hours = String(dateObj.getHours()).padStart(2, '0')
  const minutes = String(dateObj.getMinutes()).padStart(2, '0')
  return `${year}年${month}月${day}日 ${hours}:${minutes}`
}

/**
 * 格式化日期为 YYYY-MM-DD 格式
 * @param {Date|string} date - 日期对象或日期字符串
 * @returns {string} 格式化后的日期字符串，如：2024-12-25
 */
export const formatDateISO = (date = new Date()) => {
  const dateObj = typeof date === 'string' ? new Date(date) : date
  return dateObj.toISOString().slice(0, 10)
}

/**
 * 格式化日期为 YYYYMMDD 格式（用于文件名）
 * @param {Date|string} date - 日期对象或日期字符串，默认为当前时间
 * @returns {string} 格式化后的日期字符串，如：20241225
 */
export const formatDateCompact = (date = new Date()) => {
  const dateObj = typeof date === 'string' ? new Date(date) : date
  return dateObj.toISOString().slice(0, 10).replace(/-/g, '')
}

/**
 * 格式化百分比
 * @param {number} value - 当前值
 * @param {number} total - 总值
 * @returns {string} 格式化后的百分比字符串
 */
export const formatPercentage = (value, total) => {
  if (!total || total === 0) return '0%'
  return `${Math.round((value / total) * 100)}%`
}

/**
 * 格式化角色名称
 * @param {string} role - 角色代码
 * @returns {string} 角色名称
 */
export const formatRoleName = (role) => {
  const roleMap = {
    'superuser': '超级管理员',
    'departadmin': '分院管理员',
    'sxsadmin': '实训室管理员',
    'teacher': '教师'
  }
  return roleMap[role] || role
}

/**
 * 获取状态对应的标签类型
 * @param {string} status - 状态代码
 * @returns {string} Element Plus 标签类型
 */
export const getStatusType = (status) => {
  const map = {
    'NORMAL': 'success',
    'MAINTENANCE': 'warning',
    'DAMAGED': 'danger',
    'SCRAPPED': 'info',
    'BORROWED': ''
  }
  return map[status] || 'info'
}

/**
 * 格式化消息时间（智能显示）
 * - 24小时内且同一天：只显示时间 HH:mm
 * - 其他情况：显示日期 YYYY-MM-DD
 * @param {string} timeStr - 时间字符串，格式为 'YYYY-MM-DD HH:mm:ss'
 * @returns {string} 格式化后的时间字符串
 */
export const formatTimeForMessage = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now - date
  
  // 如果小于24小时且是同一天
  if (diff < 24 * 60 * 60 * 1000 && date.getDate() === now.getDate()) {
    return timeStr.split(' ')[1]?.substring(0, 5) || '' // HH:mm
  }
  return timeStr.split(' ')[0] || '' // YYYY-MM-DD
}

