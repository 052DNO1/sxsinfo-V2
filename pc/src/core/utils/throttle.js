/**
 * 防抖与节流工具函�?- 【高并发支持核心模块�?
 * 
 * @module throttle
 * @description 用于控制高频事件的触发频率，优化性能，防止重复请�?
 * 
 * 【高并发功能�?
 * - debounce（防抖）：在事件触发后等待一段时间，如果这段时间内没有再次触发，则执�?
 * - throttle（节流）：在一定时间间隔内只执行一�?
 * - once（一次性执行）：确保函数在指定时间内只能执行一�?
 * - withLock（异步锁）：在异步执行期间，重复调用会被忽略
 * 
 * @example
 * // 搜索输入防抖
 * import { debounce } from '@/core/utils/throttle'
 * const onSearch = debounce((query) => fetchResults(query), 300)
 * 
 * // 登录按钮防重复点�?
 * import { withLock } from '@/core/utils/throttle'
 * const handleLogin = withLock(async () => { ... })
 */

export function debounce(fn, delay = 300, options = {}) {
  const { immediate = false } = options
  
  let timer = null
  let isFirstCall = true
  
  const debounced = function (...args) {
    const context = this
    
    if (timer) {
      clearTimeout(timer)
    }
    
    if (immediate && isFirstCall) {
      isFirstCall = false
      fn.apply(context, args)
      return
    }
    
    timer = setTimeout(() => {
      fn.apply(context, args)
      timer = null
    }, delay)
  }
  
  debounced.cancel = function () {
    if (timer) {
      clearTimeout(timer)
      timer = null
    }
    isFirstCall = true
  }
  
  debounced.flush = function (...args) {
    this.cancel()
    fn.apply(this, args)
  }
  
  return debounced
}

export function throttle(fn, interval = 300, options = {}) {
  const { leading = true, trailing = true } = options
  
  let timer = null
  let lastArgs = null
  let lastCallTime = 0
  
  const throttled = function (...args) {
    const context = this
    const now = Date.now()
    
    lastArgs = args
    
    if (now - lastCallTime >= interval) {
      if (leading) {
        lastCallTime = now
        fn.apply(context, args)
        lastArgs = null
      } else if (timer === null) {
        timer = setTimeout(() => {
          lastCallTime = Date.now()
          timer = null
          if (trailing && lastArgs) {
            fn.apply(context, lastArgs)
            lastArgs = null
          }
        }, interval - (now - lastCallTime))
      }
    } else if (trailing && timer === null) {
      timer = setTimeout(() => {
        lastCallTime = Date.now()
        timer = null
        if (lastArgs) {
          fn.apply(context, lastArgs)
          lastArgs = null
        }
      }, interval - (now - lastCallTime))
    }
  }
  
  throttled.cancel = function () {
    if (timer) {
      clearTimeout(timer)
      timer = null
    }
    lastArgs = null
    lastCallTime = 0
  }
  
  throttled.flush = function () {
    if (lastArgs) {
      fn.apply(this, lastArgs)
    }
    this.cancel()
  }
  
  return throttled
}

export function once(fn, cooldown = 1000) {
  let lastCallTime = 0
  let pending = false
  
  return async function (...args) {
    const context = this
    const now = Date.now()
    
    if (pending || now - lastCallTime < cooldown) {
      return
    }
    
    lastCallTime = now
    pending = true
    
    try {
      const result = await fn.apply(context, args)
      return result
    } finally {
      pending = false
    }
  }
}

export function withLock(fn) {
  let locked = false
  
  return async function (...args) {
    if (locked) {
      return
    }
    
    locked = true
    
    try {
      const result = await fn.apply(this, args)
      return result
    } finally {
      locked = false
    }
  }
}

export default {
  debounce,
  throttle,
  once,
  withLock
}
