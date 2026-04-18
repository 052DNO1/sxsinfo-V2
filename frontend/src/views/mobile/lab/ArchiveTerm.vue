<template>
  <!-- 移动端直接显示内容 -->
  <div class="mobile-archive-page mobile-layout">
    <van-nav-bar
      title="归档学期"
      left-arrow
      @click-left="goBack"
      class="mobile-nav-bar"
    />

    <div class="mobile-content-wrapper">
      <!-- 当前学期信息 -->
      <van-cell-group inset v-if="currentTerm" style="margin-top: 12px;">
        <van-cell title="当前学期信息" />
        <van-cell title="学期名称" :value="currentTerm.termname" />
        <van-cell title="开始日期" :value="currentTerm.termstart" />
        <van-cell title="结束日期" :value="currentTerm.termend" />
        <van-cell title="归档状态">
          <template #value>
            <van-tag :type="currentTerm.islocked ? 'danger' : 'success'" size="small">
              {{ currentTerm.islocked ? '已归档' : '未归档' }}
            </van-tag>
          </template>
        </van-cell>
      </van-cell-group>

      <!-- 学期数据统计 -->
      <van-cell-group inset v-if="currentTermStats" style="margin-top: 12px;">
        <van-cell title="学期数据统计" />
        <van-cell title="使用记录" :value="`${currentTermStats.record_count || 0}条`" />
        <van-cell title="维护记录" :value="`${currentTermStats.maintain_count || 0}条`" />
        <van-cell title="课表记录" :value="`${currentTermStats.class_count || 0}条`" />
        <van-cell title="预约记录" :value="`${currentTermStats.booking_count || 0}条`" />
      </van-cell-group>

      <!-- 警告提示 -->
      <van-notice-bar
        v-if="currentTerm && !currentTerm.islocked"
        type="warning"
        :scrollable="false"
        wrapable
        style="margin: 12px;"
      >
        <div style="line-height: 1.6;">
          <div><strong>重要提示：</strong></div>
          <div>• 归档后除超级管理员外其他用户只能查看不能修改</div>
          <div>• 归档操作不可逆，请谨慎操作</div>
          <div>• 归档将锁定所选类型的所有记录</div>
        </div>
      </van-notice-bar>

      <!-- 归档选项 -->
      <van-cell-group inset v-if="currentTerm && !currentTerm.islocked" style="margin-top: 12px;">
        <van-cell title="选择要归档的数据类型" />
        <van-cell :value="`共 ${currentTermStats?.record_count || 0} 条`">
          <template #title>
            <div style="display: flex; align-items: center;">
              <van-icon name="records" size="20px" color="#1989fa" style="margin-right: 12px;" />
              <span>使用记录</span>
            </div>
          </template>
          <template #right-icon>
            <van-checkbox v-model="archiveTypes.records" />
          </template>
        </van-cell>
        <van-cell :value="`共 ${currentTermStats?.maintain_count || 0} 条`">
          <template #title>
            <div style="display: flex; align-items: center;">
              <van-icon name="setting-o" size="20px" color="#ff976a" style="margin-right: 12px;" />
              <span>维护记录</span>
            </div>
          </template>
          <template #right-icon>
            <van-checkbox v-model="archiveTypes.maintain" />
          </template>
        </van-cell>
        <van-cell :value="`共 ${currentTermStats?.class_count || 0} 条`">
          <template #title>
            <div style="display: flex; align-items: center;">
              <van-icon name="orders-o" size="20px" color="#07c160" style="margin-right: 12px;" />
              <span>课表记录</span>
            </div>
          </template>
          <template #right-icon>
            <van-checkbox v-model="archiveTypes.classes" />
          </template>
        </van-cell>
        <van-cell :value="`共 ${currentTermStats?.booking_count || 0} 条`">
          <template #title>
            <div style="display: flex; align-items: center;">
              <van-icon name="calendar-o" size="20px" color="#7232dd" style="margin-right: 12px;" />
              <span>预约记录</span>
            </div>
          </template>
          <template #right-icon>
            <van-checkbox v-model="archiveTypes.booking" />
          </template>
        </van-cell>
      </van-cell-group>

      <!-- 归档按钮 -->
      <div style="padding: 16px;" v-if="currentTerm && !currentTerm.islocked">
        <van-button
          type="danger"
          block
          :loading="loading"
          :disabled="!hasSelectedTypes"
          @click="handleArchiveMobile"
        >
          {{ loading ? '归档中...' : '确认归档' }}
        </van-button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/utils/api'
import { useMobile } from '@/composables/useMobile'
import { formatDateChinese } from '@/utils/formatUtils'

export default {
  name: 'ArchiveTerm',
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    // 获取用户信息（从sessionStorage）
    const user = ref(JSON.parse(sessionStorage.getItem('user') || '{}'))
    
    const currentTerm = ref(null)
    const currentTermStats = ref(null)
    const archivedTerms = ref([])
    const backUrl = ref('/')
    const archiveTypes = ref({
      records: true,
      maintain: false,
      classes: false,
      booking: false,
      equipment_maintenance: false,
      equipment_check: false
    })
    const loading = ref(false)
    
    // 移动端初始化
    const { init: initMobile, loadVantComponents } = useMobile()
    
    // 移动端归档处理
    const handleArchiveMobile = async () => {
      if (!hasSelectedTypes.value) {
        const { showFailToast } = await import('@/utils/mobileDialog')
        showFailToast('请至少选择一种要归档的数据类型')
        return
      }
      
      try {
        const { showConfirmDialog } = await import('@/utils/mobileDialog')
        await showConfirmDialog({
          title: '确认归档',
          message: '确定要归档选中的数据类型吗？此操作不可逆！',
          type: 'warning'
        })
        await handleArchive()
        const { showSuccessToast } = await import('@/utils/mobileDialog')
        showSuccessToast('归档成功')
      } catch (err) {
        if (err !== 'cancel') {
          const { showFailToast } = await import('@/utils/mobileDialog')
          showFailToast('归档失败：' + (err.message || '未知错误'))
        }
      }
    }

    const hasSelectedTypes = computed(() => {
      return Object.values(archiveTypes.value).some(v => v)
    })

    const handleArchive = async () => {
      // 检查是否有选中的类型
      if (!hasSelectedTypes.value) {
        const { showFailToast } = await import('@/utils/mobileDialog')
        await showFailToast('请至少选择一种要归档的数据类型')
        return
      }

      loading.value = true
      
      try {
        const selectedTypes = Object.keys(archiveTypes.value).filter(k => archiveTypes.value[k])
        
        // 后端路由是 /api/userinfo/archive_current_term_records/（注意是下划线）
        const response = await api.post('/userinfo/archive_current_term_records/', { archive_types: selectedTypes })
        
        const { showSuccessToast, showFailToast } = await import('@/utils/mobileDialog')
        
        if (response && response.success) {
          await showSuccessToast('归档成功！')
          // 重新加载数据以更新页面
          await loadData()
        } else {
          const errorMsg = response?.message || '归档失败，请重试'
          await showFailToast(errorMsg)
        }
      } catch (err) {
        console.error('归档失败:', err)
        
        const { showFailToast } = await import('@/utils/mobileDialog')
        
        let errorMsg = '归档失败'
        if (err.response?.data?.message) {
          errorMsg = err.response.data.message
        } else if (err.message) {
          errorMsg = err.message
        }
        await showFailToast(errorMsg)
      } finally {
        loading.value = false
      }
    }

    const formatDate = (dateString) => {
      return formatDateChinese(dateString)
    }

    const loadData = async () => {
      try {
        // 后端路由是 /api/userinfo/archive_term/（注意是下划线）
        const response = await api.get('/userinfo/archive_term/')
        
        if (response.success) {
          // 后端返回的数据结构：current_term 包含 stats 字段
          currentTerm.value = response.current_term
          // 从 current_term.stats 中提取统计数据
          if (response.current_term && response.current_term.stats) {
            currentTermStats.value = response.current_term.stats
          } else {
            currentTermStats.value = null
          }
          // 获取已归档学期列表
          archivedTerms.value = response.archived_terms || []
          backUrl.value = response.back_url || '/'
        } else {
          console.error('Load data error:', response.message)
        }
      } catch (err) {
        console.error('Load data error:', err)
        // 设置默认值，避免页面完全空白
        currentTerm.value = null
        currentTermStats.value = null
      }
    }

    const goBack = () => {
      router.go(-1)
    }

    onMounted(() => {
      // 初始化移动端检测
      const cleanupMobile = initMobile()
      onUnmounted(() => {
        if (cleanupMobile) cleanupMobile()
      })
      
      // 预加载 Vant 组件
      setTimeout(() => {
        loadVantComponents()
      }, 200)
      
      loadData()
    })

    return {
      currentTerm,
      currentTermStats,
      archivedTerms,
      backUrl,
      archiveTypes,
      loading,
      hasSelectedTypes,
      handleArchive,
      handleArchiveMobile,
      user,
      formatDate,
      goBack
    }
  }
}
</script>



