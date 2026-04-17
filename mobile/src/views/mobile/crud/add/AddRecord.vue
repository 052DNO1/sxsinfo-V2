<template>
  <div class="mobile-page">
    <van-nav-bar title="添加使用记录" left-arrow @click-left="goBack">
      <template #right>
        <van-icon name="home-o" size="20" @click="goHome" />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <van-cell-group inset title="填写信息">
        <van-field
          v-model="formData.sxsname"
          is-link
          readonly
          label="实训室"
          placeholder="请选择实训室"
          @click="showSxsPicker = true"
          required
        />
        
        <van-field
          v-model="formData.sxsdate"
          is-link
          readonly
          label="使用日期"
          placeholder="请选择日期"
          @click="showDatePicker = true"
          required
        />
        
        <van-field
          v-model="formData.sxsstart"
          label="开始时间"
          placeholder="如: 08:00"
          required
        />
        
        <van-field
          v-model="formData.sxsend"
          label="结束时间"
          placeholder="如: 10:00"
        />
        
        <van-field
          v-model="formData.sxsnum"
          type="number"
          label="使用人数"
          placeholder="请输入使用人数"
          required
        />
        
        <van-field
          v-model="formData.sxsdevice_status"
          is-link
          readonly
          label="设备状态"
          placeholder="请选择设备状态"
          @click="showStatusPicker = true"
          required
        />
        
        <van-field
          v-model="formData.sxscontent"
          rows="3"
          autosize
          type="textarea"
          label="使用内容"
          placeholder="请输入使用内容"
        />
        
        <van-field
          v-model="formData.sxsmemo"
          rows="2"
          autosize
          type="textarea"
          label="备注"
          placeholder="请输入备注信息"
        />
      </van-cell-group>

      <div class="form-tips">
        <van-notice-bar left-icon="info-o" color="#1989fa" background="#ecf9ff">
          请如实填写设备状态，如设备故障将自动跳转上报
        </van-notice-bar>
      </div>

      <div class="form-actions">
        <van-button type="primary" block round :loading="loading" @click="handleSubmit">
          提交记录
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
        title="选择日期"
        v-model="selectedDate"
        @confirm="onDateConfirm"
        @cancel="showDatePicker = false"
      />
    </van-popup>

    <van-popup v-model:show="showStatusPicker" position="bottom" round>
      <van-picker
        title="选择设备状态"
        :columns="statusOptions"
        @confirm="onStatusConfirm"
        @cancel="showStatusPicker = false"
      />
    </van-popup>
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from '@/composables/useApi'
import { showSuccess, showError, showWarning } from '@/utils/errorHandler'

export default {
  name: 'AddRecord',
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    const loading = ref(false)
    const showSxsPicker = ref(false)
    const showDatePicker = ref(false)
    const showStatusPicker = ref(false)
    
    const sxsList = ref([])
    const selectedDate = ref(['2024', '01', '01'])
    
    const formData = ref({
      sxsname: '',
      sxsname_id: '',
      sxsdate: '',
      sxsstart: '',
      sxsend: '',
      sxsnum: '',
      sxsdevice_status: '',
      sxscontent: '',
      sxsmemo: ''
    })
    
    const sxsOptions = computed(() => {
      return sxsList.value.map(item => ({
        text: item.sxsname,
        value: item.id
      }))
    })
    
    const statusOptions = [
      { text: '正常', value: '正常' },
      { text: '故障', value: '故障' }
    ]
    
    const apiComposable = useApi('', { immediate: false })
    
    const onSxsConfirm = ({ selectedOptions }) => {
      const selected = selectedOptions[0]
      formData.value.sxsname = selected.text
      formData.value.sxsname_id = selected.value
      showSxsPicker.value = false
    }
    
    const onDateConfirm = ({ selectedValues }) => {
      formData.value.sxsdate = selectedValues.join('-')
      showDatePicker.value = false
    }
    
    const onStatusConfirm = ({ selectedOptions }) => {
      formData.value.sxsdevice_status = selectedOptions[0].text
      showStatusPicker.value = false
    }
    
    const handleSubmit = async () => {
      if (!formData.value.sxsname_id) {
        showError('请选择实训室')
        return
      }
      if (!formData.value.sxsdate) {
        showError('请选择使用日期')
        return
      }
      if (!formData.value.sxsnum) {
        showError('请输入使用人数')
        return
      }
      
      loading.value = true
      
      try {
        const submitData = {
          sxsname: formData.value.sxsname_id,
          sxsdate: formData.value.sxsdate,
          sxsstart: formData.value.sxsstart,
          sxsend: formData.value.sxsend,
          sxsnum: formData.value.sxsnum,
          sxsdevice_status: formData.value.sxsdevice_status || '正常',
          sxscontent: formData.value.sxscontent,
          sxsmemo: formData.value.sxsmemo
        }
        
        const response = await apiComposable.post(submitData, { url: '/sxs/addrecord/' })
        
        if (response && response.success) {
          if (response.redirect_to_report && response.report_info) {
            showSuccess('记录创建成功，正在跳转到故障上报...')
            setTimeout(() => {
              router.push({
                path: '/report-maintenance',
                query: {
                  sxsid: response.report_info.sxsid,
                  maintainrequestdate: response.report_info.maintainrequestdate
                }
              })
            }, 500)
            return
          }
          
          showSuccess('记录创建成功')
          setTimeout(() => {
            router.push('/')
          }, 1500)
        } else {
          showError(response?.message || '创建失败')
        }
      } catch (err) {
        showError(err.response?.data?.message || '创建失败，请检查网络连接')
      } finally {
        loading.value = false
      }
    }
    
    const loadSxsList = async () => {
      try {
        const res = await apiComposable.get({}, { url: '/sxs/addrecord/' })
        if (res && res.sxs_list) {
          sxsList.value = res.sxs_list
        }
      } catch (e) {
        console.error('Failed to load sxs list', e)
      }
    }
    
    const goBack = () => {
      router.go(-1)
    }
    
    const goHome = () => {
      router.push('/')
    }
    
    watch(() => formData.value.sxsdevice_status, async (newVal) => {
      if (newVal === '故障') {
        await showWarning('您选择了设备状态为【故障】，系统将自动跳转至故障上报页面')
        router.push({
          path: '/report-maintenance',
          query: {
            sxsid: formData.value.sxsname_id,
            maintainrequestdate: formData.value.sxsdate
          }
        })
      }
    })
    
    onMounted(() => {
      loadSxsList()
      
      const today = new Date()
      selectedDate.value = [
        String(today.getFullYear()),
        String(today.getMonth() + 1).padStart(2, '0'),
        String(today.getDate()).padStart(2, '0')
      ]
      formData.value.sxsdate = selectedDate.value.join('-')
      
      if (route.query.sxsid) {
        formData.value.sxsname_id = route.query.sxsid
      }
    })
    
    return {
      formData,
      sxsOptions,
      statusOptions,
      selectedDate,
      loading,
      showSxsPicker,
      showDatePicker,
      showStatusPicker,
      onSxsConfirm,
      onDateConfirm,
      onStatusConfirm,
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

.form-tips {
  margin: 12px 0;
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
