<template>
  <div class="mobile-page">
    <van-nav-bar title="设备故障上报" left-arrow @click-left="goBack">
      <template #right>
        <van-icon name="home-o" size="20" @click="goHome" />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <van-notice-bar left-icon="warning-o" color="#ff976a" background="#fffbe8">
        请准确填写设备编号和故障描述，提交后将通知管理员处理
      </van-notice-bar>

      <van-skeleton v-if="isLoading" :row="5" animated />

      <template v-else>
        <van-cell-group inset title="故障信息">
          <van-field
            v-model="formData.sxsname_text"
            is-link
            readonly
            label="实训室"
            placeholder="请选择实训室"
            required
            @click="openSxsPicker"
          />
          
          <van-field
            v-model="formData.device_code"
            label="电脑编号"
            placeholder="请输入电脑编号 (如: 01)"
            required
            clearable
          />
          
          <van-field
            v-model="formData.reporter"
            label="上报人"
            placeholder="请输入上报人姓名"
            required
            clearable
          />
          
          <van-field
            v-model="formData.maintainrequestdate"
            is-link
            readonly
            label="上报时间"
            placeholder="请选择日期"
            required
            @click="showDatePicker = true"
          />
        </van-cell-group>

        <van-cell-group inset title="故障描述">
          <van-field
            v-model="formData.maintainrecordcontent"
            rows="4"
            autosize
            type="textarea"
            label="故障描述"
            placeholder="请详细描述设备故障情况"
            required
          />
        </van-cell-group>
      </template>

      <div class="form-actions">
        <van-button type="primary" block round :loading="loading" @click="handleSubmit">
          立即提交
        </van-button>
      </div>
    </div>

    <van-popup v-model:show="showSxsPicker" position="bottom" round>
      <van-picker
        title="选择实训室"
        :columns="sxsOptions"
        @confirm="onSxsConfirm"
        @cancel="showSxsPicker = false"
      />
    </van-popup>

    <van-popup v-model:show="showDatePicker" position="bottom" round>
      <van-date-picker
        title="选择上报时间"
        v-model="selectedDate"
        @confirm="onDateConfirm"
        @cancel="showDatePicker = false"
      />
    </van-popup>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from '@/composables/useApi'
import { useAuth } from '@/composables/useAuth'
import { useNavigation } from '@/utils/routeDecision'
import { showSuccess, showError } from '@/utils/errorHandler'

export default {
  name: 'ReportMaintenance',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const { user } = useAuth()
    const { goHome, smartBack } = useNavigation()
    
    const loading = ref(false)
    const isLoading = ref(true)
    const showSxsPicker = ref(false)
    const showDatePicker = ref(false)
    const sxsList = ref([])
    const sxsAdminMap = ref({})
    const selectedDate = ref(['2024', '01', '01'])
    
    const formData = ref({
      sxsname: '',
      sxsname_text: '',
      device_code: '',
      reporter: '',
      maintainrequestdate: '',
      maintainrecordcontent: ''
    })
    
    const apiComposable = useApi('', { immediate: false })
    
    const sxsOptions = computed(() => {
      return sxsList.value.map(sxs => ({
        text: `${sxs.sxsname} (${sxs.sxsno})`,
        value: sxs.id
      }))
    })
    
    const openSxsPicker = () => {
      showSxsPicker.value = true
    }
    
    const onSxsConfirm = ({ selectedOptions }) => {
      const selected = selectedOptions[0]
      formData.value.sxsname = selected.value
      formData.value.sxsname_text = selected.text
      showSxsPicker.value = false
    }
    
    const onDateConfirm = ({ selectedValues }) => {
      formData.value.maintainrequestdate = selectedValues.join('-')
      showDatePicker.value = false
    }
    
    const loadFormData = async () => {
      isLoading.value = true
      try {
        const response = await apiComposable.get({ is_fault_report: 'true' }, { url: '/sxs/addmaintain/0/' })
        
        if (response && response.form_fields) {
          if (response.form_fields.sxs_list) {
            sxsList.value = response.form_fields.sxs_list
            response.form_fields.sxs_list.forEach(sxs => {
              const adminId = typeof sxs.sxsadmin === 'object' ? sxs.sxsadmin?.id : sxs.sxsadmin
              if (sxs.id) {
                sxsAdminMap.value[sxs.id] = {
                  adminId: adminId,
                  name: sxs.sxsname,
                  no: sxs.sxsno
                }
              }
            })
          }
          
          formData.value.reporter = user.value?.nikename || user.value?.username || ''
          formData.value.maintainrequestdate = new Date().toISOString().split('T')[0]
          
          if (route.query?.from_record === 'true') {
            if (route.query.maintainrequestdate) {
              formData.value.maintainrequestdate = route.query.maintainrequestdate
            }
            if (route.query.sxsid && route.query.sxsid !== '0') {
              formData.value.sxsname = parseInt(route.query.sxsid)
              const sxs = sxsList.value.find(s => s.id === parseInt(route.query.sxsid))
              if (sxs) {
                formData.value.sxsname_text = `${sxs.sxsname} (${sxs.sxsno})`
              }
            }
          }
        }
      } catch (err) {
        showError('加载表单失败')
      } finally {
        isLoading.value = false
      }
    }
    
    const handleSubmit = async () => {
      if (!formData.value.sxsname) {
        showError('请选择实训室')
        return
      }
      if (!formData.value.device_code) {
        showError('请输入电脑编号')
        return
      }
      if (!formData.value.reporter) {
        showError('请输入上报人')
        return
      }
      if (!formData.value.maintainrequestdate) {
        showError('请选择上报时间')
        return
      }
      if (!formData.value.maintainrecordcontent) {
        showError('请填写故障描述')
        return
      }
      
      loading.value = true
      
      try {
        const submitData = {
          sxsname: formData.value.sxsname,
          device_code: formData.value.device_code,
          reporter: formData.value.reporter,
          maintainrequestdate: formData.value.maintainrequestdate,
          maintainrecordcontent: `[设备编号:${formData.value.device_code}] ${formData.value.maintainrecordcontent}`,
          maintaintype: 3,
          from_record: 'true',
          ismaintaind: false
        }
        
        const sxsId = formData.value.sxsname
        const apiPath = `/sxs/addmaintain/${sxsId}/`
        const response = await apiComposable.post(submitData, { url: apiPath })
        
        if (response && response.success) {
          const sxsInfo = sxsAdminMap.value[sxsId]
          if (sxsInfo && sxsInfo.adminId) {
            const messageData = {
              recipient: sxsInfo.adminId,
              subject: `【故障上报】${sxsInfo.name} (${sxsInfo.no}) - ${formData.value.device_code}`,
              content: `【设备故障上报】\n实训室：${sxsInfo.name} (${sxsInfo.no})\n电脑编号：${formData.value.device_code}\n上报人：${formData.value.reporter}\n上报时间：${formData.value.maintainrequestdate}\n故障描述：\n${formData.value.maintainrecordcontent}`
            }
            apiComposable.post(messageData, { url: '/sxs/send_message/' }).catch(e => console.error('发送通知失败', e))
          }
          
          showSuccess('故障上报成功！已通知管理员')
          setTimeout(() => {
            router.push('/')
          }, 1500)
        } else {
          showError(response?.message || '上报失败')
        }
      } catch (err) {
        showError(err.response?.data?.message || '上报失败')
      } finally {
        loading.value = false
      }
    }
    
    const goBack = () => router.go(-1)
    
    onMounted(() => {
      const today = new Date()
      selectedDate.value = [
        String(today.getFullYear()),
        String(today.getMonth() + 1).padStart(2, '0'),
        String(today.getDate()).padStart(2, '0')
      ]
      loadFormData()
    })
    
    return {
      formData,
      loading,
      isLoading,
      showSxsPicker,
      showDatePicker,
      sxsOptions,
      selectedDate,
      openSxsPicker,
      onSxsConfirm,
      onDateConfirm,
      handleSubmit,
      goBack,
      goHome
    }
  }
}
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
