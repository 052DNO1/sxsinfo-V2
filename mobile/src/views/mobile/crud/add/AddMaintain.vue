<template>
  <div class="mobile-page">
    <van-nav-bar title="添加维护记录" left-arrow @click-left="goBack">
      <template #right>
        <van-icon name="home-o" size="20" @click="goHome" />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <van-form @submit="onSubmit">
        <van-cell-group inset>
          <van-field
            v-model="formData.sxsname"
            name="sxsname"
            label="实训室"
            placeholder="请选择实训室"
            readonly
            is-link
            @click="showSxsPicker = true"
          />

          <van-field
            v-model="formData.maintain_date"
            name="maintain_date"
            label="维护日期"
            type="date"
            placeholder="请选择维护日期"
            :rules="[{ required: true, message: '请选择维护日期' }]"
          />

          <van-field
            v-model="formData.maintain_type"
            name="maintain_type"
            label="维护类型"
            placeholder="请输入维护类型"
            :rules="[{ required: true, message: '请输入维护类型' }]"
          />

          <van-field
            v-model="formData.maintain_content"
            name="maintain_content"
            label="维护内容"
            type="textarea"
            placeholder="请输入维护内容"
            rows="4"
            :rules="[{ required: true, message: '请输入维护内容' }]"
          />
        </van-cell-group>

        <div class="submit-btn">
          <van-button type="primary" block native-type="submit" :loading="loading">提交</van-button>
        </div>
      </van-form>
    </div>

    <van-popup v-model:show="showSxsPicker" position="bottom" round>
      <van-picker
        title="选择实训室"
        :columns="sxsColumns"
        @confirm="onSxsConfirm"
        @cancel="showSxsPicker = false"
      />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useApi } from '@/composables/useApi'
import { useNavigation } from '@/utils/routeDecision'
import { showToast } from 'vant'

const router = useRouter()
const route = useRoute()
const { goHome, smartBack } = useNavigation()

const loading = ref(false)
const showSxsPicker = ref(false)
const formData = ref({
  sxsid: '',
  sxsname: '',
  maintain_date: '',
  maintain_type: '',
  maintain_content: ''
})

const sxsList = ref([])
const apiComposable = useApi('', { immediate: false })

const sxsColumns = computed(() => {
  return sxsList.value.map(sxs => ({
    text: sxs.sxsname,
    value: sxs.id
  }))
})

const loadSxsList = async () => {
  try {
    const response = await apiComposable.get({}, { url: '/sxs/addmaintain/0/' })
    if (response && response.form_fields && response.form_fields.sxs_list) {
      sxsList.value = response.form_fields.sxs_list
    }
  } catch (err) {
    console.error('Load sxs list error:', err)
  }
}

const onSxsConfirm = ({ selectedOptions }) => {
  const selected = selectedOptions[0]
  formData.value.sxsid = selected.value
  formData.value.sxsname = selected.text
  showSxsPicker.value = false
}

const onSubmit = async () => {
  if (!formData.value.sxsid) {
    showToast('请选择实训室')
    return
  }
  
  if (!formData.value.maintain_date) {
    showToast('请选择维护日期')
    return
  }
  
  if (!formData.value.maintain_content) {
    showToast('请输入维护内容')
    return
  }
  
  try {
    loading.value = true
    const submitData = {
      maintainrequestdate: formData.value.maintain_date,
      maintaintype: formData.value.maintain_type || 1,
      maintainrecordcontent: formData.value.maintain_content,
      maintainrecordmemo: formData.value.maintain_memo || '',
      ismaintaind: true
    }
    const response = await apiComposable.post(submitData, { url: `/sxs/addmaintain/${formData.value.sxsid}/` })
    if (response && response.success) {
      showToast('添加成功')
      setTimeout(() => {
        router.push('/')
      }, 1000)
    } else {
      showToast(response.message || '添加失败')
    }
  } catch (err) {
    console.error('Submit error:', err)
    showToast(err.response?.data?.message || '添加失败')
  } finally {
    loading.value = false
  }
}

const goBack = () => router.go(-1)

onMounted(() => {
  loadSxsList()
  if (route.query.sxsid) {
    formData.value.sxsid = route.query.sxsid
  }
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
  padding-bottom: 60px;
}

.submit-btn {
  padding: 16px;
}
</style>
