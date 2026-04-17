<template>
  <div class="mobile-page">
    <van-nav-bar title="编辑实训室" left-arrow @click-left="goBack">
      <template #right>
        <van-icon name="home-o" size="20" @click="goHome" />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <van-skeleton v-if="loading" :row="4" animated />

      <template v-else>
        <van-cell-group inset title="基本信息">
          <van-field
            v-model="formData.sxsname"
            label="实训室名称"
            placeholder="请输入实训室名称"
            required
            clearable
          />
          
          <van-field
            v-model="formData.sxsno"
            label="实训室编号"
            placeholder="请输入实训室编号"
            clearable
          />
          
          <van-field
            v-model="formData.sxslocation"
            label="位置"
            placeholder="请输入实训室位置"
            clearable
          />
        </van-cell-group>

        <van-cell-group v-if="canAssignAdmin" inset title="管理员分配">
          <van-field
            v-model="formData.admin"
            is-link
            readonly
            label="管理员"
            placeholder="请选择管理员"
            @click="showAdminPicker = true"
          />
        </van-cell-group>

        <van-cell-group inset title="备注信息">
          <van-field
            v-model="formData.sxsdesc"
            rows="3"
            autosize
            type="textarea"
            label="备注"
            placeholder="请输入备注信息"
          />
        </van-cell-group>
      </template>

      <div class="form-actions">
        <van-button type="primary" block round :loading="submitting" @click="handleSubmit">
          保存修改
        </van-button>
      </div>
    </div>

    <van-popup v-model:show="showAdminPicker" position="bottom" round>
      <van-picker
        title="选择管理员"
        :columns="adminOptions"
        @confirm="onAdminConfirm"
        @cancel="showAdminPicker = false"
      />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNavigation } from '@/utils/routeDecision'
import { useApi } from '@/composables/useApi'
import { useAuth } from '@/composables/useAuth'
import { showSuccess, showError } from '@/utils/errorHandler'

const route = useRoute()
const router = useRouter()
const { goHome, smartBack } = useNavigation()
const { isSuperuser, isDepartAdmin } = useAuth()

const canAssignAdmin = computed(() => isSuperuser.value || isDepartAdmin.value)

const loading = ref(false)
const submitting = ref(false)
const showAdminPicker = ref(false)
const adminOptions = ref([])

const formData = ref({
  sxsname: '',
  sxsno: '',
  sxslocation: '',
  sxsdesc: '',
  admin: '',
  admin_id: ''
})

const apiComposable = useApi('', { immediate: false })

const loadFormData = async () => {
  loading.value = true
  try {
    const sxsId = route.params.id
    const response = await apiComposable.get({}, { url: `/sxs/editsxs/${sxsId}/0/` })
    
    if (response && response.initial_data) {
      formData.value.sxsname = response.initial_data.sxsname || ''
      formData.value.sxsno = response.initial_data.sxsno || ''
      formData.value.sxslocation = response.initial_data.sxslocation || ''
      formData.value.sxsdesc = response.initial_data.sxsdesc || ''
      formData.value.admin_id = response.initial_data.admin_id || 0
    }
  } catch (err) {
    showError('加载实训室信息失败')
  } finally {
    loading.value = false
  }
}

const loadAdmins = async () => {
  if (!canAssignAdmin.value) return
  
  try {
    const apiComposable = useApi('', { immediate: false })
    const response = await apiComposable.get({}, { url: '/sxs/addsxs/' })
    if (response && response.admins) {
      adminOptions.value = response.admins.map(a => ({
        text: a.id === 0 ? '未分配' : `${a.nikename || ''} (${a.username})`,
        value: a.id
      }))
      
      const currentAdmin = response.admins.find(a => a.id === formData.value.admin_id)
      if (currentAdmin) {
        formData.value.admin = currentAdmin.id === 0 ? '未分配' : `${currentAdmin.nikename || ''} (${currentAdmin.username})`
      }
    }
  } catch (err) {
    console.error('Load admins error:', err)
  }
}

const onAdminConfirm = ({ selectedOptions }) => {
  formData.value.admin = selectedOptions[0].text
  formData.value.admin_id = selectedOptions[0].value
  showAdminPicker.value = false
}

const handleSubmit = async () => {
  submitting.value = true
  try {
    const sxsId = route.params.id
    const submitData = {
      sxsname: formData.value.sxsname,
      sxsno: formData.value.sxsno,
      sxslocation: formData.value.sxslocation,
      sxsdesc: formData.value.sxsdesc
    }
    
    if (canAssignAdmin.value && (formData.value.admin_id !== undefined && formData.value.admin_id !== null && formData.value.admin_id !== '')) {
      submitData.sxsadmin = formData.value.admin_id
    }
    
    const response = await apiComposable.post(submitData, { url: `/sxs/editsxs/${sxsId}/0/` })
    
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

onMounted(async () => {
  await loadFormData()
  await loadAdmins()
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
