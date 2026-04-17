<template>
  <div class="mobile-page">
    <van-nav-bar title="添加实训室" left-arrow @click-left="goBack">
      <template #right>
        <van-icon name="home-o" size="20" @click="goHome" />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <van-notice-bar left-icon="info-o" color="#1989fa" background="#ecf9ff">
        请填写实训室基本信息，带 * 为必填项
      </van-notice-bar>

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
          required
          clearable
        />
        
        <van-field
          v-model="formData.sxslocation"
          label="位置"
          placeholder="请输入实训室位置"
          clearable
        />
        
        <van-field
          v-model="formData.sxsnum"
          type="number"
          label="工位数"
          placeholder="请输入工位数"
        />
        
        <van-field
          v-model="formData.sxsstatus"
          is-link
          readonly
          label="状态"
          placeholder="请选择状态"
          @click="showStatusPicker = true"
        />
        
        <van-field
          v-model="formData.admin"
          is-link
          readonly
          label="管理员"
          placeholder="请选择管理员"
          @click="showAdminPicker = true"
        />
      </van-cell-group>

      <van-cell-group inset title="其他信息">
        <van-field
          v-model="formData.sxsdemo"
          rows="3"
          autosize
          type="textarea"
          label="描述"
          placeholder="请输入实训室描述"
        />
      </van-cell-group>

      <div class="form-actions">
        <van-button type="primary" block round :loading="submitting" @click="handleSubmit">
          立即创建
        </van-button>
      </div>
    </div>

    <van-popup v-model:show="showStatusPicker" position="bottom" round>
      <van-picker
        title="选择状态"
        :columns="statusOptions"
        @confirm="onStatusConfirm"
        @cancel="showStatusPicker = false"
      />
    </van-popup>

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
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNavigation } from '@/utils/routeDecision'
import { useAuth } from '@/composables/useAuth'
import { useApi } from '@/composables/useApi'
import { showSuccess, showError } from '@/utils/errorHandler'

const route = useRoute()
const router = useRouter()
const { user } = useAuth()
const { goHome, smartBack } = useNavigation()

const submitting = ref(false)
const showStatusPicker = ref(false)
const showAdminPicker = ref(false)
const adminList = ref([])

const formData = ref({
  sxsname: '',
  sxsno: '',
  sxslocation: '',
  sxsnum: '',
  sxsstatus: '正常',
  admin: '',
  admin_id: '',
  sxsdemo: ''
})

const statusOptions = [
  { text: '正常', value: '正常' },
  { text: '维护中', value: '维护中' },
  { text: '停用', value: '停用' }
]

const adminOptions = ref([])

const onStatusConfirm = ({ selectedOptions }) => {
  formData.value.sxsstatus = selectedOptions[0].text
  showStatusPicker.value = false
}

const onAdminConfirm = ({ selectedOptions }) => {
  formData.value.admin = selectedOptions[0].text
  formData.value.admin_id = selectedOptions[0].value
  showAdminPicker.value = false
}

const handleSubmit = async () => {
  if (!formData.value.sxsname) {
    showError('请输入实训室名称')
    return
  }
  if (!formData.value.sxsno) {
    showError('请输入实训室编号')
    return
  }
  
  submitting.value = true
  
  try {
    const submitData = {
      sxsname: formData.value.sxsname,
      sxsno: formData.value.sxsno,
      sxslocation: formData.value.sxslocation,
      sxsnum: formData.value.sxsnum ? parseInt(formData.value.sxsnum) : 0,
      sxsstatus: formData.value.sxsstatus,
      sxsdemo: formData.value.sxsdemo
    }
    
    if (formData.value.admin_id !== undefined && formData.value.admin_id !== null && formData.value.admin_id !== '') {
      submitData.sxsadmin = formData.value.admin_id
    }
    
    const apiComposable = useApi('', { immediate: false })
    const response = await apiComposable.post(submitData, { url: '/sxs/addsxs/' })
    
    if (response && response.success) {
      showSuccess('实训室创建成功')
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

const loadAdmins = async () => {
  try {
    const apiComposable = useApi('', { immediate: false })
    const response = await apiComposable.get({}, { url: '/sxs/addsxs/' })
    if (response && response.admins) {
      adminList.value = response.admins
      adminOptions.value = response.admins.map(a => ({
        text: a.id === 0 ? '未分配' : `${a.nikename || ''} (${a.username})`,
        value: a.id
      }))
    }
  } catch (err) {
    console.error('Load admins error:', err)
  }
}

const goBack = () => {
  router.go(-1)
}

watch(() => user.value, (newUser) => {
  if (newUser && !newUser.is_superuser && !newUser.is_departadmin) {
    router.replace('/add-device')
  }
}, { immediate: true })

onMounted(() => {
  if (user.value && !user.value.is_superuser && !user.value.is_departadmin) {
    router.replace('/add-device')
    return
  }
  loadAdmins()
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
