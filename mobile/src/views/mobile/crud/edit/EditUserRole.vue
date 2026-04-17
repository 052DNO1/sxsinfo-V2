<template>
  <div class="mobile-page">
    <van-nav-bar title="编辑用户角色" left-arrow @click-left="goBack">
      <template #right>
        <van-icon name="home-o" size="20" @click="goHome" />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <van-skeleton v-if="loading" :row="5" animated />

      <template v-else>
        <van-cell-group inset title="用户信息">
          <van-cell title="用户名" :value="user?.username" />
          <van-cell title="昵称" :value="user?.nikename" />
        </van-cell-group>

        <van-cell-group inset title="角色设置">
          <van-cell v-for="role in roles" :key="role.key" :title="role.label">
            <template #right-icon>
              <van-switch v-model="role.value" />
            </template>
          </van-cell>
        </van-cell-group>
      </template>

      <div class="form-actions">
        <van-button type="primary" block round :loading="submitting" @click="handleSubmit">
          保存角色
        </van-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from '@/composables/useApi'
import { useNavigation } from '@/utils/routeDecision'
import { showSuccess, showError } from '@/utils/errorHandler'

const route = useRoute()
const router = useRouter()
const { goHome, smartBack } = useNavigation()

const loading = ref(false)
const submitting = ref(false)
const user = ref(null)
const roles = ref([])

const apiComposable = useApi('', { immediate: false })

const loadData = async () => {
  loading.value = true
  try {
    const userId = route.params.id
    const response = await apiComposable.get({}, { url: `/userinfo/updateuserrole/${userId}/` })
    
    if (response) {
      user.value = response.user
      const currentPermissions = response.current_permissions || []
      const permissionChoices = response.permission_choices || [
        { value: 1, label: '教师' },
        { value: 2, label: '实训室管理员' },
        { value: 4, label: '分院管理员' }
      ]
      
      roles.value = permissionChoices.map(choice => ({
        key: choice.value,
        label: choice.label,
        value: currentPermissions.includes(choice.value)
      }))
    }
  } catch (err) {
    showError('加载用户角色失败')
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  submitting.value = true
  try {
    const userId = route.params.id
    const permissions = roles.value
      .filter(role => role.value)
      .map(role => role.key)
    
    const submitData = { permissions }
    
    const response = await apiComposable.post(submitData, { url: `/userinfo/updateuserrole/${userId}/` })
    
    if (response && response.success) {
      showSuccess('角色保存成功')
      setTimeout(() => smartBack(), 1500)
    } else {
      showError(response?.message || '保存失败')
    }
  } catch (err) {
    showError(err.response?.data?.message || '保存失败')
  } finally {
    submitting.value = false
  }
}

const goBack = () => router.go(-1)

onMounted(() => {
  loadData()
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
  padding: 12px;
  padding-bottom: 100px;
}

.form-actions {
  padding: 16px;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
}
</style>
