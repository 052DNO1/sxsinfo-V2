<!--
  服务器设置

  桌面端/开发环境下可改后端地址，解决「一个安装包要连不同服务器」的问题。
  该页面不需要登录即可访问：服务器连不上时用户必须能进来改地址。
-->
<template>
  <div class="server-settings">
    <div class="settings-card">
      <div class="settings-header">
        <div class="header-icon">
          <el-icon :size="26">
            <Connection />
          </el-icon>
        </div>
        <div class="header-text">
          <h1>服务器设置</h1>
          <p>配置本应用连接的后端服务地址</p>
        </div>
      </div>

      <!-- 当前状态 -->
      <div class="status-panel">
        <div class="status-main">
          <el-tag
            :type="statusTagType"
            effect="dark"
            size="large"
            round
          >
            {{ statusLabel }}
          </el-tag>
          <span
            v-if="latencyText"
            class="status-latency"
          >{{ latencyText }}</span>
        </div>
        <div class="status-detail">
          <div class="detail-row">
            <span class="detail-label">当前生效地址</span>
            <span class="detail-value">{{ currentApiBaseUrl }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">配置来源</span>
            <span class="detail-value">{{ currentSourceLabel }}</span>
          </div>
          <div
            v-if="statusMessage"
            class="detail-row"
          >
            <span class="detail-label">检测结果</span>
            <span class="detail-value">{{ statusMessage }}</span>
          </div>
        </div>
      </div>

      <el-alert
        v-if="!localOverrideAllowed"
        type="info"
        :closable="false"
        show-icon
        class="mode-alert"
      >
        <template #title>
          当前为纯浏览器部署，服务器地址由构建配置决定，本页不可修改。
          如需在本地测试中修改，请使用开发模式或桌面端。
        </template>
      </el-alert>

      <!-- 地址配置 -->
      <div class="form-section">
        <div class="section-title">
          服务器地址
        </div>
        <el-input
          v-model="inputUrl"
          :disabled="!localOverrideAllowed"
          placeholder="例如 192.168.1.20:8000 或 https://lims.example.edu.cn"
          size="large"
          clearable
          @keyup.enter="handleTest"
        >
          <template #prepend>
            <el-icon><Link /></el-icon>
          </template>
        </el-input>

        <div class="field-hint">
          可只填主机和端口，系统会自动补全为 <code>{{ normalizedPreview || 'http://主机:端口/api/v1' }}</code>
        </div>

        <el-alert
          v-if="inputError"
          type="error"
          :closable="false"
          show-icon
          class="input-alert"
        >
          <template #title>
            {{ inputError }}
          </template>
        </el-alert>

        <div class="action-row">
          <el-button
            type="primary"
            size="large"
            :loading="testing"
            :disabled="!localOverrideAllowed"
            @click="handleTest"
          >
            测试连接
          </el-button>
          <el-button
            size="large"
            :loading="saving"
            :disabled="!localOverrideAllowed || !normalizedPreview"
            @click="handleSave"
          >
            保存并应用
          </el-button>
          <el-button
            size="large"
            :disabled="!localOverrideAllowed || !hasOverride"
            @click="handleReset"
          >
            恢复默认
          </el-button>
        </div>
      </div>

      <!-- 诊断信息 -->
      <el-collapse class="diagnostics">
        <el-collapse-item
          title="诊断信息"
          name="diag"
        >
          <el-descriptions
            :column="1"
            border
            size="small"
          >
            <el-descriptions-item label="运行模式">
              {{ isDesktopMode ? '桌面端' : (isDevMode ? '开发模式（浏览器）' : '浏览器部署') }}
            </el-descriptions-item>
            <el-descriptions-item label="构建时地址">
              {{ buildTimeApiBaseUrl || '未配置' }}
            </el-descriptions-item>
            <el-descriptions-item label="本机覆盖">
              {{ hasOverride ? '已设置' : '未设置' }}
            </el-descriptions-item>
            <el-descriptions-item label="健康检查地址">
              {{ healthUrl }}
            </el-descriptions-item>
            <el-descriptions-item label="服务端自检">
              <span v-if="healthPayload">{{ formatHealth(healthPayload) }}</span>
              <span v-else>无数据</span>
            </el-descriptions-item>
          </el-descriptions>
        </el-collapse-item>
      </el-collapse>

      <div class="footer-row">
        <el-button
          link
          type="primary"
          @click="goLogin"
        >
          返回登录
        </el-button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Connection, Link } from '@element-plus/icons-vue'
import {
  getApiBaseUrl,
  getRuntimeConfig,
  getBuildTimeApiBaseUrl,
  getHealthUrl,
  normalizeApiBaseUrl,
  validateApiBaseUrl,
  setApiBaseUrl,
  resetApiBaseUrl,
  hasLocalOverride,
  isDesktop,
  isLocalOverrideAllowed,
  probeServer,
  ConfigSourceLabel
} from '@/core/config/runtime'
import { useConnection, ConnectionStatus } from '@/core/config/connection'

export default {
  name: 'ServerSettings',
  components: {
    Connection,
    Link
  },
  setup() {
    const router = useRouter()
    const { status, lastError, latencyMs, serverHealth, checkConnection } = useConnection()

    const inputUrl = ref('')
    const testing = ref(false)
    const saving = ref(false)
    const inputError = ref('')
    const localOverrideAllowed = ref(isLocalOverrideAllowed())
    const hasOverride = ref(hasLocalOverride())
    const isDesktopMode = ref(isDesktop())
    const isDevMode = ref(!!import.meta.env.DEV)
    const buildTimeApiBaseUrl = ref(getBuildTimeApiBaseUrl())

    const currentApiBaseUrl = computed(() => getApiBaseUrl())
    const currentSourceLabel = computed(() => ConfigSourceLabel[getRuntimeConfig().source] || '未知')
    const healthUrl = computed(() => getHealthUrl())
    const healthPayload = computed(() => serverHealth.value)

    const normalizedPreview = computed(() => normalizeApiBaseUrl(inputUrl.value))

    const statusTagType = computed(() => {
      switch (status.value) {
        case ConnectionStatus.ONLINE: return 'success'
        case ConnectionStatus.OFFLINE: return 'danger'
        case ConnectionStatus.CHECKING: return 'warning'
        default: return 'info'
      }
    })

    const statusLabel = computed(() => {
      switch (status.value) {
        case ConnectionStatus.ONLINE: return '已连接'
        case ConnectionStatus.OFFLINE: return '无法连接'
        case ConnectionStatus.CHECKING: return '检测中'
        default: return '未检测'
      }
    })

    const statusMessage = computed(() => {
      if (status.value === ConnectionStatus.OFFLINE) return lastError.value
      if (status.value === ConnectionStatus.ONLINE) return '服务端健康检查通过'
      return ''
    })

    const latencyText = computed(() => {
      if (status.value !== ConnectionStatus.ONLINE || !latencyMs.value) return ''
      return `延迟 ${latencyMs.value} ms`
    })

    const formatHealth = (payload) => {
      if (!payload || typeof payload !== 'object') return '无数据'
      const parts = []
      if (payload.status) parts.push(`状态=${payload.status}`)
      if (payload.database) parts.push(`数据库=${payload.database}`)
      if (payload.cache) parts.push(`缓存=${payload.cache}`)
      return parts.length ? parts.join('，') : JSON.stringify(payload)
    }

    const syncFromStore = () => {
      inputUrl.value = currentApiBaseUrl.value
      hasOverride.value = hasLocalOverride()
      localOverrideAllowed.value = isLocalOverrideAllowed()
    }

    onMounted(() => {
      syncFromStore()
      checkConnection()
    })

    const validateInput = () => {
      const result = validateApiBaseUrl(inputUrl.value)
      inputError.value = result.valid ? '' : result.reason
      return result
    }

    const handleTest = async () => {
      const result = validateInput()
      if (!result.valid) return

      testing.value = true
      try {
        const probe = await probeServer(result.normalized)
        // 同步全局连通性状态，使守卫层与这里一致
        await checkConnection({ silent: true })

        if (probe.ok) {
          ElMessage.success(`连接成功（${probe.latencyMs} ms）`)
        } else {
          ElMessage.error(`连接失败：${probe.message}`)
        }
      } finally {
        testing.value = false
      }
    }

    const handleSave = async () => {
      const result = validateInput()
      if (!result.valid) return

      const changed = result.normalized !== currentApiBaseUrl.value

      if (changed) {
        try {
          await ElMessageBox.confirm(
            `将服务器地址切换为：\n${result.normalized}\n\n切换后需要重新登录，是否继续？`,
            '确认修改服务器地址',
            { type: 'warning', confirmButtonText: '确认切换', cancelButtonText: '取消' }
          )
        } catch (error) {
          return
        }
      }

      saving.value = true
      try {
        const saved = setApiBaseUrl(result.normalized)
        if (!saved.ok) {
          inputError.value = saved.reason
          return
        }

        hasOverride.value = hasLocalOverride()
        inputUrl.value = currentApiBaseUrl.value

        // 换服务器等同于换了一套账号体系，旧 token 必须作废
        sessionStorage.removeItem('access_token')
        sessionStorage.removeItem('refresh_token')
        sessionStorage.removeItem('user')
        sessionStorage.removeItem('first_login')

        const probe = await checkConnection({ silent: true })

        if (probe && probe.ok) {
          ElMessage.success('已保存并连接成功，请重新登录')
        } else {
          ElMessage.warning('已保存，但当前无法连接该服务器，请检查地址或网络')
        }

        router.push('/login').catch(() => {})
      } finally {
        saving.value = false
      }
    }

    const handleReset = async () => {
      try {
        await ElMessageBox.confirm(
          '将清除本机保存的服务器地址，回落到构建时配置或内置默认值。',
          '恢复默认地址',
          { type: 'warning', confirmButtonText: '恢复', cancelButtonText: '取消' }
        )
      } catch (error) {
        return
      }

      resetApiBaseUrl()
      syncFromStore()
      await checkConnection({ silent: true })
      ElMessage.success('已恢复默认地址')
    }

    const goLogin = () => {
      router.push('/login').catch(() => {})
    }

    return {
      inputUrl,
      testing,
      saving,
      inputError,
      localOverrideAllowed,
      hasOverride,
      isDesktopMode,
      isDevMode,
      buildTimeApiBaseUrl,
      currentApiBaseUrl,
      currentSourceLabel,
      healthUrl,
      healthPayload,
      normalizedPreview,
      statusTagType,
      statusLabel,
      statusMessage,
      latencyText,
      formatHealth,
      handleTest,
      handleSave,
      handleReset,
      goLogin
    }
  }
}
</script>

<style scoped>
.server-settings {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  min-height: 100vh;
  padding: 48px 24px;
  background: linear-gradient(135deg, #f0f2f5 0%, #e6f7ff 100%);
}

.settings-card {
  width: 100%;
  max-width: 720px;
  padding: 36px 40px 28px;
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
}

.settings-header {
  display: flex;
  gap: 16px;
  align-items: center;
  margin-bottom: 28px;
}

.header-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  color: #fff;
  background: linear-gradient(135deg, #1890ff 0%, #36cfc9 100%);
  border-radius: 14px;
}

.header-text h1 {
  margin: 0 0 4px;
  font-size: 22px;
  font-weight: 600;
  color: #1a1a1a;
}

.header-text p {
  margin: 0;
  font-size: 13px;
  color: #8c8c8c;
}

.status-panel {
  padding: 18px 20px;
  margin-bottom: 24px;
  background: #f5f7fa;
  border-radius: 12px;
}

.status-main {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 14px;
}

.status-latency {
  font-size: 13px;
  color: #8c8c8c;
}

.status-detail {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-row {
  display: flex;
  gap: 12px;
  font-size: 13px;
  line-height: 1.7;
}

.detail-label {
  flex: 0 0 88px;
  color: #8c8c8c;
}

.detail-value {
  flex: 1;
  color: #303133;
  word-break: break-all;
}

.mode-alert {
  margin-bottom: 20px;
}

.form-section {
  margin-bottom: 20px;
}

.section-title {
  margin-bottom: 10px;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.field-hint {
  margin-top: 8px;
  font-size: 12px;
  line-height: 1.7;
  color: #8c8c8c;
}

.field-hint code {
  padding: 1px 6px;
  font-size: 12px;
  color: #1890ff;
  background: #f0f7ff;
  border-radius: 4px;
}

.input-alert {
  margin-top: 12px;
}

.action-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 20px;
}

.diagnostics {
  margin-top: 8px;
  border-top: 1px solid #f0f0f0;
}

.footer-row {
  margin-top: 12px;
  text-align: center;
}
</style>
