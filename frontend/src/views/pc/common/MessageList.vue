<!-- 消息通知列表 -->
<template>
  <Index class="pc-layout">
    <template #rightcontent>
      <div class="msg-center">
        <div class="mc-header">
          <div class="mc-title">
            <el-icon><Message /></el-icon>
            <h2>消息中心</h2>
          </div>
          <div class="mc-actions">
            <el-button @click="smartBack">
              <el-icon><ArrowLeft /></el-icon>
              返回
            </el-button>
            <el-button @click="goHome">
              <el-icon><HomeFilled /></el-icon>
              首页
            </el-button>
          </div>
        </div>

        <div class="mc-stats">
          <div
            class="mc-stat"
            @click="switchTab('unread')"
          >
            <div class="stat-icon red">
              <el-icon><Bell /></el-icon>
            </div>
            <div class="stat-body">
              <span class="stat-num">{{ unreadCount }}</span>
              <span class="stat-txt">未读消息</span>
            </div>
          </div>
          <div
            class="mc-stat"
            @click="switchTab('all')"
          >
            <div class="stat-icon blue">
              <el-icon><Download /></el-icon>
            </div>
            <div class="stat-body">
              <span class="stat-num">{{ receivedCount }}</span>
              <span class="stat-txt">已接收消息</span>
            </div>
          </div>
          <div
            class="mc-stat"
            @click="switchTab('sent')"
          >
            <div class="stat-icon green">
              <el-icon><Promotion /></el-icon>
            </div>
            <div class="stat-body">
              <span class="stat-num">{{ sentCount }}</span>
              <span class="stat-txt">已发送消息</span>
            </div>
          </div>
        </div>

        <div class="mc-main">
          <div class="mc-toolbar">
            <div class="mc-tabs">
              <button 
                class="mc-tab" 
                :class="{ on: activeTab === 'all' }"
                @click="switchTab('all')"
              >
                全部消息
              </button>
              <button 
                class="mc-tab" 
                :class="{ on: activeTab === 'unread' }"
                @click="switchTab('unread')"
              >
                未读
                <i v-if="unreadCount > 0">{{ unreadCount }}</i>
              </button>
              <button 
                class="mc-tab" 
                :class="{ on: activeTab === 'read' }"
                @click="switchTab('read')"
              >
                已读
              </button>
              <button 
                class="mc-tab" 
                :class="{ on: activeTab === 'sent' }"
                @click="switchTab('sent')"
              >
                已发�?
              </button>
            </div>
            <div class="mc-search">
              <el-input 
                v-model="filters.search" 
                placeholder="搜索消息内容..."
                clearable
                @keyup.enter="handleSearch"
                @clear="handleSearch"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </div>
          </div>

          <div
            v-loading="loading"
            class="mc-list"
          >
            <template v-if="messages.length > 0">
              <div 
                v-for="item in messages" 
                :key="item.id" 
                class="mc-item"
                :class="{ unread: !item.is_read && item.direction === 'received' }"
              >
                <div class="item-check">
                  <span
                    v-if="!item.is_read && item.direction === 'received'"
                    class="dot"
                  />
                </div>
                <div
                  class="item-avatar"
                  :style="{ background: getAvatarColor(item.sender_name) }"
                >
                  <el-icon v-if="item.direction === 'sent'">
                    <User />
                  </el-icon>
                  <span v-else>{{ getInitial(item.sender_name) }}</span>
                </div>
                <div class="item-info">
                  <div class="item-row">
                    <span class="item-from">
                      {{ item.direction === 'sent' ? `发送至: ${item.recipient_name || '接收人'}` : item.sender_name }}
                    </span>
                    <span
                      class="item-type"
                      :class="getTypeClass(item)"
                    >{{ getTypeLabel(item) }}</span>
                    <span
                      v-if="!item.is_read && item.direction === 'received'"
                      class="item-badge new"
                    >新读</span>
                    <span
                      v-if="item.subject.startsWith('【回执】')"
                      class="item-badge reply"
                    >回执</span>
                  </div>
                  <div class="item-title">
                    {{ item.subject }}
                  </div>
                  <div class="item-desc">
                    {{ item.content }}
                  </div>
                </div>
                <div class="item-meta">
                  <span class="item-time">{{ formatDate(item.created_time) }}</span>
                  <div class="item-btns">
                    <el-button 
                      v-if="item.direction === 'received' && !item.is_read"
                      type="primary" 
                      size="small"
                      round
                      @click.stop="markAsRead(item)"
                    >
                      标为已读
                    </el-button>
                    <el-button 
                      type="danger" 
                      size="small"
                      round
                      plain
                      @click.stop="deleteMessage(item)"
                    >
                      删除
                    </el-button>
                  </div>
                </div>
              </div>
            </template>
            <template v-else>
              <div class="mc-empty">
                <el-icon :size="56">
                  <MessageBox />
                </el-icon>
                <p>暂无消息</p>
              </div>
            </template>
          </div>

          <Pagination
            v-if="totalMessages > 0"
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total-count="totalMessages"
            :page-sizes="[10, 20, 50]"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </template>
  </Index>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useApi, useDelete } from '@/core/hooks'
import { showSuccess } from '@/core/utils/errorHandler'
import { useNavigation } from '@/core/utils/routeDecision'
import Index from '@/views/pc/dashboard/Index.vue'
import Pagination from '@/views/pc/components/Pagination.vue'
import { 
  Message, Bell, Download, Promotion, Search, User, 
  ArrowLeft, HomeFilled, MessageBox
} from '@element-plus/icons-vue'

export default {
  name: 'MessageList',
  components: {
    Index,
    Pagination,
    Message, Bell, Download, Promotion, Search, User, 
    ArrowLeft, HomeFilled, MessageBox
  },
  setup() {
    const route = useRoute()
    const { goHome, smartBack } = useNavigation()
    
    const { loading, get: fetchMessages } = useApi('/notifications/', { immediate: false })
    const { post: markReadApi } = useApi('/notifications/', { immediate: false })
    
    const { handleDelete: execDelete } = useDelete({
      apiPathBuilder: (item) => `/notifications/${encodeURIComponent(item.id)}/`,
      refresh: () => loadData(),
      method: 'DELETE',
      confirmMessageBuilder: () => '确定要删除这条消息吗？'
    })

    const activeTab = ref('all')
    const unreadCount = ref(0)
    const sentCount = ref(0)
    const receivedCount = ref(0)
    const messages = ref([])
    const filters = ref({ search: '' })
    const currentPage = ref(1)
    const pageSize = ref(10)
    const totalMessages = ref(0)

    const handleSizeChange = (val) => {
      pageSize.value = val
      currentPage.value = 1
      loadData()
    }

    const handleCurrentChange = (val) => {
      currentPage.value = val
      loadData()
    }

    const switchTab = (tab) => {
      activeTab.value = tab
    }

    const handleSearch = () => {
      currentPage.value = 1
      loadData()
    }

    const loadData = async () => {
      const params = {
        search: filters.value.search,
        page: currentPage.value,
        page_size: pageSize.value,
        ...route.query
      }

      if (activeTab.value === 'unread') {
        params.read = 'unread'
      } else if (activeTab.value === 'read') {
        params.read = 'read'
      } else if (activeTab.value === 'sent') {
        params.direction = 'sent'
      }

      try {
        const response = await fetchMessages(params)
        if (response) {
          unreadCount.value = response.unread_count || 0
          sentCount.value = response.sent_count || 0
          receivedCount.value = response.received_count || 0
          messages.value = Array.isArray(response.messages) ? response.messages : []
          
          if (response.page_obj) {
            totalMessages.value = response.page_obj.count || 0
            if (response.page_obj.number) {
              currentPage.value = response.page_obj.number
            }
          }
        }
      } catch (err) {
      }
    }

    const markAsRead = async (message) => {
      try {
        const response = await markReadApi({}, { 
          url: `/notifications/${encodeURIComponent(message.id)}/mark-read/` 
        })
        if (response && response.success) {
          message.is_read = true
          unreadCount.value = Math.max(0, unreadCount.value - 1)
          showSuccess('已标记为已读')
        }
      } catch (err) {
      }
    }

    const deleteMessage = async (message) => {
      await execDelete(message)
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
      return name ? name.charAt(0).toUpperCase() : 'S'
    }

    const getTypeLabel = (msg) => {
      const type = msg.message_type || msg.notification_type
      if (msg.notification_type === 'SYSTEM' || type === 'SYSTEM') return '系统'
      if (type === 'MAINTENANCE') return '维护'
      if (type === 'SCHEDULE') return '课表'
      if (type === 'USER' || type === 'TEXT') return '私信'
      return '消息'
    }

    const getTypeClass = (msg) => {
      const type = msg.message_type || msg.notification_type
      if (type === 'SYSTEM') return 'tp-gray'
      if (type === 'MAINTENANCE') return 'tp-orange'
      if (type === 'SCHEDULE') return 'tp-green'
      return 'tp-blue'
    }
    
    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      return dateStr.substring(0, 16).replace('T', ' ')
    }

    watch(activeTab, () => {
      currentPage.value = 1
      loadData()
    })

    onMounted(() => {
      if (route.query.tab) {
        activeTab.value = route.query.tab
      }
      loadData()
    })

    return {
      activeTab, unreadCount, sentCount, receivedCount, messages, loading,
      filters, currentPage, pageSize, totalMessages,
      switchTab, handleSearch, markAsRead, deleteMessage,
      handleSizeChange, handleCurrentChange, smartBack, goHome,
      getAvatarColor, getInitial, getTypeLabel, getTypeClass, formatDate
    }
  }
}
</script>

<style scoped>
.msg-center {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f8fafc;
}

.mc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
}

.mc-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.mc-title .el-icon {
  font-size: 24px;
  color: #3b82f6;
}

.mc-title h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
}

.mc-actions {
  display: flex;
  gap: 8px;
}

.mc-stats {
  display: flex;
  gap: 16px;
  padding: 20px 24px;
}

.mc-stat {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 20px;
  background: #fff;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #e2e8f0;
}

.mc-stat:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon .el-icon {
  font-size: 22px;
  color: #fff;
}

.stat-icon.red { background: #ef4444; }
.stat-icon.blue { background: #3b82f6; }
.stat-icon.green { background: #10b981; }

.stat-body {
  display: flex;
  flex-direction: column;
}

.stat-num {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1;
}

.stat-txt {
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
}

.mc-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
  margin: 0 24px 24px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  overflow: hidden;
}

.mc-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e2e8f0;
  background: #fafbfc;
}

.mc-tabs {
  display: flex;
  gap: 6px;
}

.mc-tab {
  padding: 8px 18px;
  font-size: 14px;
  color: #64748b;
  background: transparent;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.mc-tab:hover {
  background: #f1f5f9;
  color: #334155;
}

.mc-tab.on {
  background: #3b82f6;
  color: #fff;
}

.mc-tab i {
  font-style: normal;
  font-size: 11px;
  padding: 2px 6px;
  background: #ef4444;
  color: #fff;
  border-radius: 10px;
}

.mc-tab.on i {
  background: rgba(255, 255, 255, 0.25);
}

.mc-search {
  width: 260px;
}

.mc-list {
  flex: 1;
  overflow-y: auto;
}

.mc-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 18px 20px;
  border-bottom: 1px solid #f1f5f9;
  transition: background 0.15s;
}

.mc-item:hover {
  background: #f8fafc;
}

.mc-item.unread {
  background: #eff6ff;
}

.mc-item.unread:hover {
  background: #dbeafe;
}

.item-check {
  width: 20px;
  padding-top: 12px;
}

.dot {
  width: 8px;
  height: 8px;
  background: #3b82f6;
  border-radius: 50%;
  display: block;
}

.item-avatar {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  flex-shrink: 0;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
  flex-wrap: wrap;
}

.item-from {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.item-type {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.tp-gray { background: #f1f5f9; color: #64748b; }
.tp-orange { background: #fef3c7; color: #d97706; }
.tp-green { background: #d1fae5; color: #059669; }
.tp-blue { background: #dbeafe; color: #2563eb; }

.item-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.item-badge.new {
  background: #fef2f2;
  color: #ef4444;
}

.item-badge.reply {
  background: #d1fae5;
  color: #059669;
}

.item-title {
  font-size: 15px;
  font-weight: 500;
  color: #334155;
  margin-bottom: 4px;
}

.mc-item.unread .item-title {
  font-weight: 600;
  color: #1e293b;
}

.item-desc {
  font-size: 13px;
  color: #94a3b8;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.item-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
  flex-shrink: 0;
  min-width: 100px;
}

.item-time {
  font-size: 12px;
  color: #94a3b8;
}

.item-btns {
  display: flex;
  gap: 6px;
  opacity: 0;
  transition: opacity 0.15s;
}

.mc-item:hover .item-btns {
  opacity: 1;
}

.mc-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  color: #cbd5e1;
}

.mc-empty .el-icon {
  color: #e2e8f0;
}

.mc-empty p {
  margin: 16px 0 0;
  font-size: 15px;
  color: #94a3b8;
}

.mc-pager {
  display: flex;
  justify-content: center;
  padding: 16px;
  border-top: 1px solid #e2e8f0;
  background: #fafbfc;
}

@media (max-width: 768px) {
  .mc-stats {
    flex-direction: column;
    padding: 12px 16px;
  }
  
  .mc-stat {
    padding: 14px 16px;
  }
  
  .mc-toolbar {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .mc-tabs {
    overflow-x: auto;
    padding-bottom: 4px;
  }
  
  .mc-search {
    width: 100%;
  }
  
  .mc-item {
    flex-direction: column;
    gap: 10px;
  }
  
  .item-check {
    display: none;
  }
  
  .item-meta {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    width: 100%;
  }
  
  .item-btns {
    opacity: 1;
  }
}
</style>
