<!-- AI智能助手 -->
<template>
  <div class="ai-assistant-page">
    <div class="page-header">
      <div class="header-left">
        <h2 class="header-title">
          <el-icon class="header-icon"><ChatDotRound /></el-icon>
          AI智能助手
        </h2>
      </div>
      <div class="header-right">
        <el-switch
          v-model="agentMode"
          active-text="Agent模式"
          inactive-text="普通模式"
          class="mode-switch"
        />
      </div>
    </div>
  </div>
    <div class="ai-container">

      <div class="chat-area" ref="chatAreaRef">
        <div v-if="messages.length === 0" class="welcome-section">
          <div class="welcome-icon">
            <el-icon :size="64"><ChatDotRound /></el-icon>
          </div>
          <h3>您好！我是实训室AI助手</h3>
          <p v-if="agentMode">我可以帮您查询、添加、修改数据，操作前会请求您的授权确认</p>
          <p v-else>您可以问我关于设备、实训室、课表等问题</p>
          
          <div class="quick-questions">
            <h4>{{ agentMode ? '试试这些操作' : '试试这些问题' }}</h4>
            <div class="question-tags">
              <el-tag 
                v-for="(example, index) in currentExamples" 
                :key="index"
                class="question-tag"
                @click="askQuestion(example.question)"
              >
                {{ example.question }}
              </el-tag>
            </div>
          </div>
        </div>
        <div v-for="(msg, index) in messages" :key="index" class="message-wrapper" :class="msg.role">
          <div class="message-avatar">
            <el-avatar v-if="msg.role === 'user'" :size="32" class="user-avatar">
              {{ userInitial }}
            </el-avatar>
            <el-avatar v-else :size="32" class="ai-avatar">
              <el-icon><ChatDotRound /></el-icon>
            </el-avatar>
          </div>
          <div class="message-content">
            <div class="message-text" v-html="formatMessage(msg.content)"></div>
            
            <div v-if="msg.missing_fields && msg.missing_fields.length > 0" class="missing-fields-section">
              <div class="missing-title">📝 请补充以下信息：</div>
              <div v-for="(field, fIdx) in msg.missing_fields" :key="fIdx" class="missing-field-item">
                <span class="field-name">{{ field.label }}:</span>
                <div v-if="field.options && field.options.length > 0" class="field-options">
                  <el-tag 
                    v-for="(opt, oIdx) in field.options" 
                    :key="oIdx"
                    class="option-tag"
                    @click="selectOption(field.field, opt)"
                  >
                    {{ field.options_desc ? field.options_desc[oIdx] : (opt.name || opt) }}
                  </el-tag>
                </div>
                <span v-else class="field-hint">请输入{{ field.label }}</span>
              </div>
            </div>
            
            <div v-if="msg.params && Object.keys(msg.params).length > 0 && !msg.requires_more_info" class="message-params">
              <div class="params-title">📋 参数预览</div>
              <div class="params-list">
                <div v-for="(value, key) in msg.params" :key="key" class="param-item">
                  <span class="param-label">{{ getFieldLabel(msg.target_entity, key) }}:</span>
                  <span class="param-value">{{ value || '(未填写)' }}</span>
                </div>
              </div>
            </div>
            
            <div v-if="msg.data && msg.data.length > 0" class="message-data">
              <el-table 
                :data="msg.data.slice(0, 10)" 
                size="small" 
                stripe
                max-height="300"
              >
                <el-table-column 
                  v-for="(value, key) in msg.data[0]" 
                  :key="key"
                  :prop="key"
                  :label="formatColumnLabel(key)"
                  min-width="100"
                />
              </el-table>
              <div v-if="msg.data.length > 10" class="data-more">
                仅显示前10条，共{{ msg.data.length }}条记录
              </div>
            </div>
            
            <div v-if="msg.steps && msg.steps.length > 0" class="message-steps">
              <div class="steps-title">执行过程</div>
              <div class="steps-list">
                <div 
                  v-for="(step, sIndex) in msg.steps" 
                  :key="sIndex" 
                  class="step-item"
                  :class="step.status"
                >
                  <el-icon v-if="step.status === 'success'" class="step-icon"><CircleCheck /></el-icon>
                  <el-icon v-else-if="step.status === 'error'" class="step-icon"><CircleClose /></el-icon>
                  <el-icon v-else class="step-icon loading"><Loading /></el-icon>
                  <span class="step-name">{{ step.step }}</span>
                  <span class="step-message">{{ step.message }}</span>
                </div>
              </div>
            </div>
            
            <div v-if="msg.sql" class="message-sql">
              <el-collapse>
                <el-collapse-item title="查看SQL语句" name="sql">
                  <pre><code>{{ msg.sql }}</code></pre>
                </el-collapse-item>
              </el-collapse>
            </div>
            
            <div v-if="msg.requires_auth && msg.auth_token" class="auth-actions">
              <div class="auth-warning">
                <el-icon><Warning /></el-icon>
                <span>此操作需要您的授权确认。</span>
              </div>
              <div class="auth-buttons">
                <el-button 
                  type="primary" 
                  @click="confirmExecute(msg.auth_token, index)"
                  :loading="msg.executing"
                >
                  <el-icon><Check /></el-icon>
                  确认执行
                </el-button>
                <el-button 
                  @click="cancelExecute(msg.auth_token, index)"
                >
                  <el-icon><Close /></el-icon>
                  取消
                </el-button>
              </div>
            </div>
            
            <div class="message-meta">
              <span class="meta-time">{{ msg.time }}</span>
              <span v-if="msg.queryTime" class="meta-duration">{{ msg.queryTime.toFixed(2) }}s</span>
              <span v-if="msg.intent_type" class="meta-intent">{{ getIntentLabel(msg.intent_type) }}</span>
            </div>
          </div>
        </div>

        <div v-if="isLoading" class="message-wrapper assistant loading">
          <div class="message-avatar">
            <el-avatar :size="32" class="ai-avatar">
              <el-icon class="loading-icon"><Loading /></el-icon>
            </el-avatar>
          </div>
          <div class="message-content">
            <div class="typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>
      </div>

      <div class="input-area">
        <el-input
          v-model="inputQuestion"
          :placeholder="agentMode ? '输入操作指令，如：帮我添加一个实训室...' : '输入您的问题，如：有多少台电脑设备？'"
          class="question-input"
          size="large"
          @keyup.enter="handleSubmit"
          :disabled="isLoading"
        >
          <template #prefix>
            <el-icon><ChatLineRound /></el-icon>
          </template>
        </el-input>
        <el-button 
          type="primary" 
          class="send-btn"
          @click="handleSubmit"
          :loading="isLoading"
          :disabled="!inputQuestion.trim()"
        >
          <el-icon><Position /></el-icon>
          发送
        </el-button>
      </div>
    </div>

    <div class="history-panel" v-if="showHistory && historyList.length > 0">
      <div class="history-header">
        <h4>历史记录</h4>
        <el-button text size="small" @click="clearHistory">清空</el-button>
      </div>
      <div class="history-list">
        <div 
          v-for="item in historyList" 
          :key="item.id" 
          class="history-item"
          @click="askQuestion(item.question)"
        >
          <el-icon><ChatLineRound /></el-icon>
          <span class="history-question">{{ item.question }}</span>
        </div>
      </div>
    </div>
  
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  ChatDotRound, ChatLineRound, Position, Loading,
  CircleCheck, CircleClose, Warning, Check, Close
} from '@element-plus/icons-vue'
import api from '@/core/api/client'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const inputQuestion = ref('')
const messages = ref([])
const isLoading = ref(false)
const chatAreaRef = ref(null)
const showHistory = ref(true)
const historyList = ref([])
const agentMode = ref(true)

const queryExamples = ref([
  { question: '添加实训室，名称是物联网实验室，门牌号是208', category: 'add' },
  { question: '添加用户，用户名zhangsan，姓名张三', category: 'add' },
  { question: '查询实训室列表', category: 'query' },
  { question: '有多少实训室', category: 'query' },
])

const agentExamples = ref([
  { question: '帮我添加一个实训室，名称是物联网实验室，门牌号是208', category: 'add' },
  { question: '添加一条使用记录，实训室是205，日期是今天', category: 'add' },
  { question: '205实训室的工位数改为0', category: 'update' },
  { question: '修改我的手机号为13800138000', category: 'update' },
  { question: '有多少台电脑设备', category: 'query' },
])

const currentExamples = computed(() => {
  return agentMode.value ? agentExamples.value : queryExamples.value
})

const userInitial = computed(() => {
  const name = userStore.user?.nickname || userStore.user?.username || 'U'
  return name.charAt(0).toUpperCase()
})

const scrollToBottom = () => {
  nextTick(() => {
    if (chatAreaRef.value) {
      chatAreaRef.value.scrollTop = chatAreaRef.value.scrollHeight
    }
  })
}

const currentSessionId = ref(null)

const handleSubmit = async () => {
  const question = inputQuestion.value.trim()
  if (!question || isLoading.value) return
  
  messages.value.push({
    role: 'user',
    content: question,
    time: formatTime(new Date())
  })
  
  inputQuestion.value = ''
  isLoading.value = true
  scrollToBottom()
  
  try {
    if (agentMode.value) {
      await handleAgentRequest(question)
    } else {
      await handleQueryRequest(question)
    }
  } catch (error) {
    messages.value.push({
      role: 'assistant',
      content: '抱歉，AI服务暂时不可用，请稍后再试。',
      time: formatTime(new Date())
    })
  } finally {
    isLoading.value = false
    scrollToBottom()
    loadHistory()
  }
}

const handleQueryRequest = async (question) => {
  const response = await api.post('/ai/local/process/', { question })
  
  if (response.intent_type === 'delete') {
    currentSessionId.value = null
    messages.value.push({
      role: 'assistant',
      content: response.message,
      intent_type: response.intent_type,
      time: formatTime(new Date())
    })
    return
  }
  
  if (response.requires_more_info) {
    currentSessionId.value = response.session_id
    messages.value.push({
      role: 'assistant',
      content: response.message,
      intent_type: response.intent_type,
      target_entity: response.target_entity,
      params: response.params,
      requires_more_info: true,
      missing_fields: response.missing_fields,
      field_options: response.field_options,
      session_id: response.session_id,
      time: formatTime(new Date())
    })
  } else if (response.requires_auth) {
    currentSessionId.value = null
    messages.value.push({
      role: 'assistant',
      content: response.message,
      intent_type: response.intent_type,
      target_entity: response.target_entity,
      params: response.params,
      requires_auth: true,
      auth_token: response.auth_token,
      entity_fields: response.entity_fields,
      executing: false,
      time: formatTime(new Date())
    })
  } else if (response.intent_type === 'query') {
    currentSessionId.value = null
    messages.value.push({
      role: 'assistant',
      content: response.message,
      data: response.data,
      steps: response.steps,
      intent_type: response.intent_type,
      queryTime: response.query_time,
      time: formatTime(new Date())
    })
  } else {
    currentSessionId.value = null
    messages.value.push({
      role: 'assistant',
      content: response.message || '操作完成',
      intent_type: response.intent_type,
      time: formatTime(new Date())
    })
  }
}

const handleAgentRequest = async (question) => {
  const requestData = { question }
  if (currentSessionId.value) {
    requestData.session_id = currentSessionId.value
  }
  
  const response = await api.post('/ai/chat/', requestData)
  
  if (response.intent_type === 'delete') {
    currentSessionId.value = null
    messages.value.push({
      role: 'assistant',
      content: response.message,
      intent_type: response.intent_type,
      time: formatTime(new Date())
    })
    return
  }
  
  if (response.requires_more_info) {
    currentSessionId.value = response.session_id
    messages.value.push({
      role: 'assistant',
      content: response.message,
      intent_type: response.intent_type,
      target_entity: response.target_entity,
      params: response.params,
      requires_more_info: true,
      missing_fields: response.missing_fields,
      field_options: response.field_options,
      session_id: response.session_id,
      time: formatTime(new Date())
    })
  } else if (response.requires_auth) {
    currentSessionId.value = null
    messages.value.push({
      role: 'assistant',
      content: response.message,
      intent_type: response.intent_type,
      target_entity: response.target_entity,
      params: response.params,
      requires_auth: true,
      auth_token: response.auth_token,
      entity_fields: response.entity_fields,
      executing: false,
      time: formatTime(new Date())
    })
  } else if (response.intent_type === 'query') {
    currentSessionId.value = null
    messages.value.push({
      role: 'assistant',
      content: response.message,
      data: response.data,
      sql: response.sql,
      steps: response.steps,
      intent_type: response.intent_type,
      queryTime: response.query_time,
      time: formatTime(new Date())
    })
  } else {
    currentSessionId.value = null
    messages.value.push({
      role: 'assistant',
      content: response.message || '操作完成',
      intent_type: response.intent_type,
      time: formatTime(new Date())
    })
  }
}

const confirmExecute = async (authToken, msgIndex) => {
  const msg = messages.value[msgIndex]
  if (!msg || msg.executing) return
  
  msg.executing = true
  msg.content = '⏳ 正在执行操作...'
  
  const endpoint = agentMode.value ? '/ai/execute/' : '/ai/local/execute/'
  
  try {
    const response = await api.post(endpoint, { auth_token: authToken })
    
    msg.content = response.success ? '✅ 操作完成' : '❌ 操作失败'
    msg.steps = response.steps || []
    msg.data = response.data
    msg.error = response.error
    msg.requires_auth = false
    msg.auth_token = null
    
    if (!response.success && response.message) {
      ElMessage.error(response.message)
    }
  } catch (error) {
    msg.content = '❌ 执行失败: ' + (error.message || '未知错误')
    msg.steps = [
      { step: '执行操作', status: 'error', message: error.message || '网络错误' }
    ]
    msg.requires_auth = false
    msg.auth_token = null
  } finally {
    msg.executing = false
    scrollToBottom()
  }
}

const cancelExecute = async (authToken, msgIndex) => {
  const msg = messages.value[msgIndex]
  
  const endpoint = agentMode.value ? '/ai/cancel/' : '/ai/local/cancel/'
  
  try {
    await api.post(endpoint, { auth_token: authToken })
  } catch (error) {
  }
  
  msg.content = '❌ 操作已取消'
  msg.requires_auth = false
  msg.auth_token = null
  currentSessionId.value = null
}

const selectOption = (fieldName, value) => {
  if (typeof value === 'object' && value !== null) {
    inputQuestion.value = `${fieldName}是${value.name || value.id}`
  } else {
    inputQuestion.value = `${fieldName}是${value}`
  }
  handleSubmit()
}

const askQuestion = (question) => {
  inputQuestion.value = question
  handleSubmit()
}

const loadHistory = async () => {
  try {
    const endpoint = '/ai/history/'
    const response = await api.get(endpoint, { limit: 10 })
    if (response.success) {
      historyList.value = response.data.map(item => ({
        id: item.id,
        question: item.question || `(${item.operation_type_display || item.operation_type}) ${item.target_entity}`
      }))
    }
  } catch (error) {
  }
}

const clearHistory = () => {
  historyList.value = []
}

const formatTime = (date) => {
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const formatMessage = (content) => {
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

const formatColumnLabel = (key) => {
  const labelMap = {
    'count': '数量',
    'device_name': '设备名称',
    'device_code': '设备编号',
    'device_type': '设备类型',
    'status': '状态',
    'sxsname': '实训室名称',
    'sxsno': '门牌号',
    'sxsnum': '工位数',
    'classname': '课程名称',
    'classweekday': '星期',
    'classjc': '节次',
    'teacher': '教师',
    'nikename': '姓名',
    'username': '用户名',
    'departname': '部门',
    'termname': '学期',
  }
  return labelMap[key] || key
}

const getIntentLabel = (intentType) => {
  const labels = {
    'query': '查询',
    'add': '添加',
    'update': '修改',
    'delete': '删除',
  }
  return labels[intentType] || intentType
}

const getFieldLabel = (entity, field) => {
  const fieldLabels = {
    'sxs': {
      'sxsname': '实训室名称',
      'sxsno': '门牌号',
      'sxsnum': '工位数',
      'sxsdepart_id': '所属部门',
      'sxsadmin_id': '管理员',
      'sxsmemo': '备注',
    },
    'sxsrecord': {
      'sxsname_id': '实训室',
      'sxsdate': '使用日期',
      'sxsstart': '开始节次',
      'sxsclasshour': '学时',
      'sxsclass': '上课班级',
      'sxsnum': '使用人数',
      'sxscontent': '实训内容',
      'sxsmemo': '备注',
    },
    'sxsclass': {
      'sxsname_id': '实训室',
      'classname': '课程名称',
      'classweekday': '星期数',
      'classjc': '节次',
      'classweek': '周次',
      'classnum': '课程人数',
      'classteacher_id': '教师',
      'class_group': '上课班级',
    },
  }
  return fieldLabels[entity]?.[field] || field
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.ai-assistant-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #fff;
  border-bottom: 1px solid #ebeef5;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.header-icon {
  color: #409eff;
}

.mode-switch {
  --el-switch-on-color: #67c23a;
}

.ai-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  max-width: 900px;
  width: 100%;
  margin: 0 auto;
  padding: 20px;
}

.chat-area {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #fff;
  border-radius: 12px;
  margin-bottom: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.welcome-section {
  text-align: center;
  padding: 40px 20px;
}

.welcome-icon {
  color: #409eff;
  margin-bottom: 20px;
}

.welcome-section h3 {
  font-size: 20px;
  color: #303133;
  margin-bottom: 8px;
}

.welcome-section p {
  color: #909399;
  margin-bottom: 24px;
}

.quick-questions h4 {
  font-size: 14px;
  color: #606266;
  margin-bottom: 12px;
}

.question-tags {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
}

.question-tag {
  cursor: pointer;
  transition: all 0.3s;
}

.question-tag:hover {
  background: #409eff;
  color: #fff;
}

.message-wrapper {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.message-wrapper.user {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.user-avatar {
  background: #409eff;
  color: #fff;
}

.ai-avatar {
  background: #f0f9ff;
  color: #409eff;
}

.message-content {
  max-width: 70%;
}

.message-wrapper.user .message-content {
  align-items: flex-end;
}

.message-text {
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.6;
  word-break: break-word;
}

.message-wrapper.user .message-text {
  background: #409eff;
  color: #fff;
  border-bottom-right-radius: 4px;
}

.message-wrapper.assistant .message-text {
  background: #f5f7fa;
  color: #303133;
  border-bottom-left-radius: 4px;
}

.message-params {
  margin-top: 12px;
  background: #fafafa;
  border-radius: 8px;
  padding: 12px;
}

.missing-fields-section {
  margin-top: 12px;
  padding: 12px;
  background: #f0f9ff;
  border: 1px solid #b3d8ff;
  border-radius: 8px;
}

.missing-title {
  font-size: 13px;
  font-weight: 500;
  color: #409eff;
  margin-bottom: 10px;
}

.missing-field-item {
  margin-bottom: 10px;
}

.missing-field-item:last-child {
  margin-bottom: 0;
}

.field-name {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
  display: block;
  margin-bottom: 6px;
}

.field-options {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.option-tag {
  cursor: pointer;
  transition: all 0.2s;
}

.option-tag:hover {
  background: #409eff;
  color: #fff;
}

.field-hint {
  font-size: 12px;
  color: #909399;
}

.params-title {
  font-size: 13px;
  font-weight: 500;
  color: #606266;
  margin-bottom: 8px;
}

.params-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.param-item {
  display: flex;
  gap: 8px;
  font-size: 13px;
}

.param-label {
  color: #909399;
  min-width: 80px;
}

.param-value {
  color: #303133;
}

.message-data {
  margin-top: 12px;
  border-radius: 8px;
  overflow: hidden;
}

.data-more {
  padding: 8px;
  text-align: center;
  font-size: 12px;
  color: #909399;
  background: #fafafa;
}

.message-steps {
  margin-top: 12px;
  background: #fafafa;
  border-radius: 8px;
  padding: 12px;
}

.steps-title {
  font-size: 13px;
  font-weight: 500;
  color: #606266;
  margin-bottom: 8px;
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.step-item.success .step-icon {
  color: #67c23a;
}

.step-item.error .step-icon {
  color: #f56c6c;
}

.step-item.pending .step-icon {
  color: #909399;
}

.step-icon.loading {
  animation: spin 1s linear infinite;
}

.step-name {
  font-weight: 500;
  color: #303133;
}

.step-message {
  color: #909399;
}

.message-sql {
  margin-top: 8px;
}

.message-sql pre {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 12px;
  border-radius: 6px;
  font-size: 12px;
  overflow-x: auto;
}

.auth-actions {
  margin-top: 12px;
  background: #fdf6ec;
  border: 1px solid #e6a23c;
  border-radius: 8px;
  padding: 12px;
}

.auth-warning {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #e6a23c;
  font-size: 13px;
  margin-bottom: 12px;
}

.auth-buttons {
  display: flex;
  gap: 12px;
}

.message-meta {
  display: flex;
  gap: 12px;
  margin-top: 6px;
  font-size: 12px;
  color: #c0c4cc;
}

.meta-intent {
  background: #f0f9ff;
  color: #409eff;
  padding: 2px 8px;
  border-radius: 4px;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 12px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #409eff;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.6);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.loading-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.input-area {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.question-input {
  flex: 1;
}

.send-btn {
  padding: 0 24px;
}

.history-panel {
  position: fixed;
  right: 20px;
  top: 100px;
  width: 280px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #ebeef5;
}

.history-header h4 {
  font-size: 14px;
  color: #303133;
}

.history-list {
  max-height: 300px;
  overflow-y: auto;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  cursor: pointer;
  transition: background 0.3s;
}

.history-item:hover {
  background: #f5f7fa;
}

.history-question {
  font-size: 13px;
  color: #606266;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 768px) {
  .history-panel {
    display: none;
  }
  
  .message-content {
    max-width: 85%;
  }
}
</style>
