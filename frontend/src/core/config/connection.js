/**
 * 服务器连通性状态
 *
 * @module core/config/connection
 * @description 集中管理「后端服务器是否可达」，供全局提示层与设置页使用。
 *
 * 【为什么需要】
 * 桌面端/Web 端一旦连不上后端，如果只是白屏或一堆失败提示，
 * 用户完全不知道发生了什么、该找谁、能做什么。
 * 这里把连通性变成显式状态：离线时给出可操作的界面（重试 / 改服务器地址）。
 *
 * 【防抖设计】
 * 单个请求的网络错误不足以判定服务器离线（可能是瞬时抖动、
 * 也可能是被取消的请求）。因此网络错误只触发一次「探活」，
 * 由探活结果决定是否切换为离线，避免全局遮罩频繁闪烁。
 */

import { ref, computed } from 'vue'
import { probeServer, getApiBaseUrl, subscribeRuntimeConfig } from './runtime'

/** 连通性状态枚举 */
export const ConnectionStatus = {
  /** 尚未探测 */
  UNKNOWN: 'unknown',
  /** 正在探测 */
  CHECKING: 'checking',
  /** 可达 */
  ONLINE: 'online',
  /** 不可达 */
  OFFLINE: 'offline'
}

const status = ref(ConnectionStatus.UNKNOWN)
const lastError = ref('')
const lastCheckAt = ref(0)
const latencyMs = ref(0)
const serverHealth = ref(null)
const probedApiBaseUrl = ref('')

/** 并发探活去重：同一时刻只跑一次 */
let probeInFlight = null
/** 网络错误触发的延迟探活定时器 */
let debounceTimer = null

const isOffline = computed(() => status.value === ConnectionStatus.OFFLINE)
const isChecking = computed(() => status.value === ConnectionStatus.CHECKING)
const isOnline = computed(() => status.value === ConnectionStatus.ONLINE)

/** 应用当前生效的 API 地址发生变化时重置状态（换了服务器就得重新判定） */
subscribeRuntimeConfig(() => {
  if (probedApiBaseUrl.value && probedApiBaseUrl.value !== getApiBaseUrl()) {
    status.value = ConnectionStatus.UNKNOWN
    lastError.value = ''
    serverHealth.value = null
  }
})

/**
 * 执行一次服务器探活
 * @param {{silent?: boolean}} [options] silent=true 时不显示「探测中」状态
 * @returns {Promise<{ok: boolean, message: string, latencyMs: number}>}
 */
export function checkConnection(options = {}) {
  if (probeInFlight) return probeInFlight

  const target = getApiBaseUrl()
  probedApiBaseUrl.value = target

  if (!options.silent) {
    status.value = ConnectionStatus.CHECKING
  }

  probeInFlight = probeServer(target)
    .then((result) => {
      lastCheckAt.value = Date.now()
      latencyMs.value = result.latencyMs
      serverHealth.value = result.data || null

      if (result.ok) {
        status.value = ConnectionStatus.ONLINE
        lastError.value = ''
      } else {
        status.value = ConnectionStatus.OFFLINE
        lastError.value = result.message || '无法连接到服务器'
      }

      return result
    })
    .catch((error) => {
      status.value = ConnectionStatus.OFFLINE
      lastError.value = (error && error.message) || '无法连接到服务器'
      return { ok: false, message: lastError.value, latencyMs: 0 }
    })
    .finally(() => {
      probeInFlight = null
    })

  return probeInFlight
}

/**
 * 业务请求成功：说明服务器可达，立刻纠正离线状态
 */
export function reportRequestSuccess() {
  if (status.value !== ConnectionStatus.ONLINE) {
    status.value = ConnectionStatus.ONLINE
    lastError.value = ''
    if (debounceTimer) {
      clearTimeout(debounceTimer)
      debounceTimer = null
    }
  }
}

/**
 * 业务请求失败：仅对「网络层失败」做延迟探活确认
 *
 * 服务器返回了 HTTP 状态码（哪怕 4xx/5xx）说明连接是通的，
 * 不属于连通性问题，交给业务层处理。
 *
 * @param {object} error axios 错误对象
 */
export function reportRequestFailure(error) {
  if (!error) return

  // 服务器有响应 => 连接正常
  if (error.response) {
    reportRequestSuccess()
    return
  }

  // 主动取消的请求不算网络故障
  if (error.code === 'ERR_CANCELED' || error.name === 'CanceledError') return
  // 请求去重被拒不算网络故障
  if (error.message === 'Duplicate request') return

  // 真正可疑的网络层失败：延迟探活，由探活结果决定是否切离线
  if (debounceTimer) return
  debounceTimer = setTimeout(() => {
    debounceTimer = null
    checkConnection({ silent: true })
  }, 1200)
}

/**
 * 组合式用法：组件中获取连通性状态与操作
 * @returns {object}
 */
export function useConnection() {
  return {
    status,
    isOffline,
    isChecking,
    isOnline,
    lastError,
    lastCheckAt,
    latencyMs,
    serverHealth,
    checkConnection,
    reportRequestSuccess,
    reportRequestFailure
  }
}
