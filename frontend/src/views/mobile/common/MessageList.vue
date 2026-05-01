<template>
  <div class="mobile-page">
    <van-nav-bar
      title="消息中心"
      left-arrow
      @click-left="goBack"
    >
      <template #right>
        <van-icon
          name="home-o"
          size="20"
          @click="goHome"
        />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <div class="stats-row">
        <div
          class="stat-item"
          @click="switchTab('unread')"
        >
          <van-badge
            :content="messageStats.unreadCount || ''"
            :show-zero="false"
          >
            <van-icon
              name="bell"
              size="24"
              color="#ee0a24"
            />
          </van-badge>
          <span>未读 {{ messageStats.unreadCount }}</span>
        </div>
        <div
          class="stat-item"
          @click="switchTab('all')"
        >
          <van-icon
            name="comment-o"
            size="24"
            color="#1989fa"
          />
          <span>全部</span>
        </div>
        <div
          class="stat-item"
          @click="switchTab('sent')"
        >
          <van-icon
            name="send-gift-o"
            size="24"
            color="#07c160"
          />
          <span>已发 {{ messageStats.sentCount }}</span>
        </div>
      </div>

      <van-search
        v-model="messageFilters.search"
        placeholder="搜索消息..."
        shape="round"
        @search="handleSearch"
        @clear="handleSearchClear"
      />

      <van-dropdown-menu v-if="messageTypeColumns.length > 1">
        <van-dropdown-item
          v-model="messageFilters.message_type"
          :options="messageTypeColumns"
          @change="handleFilterChange"
        />
      </van-dropdown-menu>

      <van-tabs
        v-model="activeTab"
        @change="handleTabChange"
      >
        <van-tab
          title="全部"
          name="all"
        />
        <van-tab
          title="未读"
          name="unread"
        />
        <van-tab
          title="已读"
          name="read"
        />
        <van-tab
          title="已发送"
          name="sent"
        />
      </van-tabs>

      <van-pull-refresh
        v-model="refreshing"
        @refresh="onRefresh"
      >
        <van-list
          v-model:loading="loading"
          :finished="finished"
          finished-text="没有更多了"
          @load="loadMore"
        >
          <van-empty
            v-if="!loading && messages.length === 0"
            description="暂无消息"
          />

          <div
            v-else
            class="message-list"
          >
            <div
              v-for="item in messages"
              :key="item.id"
              class="message-item"
              :class="{ unread: !item.is_read && item.direction !== 'sent' }"
              @click="handleItemClick(item)"
            >
              <div
                class="message-avatar"
                :style="{ background: getAvatarColor(item.sender_name || item.recipient_name) }"
              >
                {{ getInitial(item.direction === 'sent' ? item.recipient_name : item.sender_name) }}
              </div>
              <div class="message-content">
                <div class="message-header">
                  <span class="message-from">
                    {{ item.direction === 'sent' ? `发送至: ${item.recipient_name}` : item.sender_name }}
                  </span>
                  <span class="message-time">{{ formatDate(item.created_at || item.created_time) }}</span>
                </div>
                <div class="message-title">
                  {{ item.subject || item.title }}
                </div>
                <div class="message-body">
                  {{ item.content || item.body }}
                </div>
                <div
                  v-if="getMessageTypeLabel(item.message_type)"
                  class="message-type-tag"
                >
                  <van-tag
                    type="primary"
                    size="small"
                  >
                    {{ getMessageTypeLabel(item.message_type) }}
                  </van-tag>
                </div>
              </div>
              <div class="message-actions">
                <van-button
                  v-if="!item.is_read && item.direction !== 'sent'"
                  type="primary"
                  size="mini"
                  round
                  @click.stop="markAsRead(item)"
                >
                  已读
                </van-button>
                <van-button
                  type="danger"
                  size="mini"
                  plain
                  round
                  @click.stop="handleDeleteMessage(item)"
                >
                  删除
                </van-button>
              </div>
            </div>
          </div>
        </van-list>
      </van-pull-refresh>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { notificationService } from '@/core/services/BaseService'
import { useNavigation } from '@/core/utils/routeDecision'
import { showSuccess, showError, showConfirm } from '@/core/utils/errorHandler'

const route = useRoute()
const router = useRouter()
const { goHome, smartBack } = useNavigation()

const activeTab = ref('all')
const loading = ref(false)
const refreshing = ref(false)
const finished = ref(false)
const messages = ref([])
const currentPage = ref(1)
const pageSize = ref(15)

const messageStats = ref({ unreadCount: 0, sentCount: 0, receivedCount: 0 })
const messageTypes = ref({})
const notificationTypes = ref({})
const messageFilters = ref({ search: '', message_type: '' })

const messageTypeColumns = computed(() => {
  const columns = [{ text: '全部类型', value: '' }]
  Object.entries(messageTypes.value).forEach(([value, label]) => {
    columns.push({ text: label, value })
  })
  Object.entries(notificationTypes.value).forEach(([value, label]) => {
    columns.push({ text: label, value })
  })
  return columns
})

const getMessageTypeLabel = (value) => {
  if (!value) return ''
  if (messageTypes.value[value]) return messageTypes.value[value]
  if (notificationTypes.value[value]) return notificationTypes.value[value]
  return ''
}

const getAvatarColor = (name) => {
  if (!name) return '#909399'
  const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
}

const getInitial = (name) => {
  return name ? name.charAt(0).toUpperCase() : 'U'
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return dateStr.substring(0, 16).replace('T', ' ')
}

const switchTab = (tab) => {
  activeTab.value = tab
  handleTabChange()
}

const handleTabChange = () => {
  currentPage.value = 1
  finished.value = false
  messages.value = []
  loadMessages()
}

const loadMessages = async () => {
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ...messageFilters.value
    }

    if (activeTab.value === 'unread') {
      params.read = 'unread'
    } else if (activeTab.value === 'read') {
      params.read = 'read'
    } else if (activeTab.value === 'sent') {
      params.direction = 'sent'
    }

    const response = await notificationService.list(params)
    
    if (response) {
      messageStats.value.unreadCount = response.unread_count || 0
      messageStats.value.sentCount = response.sent_count || 0
      messageStats.value.receivedCount = response.received_count || 0
      
      if (response.message_types) messageTypes.value = response.message_types
      if (response.notification_types) notificationTypes.value = response.notification_types
      
      const list = response.messages || response.list || response.data?.list || []
      
      if (currentPage.value === 1) {
        messages.value = list
      } else {
        messages.value.push(...list)
      }
      
      finished.value = list.length < pageSize.value
    }
  } catch (err) {
    console.error('Load messages error:', err)
    finished.value = true
  }
}

const loadMore = async () => {
  if (refreshing.value) return
  currentPage.value++
  await loadMessages()
  loading.value = false
}

const onRefresh = async () => {
  currentPage.value = 1
  finished.value = false
  await loadMessages()
  refreshing.value = false
}

const markAsRead = async (message) => {
  try {
    await notificationService.markRead(message.id)
    message.is_read = true
    messageStats.value.unreadCount = Math.max(0, messageStats.value.unreadCount - 1)
    showSuccess('已标记为已读')
  } catch (err) {
    showError('操作失败')
  }
}

const handleDeleteMessage = async (message) => {
  const confirmed = await showConfirm({
    title: '确认删除',
    message: '确定要删除这条消息吗？',
    type: 'danger'
  })
  
  if (!confirmed) return
  
  try {
    await notificationService.delete(message.id)
    messages.value = messages.value.filter(m => m.id !== message.id)
    showSuccess('删除成功')
  } catch (err) {
    if (err !== 'cancel') {
      showError('删除失败')
    }
  }
}

const handleSearch = () => {
  currentPage.value = 1
  finished.value = false
  messages.value = []
  loadMessages()
}

const handleSearchClear = () => {
  messageFilters.value.search = ''
  handleSearch()
}

const handleFilterChange = () => {
  currentPage.value = 1
  finished.value = false
  messages.value = []
  loadMessages()
}

const handleItemClick = (item) => {
  if (!item.is_read && item.direction !== 'sent') {
    markAsRead(item)
  }
}

const goBack = () => router.go(-1)

onMounted(() => {
  if (route.query.tab) {
    activeTab.value = route.query.tab
  }
  loadMessages()
})
</script>

<style scoped>
.mobile-page {
  min-height: 100vh;
  background: #f7f8fa;
  display: flex;
  flex-direction: column;
}

.page-content {
  flex: 1;
  overflow-y: auto;
}

.stats-row {
  display: flex;
  justify-content: space-around;
  padding: 12px 16px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  cursor: pointer;
}

.stat-item span {
  font-size: 11px;
  color: #646566;
}

.message-list {
  padding: 12px;
}

.message-item {
  display: flex;
  gap: 12px;
  padding: 14px;
  background: #fff;
  border-radius: 10px;
  margin-bottom: 10px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.message-item.unread {
  background: #ecf5ff;
  border-left: 3px solid #1989fa;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 600;
  font-size: 16px;
  flex-shrink: 0;
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.message-from {
  font-size: 13px;
  font-weight: 500;
  color: #323233;
}

.message-time {
  font-size: 11px;
  color: #969799;
}

.message-title {
  font-size: 14px;
  color: #323233;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 500;
}

.message-body {
  font-size: 12px;
  color: #969799;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.message-type-tag {
  margin-top: 6px;
}

.message-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}
</style>