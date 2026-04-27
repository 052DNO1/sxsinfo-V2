/**
 * 多标签页/窗口同步管理器
 * 
 * 解决问题：
 * 1. 多标签页登录时Token冲突导致被踢出
 * 2. 一个标签页登出影响其他标签页
 * 3. Token刷新后其他标签页不知道
 * 4. 多开后缓存全部失效（核心问题！）
 * 
 * 使用 BroadcastChannel API 实现跨标签页通信
 */

const CHANNEL_NAME = 'v2_auth_sync'

class TabSyncManager {
  constructor() {
    this.channel = null
    this.tabId = this.generateTabId()
    this.isMaster = false
    this.listeners = new Map()
    this.init()
  }

  generateTabId() {
    return `tab_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  init() {
    if (typeof BroadcastChannel === 'undefined') {
      console.warn('[TabSync] BroadcastChannel not supported')
      return
    }

    try {
      this.channel = new BroadcastChannel(CHANNEL_NAME)
    } catch (error) {
      console.error('[TabSync] Failed to create BroadcastChannel:', error)
      return
    }
    
    this.channel.onmessage = (event) => {
      const { type, payload, sourceTabId } = event.data
      
      if (sourceTabId === this.tabId) return

      this.handleMessage(type, payload)
    }

    window.addEventListener('storage', (event) => {
      if (event.key === 'access_token' || event.key === 'refresh_token') {
        const newValue = event.newValue
        const oldValue = event.oldValue
        
        if (!newValue && oldValue) {
          this.broadcast('token_cleared', { key: event.key })
        } else if (newValue && newValue !== oldValue) {
          this.broadcast('token_updated', { 
            key: event.key, 
            value: newValue 
          })
        }
      }
    })

    this.checkMasterStatus()
    
    setInterval(() => {
      this.checkMasterStatus()
    }, 5000)
  }

  checkMasterStatus() {
    const hasToken = !!sessionStorage.getItem('access_token')
    if (hasToken && !this.isMaster) {
      this.isMaster = true
      this.broadcast('master_claimed', { tabId: this.tabId })
    } else if (!hasToken && this.isMaster) {
      this.isMaster = false
    }
  }

  handleMessage(type, payload) {
    switch (type) {
      case 'login':
        this.emit('onLogin', payload)
        break
      case 'logout':
        this.emit('onLogout', payload)
        break
      case 'token_refreshed':
        this.emit('onTokenRefreshed', payload)
        break
      case 'token_cleared':
        this.emit('onTokenCleared', payload)
        break
      case 'token_updated':
        this.emit('onTokenUpdated', payload)
        break
      case 'master_claimed':
        if (payload.tabId !== this.tabId) {
          this.isMaster = false
        }
        break
      case 'ping':
        this.respondToPing(payload)
        break
      case 'pong':
        break
      // 缓存同步事件
      case 'cache_cleared':
        this.emit('onCacheCleared', payload)
        break
      case 'cache_pattern_cleared':
        this.emit('onCachePatternCleared', payload)
        break
      case 'cache_updated':
        this.emit('onCacheUpdated', payload)
        break
    }
  }

  broadcast(type, payload) {
    if (!this.channel) return
    
    try {
      this.channel.postMessage({
        type,
        payload,
        sourceTabId: this.tabId,
        timestamp: Date.now()
      })
    } catch (error) {
      console.error('[TabSync] Broadcast error:', error)
    }
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event).push(callback)
  }

  off(event, callback) {
    if (!this.listeners.has(event)) return
    
    const callbacks = this.listeners.get(event)
    const index = callbacks.indexOf(callback)
    if (index !== -1) {
      callbacks.splice(index, 1)
    }
  }

  emit(event, payload) {
    const callbacks = this.listeners.get(event)
    if (callbacks) {
      callbacks.forEach(callback => {
        try {
          callback(payload)
        } catch (error) {
          console.error(`[TabSync] Error in ${event} listener:`, error)
        }
      })
    }
  }

  notifyLogin(tokenData) {
    this.broadcast('login', {
      access: tokenData.access,
      refresh: tokenData.refresh,
      user: tokenData.user
    })
  }

  notifyLogout() {
    this.broadcast('logout', { timestamp: Date.now() })
  }

  notifyTokenRefreshed(newTokens) {
    this.broadcast('token_refreshed', {
      access: newTokens.access,
      refresh: newTokens.refresh
    })
  }

  // 缓存同步方法
  notifyCacheCleared(options = {}) {
    this.broadcast('cache_cleared', {
      ...options,
      timestamp: Date.now()
    })
  }

  notifyCachePatternCleared(pattern, options = {}) {
    this.broadcast('cache_pattern_cleared', {
      pattern: pattern.toString(),
      ...options,
      timestamp: Date.now()
    })
  }

  notifyCacheUpdated(url, params, data, options = {}) {
    this.broadcast('cache_updated', {
      url,
      params,
      data,
      ...options,
      timestamp: Date.now()
    })
  }

  pingOtherTabs() {
    this.broadcast('ping', { tabId: this.tabId })
  }

  respondToPing(payload) {
    this.broadcast('pong', { 
      targetTabId: payload.tabId,
      respondingTabId: this.tabId 
    })
  }

  destroy() {
    if (this.channel) {
      this.channel.close()
      this.channel = null
    }
    this.listeners.clear()
  }
}

const tabSyncManager = new TabSyncManager()

export default tabSyncManager
export { TabSyncManager }
