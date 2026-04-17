export function isErrorType(error, type) {
  if (!error) return false
  if (error.type === type) return true
  if (error.name && error.name.toLowerCase().includes(type.toLowerCase())) return true
  if (error.code && error.code.toLowerCase().includes(type.toLowerCase())) return true
  return false
}

export function normalizeError(error) {
  if (!error) return { message: '未知错误', code: 'UNKNOWN_ERROR' }
  
  if (error.code === 'ECONNABORTED' || error?.message?.includes('timeout')) {
    return { message: error.message || '请求超时', code: 'TIMEOUT_ERROR', type: 'timeout' }
  }
  
  if (error.code === 'ERR_NETWORK' || error?.message === 'Network Error') {
    return { message: '网络连接失败', code: 'NETWORK_ERROR', type: 'network' }
  }
  
  if (error?.response) {
    const status = error.response.status
    const data = error.response.data || {}
    
    const typeMap = {
      401: { type: 'authentication', code: 'AUTH_ERROR' },
      403: { type: 'permission', code: 'PERMISSION_ERROR' },
      404: { type: 'not_found', code: 'NOT_FOUND_ERROR' }
    }
    
    if (typeMap[status]) {
      return { message: data.message || '请求失败', ...typeMap[status], status }
    }
    
    if (status === 400 && data.errors) {
      return { message: data.message || '数据验证失败', code: 'VALIDATION_ERROR', type: 'validation', errors: data.errors }
    }
    
    return { message: data.message || `请求失败 (${status})`, code: `API_ERROR_${status}`, type: 'api', status, response: data }
  }
  
  if (error?.success === false) {
    return { message: error.message || '操作失败', code: error.code || 'BUSINESS_ERROR', type: 'business', errors: error.errors }
  }
  
  if (error instanceof Error) {
    return { message: error.message, code: 'ERROR', type: 'error' }
  }
  
  if (typeof error === 'string') {
    return { message: error, code: 'STRING_ERROR', type: 'string' }
  }
  
  return { message: '未知错误', code: 'UNKNOWN_ERROR', type: 'unknown' }
}
