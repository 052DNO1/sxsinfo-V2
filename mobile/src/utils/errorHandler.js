import { normalizeError, isErrorType } from './errors'
import { showDialog, showConfirmDialog as vantConfirmDialog, showToast } from 'vant'

export const showMessage = async (message, type = 'info', title = null) => {
  const titleMap = {
    'success': '成功',
    'error': '错误',
    'warning': '警告',
    'info': '提示'
  }
  const finalTitle = title || titleMap[type] || '提示'
  
  try {
    await showDialog({
      title: finalTitle,
      message: message,
      confirmButtonText: '确定',
      theme: type === 'error' ? 'danger' : 'default'
    })
  } catch (err) {
    if (err === 'cancel' || err === 'close' || String(err).toLowerCase().includes('close')) {
      return
    }
    throw err
  }
}

export const showSuccess = async (message, title = '成功') => {
  showToast({
    type: 'success',
    message: message
  })
}

export const showError = async (error, title = '错误') => {
  let message = '操作失败'

  if (typeof error === 'string') {
    message = error
  }
  else if (error?.message && error?.type) {
    message = error.message
  }
  else if (error?.response?.data?.message) {
    message = error.response.data.message
  } else if (error?.message) {
    message = error.message
  }
  else {
    try {
      const normalizedError = normalizeError(error)
      message = normalizedError.message
    } catch (e) {
      console.warn('Error normalization failed:', e)
    }
  }

  showToast({
    type: 'fail',
    message: message
  })
}

export const showWarning = async (message, title = '提示') => {
  showToast({
    message: message
  })
}

export const showInfo = async (message, title = '提示') => {
  showToast({
    message: message
  })
}

export const showConfirm = async (message, title = '确认操作', options = {}) => {
  try {
    await vantConfirmDialog({
      title: title,
      message: message,
      confirmButtonText: options.confirmButtonText || '确定',
      cancelButtonText: options.cancelButtonText || '取消',
    })
    return true
  } catch (error) {
    return false
  }
}

export const safeAlert = async (message) => {
  return showInfo(message, '提示')
}

export const showConfirmDialogWrapper = async (options) => {
  const message = typeof options === 'string' ? options : (options?.message || options?.title || '确定要执行此操作吗？')
  
  try {
    await vantConfirmDialog({
      title: options?.title || '确认操作',
      message: message,
      confirmButtonText: options?.confirmButtonText || '确定',
      cancelButtonText: options?.cancelButtonText || '取消',
    })
    return Promise.resolve()
  } catch (error) {
    return Promise.reject('cancel')
  }
}

export const safeConfirm = async (message) => {
  return showConfirm(message)
}

export const handleError = async (error, options = {}) => {
  const {
    showError: shouldShow = true,
    customMessage,
    onError
  } = options

  const normalizedError = normalizeError(error)

  const errorInfo = {
    message: customMessage || normalizedError.message,
    code: normalizedError.code,
    details: normalizedError.details,
    type: normalizedError.type,
    status: normalizedError.status,
    originalError: error
  }

  if (shouldShow) {
    await showError(errorInfo.message)
  }

  if (onError) {
    onError(errorInfo, error)
  }

  if (process.env.NODE_ENV === 'development') {
    console.error('错误处理:', errorInfo, error)
  }

  return errorInfo
}

export const handleApiError = async (error, options = {}) => {
  return handleError(error, {
    ...options,
    type: 'api'
  })
}

export const handleApiCall = async (apiCall, options = {}) => {
  const {
    successMessage,
    errorMessage,
    showSuccess: shouldShowSuccess = true,
    showError: shouldShowError = true,
    onSuccess,
    onError
  } = options

  try {
    const response = await apiCall

    if (response && response.success) {
      const message = successMessage || response.message || '操作成功'
      if (shouldShowSuccess) {
        await showSuccess(message)
      }
      if (onSuccess) {
        await onSuccess(response)
      }
      return { success: true, data: response }
    } else {
      const message = errorMessage || response?.message || '操作失败'
      if (shouldShowError) {
        await showError(message)
      }
      if (onError) {
        await onError(response)
      }
      return { success: false, data: response }
    }
  } catch (err) {
    console.error('API调用失败:', err)
    if (shouldShowError) {
      await handleApiError(err, { showError: true, onError })
    }
    if (onError) {
      await onError(err)
    }
    return { success: false, error: err }
  }
}

export const formatBatchResult = ({ successItems = [], failedItems = [], successLabel = '项', failedLabel = '项' }) => {
  let message = ''

  if (successItems.length > 0) {
    message = `成功 ${successLabel} ${successItems.length} 个`
    if (successItems.length <= 5) {
      message += '：\n' + successItems.join('\n')
    } else {
      message += '：\n' + successItems.slice(0, 5).join('\n')
      message += `\n...还有 ${successItems.length - 5} 个`
    }
  }

  if (failedItems.length > 0) {
    if (message) message += '\n\n'
    message += `失败 ${failedLabel} ${failedItems.length} 个`
    if (failedItems.length <= 5) {
      const failedMessages = failedItems.map(item => {
        if (typeof item === 'string') return item
        if (item.username && item.reason) return `${item.username}: ${item.reason}`
        if (item.id && item.reason) return `ID ${item.id}: ${item.reason}`
        return String(item)
      })
      message += '：\n' + failedMessages.join('\n')
    } else {
      const failedMessages = failedItems.slice(0, 5).map(item => {
        if (typeof item === 'string') return item
        if (item.username && item.reason) return `${item.username}: ${item.reason}`
        if (item.id && item.reason) return `ID ${item.id}: ${item.reason}`
        return String(item)
      })
      message += '：\n' + failedMessages.join('\n')
      message += `\n...还有 ${failedItems.length - 5} 个失败`
    }
  }

  return message
}

export const extractFailedItems = (response) => {
  return response?.failed_users ||
    response?.failed_records ||
    response?.failed_depts ||
    response?.failed_terms ||
    []
}

export { normalizeError, isErrorType } from './errors'
export { showConfirmDialogWrapper as showConfirmDialog }

export default {
  showMessage,
  showSuccess,
  showError,
  showWarning,
  showInfo,
  showConfirm,
  showConfirmDialog: showConfirmDialogWrapper,
  safeAlert,
  safeConfirm,
  handleError,
  handleApiError,
  handleApiCall,
  formatBatchResult,
  extractFailedItems,
  normalizeError,
  isErrorType
}
