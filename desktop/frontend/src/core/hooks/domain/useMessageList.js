import { ref, computed, onMounted, watch } from 'vue'
import { useApi } from '@/core/hooks'

export function useMessageList() {
  const { get: messageListApi } = useApi('notifications/', { immediate: false })
  const { post: markReadApi } = useApi('', { immediate: false })
  const { post: deleteMessageApi } = useApi('', { immediate: false })

  const messageStats = ref({
    unreadCount: 0,
    sentCount: 0,
    receivedCount: 0
  })
  const messages = ref([])
  const messageTypes = ref({})
  const notificationTypes = ref({})
  const messageFilters = ref({
    search: '',
    message_type: ''
  })
  const selectedMessage = ref(null)

  const messageTypeColumns = computed(() => {
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

  const getMessageTypeLabel = (value) => {
    if (!value) return ''
    if (messageTypes.value && messageTypes.value[value]) {
      return messageTypes.value[value]
    }
    if (notificationTypes.value && notificationTypes.value[value]) {
      return notificationTypes.value[value]
    }
    return ''
  }

  const loadMessages = async () => {
    try {
      const response = await messageListApi({ ...messageFilters.value })
      messageStats.value.unreadCount = response.unread_count || 0
      messageStats.value.sentCount = response.sent_count || 0
      messageStats.value.receivedCount = response.received_count || 0
      messages.value = response.messages || []
      messageTypes.value = response.message_types || {}
      notificationTypes.value = response.notification_types || {}
    } catch (err) {
    }
  }

  const markAsRead = async (message, showSuccess, showError) => {
    try {
      const response = await markReadApi({}, { url: `notifications/${message.id}/mark-read/` })
      if (response.success) {
        message.is_read = true
        messageStats.value.unreadCount--
        if (showSuccess) showSuccess('已标记为已读')
      }
    } catch (err) {
      if (showError) showError('操作失败：' + (err.message || '未知错误'))
    }
  }

  const deleteMessage = async (message, showSuccess, showError, showConfirm) => {
    try {
      if (showConfirm) {
        await showConfirm({
          title: '确认删除',
          message: '确定要删除这条消息吗？',
          type: 'danger'
        })
      }
      const response = await deleteMessageApi({}, { url: `notifications/${message.id}/delete/`, method: 'post' })
      if (response.success) {
        messages.value = messages.value.filter(m => m.id !== message.id)
        if (showSuccess) showSuccess('删除成功')
        return true
      } else {
        if (showError) showError(response.message || '删除失败')
        return false
      }
    } catch (err) {
      if (err !== 'cancel' && showError) {
        showError('删除失败：' + (err.message || '未知错误'))
      }
      return false
    }
  }

  const showMessageDetail = (message) => {
    selectedMessage.value = message
    return message
  }

  const resetFilters = () => {
    messageFilters.value = {
      search: '',
      message_type: ''
    }
    loadMessages()
  }

  onMounted(loadMessages)

  return {
    messageStats,
    messages,
    messageTypes,
    notificationTypes,
    messageFilters,
    messageTypeColumns,
    selectedMessage,
    getMessageTypeLabel,
    loadMessages,
    markAsRead,
    deleteMessage,
    showMessageDetail,
    resetFilters
  }
}
