/**
 * 通用数据格式化工具
 */

export const formatNumber = (num: number | null | undefined, decimals: number = 1): number => {
  if (!num && num !== 0) return 0
  const factor = Math.pow(10, decimals)
  return Math.round(num * factor) / factor
}

export const formatDate = (date: Date | string = new Date()): string => {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleString('zh-CN')
}

export const formatDateISO = (date: Date | string = new Date()): string => {
  const d = typeof date === 'string' ? new Date(date) : date
  if (isNaN(d.getTime())) return ''
  return d.toISOString().slice(0, 10)
}

export const formatDateChinese = (date: Date | string | null | undefined): string => {
  if (!date) return ''
  const d = typeof date === 'string' ? new Date(date) : date
  if (isNaN(d.getTime())) return ''
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}年${month}月${day}日`
}

export const formatPercentage = (value: number, total: number): string => {
  if (!total) return '0%'
  return `${Math.round((value / total) * 100)}%`
}

type DeviceStatus = 'NORMAL' | 'MAINTENANCE' | 'DAMAGED' | 'SCRAPPED'

export const getStatusType = (status: DeviceStatus): 'success' | 'warning' | 'danger' | 'info' => {
  const map: Record<DeviceStatus, 'success' | 'warning' | 'danger' | 'info'> = {
    'NORMAL': 'success',
    'MAINTENANCE': 'warning',
    'DAMAGED': 'danger',
    'SCRAPPED': 'info'
  }
  return map[status] || 'info'
}

export const formatTimeSmart = (timeStr: string | null | undefined): string => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  const now = new Date()
  if (date.toDateString() === now.toDateString()) {
    return timeStr.split(' ')[1]?.substring(0, 5) || ''
  }
  return timeStr.split(' ')[0] || ''
}

type UserRole = 'superuser' | 'systemadmin' | 'departadmin' | 'sxsadmin' | 'teacher' | 'student'

export const formatRoleName = (role: UserRole | string): string => {
  const roleMap: Record<string, string> = {
    'superuser': '超级管理员',
    'systemadmin': '系统管理员',
    'departadmin': '分院管理员',
    'sxsadmin': '实训室管理员',
    'teacher': '教师',
    'student': '学生'
  }
  return roleMap[role] || role
}
