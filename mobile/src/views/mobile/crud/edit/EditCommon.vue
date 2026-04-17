<template>
  <div class="mobile-page">
    <van-nav-bar :title="header || '编辑'" left-arrow @click-left="goBack">
      <template #right>
        <van-icon name="home-o" size="20" @click="goHome" />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <van-skeleton v-if="loading" :row="5" animated />

      <template v-else>
        <van-cell-group inset title="基本信息">
          <van-field
            v-for="field in textFields"
            :key="field.name"
            v-model="formData[field.name]"
            :label="field.label"
            :placeholder="field.placeholder"
            :required="field.required"
            clearable
          />
        </van-cell-group>

        <van-cell-group inset title="选择信息">
          <van-field
            v-for="field in selectFields"
            :key="field.name"
            v-model="formData[field.name + '_text']"
            is-link
            readonly
            :label="field.label"
            :placeholder="field.placeholder"
            @click="openPicker(field)"
          />
        </van-cell-group>

        <van-cell-group inset title="其他信息">
          <van-field
            v-for="field in textareaFields"
            :key="field.name"
            v-model="formData[field.name]"
            rows="3"
            autosize
            type="textarea"
            :label="field.label"
            :placeholder="field.placeholder"
          />
        </van-cell-group>
      </template>

      <div class="form-actions">
        <van-button type="primary" block round :loading="submitting" @click="handleSubmit">
          保存修改
        </van-button>
      </div>
    </div>

    <van-popup v-model:show="showPicker" position="bottom" round>
      <van-picker
        :title="'选择' + currentField?.label"
        :columns="currentOptions"
        @confirm="onPickerConfirm"
        @cancel="showPicker = false"
      />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNavigation } from '@/utils/routeDecision'
import { useApi } from '@/composables/useApi'
import { showSuccess, showError } from '@/utils/errorHandler'

const route = useRoute()
const router = useRouter()
const { goHome, smartBack } = useNavigation()

const loading = ref(false)
const submitting = ref(false)
const formFields = ref([])
const formData = ref({})
const header = ref('')
const showPicker = ref(false)
const currentField = ref(null)
const currentOptions = ref([])

const apiComposable = useApi('', { immediate: false })

const textFields = computed(() => {
  return formFields.value.filter(f => ['text', 'number', 'email', 'tel', 'date'].includes(f.type))
})

const selectFields = computed(() => {
  return formFields.value.filter(f => f.type === 'select')
})

const textareaFields = computed(() => {
  return formFields.value.filter(f => f.type === 'textarea')
})

const openPicker = (field) => {
  currentField.value = field
  currentOptions.value = (field.options || []).map(opt => ({
    text: opt.label,
    value: opt.value
  }))
  showPicker.value = true
}

const onPickerConfirm = ({ selectedOptions }) => {
  if (currentField.value) {
    const selected = selectedOptions[0]
    formData.value[currentField.value.name] = selected.value
    formData.value[currentField.value.name + '_text'] = selected.text
  }
  showPicker.value = false
}

const loadFormData = async () => {
  loading.value = true
  try {
    const path = route.path
    const response = await apiComposable.get({}, { url: path })
    
    if (response) {
      header.value = response.header || '编辑'
      formFields.value = response.form_fields || []
      
      const initialData = {}
      formFields.value.forEach(field => {
        initialData[field.name] = field.default || ''
        if (field.type === 'select' && field.options) {
          const selected = field.options.find(o => o.value === field.default || o.selected)
          if (selected) {
            initialData[field.name + '_text'] = selected.label
          }
        }
      })
      
      if (response.initial_data) {
        Object.keys(response.initial_data).forEach(key => {
          initialData[key] = response.initial_data[key]
          const field = formFields.value.find(f => f.name === key)
          if (field && field.type === 'select' && field.options) {
            const selected = field.options.find(o => o.value === response.initial_data[key])
            if (selected) {
              initialData[key + '_text'] = selected.label
            }
          }
        })
      }
      
      formData.value = initialData
    }
  } catch (err) {
    showError('加载数据失败')
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  submitting.value = true
  try {
    const path = route.path
    const submitData = {}
    formFields.value.forEach(field => {
      submitData[field.name] = formData.value[field.name]
    })
    
    const response = await apiComposable.post(submitData, { url: path })
    
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
