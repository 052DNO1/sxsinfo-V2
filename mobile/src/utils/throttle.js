/**
 * 防抖与节流工具函数 - 【高并发支持核心模块】
 * 
 * @module throttle
 * @description 用于控制高频事件的触发频率，优化性能，防止重复请求
 * 
 * 【高并发功能】
 * - debounce（防抖）：在事件触发后等待一段时间，如果这段时间内没有再次触发，则执行
 * - throttle（节流）：在一定时间间隔内只执行一次
 * - once（一次性执行）：确保函数在指定时间内只能执行一次
 * - withLock（异步锁）：在异步执行期间，重复调用会被忽略
 * 
 * @example
 * // 搜索输入防抖
 * import { debounce } from '@/utils/throttle'
 * const onSearch = debounce((query) => fetchResults(query), 300)
 * 
 * // 登录按钮防重复点击
 * import { withLock } from '@/utils/throttle'
 * const handleLogin = withLock(async () => { ... })
 */

/**
 * 防抖函数
 * 
 * 在事件被触发后，等待一定时间再执行回调
 * 如果在等待时间内再次触发，则重新计时
 * 
 * @param {Function} fn - 要执行的函数
 * @param {number} delay - 延迟时间（毫秒）
 * @param {Object} options - 配置选项
 * @param {boolean} options.immediate - 是否立即执行（第一次触发时）
 * @returns {Function} 防抖后的函数
 * 
 * @example
 * // 搜索输入防抖
 * const debouncedSearch = debounce((query) => {
 *   fetchResults(query)
 * }, 300)
 * 
 * input.addEventListener('input', (e) => {
 *   debouncedSearch(e.target.value)
 * })
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

/**
 * 节流函数
 * 
 * 在一定时间间隔内只执行一次回调
 * 适用于持续触发的事件（如滚动、resize）
 * 
 * @param {Function} fn - 要执行的函数
 * @param {number} interval - 时间间隔（毫秒）
 * @param {Object} options - 配置选项
 * @param {boolean} options.leading - 是否在开始时立即执行
 * @param {boolean} options.trailing - 是否在结束时执行最后一次
 * @returns {Function} 节流后的函数
 * 
 * @example
 * // 滚动事件节流
 * const throttledScroll = throttle(() => {
 *   updateScrollPosition()
 * }, 200)
 * 
 * window.addEventListener('scroll', throttledScroll)
 */
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

/**
 * 创建一次性执行函数
 * 
 * 确保函数在指定时间内只能执行一次
 * 适用于防止重复提交等场景
 * 
 * @param {Function} fn - 要执行的函数
 * @param {number} cooldown - 冷却时间（毫秒）
 * @returns {Function} 限制后的函数
 * 
 * @example
 * // 防止重复点击提交
 * const submitOnce = once(() => {
 *   submitForm()
 * }, 1000)
 * 
 * button.addEventListener('click', submitOnce)
 */
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

/**
 * 创建带锁的异步函数
 * 
 * 在异步执行期间，重复调用会被忽略
 * 适用于防止并发执行同一操作
 * 
 * @param {Function} fn - 要执行的异步函数
 * @returns {Function} 带锁的函数
 * 
 * @example
 * // 防止登录按钮重复点击
 * const lockedLogin = withLock(async (credentials) => {
 *   await login(credentials)
 * })
 */
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
