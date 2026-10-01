<!--
  服务器连接守卫

  后端不可达时接管整个界面，给出「发生什么 / 连的哪台 / 能做什么」，
  而不是让用户面对白屏或一堆失败的请求提示。

  【为什么不用 UI 组件库】
  本组件挂在 App.vue 上，而 App.vue 由 PC 端和移动端两个构建共用。
  移动端构建只自动注册 Vant、PC 端只自动注册 Element Plus，
  因此这里刻意只用原生标签 + 作用域样式，保证两个构建都不依赖组件库。
-->
<template>
  <div
    v-if="visible"
    class="connection-guard"
  >
    <div class="guard-card">
      <div class="guard-icon">
        <svg
          viewBox="0 0 24 24"
          width="44"
          height="44"
          fill="none"
          stroke="currentColor"
          stroke-width="1.6"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z" />
          <line
            x1="12"
            y1="9"
            x2="12"
            y2="13"
          />
          <line
            x1="12"
            y1="17"
            x2="12.01"
            y2="17"
          />
        </svg>
      </div>

      <h2 class="guard-title">
        无法连接到服务器
      </h2>

      <p class="guard-desc">
        {{ lastError || '网络不可达或后端服务未启动' }}
      </p>

      <div class="guard-meta">
        <div class="meta-row">
          <span class="meta-label">服务器地址</span>
          <span class="meta-value">{{ apiBaseUrl }}</span>
        </div>
        <div
          v-if="lastCheckText"
          class="meta-row"
        >
          <span class="meta-label">最近检测</span>
          <span class="meta-value">{{ lastCheckText }}</span>
        </div>
      </div>

      <div class="guard-actions">
        <button
          class="guard-btn primary"
          :disabled="isChecking"
          @click="handleRetry"
        >
          {{ isChecking ? '检测中...' : '重新检测' }}
        </button>
        <button
          v-if="hasSettingsRoute"
          class="guard-btn"
          @click="goSettings"
        >
          服务器设置
        </button>
        <button
          class="guard-btn ghost"
          @click="handleDismiss"
        >
          仍然继续
        </button>
      </div>

      <p class="guard-hint">
        {{ autoRetryHint }}
      </p>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, onUnmounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useConnection, ConnectionStatus } from '@/core/config/connection'
import { getApiBaseUrl } from '@/core/config/runtime'

/** 离线状态下自动重新探测的间隔（毫秒） */
const AUTO_RETRY_INTERVAL = 15000

export default {
  name: 'ConnectionGuard',
  setup() {
    const router = useRouter()
    const {
      status,
      isOffline,
      isChecking,
      lastError,
      lastCheckAt,
      checkConnection
    } = useConnection()

    /** 用户选择「仍然继续」后暂时隐藏，下次连通性变化时自动恢复拦截 */
    const dismissed = ref(false)

    const apiBaseUrl = computed(() => getApiBaseUrl())

    const visible = computed(() => isOffline.value && !dismissed.value)

    const hasSettingsRoute = computed(() => {
      try {
        return router.hasRoute('ServerSettings')
      } catch (error) {
        return false
      }
    })

    const lastCheckText = computed(() => {
      if (!lastCheckAt.value) return ''
      const diff = Math.floor((Date.now() - lastCheckAt.value) / 1000)
      if (diff < 5) return '刚刚'
      if (diff < 60) return `${diff} 秒前`
      return `${Math.floor(diff / 60)} 分钟前`
    })

    const autoRetryHint = computed(() =>
      `${AUTO_RETRY_INTERVAL / 1000} 秒后自动重新检测`
    )

    /** 一旦重新判定为离线（说明又失败了），恢复拦截 */
    watch(status, (next, prev) => {
      if (next === ConnectionStatus.OFFLINE && prev !== ConnectionStatus.OFFLINE) {
        dismissed.value = false
      }
    })

    const handleRetry = () => {
      dismissed.value = false
      checkConnection()
    }

    const goSettings = () => {
      dismissed.value = true
      router.push('/server-settings').catch(() => {})
    }

    const handleDismiss = () => {
      dismissed.value = true
    }

    // 离线期间定时自动重探，服务器恢复后界面自动放行
    let autoRetryTimer = null

    const startAutoRetry = () => {
      if (autoRetryTimer) return
      autoRetryTimer = setInterval(() => {
        if (isOffline.value && document.visibilityState === 'visible') {
          checkConnection({ silent: true })
        }
      }, AUTO_RETRY_INTERVAL)
    }

    const stopAutoRetry = () => {
      if (autoRetryTimer) {
        clearInterval(autoRetryTimer)
        autoRetryTimer = null
      }
    }

    onMounted(() => {
      startAutoRetry()
    })

    onUnmounted(() => {
      stopAutoRetry()
    })

    onBeforeUnmount(() => {
      stopAutoRetry()
    })

    return {
      visible,
      isChecking,
      lastError,
      apiBaseUrl,
      lastCheckText,
      autoRetryHint,
      hasSettingsRoute,
      handleRetry,
      goSettings,
      handleDismiss
    }
  }
}
</script>

<style scoped>
.connection-guard {
  position: fixed;
  inset: 0;
  z-index: 99990;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: linear-gradient(135deg, #f0f2f5 0%, #e6f7ff 100%);
}

.guard-card {
  width: 100%;
  max-width: 460px;
  padding: 40px 36px 28px;
  background: #ffffff;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
  text-align: center;
}

.guard-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  margin-bottom: 20px;
  border-radius: 50%;
  color: #fa8c16;
  background: #fff7e6;
}

.guard-title {
  margin: 0 0 10px;
  font-size: 22px;
  font-weight: 600;
  color: #1a1a1a;
}

.guard-desc {
  margin: 0 0 24px;
  font-size: 14px;
  line-height: 1.6;
  color: #8c8c8c;
  word-break: break-all;
}

.guard-meta {
  padding: 14px 16px;
  margin-bottom: 24px;
  text-align: left;
  background: #f5f7fa;
  border-radius: 10px;
}

.meta-row {
  display: flex;
  gap: 12px;
  font-size: 13px;
  line-height: 1.8;
}

.meta-label {
  flex: 0 0 72px;
  color: #8c8c8c;
}

.meta-value {
  flex: 1;
  color: #303133;
  word-break: break-all;
}

.guard-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.guard-btn {
  min-width: 104px;
  height: 40px;
  padding: 0 20px;
  font-size: 14px;
  color: #1890ff;
  cursor: pointer;
  background: #fff;
  border: 1px solid #91d5ff;
  border-radius: 20px;
  transition: all 0.25s;
}

.guard-btn:hover:not(:disabled) {
  color: #fff;
  background: #1890ff;
  border-color: #1890ff;
}

.guard-btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.guard-btn.primary {
  color: #fff;
  background: linear-gradient(90deg, #1890ff 0%, #36cfc9 100%);
  border: none;
}

.guard-btn.primary:hover:not(:disabled) {
  box-shadow: 0 8px 16px rgba(24, 144, 255, 0.3);
  transform: translateY(-1px);
}

.guard-btn.ghost {
  color: #8c8c8c;
  background: transparent;
  border-color: #e0e0e0;
}

.guard-btn.ghost:hover {
  color: #595959;
  background: #f5f5f5;
  border-color: #d9d9d9;
}

.guard-hint {
  margin: 20px 0 0;
  font-size: 12px;
  color: #bfbfbf;
}
</style>
