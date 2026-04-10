/**
 * 通用数据格式化工�? */

export const formatNumber = (num, decimals = 1) => {
  if (!num && num !== 0) return 0
  const factor = Math.pow(10, decimals)
  return Math.round(num * factor) / factor
}

export const formatDate = (date = new Date()) => {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleString('zh-CN')
}

export const formatDateISO = (date = new Date()) => {
  const d = typeof date === 'string' ? new Date(date) : date
  if (isNaN(d.getTime())) return ''
  return d.toISOString().slice(0, 10)
}

export const formatDateChinese = (date) => {
  if (!date) return ''
  const d = typeof date === 'string' ? new Date(date) : date
  if (isNaN(d.getTime())) return ''
  return `${d.getFullYear()}�?{String(d.getMonth() + 1).padStart(2, '0')}�?{String(d.getDate()).padStart(2, '0')}日`
}

export const formatPercentage = (value, total) => {
  if (!total) return '0%'
  return `${Math.round((value / total) * 100)}%`
}

export const getStatusType = (status) => {
  const map = {
    'NORMAL': 'success',
    'MAINTENANCE': 'warning',
    'DAMAGED': 'danger',
    'SCRAPPED': 'info'
  }
  return map[status] || 'info'
}

export const formatTimeSmart = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  const now = new Date()
  if (date.toDateString() === now.toDateString()) {
    return timeStr.split(' ')[1]?.substring(0, 5) || ''
  }
  return timeStr.split(' ')[0] || ''
}

export const formatRoleName = (role) => {
  const roleMap = {
    'superuser': '超级管理员',
    'systemadmin': '系统管理员',
    'departadmin': '分院管理员',
    'sxsadmin': '实训室管理员',
    'teacher': '教师',
    'student': '学生'
  }
  return roleMap[role] || role
}
