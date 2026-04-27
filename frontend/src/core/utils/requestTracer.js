/**
 * API 请求追踪器 - 用于诊断缓存问题
 * 
 * 使用方法：
 * 在浏览器控制台执行：enableRequestTracing()
 * 然后访问页面，查看所有API请求的详细信息
 */

let _tracingEnabled = false

export function enableRequestTracing() {
  _tracingEnabled = true
  console.log('%c🔍 [请求追踪] 已启用', 'background: #9C27B0; color: white; padding: 4px 8px; border-radius: 4px;')
  console.log('%c提示: 访问页面后，查看控制台中的详细请求日志', 'color: #666;')
}

export function disableRequestTracing() {
  _tracingEnabled = false
  console.log('%c[请求追踪] 已禁用', 'color: #666;')
}

export function isTracingEnabled() {
  return _tracingEnabled
}

/**
 * 记录请求详情（在拦截器中调用）
 */
export function logRequestDetails(phase, config, data = null) {
  if (!_tracingEnabled) return
  
  const timestamp = new Date().toLocaleTimeString()
  const userId = window.__tabUserContext?.userId || 'unknown'
  
  console.group(`%c[${timestamp}] ${phase}`, 'font-weight: bold; color: #2196F3;')
  
  console.log('URL:', config?.url)
  console.log('Method:', config?.method || 'GET')
  console.log('用户ID:', userId)
  console.log('Token指纹:', window.__tabUserContext?.tokenFingerprint?.substring(0, 12))
  
  if (config?._forceNoCache) {
    console.warn('⚠️ 强制不缓存模式')
    console.warn('Cache-Control头:', config.headers?.['Cache-Control'])
  }
  
  if (config?._fromCache) {
    console.info('✅ 命中缓存')
  }
  
  if (data !== null) {
    console.log('响应数据:', data)
    
    // 检查是否是列表数据
    if (Array.isArray(data)) {
      console.log(`📊 数据条数: ${data.length}`)
      if (data.length > 0 && data[0]?.admin) {
        console.log('👤 数据管理员:', data.map(item => item.admin?.name || item.admin?.username).join(', '))
      }
    } else if (data?.results) {
      console.log(`📊 分页数据: 共 ${data.count} 条`)
    }
  }
  
  console.groupEnd()
}

// 自动挂载到window
if (typeof window !== 'undefined') {
  window.enableRequestTracing = enableRequestTracing
  window.disableRequestTracing = disableRequestTracing
}
