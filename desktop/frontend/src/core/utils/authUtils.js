/**
 * 认证相关工具函数
 * 处理登录错误消息映射等
 */

/**
 * 将后端或通用的错误消息转换为用户友好的中文提示
 * @param {string} msg - 原始错误消息
 * @returns {string} 转换后的中文消息
 */
export const translateErrorMessage = (msg) => {
  if (!msg) return msg
  const lowerMsg = String(msg).toLowerCase()
  
  if (lowerMsg.includes('user not found') || lowerMsg.includes('account not found') || 
      lowerMsg.includes('user does not exist') || lowerMsg.includes('account does not exist') ||
      lowerMsg.includes('user matching query does not exist') || lowerMsg.includes('doesn\'t exist') ||
      lowerMsg.includes('账户不存在') || lowerMsg.includes('用户不存在')) {
    return '账户不存在，请检查用户名'
  }
  
  if (lowerMsg.includes('account is disabled') || lowerMsg.includes('user is disabled') || 
      lowerMsg.includes('account is inactive') || lowerMsg.includes('user is inactive') ||
      lowerMsg.includes('banned') || lowerMsg.includes('账户被禁用') || 
      lowerMsg.includes('被禁用') || lowerMsg.includes('停用')) {
    return '该账户已被禁用，请联系管理员'
  }
  
  if (lowerMsg.includes('password') || lowerMsg.includes('密码错误') || lowerMsg.includes('密码不对') ||
      lowerMsg.includes('invalid password') || lowerMsg.includes('wrong password')) {
    return '密码错误，请重新输入'
  }
  
  if (lowerMsg.includes('invalid credentials') || lowerMsg.includes('credentials were not provided')) {
    return '用户名或密码错误'
  }
  
  return msg
}

/**
 * 从 API 错误对象中提取并转换错误消息
 * @param {Error} err - API 错误对象
 * @returns {string} 用户友好的错误消息
 */
export const getLoginErrorMessage = (err) => {
  if (err.response) {
    const status = err.response.status
    const data = err.response.data || {}
    let backendMsg = data.detail || data.message || data.msg || data.error
    
    if (!backendMsg && data.non_field_errors && Array.isArray(data.non_field_errors) && data.non_field_errors.length > 0) {
      backendMsg = data.non_field_errors[0]
    }
    
    if (backendMsg) {
      return translateErrorMessage(backendMsg)
    }
    
    const errorMap = {
      403: 'CSRF验证失败，请刷新页面重试',
      400: '请求参数错误',
      401: '用户名或密码错误',
      404: '请求的资源不存在',
      500: '服务器错误，请稍后重试'
    }
    return errorMap[status] || `登录失败 (${status})`
  }
  
  if (err.request) {
    return '无法连接到服务器，请检查后端服务是否运行'
  }
  
  const msg = err.message || '登录失败，请检查网络连接'
  return translateErrorMessage(msg)
}
