<template>
  <div v-if="isLoggedIn" class="ai-float-ball" @click="handleBallClick" :class="{ 'has-new': hasNewMessage }">
    <el-badge :value="unreadCount" :hidden="unreadCount === 0" :max="9">
      <div class="ball-inner">
        <el-icon :size="24"><ChatDotRound /></el-icon>
      </div>
    </el-badge>
    
    <transition name="drawer">
      <div v-if="visible" class="ai-drawer" @click.stop>
        <div class="drawer-header">
          <div class="header-title">
            <el-icon><ChatDotRound /></el-icon>
            <span>AI智能助手</span>
          </div>
          <div class="header-actions">
            <el-switch
              v-model="agentMode"
              size="small"
              active-text="Agent"
              inactive-text="本地"
              class="mode-switch"
            />
            <el-button class="close-btn" @click="closeDrawer" circle size="small">
              <el-icon><Close /></el-icon>
            </el-button>
          </div>
        </div>
        
        <div class="drawer-body" ref="chatBodyRef">
          <div v-if="messages.length === 0" class="welcome-area">
            <div class="welcome-icon">
              <el-icon :size="48"><ChatDotRound /></el-icon>
            </div>
            <h4>您好！我是AI助手</h4>
            <p v-if="agentMode">我可以帮您查询、添加、修改数据</p>
            <p v-else>可以问我关于设备、实训室、课表等问题</p>
            <div class="quick-tags">
              <el-tag 
                v-for="(ex, i) in currentExamples" 
                :key="i" 
                size="small"
                class="quick-tag"
                @click="askQuestion(ex.question)"
              >
                {{ ex.question }}
              </el-tag>
            </div>
          </div>
          
          <div v-for="(msg, idx) in messages" :key="idx" class="msg-item" :class="msg.role">
            <div class="msg-avatar">
              <el-avatar v-if="msg.role === 'user'" :size="28">
                {{ userInitial }}
              </el-avatar>
              <el-avatar v-else :size="28" class="ai-avatar">
                <el-icon><ChatDotRound /></el-icon>
              </el-avatar>
            </div>
            <div class="msg-content">
              <div class="msg-text" v-html="formatContent(msg.content)"></div>
              
              <div v-if="msg.missing_fields && msg.missing_fields.length > 0" class="missing-fields">
                <div v-for="(field, fi) in msg.missing_fields" :key="fi" class="missing-field">
                  <span class="field-label">{{ field.label }}:</span>
                  <div v-if="field.options && field.options.length > 0" class="field-options">
                    <el-tag 
                      v-for="(opt, oi) in field.options" 
                      :key="oi"
                      size="small"
                      class="option-tag"
                      @click="selectOption(field.field, opt)"
                    >
                      {{ field.options_desc ? field.options_desc[oi] : (opt.name || opt) }}
                    </el-tag>
                  </div>
                </div>
              </div>
              
              <div v-if="msg.params && Object.keys(msg.params).length > 0 && !msg.requires_more_info" class="msg-params">
                <div v-for="(value, key) in msg.params" :key="key" class="param-row">
                  <span class="param-label">{{ key }}:</span>
                  <span class="param-value">{{ value || '-' }}</span>
                </div>
              </div>
              
              <div v-if="msg.steps && msg.steps.length > 0" class="msg-steps">
                <div v-for="(step, si) in msg.steps" :key="si" class="step-row" :class="step.status">
                  <el-icon v-if="step.status === 'success'" class="step-icon"><CircleCheck /></el-icon>
                  <el-icon v-else-if="step.status === 'error'" class="step-icon"><CircleClose /></el-icon>
                  <el-icon v-else class="step-icon spin"><Loading /></el-icon>
                  <span>{{ step.step }}: {{ step.message }}</span>
                </div>
              </div>
              
              <div v-if="msg.data && msg.data.length > 0" class="msg-data">
                <el-table :data="msg.data.slice(0, 5)" size="small" max-height="150">
                  <el-table-column 
                    v-for="(v, k) in msg.data[0]" 
                    :key="k"
                    :prop="k"
                    :label="formatLabel(k)"
                    min-width="80"
                  />
                </el-table>
                <div v-if="msg.data.length > 5" class="more-tip">
                  共{{ msg.data.length }}条，仅显?�?
                </div>
              </div>
              <div v-if="msg.data && msg.data.length === 0" class="msg-empty">
                <el-empty description="暂无数据" :image-size="60" />
              </div>
              
              <div v-if="msg.requires_auth && msg.auth_token" class="auth-area">
                <div class="auth-tip">
                  <el-icon><Warning /></el-icon>
                  <span>需要授权确认执行</span>
                </div>
                <div class="auth-btns">
                  <el-button type="primary" size="small" @click="confirmExecute(msg.auth_token, idx)" :loading="msg.executing">
                    确认执行
                  </el-button>
                  <el-button size="small" @click="cancelExecute(msg.auth_token, idx)">
                    取消
                  </el-button>
                </div>
              </div>
            </div>
          </div>
          
          <div v-if="loading" class="msg-item assistant">
            <div class="msg-avatar">
              <el-avatar :size="28" class="ai-avatar">
                <el-icon class="spin"><Loading /></el-icon>
              </el-avatar>
            </div>
            <div class="msg-content">
              <div class="typing">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="drawer-footer">
          <el-input
            v-model="inputText"
            :placeholder="agentMode ? '输入操作指令...' : '输入问题...'"
            @keyup.enter="sendQuestion"
            :disabled="loading"
          >
            <template #suffix>
              <el-button type="primary" @click="sendQuestion" :loading="loading" circle size="small">
                <el-icon><Position /></el-icon>
              </el-button>
            </template>
          </el-input>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { ChatDotRound, Close, Position, Loading, CircleCheck, CircleClose, Warning } from '@element-plus/icons-vue'
import api from '@/core/api/client'
import { useUserStore } from '@/core/store/user'

const userStore = useUserStore()

const isLoggedIn = computed(() => !!userStore.user?.id)

const visible = ref(false)
const inputText = ref('')
const messages = ref([])
const loading = ref(false)
const chatBodyRef = ref(null)
const hasNewMessage = ref(false)
const unreadCount = ref(0)
const agentMode = ref(true)

const userInitial = computed(() => {
  const name = userStore.user?.nickname || userStore.user?.username || 'U'
  return name.charAt(0).toUpperCase()
})

const queryExamples = ref([
  { question: '添加实训室' },
  { question: '添加用户' },
  { question: '查询实训室' },
  { question: '有多少实训室' },
])

const agentExamples = ref([
  { question: '添加实训室' },
  { question: '添加使用记录' },
  { question: '有多少台电脑' },
])

const currentExamples = computed(() => {
  return agentMode.value ? agentExamples.value : queryExamples.value
})

const closeDrawer = () => {
  visible.value = false
}

const handleBallClick = (e) => {
  if (visible.value) {
    e.stopPropagation()
    closeDrawer()
  } else {
    visible.value = true
    unreadCount.value = 0
    hasNewMessage.value = false
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (chatBodyRef.value) {
      chatBodyRef.value.scrollTop = chatBodyRef.value.scrollHeight
    }
  })
}

const currentSessionId = ref(null)

const sendQuestion = async () => {
  const q = inputText.value.trim()
  if (!q || loading.value) return
  
  messages.value.push({
    role: 'user',
    content: q,
    time: new Date()
  })
  
  inputText.value = ''
  loading.value = true
  scrollToBottom()
  
  try {
    if (agentMode.value) {
      await handleAgentRequest(q)
    } else {
      await handleQueryRequest(q)
    }
  } catch (e) {
    messages.value.push({
      role: 'assistant',
      content: 'AI服务暂时不可用，请稍后再试',
      time: new Date()
    })
  } finally {
    loading.value = false
    scrollToBottom()
    
    if (!visible.value) {
      unreadCount.value++
      hasNewMessage.value = true
    }
  }
}

const handleQueryRequest = async (q) => {
  const requestData = { question: q }
  if (currentSessionId.value) {
    requestData.session_id = currentSessionId.value
  }
  
  const res = await api.post('/ai/local/process/', requestData)
  
  if (res.intent_type === 'delete') {
    currentSessionId.value = null
    messages.value.push({
      role: 'assistant',
      content: res.message,
      intent_type: res.intent_type,
      time: new Date()
    })
    return
  }
  
  if (res.requires_more_info) {
    currentSessionId.value = res.session_id
    let content = res.message
    if (res.missing_fields && res.missing_fields.length > 0) {
      content += '\n\n'
      res.missing_fields.forEach((field, idx) => {
        if (field.options && field.options.length > 0) {
          const options = field.options_desc || field.options
          content += `${idx + 1}. ${field.label}: ${options.join(' / ')}\n`
        } else {
          content += `${idx + 1}. ${field.label}\n`
        }
      })
    }
    
    messages.value.push({
      role: 'assistant',
      content: content,
      intent_type: res.intent_type,
      target_entity: res.target_entity,
      params: res.params,
      requires_more_info: true,
      missing_fields: res.missing_fields,
      field_options: res.field_options,
      session_id: res.session_id,
      time: new Date()
    })
  } else if (res.requires_auth) {
    currentSessionId.value = null
    messages.value.push({
      role: 'assistant',
      content: res.message,
      intent_type: res.intent_type,
      target_entity: res.target_entity,
      params: res.params,
      requires_auth: true,
      auth_token: res.auth_token,
      executing: false,
      time: new Date()
    })
  } else if (res.intent_type === 'query') {
    currentSessionId.value = null
    messages.value.push({
      role: 'assistant',
      content: res.message,
      data: res.data,
      steps: res.steps,
      intent_type: res.intent_type,
      time: new Date()
    })
  } else {
    currentSessionId.value = null
    messages.value.push({
      role: 'assistant',
      content: res.message || '操作完成',
      intent_type: res.intent_type,
      time: new Date()
    })
  }
}

const handleAgentRequest = async (q) => {
  const requestData = { question: q }
  if (currentSessionId.value) {
    requestData.session_id = currentSessionId.value
  }
  
  const res = await api.post('/ai/chat/', requestData)
  
  if (res.intent_type === 'delete') {
    messages.value.push({
      role: 'assistant',
      content: res.message,
      intent_type: res.intent_type,
      time: new Date()
    })
    currentSessionId.value = null
    return
  }
  
  if (res.requires_more_info) {
    currentSessionId.value = res.session_id
    
    let content = res.message
    if (res.missing_fields && res.missing_fields.length > 0) {
      content += '\n\n'
      res.missing_fields.forEach((field, idx) => {
        if (field.options && field.options.length > 0) {
          const options = field.options_desc || field.options
          content += `${idx + 1}. ${field.label}: ${options.join(' / ')}\n`
        } else {
          content += `${idx + 1}. ${field.label}\n`
        }
      })
    }
    
    messages.value.push({
      role: 'assistant',
      content: content,
      intent_type: res.intent_type,
      target_entity: res.target_entity,
      params: res.params,
      requires_more_info: true,
      missing_fields: res.missing_fields,
      field_options: res.field_options,
      session_id: res.session_id,
      time: new Date()
    })
  } else if (res.requires_auth) {
    currentSessionId.value = null
    messages.value.push({
      role: 'assistant',
      content: res.message,
      intent_type: res.intent_type,
      target_entity: res.target_entity,
      params: res.params,
      requires_auth: true,
      auth_token: res.auth_token,
      executing: false,
      time: new Date()
    })
  } else if (res.intent_type === 'query') {
    currentSessionId.value = null
    messages.value.push({
      role: 'assistant',
      content: res.message,
      data: res.data,
      steps: res.steps,
      intent_type: res.intent_type,
      time: new Date()
    })
  } else {
    currentSessionId.value = null
    messages.value.push({
      role: 'assistant',
      content: res.message || '操作完成',
      intent_type: res.intent_type,
      time: new Date()
    })
  }
}

const confirmExecute = async (token, idx) => {
  const msg = messages.value[idx]
  if (!msg || msg.executing) return
  
  msg.executing = true
  msg.content = '正在执行...'
  
  const endpoint = agentMode.value ? '/ai/execute/' : '/ai/local/execute/'
  
  try {
    const res = await api.post(endpoint, { auth_token: token })
    
    if (res.success) {
      msg.content = res.message || '操作完成'
      msg.steps = res.steps || []
      msg.data = res.data
    } else {
      msg.content = '操作失败' + (res.error || res.message || '未知错误')
      msg.steps = [{ step: '执行', status: 'error', message: res.error || res.message || '未知错误' }]
    }
    msg.requires_auth = false
    msg.auth_token = null
  } catch (e) {
    msg.content = '执行失败' + (e.message || '未知错误')
    msg.steps = [{ step: '执行', status: 'error', message: e.message || '网络错误' }]
    msg.requires_auth = false
    msg.auth_token = null
  } finally {
    msg.executing = false
    scrollToBottom()
  }
}

const cancelExecute = async (token, idx) => {
  const msg = messages.value[idx]
  
  const endpoint = agentMode.value ? '/ai/cancel/' : '/ai/local/cancel/'
  
  try {
    await api.post(endpoint, { auth_token: token })
  } catch (e) {
  }
  
  msg.content = '操作已取消'
  msg.requires_auth = false
  msg.auth_token = null
  currentSessionId.value = null
}

const selectOption = (fieldName, value) => {
  if (typeof value === 'object' && value !== null) {
    inputText.value = `${fieldName}${value.name || value.id}`
  } else {
    inputText.value = `${fieldName}${value}`
  }
  sendQuestion()
}

const askQuestion = (q) => {
  inputText.value = q
  sendQuestion()
}

const formatContent = (content) => {
  if (!content) return ''
  const escapeHtml = (text) => {
    const map = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;'
    }
    return text.replace(/[&<>"']/g, m => map[m])
  }
  return escapeHtml(content).replace(/\n/g, '<br>')
}

const formatLabel = (key) => {
  const map = {
    count: '数量', device_name: '设备', laboratory_name: '实训室',
    course_name: '课程', teacher: '教师', nickname: '姓名'
  }
  return map[key] || key
}
</script>

<style scoped>
.ai-float-ball {
  position: fixed;
  right: 24px;
  bottom: 80px;
  z-index: 1001;
}

.ball-inner {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #409eff, #67c23a);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.4);
  transition: all 0.3s;
}

.ball-inner:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 24px rgba(64, 158, 255, 0.5);
}

.has-new .ball-inner {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 4px 16px rgba(64, 158, 255, 0.4); }
  50% { box-shadow: 0 4px 24px rgba(64, 158, 255, 0.8); }
}

.ai-drawer {
  position: fixed;
  right: 24px;
  bottom: 150px;
  width: 380px;
  height: 520px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 1000;
}

.drawer-enter-active,
.drawer-leave-active {
  transition: all 0.3s ease;
}

.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: linear-gradient(135deg, #409eff, #67c23a);
  color: #fff;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.mode-switch {
  --el-switch-on-color: #fff;
  --el-switch-off-color: rgba(255,255,255,0.3);
}

.mode-switch :deep(.el-switch__label) {
  color: #fff !important;
  font-size: 11px;
}

.close-btn {
  background: rgba(255,255,255,0.2) !important;
  border: none !important;
  color: #fff !important;
}

.drawer-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #f8fafc;
}

.welcome-area {
  text-align: center;
  padding: 20px 0;
}

.welcome-icon {
  color: #409eff;
  margin-bottom: 12px;
}

.welcome-area h4 {
  margin: 0 0 4px;
  color: #303133;
}

.welcome-area p {
  font-size: 12px;
  color: #909399;
  margin: 0 0 16px;
}

.quick-tags {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 6px;
}

.quick-tag {
  cursor: pointer;
  transition: all 0.2s;
}

.quick-tag:hover {
  background: #409eff;
  color: #fff;
}

.msg-item {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}

.msg-item.user {
  flex-direction: row-reverse;
}

.msg-avatar {
  flex-shrink: 0;
}

.ai-avatar {
  background: #ecf5ff;
  color: #409eff;
}

.msg-content {
  max-width: 75%;
}

.msg-text {
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.5;
}

.msg-item.user .msg-text {
  background: #409eff;
  color: #fff;
  border-bottom-right-radius: 4px;
}

.msg-item.assistant .msg-text {
  background: #fff;
  color: #303133;
  border-bottom-left-radius: 4px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}

.msg-params {
  margin-top: 8px;
  padding: 8px;
  background: #fafafa;
  border-radius: 6px;
  font-size: 12px;
}

.missing-fields {
  margin-top: 10px;
  padding: 10px;
  background: #f0f9ff;
  border: 1px solid #b3d8ff;
  border-radius: 8px;
}

.missing-field {
  margin-bottom: 8px;
}

.missing-field:last-child {
  margin-bottom: 0;
}

.field-label {
  font-size: 12px;
  color: #606266;
  font-weight: 500;
  display: block;
  margin-bottom: 6px;
}

.field-options {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.option-tag {
  cursor: pointer;
  transition: all 0.2s;
}

.option-tag:hover {
  background: #409eff;
  color: #fff;
}

.param-row {
  display: flex;
  gap: 8px;
  margin-bottom: 4px;
}

.param-row:last-child {
  margin-bottom: 0;
}

.param-label {
  color: #909399;
  min-width: 60px;
}

.param-value {
  color: #303133;
}

.msg-steps {
  margin-top: 8px;
  padding: 8px;
  background: #fafafa;
  border-radius: 6px;
  font-size: 12px;
}

.step-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
}

.step-row:last-child {
  margin-bottom: 0;
}

.step-row.success .step-icon {
  color: #67c23a;
}

.step-row.error .step-icon {
  color: #f56c6c;
}

.step-row.pending .step-icon {
  color: #909399;
}

.auth-area {
  margin-top: 8px;
  padding: 10px;
  background: #fdf6ec;
  border: 1px solid #e6a23c;
  border-radius: 8px;
}

.auth-tip {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #e6a23c;
  font-size: 12px;
  margin-bottom: 8px;
}

.auth-btns {
  display: flex;
  gap: 8px;
}

.msg-data {
  margin-top: 8px;
  border-radius: 8px;
  overflow: hidden;
}

.more-tip {
  font-size: 11px;
  color: #909399;
  text-align: center;
  padding: 4px;
  background: #fafafa;
}

.typing {
  display: flex;
  gap: 4px;
  padding: 10px 14px;
  background: #fff;
  border-radius: 12px;
}

.typing span {
  width: 6px;
  height: 6px;
  background: #409eff;
  border-radius: 50%;
  animation: typing 1.2s infinite;
}

.typing span:nth-child(2) { animation-delay: 0.2s; }
.typing span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-4px); opacity: 1; }
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.drawer-footer {
  padding: 12px 16px;
  background: #fff;
  border-top: 1px solid #ebeef5;
}

.drawer-footer :deep(.el-input__wrapper) {
  padding-right: 8px;
}

.drawer-footer :deep(.el-input__suffix) {
  display: flex;
  align-items: center;
}
</style>
