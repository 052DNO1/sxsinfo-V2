/**
 * 运行时配置层（Web 端 / 桌面端通用）
 *
 * @module core/config/runtime
 * @description 解决「后端 API 地址不能在构建时写死」的问题。
 * 同一份安装包要能连本地测试环境，也要能连学校生产服务器。
 *
 * 【解析优先级】（从高到低）
 *   1. window.__LIMS_CONFIG__              —— 桌面壳(Tauri)在页面加载前注入
 *   2. 本地持久化配置                       —— 由「服务器设置」页写入
 *   3. import.meta.env.VITE_API_V2_BASE_URL —— 构建时注入
 *   4. 内置默认值 DEFAULT_API_BASE_URL
 *
 * 【零回归原则】
 * 纯浏览器部署（非 dev、非桌面壳）下第 2 层被禁用，
 * 解析结果与改造前完全一致：VITE_API_V2_BASE_URL || 默认值。
 * 因此 Web 端（Docker + Nginx）部署行为不受任何影响。
 *
 * @example
 * import { getApiBaseUrl, setApiBaseUrl, probeServer } from '@/core/config/runtime'
 *
 * getApiBaseUrl()                        // => 'http://localhost:8000/api/v1'
 * setApiBaseUrl('192.168.1.20:8000')     // => 'http://192.168.1.20:8000/api/v1'
 * await probeServer()                    // => { ok: true, latencyMs: 42, ... }
 */

/** 内置默认后端地址（与改造前 client.js 的兜底值保持一致） */
export const DEFAULT_API_BASE_URL = 'http://localhost:8000/api/v1'

/** 本地持久化配置的存储键（带版本号，便于将来结构升级） */
export const RUNTIME_CONFIG_KEY = 'lims.runtime.config.v1'

/** 健康检查路径（相对 API 根路径） */
const HEALTH_PATH = '/common/health/'

/** 上下文注入对象名（桌面壳写入 window.__LIMS_CONFIG__） */
const INJECTED_KEY = '__LIMS_CONFIG__'

/** 配置来源标识，用于在设置页展示「当前地址从哪来」 */
export const ConfigSource = {
  INJECTED: 'injected',
  LOCAL: 'local',
  BUILD: 'build',
  DEFAULT: 'default'
}

export const ConfigSourceLabel = {
  [ConfigSource.INJECTED]: '桌面端配置',
  [ConfigSource.LOCAL]: '本机已保存',
  [ConfigSource.BUILD]: '构建时配置',
  [ConfigSource.DEFAULT]: '内置默认值'
}

// ─────────────────────────────────────────────
// 环境探测
// ─────────────────────────────────────────────

/**
 * 是否运行在桌面壳（Tauri）内
 * 桌面壳会在页面加载前设置 window.__LIMS_DESKTOP__
 * @returns {boolean}
 */
export function isDesktop() {
  if (typeof window === 'undefined') return false
  return window.__LIMS_DESKTOP__ === true || !!window.__TAURI_INTERNALS__ || !!window.__TAURI__
}

/**
 * 是否允许读写「本机保存的服务器地址」
 *
 * 纯浏览器生产部署下必须为 false，否则一次误操作会把写死的
 * 相对路径( /api/v1 )覆盖成本机地址，导致 Web 部署失效。
 *
 * @returns {boolean}
 */
export function isLocalOverrideAllowed() {
  if (typeof window === 'undefined') return false
  if (isDesktop()) return true
  return !!import.meta.env.DEV || import.meta.env.VITE_ALLOW_RUNTIME_CONFIG === 'true'
}

/** 读取桌面壳注入的配置对象（无则返回 null） */
function readInjectedConfig() {
  if (typeof window === 'undefined') return null
  const injected = window[INJECTED_KEY]
  if (injected && typeof injected === 'object') return injected
  return null
}

/**
 * 同步内存中的注入对象
 *
 * 桌面壳注入的值优先级最高，若只改本机存储而不改它，
 * resolve() 会立刻把新地址覆盖回旧值（本次会话失效），
 * 重启后也会因为壳又注入旧值而回退。
 *
 * @param {string|null} apiBaseUrl 传 null 表示清除
 */
function syncInjectedConfig(apiBaseUrl) {
  const injected = readInjectedConfig()
  if (!injected) return
  if (apiBaseUrl) {
    injected.apiBaseUrl = apiBaseUrl
  } else {
    delete injected.apiBaseUrl
  }
}

/**
 * 把地址落到桌面端的应用配置文件（%APPDATA%\<identifier>\config.json）
 *
 * 走 Tauri IPC，不依赖 @tauri-apps/api 包：
 * 应用开启了 withGlobalTauri，window.__TAURI__.core.invoke 可直接使用。
 * 失败不抛错——本机存储仍然生效，不影响本次会话。
 *
 * @param {string|null} apiBaseUrl
 */
function persistToDesktop(apiBaseUrl) {
  if (!isDesktop()) return

  let invoke = null
  try {
    invoke =
      (window.__TAURI__ && window.__TAURI__.core && window.__TAURI__.core.invoke) ||
      (window.__TAURI_INTERNALS__ && window.__TAURI_INTERNALS__.invoke) ||
      null
  } catch (error) {
    invoke = null
  }

  if (typeof invoke !== 'function') return

  try {
    const result = invoke('set_server_config', { apiBaseUrl: apiBaseUrl || null })
    if (result && typeof result.catch === 'function') {
      result.catch((error) => {
        console.warn('[runtime] 桌面端配置文件写入失败:', error)
      })
    }
  } catch (error) {
    console.warn('[runtime] 桌面端配置文件写入失败:', error)
  }
}

/** 读取本机持久化配置（无则返回 null） */
function readLocalConfig() {
  if (typeof window === 'undefined') return null
  try {
    const raw = window.localStorage.getItem(RUNTIME_CONFIG_KEY)
    if (!raw) return null
    const parsed = JSON.parse(raw)
    if (parsed && typeof parsed === 'object') return parsed
    return null
  } catch (error) {
    console.warn('[runtime] 本机配置解析失败，已忽略:', error)
    return null
  }
}

// ─────────────────────────────────────────────
// 地址规范化与校验
// ─────────────────────────────────────────────

/**
 * 把用户输入的地址规范化为完整的 API 根地址
 *
 * 规则：
 * - 缺少协议时补 http://
 * - 路径为空或 '/' 时补 /api/v1
 * - 去掉末尾多余的 '/'
 * - 以 '/' 开头的相对地址（如 /api/v1）原样保留，用于 Nginx 同源部署
 *
 * @param {string} input 用户输入
 * @returns {string} 规范化后的地址
 *
 * @example
 * normalizeApiBaseUrl('192.168.1.20:8000')          // 'http://192.168.1.20:8000/api/v1'
 * normalizeApiBaseUrl('https://a.edu.cn/')          // 'https://a.edu.cn/api/v1'
 * normalizeApiBaseUrl('https://a.edu.cn/x/api/v1/') // 'https://a.edu.cn/x/api/v1'
 * normalizeApiBaseUrl('/api/v1')                    // '/api/v1'
 */
export function normalizeApiBaseUrl(input) {
  let value = String(input == null ? '' : input).trim()
  if (!value) return ''

  // 同源相对路径：仅做去尾斜杠与补默认路径
  if (value.startsWith('/')) {
    value = value.replace(/\/+$/, '')
    if (!value || value === '') return ''
    return value === '' ? '/api/v1' : value
  }

  // 桌面端用户习惯直接填 IP:端口，这里补上协议
  if (!/^https?:\/\//i.test(value)) {
    value = 'http://' + value
  }

  try {
    const url = new URL(value)
    let pathname = url.pathname.replace(/\/+$/, '')
    if (!pathname) pathname = '/api/v1'
    // 允许部署在子路径下（如 https://host/lims/api/v1）
    if (!/\/api\/v\d+$/.test(pathname) && pathname !== '/api/v1') {
      // 用户显式给了非 /api/vN 的路径时尊重原样，不做猜测
    }
    return `${url.protocol}//${url.host}${pathname}`
  } catch (error) {
    return ''
  }
}

/**
 * 校验用户输入的地址是否可用
 * @param {string} input 用户输入
 * @returns {{valid: boolean, normalized: string, reason: string}}
 */
export function validateApiBaseUrl(input) {
  const normalized = normalizeApiBaseUrl(input)
  if (!normalized) {
    return { valid: false, normalized: '', reason: '请输入有效的服务器地址' }
  }
  if (normalized.startsWith('/')) {
    return { valid: true, normalized, reason: '' }
  }
  try {
    const url = new URL(normalized)
    if (!url.hostname) {
      return { valid: false, normalized, reason: '地址缺少主机名' }
    }
    return { valid: true, normalized, reason: '' }
  } catch (error) {
    return { valid: false, normalized: '', reason: '地址格式无法解析' }
  }
}

/**
 * 由 API 根地址推导健康检查地址
 * @param {string} [apiBaseUrl] 缺省使用当前生效地址
 * @returns {string}
 */
export function getHealthUrl(apiBaseUrl) {
  const base = apiBaseUrl || getApiBaseUrl()
  if (!base) return ''
  return base.replace(/\/+$/, '') + HEALTH_PATH
}

/**
 * 由 API 根地址推导可读的服务根地址（用于展示与打开浏览器）
 * @param {string} [apiBaseUrl]
 * @returns {string}
 */
export function getServerOrigin(apiBaseUrl) {
  const base = apiBaseUrl || getApiBaseUrl()
  if (!base) return ''
  try {
    return new URL(base).origin
  } catch (error) {
    return ''
  }
}

// ─────────────────────────────────────────────
// 配置解析（带内存缓存 + 订阅通知）
// ─────────────────────────────────────────────

const listeners = new Set()

/** 内存中的当前生效配置，模块加载时立即解析一次 */
let current = resolve()

/**
 * 按优先级解析出最终生效的配置
 * @returns {{apiBaseUrl: string, source: string, injected: object|null, local: object|null}}
 */
function resolve() {
  const injected = readInjectedConfig()
  const local = isLocalOverrideAllowed() ? readLocalConfig() : null
  const buildTime = import.meta.env.VITE_API_V2_BASE_URL

  // 1. 桌面壳注入（最高优先级）
  const injectedUrl = injected && injected.apiBaseUrl
    ? normalizeApiBaseUrl(injected.apiBaseUrl)
    : ''
  if (injectedUrl) {
    return { apiBaseUrl: injectedUrl, source: ConfigSource.INJECTED, injected, local }
  }

  // 2. 本机保存
  const localUrl = local && local.apiBaseUrl ? normalizeApiBaseUrl(local.apiBaseUrl) : ''
  if (localUrl) {
    return { apiBaseUrl: localUrl, source: ConfigSource.LOCAL, injected, local }
  }

  // 3. 构建时注入
  const buildUrl = buildTime ? normalizeApiBaseUrl(buildTime) : ''
  if (buildUrl) {
    return { apiBaseUrl: buildUrl, source: ConfigSource.BUILD, injected, local }
  }

  // 4. 内置默认值
  return {
    apiBaseUrl: DEFAULT_API_BASE_URL,
    source: ConfigSource.DEFAULT,
    injected,
    local
  }
}

/** 通知所有订阅者配置已变化 */
function notify() {
  listeners.forEach((fn) => {
    try {
      fn(current)
    } catch (error) {
      console.error('[runtime] 配置订阅回调异常:', error)
    }
  })
}

/**
 * 获取当前生效的完整配置
 * @returns {{apiBaseUrl: string, source: string}}
 */
export function getRuntimeConfig() {
  return { apiBaseUrl: current.apiBaseUrl, source: current.source }
}

/**
 * 获取当前生效的 API 根地址
 *
 * 这是全应用唯一的 API 地址来源，请求层必须通过它取值，
 * 不允许再直接读 import.meta.env，否则运行时切换地址会失效。
 *
 * @returns {string}
 */
export function getApiBaseUrl() {
  return current.apiBaseUrl
}

/**
 * 订阅配置变化
 * @param {(config: {apiBaseUrl: string, source: string}) => void} fn
 * @returns {() => void} 取消订阅
 */
export function subscribeRuntimeConfig(fn) {
  if (typeof fn !== 'function') return () => {}
  listeners.add(fn)
  return () => listeners.delete(fn)
}

/**
 * 重新解析配置（用于本机配置被外部改动后手动刷新）
 * @returns {{apiBaseUrl: string, source: string}}
 */
export function reloadRuntimeConfig() {
  current = resolve()
  notify()
  return getRuntimeConfig()
}

/**
 * 设置并持久化 API 根地址
 *
 * @param {string} input 用户输入的地址
 * @param {{persist?: boolean}} [options] persist=false 时仅本次会话生效
 * @returns {{ok: boolean, apiBaseUrl: string, reason: string}}
 */
export function setApiBaseUrl(input, options = {}) {
  const { valid, normalized, reason } = validateApiBaseUrl(input)
  if (!valid) {
    return { ok: false, apiBaseUrl: current.apiBaseUrl, reason }
  }

  const persist = options.persist !== false

  if (persist) {
    if (isLocalOverrideAllowed()) {
      try {
        window.localStorage.setItem(
          RUNTIME_CONFIG_KEY,
          JSON.stringify({ apiBaseUrl: normalized, updatedAt: new Date().toISOString() })
        )
      } catch (error) {
        console.warn('[runtime] 本机配置写入失败:', error)
      }
    }
    // 桌面端还要写应用配置文件，否则重启后被注入的旧值覆盖
    persistToDesktop(normalized)
  }

  // 无论是否持久化，本次会话都必须立刻生效
  syncInjectedConfig(normalized)

  current = resolve()
  notify()
  return { ok: true, apiBaseUrl: current.apiBaseUrl, reason: '' }
}

/**
 * 清除本机保存的地址，回落到构建时配置 / 内置默认值
 * @returns {{apiBaseUrl: string, source: string}}
 */
export function resetApiBaseUrl() {
  if (typeof window !== 'undefined') {
    try {
      window.localStorage.removeItem(RUNTIME_CONFIG_KEY)
    } catch (error) {
      console.warn('[runtime] 本机配置清除失败:', error)
    }
  }

  // 桌面端配置文件同样要清，否则其注入值仍会压过构建时配置
  syncInjectedConfig(null)
  persistToDesktop(null)

  current = resolve()
  notify()
  return getRuntimeConfig()
}

/**
 * 是否存在可被清除的本机覆盖配置
 *
 * 桌面端有两处来源：应用配置文件（经壳注入）与 WebView 本机存储，
 * 任一存在都算有覆盖。
 *
 * @returns {boolean}
 */
export function hasLocalOverride() {
  if (readLocalConfig()) return true
  const injected = readInjectedConfig()
  return !!(injected && injected.apiBaseUrl)
}

/** 构建时配置（用于设置页展示对比） */
export function getBuildTimeApiBaseUrl() {
  return import.meta.env.VITE_API_V2_BASE_URL
    ? normalizeApiBaseUrl(import.meta.env.VITE_API_V2_BASE_URL)
    : ''
}

// ─────────────────────────────────────────────
// 服务器连通性探测
// ─────────────────────────────────────────────

/**
 * 探测后端服务器是否可用
 *
 * 直连健康检查端点 /common/health/，不使用业务 axios 实例，
 * 避免触发 token 刷新、请求队列与全局错误提示。
 *
 * @param {string} [apiBaseUrl] 缺省探测当前生效地址
 * @param {{timeout?: number}} [options]
 * @returns {Promise<{ok: boolean, status: number, latencyMs: number, message: string, data: object|null}>}
 */
export async function probeServer(apiBaseUrl, options = {}) {
  const url = getHealthUrl(apiBaseUrl)
  const timeout = options.timeout || 6000
  const startedAt = Date.now()

  if (!url) {
    return { ok: false, status: 0, latencyMs: 0, message: '服务器地址为空', data: null }
  }

  const controller = typeof AbortController !== 'undefined' ? new AbortController() : null
  const timer = controller ? setTimeout(() => controller.abort(), timeout) : null

  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: { Accept: 'application/json' },
      cache: 'no-store',
      signal: controller ? controller.signal : undefined
    })

    const latencyMs = Date.now() - startedAt
    let data = null
    try {
      data = await response.json()
    } catch (error) {
      data = null
    }

    if (!response.ok) {
      return {
        ok: false,
        status: response.status,
        latencyMs,
        message: `服务器返回 ${response.status}`,
        data
      }
    }

    // 后端健康检查在数据库/缓存异常时返回 503，
    // 因此能走到这里通常代表服务正常；仍显式确认一次 status 字段。
    const healthy = !data || data.status === 'healthy' || data.success === true
    return {
      ok: healthy,
      status: response.status,
      latencyMs,
      message: healthy ? '连接正常' : '服务端自检未通过',
      data
    }
  } catch (error) {
    const latencyMs = Date.now() - startedAt
    const isTimeout = error && error.name === 'AbortError'
    return {
      ok: false,
      status: 0,
      latencyMs,
      message: isTimeout ? `连接超时（${timeout / 1000}s）` : '无法连接到服务器',
      data: null
    }
  } finally {
    if (timer) clearTimeout(timer)
  }
}
