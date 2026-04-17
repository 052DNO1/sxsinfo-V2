<template>
  <div class="mobile-page">
    <van-nav-bar :title="isSelfEdit ? '修改个人信息' : '编辑用户'" left-arrow @click-left="goBack">
      <template #right>
        <van-icon name="home-o" size="20" @click="goHome" />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <van-skeleton v-if="loading" :row="5" animated />

      <template v-else>
        <van-cell-group inset title="基本信息">
          <van-field
            v-model="formData.username"
            label="用户名"
            placeholder="请输入用户名"
            readonly
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
            clearable
          />

          <van-field
            v-model="formData.phone"
            type="tel"
            label="手机号"
            placeholder="请输入手机号"
            clearable
          />

          <van-field
            v-if="showDeptField"
            v-model="formData.depart"
            is-link
            readonly
            label="部门"
            placeholder="请选择部门"
            @click="showDeptPicker = true"
          />
        </van-cell-group>

        <van-cell-group v-if="!isSelfEdit" inset title="角色设置">
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
      </template>

      <div class="form-actions">
        <van-button type="primary" block round :loading="submitting" @click="handleSubmit">
          保存修改
        </van-button>
      </div>
    </div>

    <van-popup v-model:show="showDeptPicker" position="bottom" round>
      <van-picker
        title="选择部门"
        :columns="deptOptions"
        :model-value="pickerDeptValue"
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
import { showSuccess, showError, showConfirmDialog } from '@/utils/errorHandler'

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

const isSelfEdit = computed(() => {
  const userId = route.params.id
  return !userId || (user.value && String(user.value.id) === String(userId))
})

const pickerDeptValue = computed(() => {
  if (formData.value.depart_id && deptOptions.value.length > 0) {
    return [String(formData.value.depart_id)]
  }
  return []
})

const formData = ref({
  id: '',
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

const onDeptConfirm = ({ selectedOptions, selectedValues }) => {
  if (selectedOptions && selectedOptions.length > 0) {
    formData.value.depart = selectedOptions[0].text
    formData.value.depart_id = selectedOptions[0].value
  } else if (selectedValues && selectedValues.length > 0) {
    const selected = deptOptions.value.find(d => String(d.value) === String(selectedValues[0]))
    if (selected) {
      formData.value.depart = selected.text
      formData.value.depart_id = selected.value
    }
  }
  showDeptPicker.value = false
}

const loadDepts = async () => {
  try {
    const apiComposable = useApi('', { immediate: false })
    const response = await apiComposable.get({}, { url: '/userinfo/adduser/1/' })
    if (response && response.departments) {
      deptOptions.value = response.departments.map(d => ({
        text: d.departname || d.name,
        value: d.id
      }))
    } else if (response && response.dept_list) {
      deptOptions.value = response.dept_list.map(d => ({
        text: d.departname || d.name,
        value: d.id
      }))
    }
  } catch (err) {
    console.error('Load depts error:', err)
  }
}

const loadUserData = async () => {
  loading.value = true
  try {
    let userId = route.params.id
    if (!userId) {
      userId = user.value?.id
    }
    if (!userId) {
      showError('无法获取用户信息')
      return
    }
    
    const apiComposable = useApi('', { immediate: false })
    const response = await apiComposable.get({}, { url: `/userinfo/updateuserrole/${userId}/` })
    
    if (response) {
      const userData = response.user || response
      const currentPermissions = response.current_permissions || []
      const userType = userData.user_type ?? 0
      
      const hasPermission = (perm) => currentPermissions.includes(perm) || (userType & perm) !== 0
      
      const departName = userData.depart_name || userData.departname || userData.depart?.name || ''
      const departId = userData.depart_id || userData.depart?.id || ''
      
      formData.value = {
        id: userId,
        username: userData.username || '',
        nikename: userData.nikename || '',
        email: userData.email || '',
        phone: userData.phone || '',
        depart: departName,
        depart_id: departId,
        is_departadmin: hasPermission(4),
        is_sxsadmin: hasPermission(2),
        is_teacher: hasPermission(1),
        memo: userData.memo || '',
        user_type: userType
      }
    }
  } catch (err) {
    showError('加载用户信息失败')
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  submitting.value = true
  
  try {
    const permissions = []
    if (formData.value.is_teacher) permissions.push(1)
    if (formData.value.is_sxsadmin) permissions.push(2)
    if (formData.value.is_departadmin) permissions.push(4)
    
    const submitData = {
      username: formData.value.username,
      nikename: formData.value.nikename,
      email: formData.value.email,
      phone: formData.value.phone,
      permissions: permissions,
      memo: formData.value.memo
    }
    
    if (showDeptField.value && formData.value.depart_id) {
      submitData.depart = formData.value.depart_id
    }
    
    let userId = route.params.id
    if (!userId) {
      userId = user.value?.id
    }
    if (!userId) {
      showError('无法保存，用户ID缺失')
      return
    }
    const apiComposable = useApi('', { immediate: false })
    const response = await apiComposable.post(submitData, { url: `/userinfo/updateuserrole/${userId}/` })
    
    if (response && response.success) {
      showSuccess('保存成功')
      await loadUserData()
      setTimeout(() => {
        smartBack()
      }, 1500)
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
  loadUserData()
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