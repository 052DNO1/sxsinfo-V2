<template>
  <div class="mobile-ai-assistant-page mobile-layout">
    <van-nav-bar
      :title="header || 'AI智能助手'"
      left-arrow
      @click-left="handleBack"
      class="mobile-nav-bar"
    >
      <template #left>
        <van-icon name="arrow-left" />
      </template>
    </van-nav-bar>

    <div class="mobile-ai-container" @click="handleContainerClick">
      <div class="mobile-chat-messages" ref="chatMessagesRef">
        <div class="mobile-message ai-message">
          <div class="mobile-message-avatar">
            <van-icon name="service-o" size="24px" color="#1989fa" />
          </div>
          <div class="mobile-message-content">
            <div class="mobile-message-text">
              您好！我是您的AI智能助手，可以通过自然语言帮您完成各种操作。<br /><br />
              <strong>我可以帮您：</strong><br />
              • <van-icon name="shop-o" size="14px" /> 查看和管理实训室（例如：查看全部实训室、查看实训室详情）<br />
              • <van-icon name="upload" size="14px" /> 导入课表（例如：我需要导入课表、批量导入课表）<br />
              • <van-icon name="records" size="14px" /> 查看使用记录（例如：查看实训室使用记录）<br />
              • <van-icon name="setting-o" size="14px" /> 查看维护记录（例如：查看实训室维护记录）<br />
              • <van-icon name="user-o" size="14px" /> 用户管理（例如：分配权限、查看用户信息）<br />
              • <van-icon name="chart-trending-o" size="14px" /> 查看统计信息（例如：查看综合统计）<br />
              • <van-icon name="search" size="14px" /> 全局搜索（例如：搜索实训室、用户、课表）<br /><br />
              请输入"帮助"查看详细说明，或直接告诉我您的需求！
            </div>
            <div class="mobile-message-time">{{ getCurrentTime() }}</div>
          </div>
        </div>
        <div v-for="(msg, index) in messages" :key="index" class="mobile-message" :class="msg.type">
          <div class="mobile-message-avatar">
            <van-icon 
              :name="msg.type === 'user-message' ? 'user-o' : 'service-o'" 
              size="24px" 
              :color="msg.type === 'user-message' ? '#07c160' : '#1989fa'" 
            />
          </div>
          <div class="mobile-message-content">
            <div class="mobile-message-text" v-html="processMessageButtons(msg.text)"></div>
            <div class="mobile-message-time">{{ msg.time }}</div>
          </div>
        </div>
        <div v-if="isProcessing" class="mobile-message ai-message">
          <div class="mobile-message-avatar">
            <van-icon name="service-o" size="24px" color="#1989fa" />
          </div>
          <div class="mobile-message-content">
            <div class="mobile-message-text">正在思考中...</div>
          </div>
        </div>
      </div>

      <div class="mobile-chat-input-container">
        <div class="mobile-chat-input-wrapper">
          <van-field
            v-model="inputMessage"
            type="textarea"
            rows="2"
            placeholder="输入您的消息..."
            autocomplete="off"
            :disabled="isProcessing"
            @keypress="handleKeyPress"
            class="mobile-chat-input"
          />
          <van-button
            type="primary"
            size="small"
            @click="sendMessage"
            :disabled="isProcessing || !inputMessage.trim()"
            class="mobile-send-btn"
          >
            发送
          </van-button>
        </div>
        <div class="mobile-quick-actions">
          <van-button
            size="small"
            plain
            type="primary"
            @click="sendQuickMessage('帮助')"
            class="mobile-quick-action-btn"
          >
            <van-icon name="question-o" size="14px" style="margin-right: 4px;" />
            帮助
          </van-button>
          <van-button
            v-if="user?.is_superuser || user?.is_departadmin"
            size="small"
            plain
            type="primary"
            @click="sendQuickMessage('查看全部实训室')"
            class="mobile-quick-action-btn"
          >
            <van-icon name="shop-o" size="14px" style="margin-right: 4px;" />
            查看实训室
          </van-button>
          <van-button
            size="small"
            plain
            type="primary"
            @click="sendQuickMessage('我需要导入课表')"
            class="mobile-quick-action-btn"
          >
            <van-icon name="upload" size="14px" style="margin-right: 4px;" />
            导入课表
          </van-button>
          <van-button
            size="small"
            plain
            type="primary"
            @click="sendQuickMessage('查看使用记录')"
            class="mobile-quick-action-btn"
          >
            <van-icon name="records" size="14px" style="margin-right: 4px;" />
            使用记录
          </van-button>
          <van-button
            v-if="user?.is_superuser || user?.is_departadmin"
            size="small"
            plain
            type="primary"
            @click="sendQuickMessage('查看综合统计')"
            class="mobile-quick-action-btn"
          >
            <van-icon name="chart-trending-o" size="14px" style="margin-right: 4px;" />
            综合统计
          </van-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi, useAuth } from '@/core/hooks'
import { useMobile } from '@/composables/useMobile'

export default {
  name: 'AiAssistant',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const { user } = useAuth()
    const header = ref('AI智能助手')
    const inputMessage = ref('')
    const messages = ref([])
    const isProcessing = ref(false)
    const chatMessagesRef = ref(null)
    
    const { init: initMobile, loadVantComponents } = useMobile()
    
    let cleanup = null
    onMounted(async () => {
      cleanup = initMobile()
      loadVantComponents()
      loadData()
    })
    
    onUnmounted(() => {
      if (cleanup) cleanup()
    })

    const getCurrentTime = () => {
      return new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    }

    const processMessageButtons = (text) => {
      if (!text) return text
      
      const buttonRegex = /\[BUTTON:([^\|]+)\|([^\]]+)\]/g
      
      return text.replace(buttonRegex, (match, buttonText, url) => {
        let finalUrl = url.trim()
        
        if (!finalUrl.startsWith('/')) {
          finalUrl = '/' + finalUrl
        }
        
        const escapedUrl = finalUrl.replace(/'/g, "\\'").replace(/"/g, '&quot;')
        const escapedText = buttonText.replace(/</g, '&lt;').replace(/>/g, '&gt;')
        
        return `<button class="ai-message-button" data-url="${escapedUrl}">${escapedText}</button>`
      })
    }

    const handleButtonClick = (url) => {
      if (url) {
        router.push(url)
      }
    }

    const handleContainerClick = (event) => {
      const button = event.target.closest('.ai-message-button')
      if (button) {
        event.preventDefault()
        const url = button.getAttribute('data-url')
        if (url) {
          handleButtonClick(url)
        }
      }
    }

    const setupButtonListeners = () => {
      nextTick(() => {
        scrollToBottom()
      })
    }

    const scrollToBottom = () => {
      nextTick(() => {
        if (chatMessagesRef.value) {
          chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
        }
      })
    }

    const handleKeyPress = (event) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault()
        sendMessage()
      }
    }

    const sendQuickMessage = (message) => {
      inputMessage.value = message
      sendMessage()
    }

    const sendMessage = async () => {
      if (!inputMessage.value.trim() || isProcessing.value) return

      const userMessage = inputMessage.value.trim()
      inputMessage.value = ''

      messages.value.push({
        type: 'user-message',
        text: userMessage,
        time: getCurrentTime()
      })

      scrollToBottom()
      isProcessing.value = true

      try {
        const { post: aiApi } = useApi('/sxs/ai_assistant/', { immediate: false })
        const response = await aiApi({ message: userMessage })
        messages.value.push({
          type: 'ai-message',
          text: response.message || response.response || '抱歉，我无法理解您的请求。',
          time: getCurrentTime()
        })
        setupButtonListeners()
      } catch (err) {
        console.error('AI助手错误:', err)
        messages.value.push({
          type: 'ai-message',
          text: '抱歉，处理您的请求时出现了错误。请稍后再试。',
          time: getCurrentTime()
        })
      } finally {
        isProcessing.value = false
        scrollToBottom()
      }
    }

    const loadData = async () => {
      try {
        const { get: loadAiData } = useApi('/sxs/ai_assistant/', { immediate: false })
        const response = await loadAiData()
        if (response.data && response.data.header) {
          // 移除可能的 emoji 字符（包括机器人、空格等）
          header.value = response.data.header.replace(/[🤖\s]*/g, '').trim() || 'AI智能助手'
        } else if (response.header) {
          header.value = response.header.replace(/[🤖\s]*/g, '').trim() || 'AI智能助手'
        } else {
          header.value = 'AI智能助手'
        }
      } catch (err) {
        console.error('加载AI助手数据错误:', err)
        header.value = 'AI智能助手'
      }
    }

    const handleBack = () => {
      router.push('/')
    }

    return {
      header,
      inputMessage,
      messages,
      isProcessing,
      chatMessagesRef,
      user,
      getCurrentTime,
      scrollToBottom,
      handleKeyPress,
      sendQuickMessage,
      sendMessage,
      loadData,
      handleBack,
      processMessageButtons,
      handleButtonClick,
      setupButtonListeners,
      handleContainerClick
    }
  }
}
</script>

<style scoped>
@import '@/assets/css/mobile.css';
</style>
