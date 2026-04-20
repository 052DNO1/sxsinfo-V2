<template>
  <el-dialog
    v-model="visible"
    title="⚠️ 学期设置提醒"
    width="440px"
    :close-on-click-modal="false"
    :show-close="false"
    center
    append-to-body
  >
    <div style="text-align: center; padding: 10px 0;">
      <el-icon :size="48" color="#FF9500" style="margin-bottom: 12px;">
        <WarningFilled />
      </el-icon>
      <p style="font-size: 16px; margin: 12px 0;">
        当前未设置<span style="color: #F56C6C; font-weight: bold;">"当前学期"</span>
      </p>
      <p style="color: #909399; font-size: 14px;">
        作为<span style="color: #409EFF;">系统管理员</span>，
        请立即设置当前学期以确保系统正常运行。
      </p>
    </div>
    <template #footer>
      <div style="display: flex; gap: 12px; justify-content: center;">
        <el-button type="primary" icon="CircleCheck" @click="goToSetTerm">
          立即去设置
        </el-button>
        <el-button @click="handleSkip">暂时跳过</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { WarningFilled } from '@element-plus/icons-vue'
import { useApi } from '@/core/hooks'

const visible = ref(false)
const router = useRouter()
const route = useRoute()
const { get: checkTermStatusApi } = useApi('/semesters/current/', { immediate: false })

const checkTermStatus = async () => {
  const token = localStorage.getItem('access_token') || localStorage.getItem('token') || sessionStorage.getItem('token')

  if (!token || route.path.includes('/login')) {
    visible.value = false
    return
  }

  try {
    const res = await checkTermStatusApi()
    if (res && res.success && res.data) {
      const { is_superuser, is_current } = res.data
      const hasCurrentTerm = !!is_current
      if (hasCurrentTerm) {
        visible.value = false
        localStorage.removeItem('skip_term_reminder')
      } else if (is_superuser && !hasCurrentTerm) {
        const skip = localStorage.getItem('skip_term_reminder')
        visible.value = skip !== 'true'
      } else {
        visible.value = false
      }
    }
  } catch (e) {
    visible.value = false
  }
}

const goToSetTerm = () => {
  visible.value = false
  router.push('/pc/term/list')
}

const handleSkip = () => {
  visible.value = false
  localStorage.setItem('skip_term_reminder', 'true')
}

onMounted(() => {
  checkTermStatus()
})
</script>
