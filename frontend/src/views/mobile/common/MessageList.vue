<template>
  <div class="message-page">
    <!-- 顶部导航栏 -->
    <header class="message-header">
      <button class="header-back" @click="goBack" aria-label="返回">
        <span class="back-icon">←</span>
      </button>
      <h1 class="header-title">消息中心</h1>
      <div class="header-placeholder"></div>
    </header>

    <!-- 消息统计 -->
    <section class="message-stats">
      <div class="stat-card stat-unread">
        <div class="stat-value">{{ unreadCount }}</div>
        <div class="stat-label">
          <span class="stat-icon">💬</span>
          <span>未读</span>
        </div>
      </div>
      <div class="stat-card stat-sent">
        <div class="stat-value">{{ sentCount }}</div>
        <div class="stat-label">
          <span class="stat-icon">📤</span>
          <span>已发送</span>
        </div>
      </div>
      <div class="stat-card stat-received">
        <div class="stat-value">{{ receivedCount }}</div>
        <div class="stat-label">
          <span class="stat-icon">📥</span>
          <span>已接收</span>
        </div>
      </div>
    </section>

    <!-- 搜索和筛选 -->
    <section class="message-filters">
      <!-- 搜索框 -->
      <div class="search-box">
        <span class="search-icon">🔍</span>
          <input
            v-model="filters.search"
            type="text"
          class="search-input"
            placeholder="搜索消息主题或内容..."
            @input="handleSearchInput"
          />
        <button
            v-if="filters.search"
          class="search-clear"
            @click="filters.search = ''"
          aria-label="清除搜索"
        >
          ✕
        </button>
      </div>
      
      <!-- 消息类型选择 -->
      <div class="filter-box" @click="showTypePicker = true">
        <span class="filter-icon">📋</span>
        <div class="filter-content">
          <span class="filter-label">消息类型</span>
          <span class="filter-value">{{ getTypeLabel(filters.message_type) || '全部' }}</span>
        </div>
        <span class="filter-arrow">›</span>
      </div>
      
      <!-- 操作按钮 -->
      <div class="filter-actions">
        <button class="btn btn-primary" @click="handleFilter">筛选</button>
        <button class="btn btn-secondary" @click="handleReset">重置</button>
      </div>
    </section>

    <!-- 消息列表 -->
    <section class="message-list-section">
      <div v-if="messages.length > 0" class="message-list">
        <article
          v-for="message in messages"
          :key="message.id"
          class="message-card"
          :class="{ 'message-unread': !message.is_read }"
          @click="showMessageDetail(message)"
        >
          <div class="message-avatar">
            <span class="avatar-icon">💬</span>
          </div>
          <div class="message-body">
            <h3 class="message-subject">{{ message.subject }}</h3>
            <p class="message-preview">{{ message.content }}</p>
            <div class="message-info">
              <span class="message-sender">{{ message.sender_name }}</span>
              <span class="message-time">{{ message.created_time }}</span>
            </div>
          </div>
          <div class="message-status">
            <span v-if="!message.is_read" class="badge badge-unread">未读</span>
            <span class="message-arrow">›</span>
          </div>
        </article>
      </div>
      <div v-else class="message-empty">
        <div class="empty-icon">💬</div>
        <p class="empty-text">暂无消息</p>
      </div>
    </section>

    <!-- 消息类型选择器 -->
    <div v-if="showTypePicker" class="picker-modal" @click="showTypePicker = false">
      <div class="picker-content" @click.stop>
        <div class="picker-header">
          <button class="picker-btn picker-cancel" @click="showTypePicker = false">取消</button>
          <h2 class="picker-title">选择消息类型</h2>
          <button class="picker-btn picker-confirm" @click="handlePickerConfirm">确定</button>
        </div>
        <div class="picker-list">
          <div
            v-for="(option, index) in typeColumns"
            :key="index"
            class="picker-item"
            :class="{ 'picker-item-active': selectedPickerValue === option.value }"
            @click="selectedPickerValue = option.value"
          >
            {{ option.text }}
          </div>
        </div>
      </div>
    </div>

    <!-- 消息详情弹窗 -->
    <div v-if="showDetail" class="detail-modal" @click="showDetail = false">
      <div class="detail-content" @click.stop>
        <header class="detail-header">
          <button class="detail-back" @click="showDetail = false" aria-label="关闭">
            <span class="back-icon">←</span>
          </button>
          <h2 class="detail-title">{{ selectedMessage?.subject }}</h2>
          <button
            class="detail-delete"
            @click="deleteMessageMobile(selectedMessage)"
            aria-label="删除"
          >
            🗑
          </button>
        </header>
        <div v-if="selectedMessage" class="detail-body">
          <div class="detail-meta">
            <span class="detail-time">{{ selectedMessage.created_time }}</span>
            <span class="detail-sender">发件人: {{ selectedMessage.sender_name }}</span>
          </div>
          <div class="detail-text">{{ selectedMessage.content }}</div>
          <div v-if="!selectedMessage.is_read" class="detail-actions">
            <button class="btn btn-primary btn-block" @click="markAsReadMobile(selectedMessage)">
              标记已读
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部导航栏 -->
    <van-tabbar v-model="activeTab" fixed>
      <van-tabbar-item icon="home-o" @click="navigateTo('/')">首页</van-tabbar-item>
      <van-tabbar-item icon="apps-o" @click="navigateToFunction">功能</van-tabbar-item>
      <van-tabbar-item icon="chat-o" :name="2">消息</van-tabbar-item>
      <van-tabbar-item icon="user-o" @click="navigateToPersonal">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi, useAuth } from '@/core/hooks'

export default {
  name: 'MessageList',
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    // 数据状态
    const unreadCount = ref(0)
    const sentCount = ref(0)
    const receivedCount = ref(0)
    const messages = ref([])
    const messageTypes = ref({})
    const notificationTypes = ref({})
    const filters = ref({
      search: '',
      message_type: ''
    })
    
    // UI 状态
    const showTypePicker = ref(false)
    const showDetail = ref(false)
    const selectedMessage = ref(null)
    const selectedPickerValue = ref('')
    const activeTab = ref(2) // 消息页面默认选中消息标签
    
    // 计算属性
    const typeColumns = computed(() => {
      const columns = [{ text: '全部', value: '' }]
      if (messageTypes.value) {
        Object.entries(messageTypes.value).forEach(([value, label]) => {
          columns.push({ text: label, value })
        })
      }
      if (notificationTypes.value) {
        Object.entries(notificationTypes.value).forEach(([value, label]) => {
          columns.push({ text: label, value })
        })
      }
      return columns
    })

    // 方法
    const goBack = () => {
      router.go(-1)
    }

    const navigateTo = (path) => {
      router.push(path).catch(err => {
        if (err.name !== 'NavigationDuplicated') {
          console.error('导航失败:', err)
        }
      })
    }

    const navigateToFunction = () => {
      // 使用 sessionStorage 传递要激活的标签页
      sessionStorage.setItem('activeTab', '1')
      navigateTo('/')
    }

    const navigateToPersonal = () => {
      // 使用 sessionStorage 传递要激活的标签页
      sessionStorage.setItem('activeTab', '3')
      navigateTo('/')
    }

    const handleFilter = () => {
      router.push({ query: { ...filters.value } })
      loadData()
    }

    const handleReset = () => {
      filters.value = {
        search: '',
        message_type: ''
      }
      router.push({ query: {} })
      loadData()
    }

    const handleSearchInput = () => {
      // 可以添加防抖搜索逻辑
    }

    const getTypeLabel = (value) => {
      if (!value) return ''
      const option = typeColumns.value.find(col => col.value === value)
      return option ? option.text : ''
    }

    const handlePickerConfirm = () => {
      filters.value.message_type = selectedPickerValue.value
      showTypePicker.value = false
    }

    const showMessageDetail = (message) => {
      selectedMessage.value = message
      showDetail.value = true
      if (!message.is_read) {
        markAsReadMobile(message)
      }
    }

    const markAsReadMobile = async (message) => {
      try {
        const { showSuccessToast } = await import('@/utils/mobileDialog')
        const { post: markReadApi } = useApi(`/message/${message.id}/mark-read/`, { immediate: false })
        const response = await markReadApi()
        if (response.success) {
          message.is_read = true
          unreadCount.value--
          showSuccessToast('已标记为已读')
        }
      } catch (err) {
        const { showFailToast } = await import('@/utils/mobileDialog')
        showFailToast('操作失败：' + (err.message || '未知错误'))
      }
    }

    const deleteMessageMobile = async (message) => {
      try {
        const { showConfirmDialog } = await import('@/utils/mobileDialog')
        await showConfirmDialog({
          title: '确认删除',
          message: '确定要删除这条消息吗？',
          type: 'danger'
        })
        const { showSuccessToast, showFailToast } = await import('@/utils/mobileDialog')
        const { delete: deleteApi } = useApi(`/message/${message.id}/`, { immediate: false })
        const response = await deleteApi()
        if (response.success) {
          messages.value = messages.value.filter(m => m.id !== message.id)
          showDetail.value = false
          showSuccessToast('删除成功')
        } else {
          showFailToast(response.message || '删除失败')
        }
      } catch (err) {
        if (err !== 'cancel') {
          const { showFailToast } = await import('@/utils/mobileDialog')
          showFailToast('删除失败：' + (err.message || '未知错误'))
        }
      }
    }

    const loadData = async () => {
      try {
        const { get: messageListApi } = useApi('/message-list/', { immediate: false })
        const response = await messageListApi({ ...filters.value, ...route.query })
        unreadCount.value = response.unread_count || 0
        sentCount.value = response.sent_count || 0
        receivedCount.value = response.received_count || 0
        messages.value = response.messages || []
        messageTypes.value = response.message_types || {}
        notificationTypes.value = response.notification_types || {}
      } catch (err) {
        console.error('Load messages error:', err)
      }
    }

    // 生命周期
    onMounted(() => {
      filters.value = { ...route.query }
      selectedPickerValue.value = filters.value.message_type || ''
      loadData()
    })

    return {
      unreadCount,
      sentCount,
      receivedCount,
      messages,
      filters,
      showTypePicker,
      showDetail,
      selectedMessage,
      selectedPickerValue,
      typeColumns,
      goBack,
      navigateTo,
      navigateToFunction,
      navigateToPersonal,
      handleFilter,
      handleReset,
      handleSearchInput,
      getTypeLabel,
      handlePickerConfirm,
      showMessageDetail,
      markAsReadMobile,
      deleteMessageMobile,
      activeTab
    }
  }
}
</script>

<style scoped>
/* 页面容器 */
.message-page {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 80px; /* 为底部导航栏留出空间 */
}

/* 顶部导航栏 */
.message-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 44px;
  padding: 0 16px;
  background: #fff;
  border-bottom: 1px solid #e5e5e5;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-back {
  background: none;
  border: none;
  padding: 8px;
  cursor: pointer;
  font-size: 20px;
  color: #333;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 40px;
  height: 40px;
}

.header-title {
  flex: 1;
  text-align: center;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.header-placeholder {
  min-width: 40px;
}

/* 消息统计 */
.message-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  padding: 16px;
  background: #fff;
  margin: 12px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.stat-card {
  text-align: center;
  padding: 16px 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
  line-height: 1;
}

.stat-unread .stat-value {
  color: #ff4757;
}

.stat-sent .stat-value,
.stat-received .stat-value {
  color: #3742fa;
}

.stat-label {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-size: 13px;
  color: #666;
}

.stat-icon {
  font-size: 16px;
}

/* 搜索和筛选 */
.message-filters {
  padding: 0 16px 16px;
}

.search-box {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.search-icon {
  font-size: 18px;
  color: #999;
  margin-right: 8px;
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 14px;
  color: #333;
  background: transparent;
}

.search-input::placeholder {
  color: #999;
}

.search-clear {
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  font-size: 18px;
  color: #999;
  margin-left: 8px;
}

.filter-box {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 12px;
  cursor: pointer;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.filter-icon {
  font-size: 18px;
  color: #999;
  margin-right: 8px;
}

.filter-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.filter-label {
  font-size: 12px;
  color: #999;
}

.filter-value {
  font-size: 14px;
  color: #333;
}

.filter-arrow {
  font-size: 20px;
  color: #ccc;
  margin-left: 8px;
}

.filter-actions {
  display: flex;
  gap: 12px;
}

.btn {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #3742fa;
  color: #fff;
}

.btn-primary:active {
  background: #2f38d9;
}

.btn-secondary {
  background: #f1f2f6;
  color: #333;
}

.btn-secondary:active {
  background: #dfe4ea;
}

.btn-block {
  width: 100%;
}

/* 消息列表 */
.message-list-section {
  padding: 0 16px;
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message-card {
  display: flex;
  align-items: flex-start;
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.message-card:active {
  transform: scale(0.98);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.message-unread {
  background: #fff9f0;
  border-left: 3px solid #ffa502;
}

.message-avatar {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f1f2f6;
  border-radius: 12px;
  margin-right: 12px;
  flex-shrink: 0;
}

.avatar-icon {
  font-size: 24px;
}

.message-body {
  flex: 1;
  min-width: 0;
}

.message-subject {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.message-preview {
  font-size: 14px;
  color: #666;
  margin: 0 0 8px 0;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.message-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #999;
}

.message-status {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
  margin-left: 12px;
  flex-shrink: 0;
}

.badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

.badge-unread {
  background: #ff4757;
  color: #fff;
}

.message-arrow {
  font-size: 18px;
  color: #ccc;
}

.message-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-text {
  font-size: 14px;
  color: #999;
  margin: 0;
}

/* 选择器弹窗 */
.picker-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  align-items: flex-end;
  animation: fadeIn 0.2s;
}

.picker-content {
  width: 100%;
  background: #fff;
  border-radius: 20px 20px 0 0;
  max-height: 70vh;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s;
}

.picker-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid #e5e5e5;
}

.picker-title {
  flex: 1;
  text-align: center;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.picker-btn {
  background: none;
  border: none;
  padding: 8px 16px;
  font-size: 14px;
  cursor: pointer;
}

.picker-cancel {
  color: #999;
}

.picker-confirm {
  color: #3742fa;
}

.picker-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.picker-item {
  padding: 14px 16px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  transition: background 0.2s;
}

.picker-item:active {
  background: #f1f2f6;
}

.picker-item-active {
  color: #3742fa;
  background: #f0f1ff;
  font-weight: 500;
}

/* 详情弹窗 */
.detail-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  align-items: flex-end;
  animation: fadeIn 0.2s;
}

.detail-content {
  width: 100%;
  background: #fff;
  border-radius: 20px 20px 0 0;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s;
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid #e5e5e5;
}

.detail-back,
.detail-delete {
  background: none;
  border: none;
  padding: 8px;
  cursor: pointer;
  font-size: 20px;
  color: #333;
  min-width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.detail-title {
  flex: 1;
  text-align: center;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0;
  padding: 0 16px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.detail-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.detail-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 16px;
  font-size: 12px;
  color: #999;
}

.detail-text {
  font-size: 14px;
  color: #333;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.detail-actions {
  margin-top: 24px;
}

/* 动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}
</style> 
