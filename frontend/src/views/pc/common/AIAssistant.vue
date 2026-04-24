<!-- AI智能助手 - 简洁版 -->
<template>
  <div class="ai-page">
    <!-- 头部 -->
    <div class="header">
      <h2>🤖 AI智能助手</h2>
      <p>支持：查询数据、添加用户/实训室、修改信息</p>
    </div>

    <!-- 聊天区域 -->
    <div class="chat-area" ref="chatRef">
      <!-- 欢迎消息 -->
      <div v-if="messages.length === 0" class="welcome">
        <p>您好！我是实训室AI助手，可以帮您：</p>
        <div class="examples">
          <el-tag @click="ask('查询所有实训室')">查询所有实训室</el-tag>
          <el-tag @click="ask('查询所有用户')">查询所有用户</el-tag>
          <el-tag @click="ask('添加用户')">添加用户</el-tag>
          <el-tag @click="ask('添加实训室')">添加实训室</el-tag>
        </div>
      </div>

      <!-- 消息列表 -->
      <div v-for="(msg, i) in messages" :key="i" class="msg" :class="msg.role">
        <div class="bubble">
          <div v-html="formatMsg(msg.content)"></div>
          
          <!-- 数据表格 -->
          <el-table v-if="msg.data?.length" :data="msg.data" size="small" stripe>
            <el-table-column v-for="(v, k) in msg.data[0]" :key="k" :prop="k" :label="k" />
          </el-table>

          <!-- 确认按钮 -->
          <div v-if="msg.requires_confirm" class="actions">
            <el-button type="primary" @click="confirm(msg.token)">确认执行</el-button>
            <el-button @click="cancel(msg.token)">取消</el-button>
          </div>
        </div>
      </div>

      <!-- 加载中 -->
      <div v-if="loading" class="msg assistant">
        <div class="bubble">思考中...</div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="input-area">
      <el-input
        v-model="input"
        placeholder="输入问题或指令..."
        @keyup.enter="send"
        :disabled="loading"
      />
      <el-button type="primary" @click="send" :loading="loading">发送</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/core/api/client'

const input = ref('')
const messages = ref([])
const loading = ref(false)
const chatRef = ref(null)
const sessionId = ref(null)

const ask = (text) => {
  input.value = text
  send()
}

const send = async () => {
  const text = input.value.trim()
  if (!text || loading.value) return

  messages.value.push({ role: 'user', content: text })
  input.value = ''
  loading.value = true

  try {
    const data = { question: text }
    if (sessionId.value) data.session_id = sessionId.value

    const res = await api.post('/ai/process/', data)
    
    // 从 res.data 中获取实际的AI响应
    const aiRes = res.data || res

    // 处理响应
    if (aiRes.requires_more) {
      sessionId.value = aiRes.session_id
      messages.value.push({
        role: 'assistant',
        content: aiRes.message,
        missing: aiRes.missing_fields,
      })
    } else if (aiRes.requires_confirm) {
      sessionId.value = null
      messages.value.push({
        role: 'assistant',
        content: aiRes.message,
        requires_confirm: true,
        token: aiRes.token,
      })
    } else {
      sessionId.value = null
      messages.value.push({
        role: 'assistant',
        content: aiRes.message,
        data: aiRes.data,
      })
    }

    scrollToBottom()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '请求失败')
  } finally {
    loading.value = false
  }
}

const confirm = async (token) => {
  loading.value = true
  try {
    const res = await api.post('/ai/execute/', { token })
    const aiRes = res.data || res
    messages.value.push({
      role: 'assistant',
      content: aiRes.message,
    })
    scrollToBottom()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '执行失败')
  } finally {
    loading.value = false
  }
}

const cancel = async (token) => {
  try {
    await api.post('/ai/cancel/', { token })
    messages.value.push({ role: 'assistant', content: '操作已取消' })
  } catch (e) {
    ElMessage.error('取消失败')
  }
}

const formatMsg = (text) => {
  return text?.replace(/\n/g, '<br>') || ''
}

const scrollToBottom = () => {
  nextTick(() => {
    if (chatRef.value) {
      chatRef.value.scrollTop = chatRef.value.scrollHeight
    }
  })
}
</script>

<style scoped>
.ai-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.header {
  padding: 20px;
  background: #fff;
  border-bottom: 1px solid #ebeef5;
}

.header h2 {
  margin: 0 0 8px 0;
  font-size: 20px;
}

.header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.chat-area {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.welcome {
  text-align: center;
  padding: 40px 20px;
  color: #606266;
}

.examples {
  margin-top: 20px;
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
}

.examples .el-tag {
  cursor: pointer;
}

.msg {
  margin-bottom: 16px;
  display: flex;
}

.msg.user {
  justify-content: flex-end;
}

.msg.assistant {
  justify-content: flex-start;
}

.bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.msg.user .bubble {
  background: #409eff;
  color: #fff;
}

.el-table {
  margin-top: 12px;
}

.actions {
  margin-top: 12px;
  display: flex;
  gap: 10px;
}

.input-area {
  padding: 16px 20px;
  background: #fff;
  border-top: 1px solid #ebeef5;
  display: flex;
  gap: 10px;
}

.input-area .el-input {
  flex: 1;
}
</style>
