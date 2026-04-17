<template>
  <div class="mobile-page">
    <van-nav-bar title="添加用户" left-arrow @click-left="goBack">
      <template #right>
        <van-icon name="home-o" size="20" @click="goHome" />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <van-notice-bar left-icon="info-o" color="#1989fa" background="#ecf9ff">
        请填写用户基本信息，带 * 为必填项
      </van-notice-bar>

      <van-skeleton v-if="loading" :row="5" animated />

      <van-form v-else @submit="handleSubmit">
        <van-cell-group inset title="基本信息">
          <van-field
            v-model="formData.username"
            label="用户名"
            placeholder="请输入用户名"
            required
            clearable
            :rules="[{ required: true, message: '请输入用户名' }]"
          />

          <van-field
            v-model="formData.nikename"
            label="昵称"
            placeholder="请输入昵称"
            clearable
          />

          <van-field
            v-model="formData.email"
            type="email"
            label="邮箱"
            placeholder="请输入邮箱"
            required
            clearable
            :rules="emailRules"
          />

          <van-field
            v-model="formData.phone"
            type="tel"
            label="手机号"
            placeholder="请输入手机号"
            clearable
            :rules="phoneRules"
          />

          <van-field
            v-if="showDeptField"
            v-model="formData.depart"
            is-link
            readonly
            label="部门"
            placeholder="请选择部门"
            required
            :rules="[{ required: true, message: '请选择部门' }]"
            @click="showDeptPicker = true"
          />
        </van-cell-group>

        <van-cell-group inset title="角色设置">
        
          <van-cell title="分院管理员">
            <template #right-icon>
              <van-switch v-model="formData.is_departadmin" />
            </template>
          </van-cell>

          <van-cell title="实训室管理员">
            <template #right-icon>
              <van-switch v-model="formData.is_sxsadmin" />
            </template>
          </van-cell>

          <van-cell title="教师">
            <template #right-icon>
              <van-switch v-model="formData.is_teacher" />
            </template>
          </van-cell>
        </van-cell-group>

        <van-cell-group inset title="其他信息">
          <van-field
            v-model="formData.memo"
            rows="3"
            autosize
            type="textarea"
            label="备注"
            placeholder="请输入备注"
          />
        </van-cell-group>

        <div class="form-actions">
          <van-button type="primary" block round :loading="submitting" native-type="submit">
            立即创建
          </van-button>
        </div>
      </van-form>
    </div>

    <van-popup v-model:show="showDeptPicker" position="bottom" round>
      <van-picker
        title="选择部门"
        :columns="deptOptions"
        @confirm="onDeptConfirm"
        @cancel="showDeptPicker = false"
      />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNavigation } from '@/utils/routeDecision'
import { useAuth } from '@/composables/useAuth'
import { useApi } from '@/composables/useApi'
import { showSuccess, showError } from '@/utils/errorHandler'
import { validateEmail, validatePhone } from '@/utils/validation'

const route = useRoute()
const router = useRouter()
const { goHome, smartBack } = useNavigation()
const { user } = useAuth()

const loading = ref(false)
const submitting = ref(false)
const showDeptPicker = ref(false)
const deptOptions = ref([])

const showDeptField = computed(() => {
  return user.value && user.value.is_superuser
})

const emailRules = [
  { required: true, message: '请输入邮箱' },
  { pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: '请输入正确的邮箱格式（必须包含@）' }
]

const phoneRules = [
  { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的11位手机号码' }
]

const formData = ref({
  username: '',
  nikename: '',
  email: '',
  phone: '',
  depart: '',
  depart_id: '',
  is_departadmin: false,
  is_sxsadmin: false,
  is_teacher: false,
  memo: ''
})

const onDeptConfirm = ({ selectedOptions }) => {
  formData.value.depart = selectedOptions[0].text
  formData.value.depart_id = selectedOptions[0].value
  showDeptPicker.value = false
}

const loadDepts = async () => {
  loading.value = true
  const typeid = route.params.id || '1'
  try {
    const apiComposable = useApi('', { immediate: false })
    const response = await apiComposable.get({}, { url: `/userinfo/adduser/${typeid}/` })
    console.log('AddUser API response:', response)
    if (response && response.departments) {
      deptOptions.value = response.departments.map(d => ({
        text: d.departname || d.name,
        value: d.id
      }))
      console.log('Dept options:', deptOptions.value)
    } else if (response && response.dept_list) {
      deptOptions.value = response.dept_list.map(d => ({
        text: d.departname || d.name,
        value: d.id
      }))
      console.log('Dept options from dept_list:', deptOptions.value)
    } else if (response && Array.isArray(response.object_list)) {
      deptOptions.value = response.object_list.map(d => ({
        text: d.departname || d.name,
        value: d.id
      }))
      console.log('Dept options from object_list:', deptOptions.value)
    }
  } catch (err) {
    console.error('Load depts error:', err)
    showError('加载部门列表失败')
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  submitting.value = true
  
  try {
    const submitData = {
      username: formData.value.username,
      nikename: formData.value.nikename,
      email: formData.value.email,
      phone: formData.value.phone,
      is_departadmin: formData.value.is_departadmin,
      is_sxsadmin: formData.value.is_sxsadmin,
      is_teacher: formData.value.is_teacher,
      memo: formData.value.memo
    }
    
    if (showDeptField.value && formData.value.depart_id) {
      submitData.depart = formData.value.depart_id
    }
    
    const typeid = route.params.id || '1'
    const apiComposable = useApi('', { immediate: false })
    const response = await apiComposable.post(submitData, { url: `/userinfo/adduser/${typeid}/` })
    
    if (response && response.success) {
      showSuccess('用户创建成功')
      setTimeout(() => {
        smartBack()
      }, 1500)
    } else {
      showError(response?.message || '创建失败')
    }
  } catch (err) {
    showError(err.response?.data?.message || '创建失败')
  } finally {
    submitting.value = false
  }
}

const goBack = () => router.go(-1)

onMounted(() => {
  loadDepts()
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