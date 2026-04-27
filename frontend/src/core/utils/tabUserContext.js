/**
 * 标签页级用户上下文管理器 - 【多标签页独立登录版本】
 * 
 * 核心原则：每个标签页独立登录状态
 * 
 * 实现方式：
 * - Token 存储在 sessionStorage，每个标签页独立
 * - 不同标签页可以登录不同账号，互不干扰
 * - 直接解析 JWT Token 的 payload 获取 user_id
 */

class TabUserContext {
  constructor() {
    // ✨ 纯内存变量（不依赖任何共享存储）
    this.userId = null
    this.username = null
    this.loginTimestamp = null
    
    // ✨ Token指纹（从JWT payload提取，唯一且稳定）
    this.tokenFingerprint = null
    
    // 版本控制
    this.contextVersion = 0
    
    // 防抖控制
    this._lastRefreshTime = 0
    this._refreshCooldown = 300  // 300ms冷却
    
    // 初始化（只读token，不读sessionStorage）
    this.init()
  }

  init() {
    console.log('[TabContext] 🚀 初始化标签页级用户上下文')
    
    // 从token初始化（这是唯一可靠的数据源）
    const result = this.refreshFromToken()
    
    if (result) {
      console.log(`[TabContext] ✅ 初始化完成: userId=${this.userId}, fingerprint=${this.tokenFingerprint?.substring(0, 8)}...`)
    } else {
      console.log('[TabContext] ⚠️ 未检测到有效token，使用匿名模式')
    }

    // 监听storage事件（仅用于版本号同步，不用于读取用户数据）
    window.addEventListener('storage', (event) => {
      if (event.key === 'v2_user_context_version') {
        const newVersion = parseInt(event.newValue) || 0
        if (newVersion > this.contextVersion) {
          console.log(`[TabContext] 🔄 检测到上下文版本变更 (${this.contextVersion} → ${newVersion})`)
          this.contextVersion = newVersion
          // 重新验证token（不读sessionStorage！）
          this.refreshFromToken()
        }
      }
    })
  }

  /**
   * ✨✨✨ 核心方法：从JWT Token解析用户身份
   * 完全不依赖 sessionStorage！
   */
  refreshFromToken() {
    // 防抖：避免频繁刷新
    const now = Date.now()
    if (now - this._lastRefreshTime < this._refreshCooldown) {
      return null
    }
    this._lastRefreshTime = now

    try {
      const token = sessionStorage.getItem('access_token')
      
      if (!token) {
        console.log('[TabContext] 未找到access_token，清空上下文')
        this.clear()
        return null
      }

      // ✨ 关键：生成token指纹（基于JWT payload的唯一标识）
      const newFingerprint = this.generateTokenFingerprint(token)
      
      // 检查指纹是否变化（用于检测用户切换）
      if (this.tokenFingerprint && this.tokenFingerprint !== newFingerprint) {
        console.log(`[TabContext] 👤 检测到用户切换！`)
        console.log(`   旧指纹: ${this.tokenFingerprint?.substring(0, 12)}`)
        console.log(`   新指纹: ${newFingerprint.substring(0, 12)}`)
        
        this.contextVersion++
        this.loginTimestamp = now
        
        // 广播版本变更（让其他标签页知道）
        try {
          localStorage.setItem('v2_user_context_version', this.contextVersion.toString())
        } catch (e) {
          // 忽略
        }
      }
      
      this.tokenFingerprint = newFingerprint
      
      // ✨ 尝试从JWT payload中解析user_id
      const decodedPayload = this.decodeJWTPayload(token)
      
      if (decodedPayload && decodedPayload.user_id) {
        // 成功从token中提取到用户ID
        const newUserId = decodedPayload.user_id
        
        if (this.userId && this.userId !== newUserId) {
          console.log(`[TabContext] 👤 用户ID变更: ${this.userId} → ${newUserId}`)
        }
        
        this.userId = newUserId
        this.username = decodedPayload.username || decodedPayload.email || `user_${newUserId}`
        
        return {
          id: newUserId,
          username: this.username,
          source: 'jwt_payload',
          fingerprint: newFingerprint
        }
      }
      
      // 如果无法从payload解析，使用token指纹作为匿名标识
      if (!this.userId) {
        this.userId = `anon_${newFingerprint.substring(0, 8)}`
        console.log(`[TabContext] 使用匿名模式: ${this.userId}`)
        
        return {
          id: this.userId,
          isAnonymous: true,
          source: 'token_fingerprint',
          fingerprint: newFingerprint
        }
      }
      
      return {
        id: this.userId,
        username: this.username,
        fingerprint: newFingerprint
      }
      
    } catch (e) {
      console.error('[TabContext] ❌ refreshFromToken 失败:', e)
      this.clear()
      return null
    }
  }

  /**
   * 解析JWT Token的payload部分
   * JWT格式: header.payload.signature
   * payload是base64url编码的JSON
   */
  decodeJWTPayload(token) {
    try {
      const parts = token.split('.')
      if (parts.length !== 3) {
        console.warn('[TabContext] 无效的JWT格式')
        return null
      }

      const payload = parts[1]
      
      // Base64URL解码
      const base64 = payload.replace(/-/g, '+').replace(/_/g, '/')
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      )

      const decoded = JSON.parse(jsonPayload)
      
      console.log(`[TabContext] 📋 JWT Payload 解析成功:`, {
        user_id: decoded.user_id,
        exp: decoded.exp,
        iat: decoded.iat
      })
      
      return decoded
      
    } catch (e) {
      console.error('[TabContext] ❌ JWT解析失败:', e)
      return null
    }
  }

  /**
   * 生成token的唯一指纹
   */
  generateTokenFingerprint(token) {
    if (!token) return 'no_token'
    
    try {
      // JWT格式: header.payload.signature
      const parts = token.split('.')
      if (parts.length >= 2) {
        // 使用完整的payload部分作为指纹（包含user_id等信息）
        // 不同用户的JWT有不同的payload
        return parts[1]  // 返回完整payload（已编码）
      }
      // 降级方案：取前20个字符
      return token.substring(0, 20)
    } catch (e) {
      return token.substring(0, 12)
    }
  }

  /**
   * 手动设置用户信息（仅在login()时调用）
   * 用于补充JWT中没有的信息（如username等）
   */
  setUserInfo(userInfo) {
    if (!userInfo) return
    
    const oldUserId = this.userId
    const newUserId = userInfo.id || userInfo.user_id
    
    if (oldUserId && newUserId && oldUserId !== newUserId) {
      console.log(`[TabContext] 👤 setUserInfo: 用户切换 ${oldUserId} → ${newUserId}`)
      this.contextVersion++
      this.loginTimestamp = Date.now()
      
      // 广播版本变更
      try {
        localStorage.setItem('v2_user_context_version', this.contextVersion.toString())
      } catch (e) {}
    } else if (!oldUserId && newUserId) {
      this.contextVersion++
      this.loginTimestamp = Date.now()
    }

    this.userId = newUserId
    this.username = userInfo.username || userInfo.nickname || userInfo.email || this.username
    
    console.log(`[TabContext] ✅ 用户信息已更新: id=${this.userId}, name=${this.username}`)
  }

  clear() {
    this.userId = null
    this.username = null
    this.loginTimestamp = null
    this.tokenFingerprint = null
  }

  /**
   * 获取当前标签页的唯一用户标识
   */
  getUniqueUserId() {
    if (this.userId && !this.userId.toString().startsWith('anon_')) {
      return this.userId.toString()
    }
    
    if (this.tokenFingerprint) {
      return `fp_${this.tokenFingerprint.substring(0, 12)}`
    }
    
    return `ts_${Date.now()}`
  }

  /**
   * 获取缓存用的完整前缀
   * 格式: uid_{userId}_fp_{token指纹}
   */
  getCachePrefix() {
    const userId = this.getUniqueUserId()
    const fingerprint = this.tokenFingerprint ? this.tokenFingerprint.substring(0, 16) : 'unknown'
    
    return `uid_${userId}_fp_${fingerprint}`
  }

  /**
   * 调试用：打印当前状态
   */
  debugInfo() {
    return {
      userId: this.userId,
      username: this.username,
      tokenFingerprint: this.tokenFingerprint?.substring(0, 16),
      contextVersion: this.contextVersion,
      loginTimestamp: this.loginTimestamp,
      cachePrefix: this.getCachePrefix()
    }
  }
}

// 全局单例（每个标签页一个独立实例）
const tabUserContext = new TabUserContext()

// 挂载到window方便调试
if (typeof window !== 'undefined') {
  window.__tabUserContext = tabUserContext
}

export default tabUserContext
export { TabUserContext }
