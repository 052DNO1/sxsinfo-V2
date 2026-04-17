<template>
  <div class="mobile-page">
    <van-nav-bar title="编辑分院" left-arrow @click-left="goBack">
      <template #right>
        <van-icon name="home-o" size="20" @click="goHome" />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <van-skeleton v-if="loading" :row="5" animated />

      <template v-else>
        <van-cell-group inset title="基本信息">
          <van-field
            v-model="formData.departname"
            label="分院名称"
            placeholder="请输入分院名称"
            required
            clearable
          />
        </van-cell-group>

        <van-cell-group inset title="其他信息">
          <van-field
            v-model="formData.departdemo"
            rows="3"
            autosize
            type="textarea"
            label="分院描述"
            placeholder="请输入分院描述"
          />
        </van-cell-group>
      </template>

      <div class="form-actions">
        <van-button type="primary" block round :loading="submitting" @click="handleSubmit">
          保存修改
        </van-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNavigation } from '@/utils/routeDecision'
import { useApi } from '@/composables/useApi'
import { showSuccess, showError } from '@/utils/errorHandler'

const route = useRoute()
const router = useRouter()
const { goHome, smartBack } = useNavigation()

const loading = ref(false)
const submitting = ref(false)
const formData = ref({
  departname: '',
  departdemo: ''
})

const apiComposable = useApi('', { immediate: false })

const loadFormData = async () => {
  loading.value = true
  try {
    const deptId = route.params.id
    const response = await apiComposable.get({}, { url: `/userinfo/updatedept/${deptId}/` })
    
    if (response && response.dept) {
      formData.value.departname = response.dept.departname || ''
      formData.value.departdemo = response.dept.departdemo || ''
    }
  } catch (err) {
    showError('加载分院信息失败')
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!formData.value.departname) {
    showError('请输入分院名称')
    return
  }
  
  submitting.value = true
  try {
    const deptId = route.params.id
    const response = await apiComposable.post(formData.value, { url: `/userinfo/updatedept/${deptId}/` })
    
    if (response && response.success) {
      showSuccess(response.message || '保存成功')
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
  loadFormData()
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
