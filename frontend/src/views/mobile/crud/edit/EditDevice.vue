<template>
  <div class="mobile-page">
    <van-nav-bar
      title="编辑设备"
      left-arrow
      @click-left="goBack"
    >
      <template #right>
        <van-icon
          name="home-o"
          size="20"
          color="#4F6EF7"
          @click="goHome"
        />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <div class="form-hero">
        <div class="form-hero-icon">
          <van-icon
            name="desktop-o"
            size="28"
          />
        </div>
        <h2>编辑设备</h2>
        <p>修改设备基本信息</p>
      </div>

      <van-skeleton
        v-if="loading"
        :row="5"
        animated
      />

      <van-form
        v-else
        @submit="handleSubmit"
      >
        <div class="form-section animate-fade-in-up animate-delay-1">
          <div class="section-label">
            <span>📋</span> 基本信息
          </div>
          <van-cell-group inset>
            <van-field
              v-model="formData.code"
              label="设备编号"
              placeholder="请输入设备编号"
              required
              clearable
              :rules="[{ required: true, message: '请输入设备编号' }]"
            />
            <van-field
              v-model="formData.name"
              label="设备名称"
              placeholder="请输入设备名称"
              required
              clearable
              :rules="[{ required: true, message: '请输入设备名称' }]"
            />
            <van-field
              v-model="categoryText"
              is-link
              readonly
              label="类型"
              placeholder="请选择类型"
              required
              @click="showCategoryPicker = true"
            />
            <van-field
              v-model="formData.brand"
              label="品牌"
              placeholder="请输入品牌"
              clearable
            />
            <van-field
              v-model="formData.model"
              label="型号"
              placeholder="请输入型号"
              clearable
            />
            <van-field
              v-model="formData.config"
              label="配置"
              placeholder="如：i5-12500/16g/512g"
              clearable
            />
          </van-cell-group>
        </div>

        <div class="form-section animate-fade-in-up animate-delay-2">
          <div class="section-label">
            <span>📍</span> 位置信息
          </div>
          <van-cell-group inset>
            <van-field
              v-model="laboratoryText"
              is-link
              readonly
              label="所属实训室"
              placeholder="请选择实训室"
              required
              @click="showLabPicker = true"
            />
          </van-cell-group>
        </div>

        <div class="form-section animate-fade-in-up animate-delay-3">
          <div class="section-label">
            <span>⚙️</span> 状态与备注
          </div>
          <van-cell-group inset>
            <van-field
              v-model="statusText"
              is-link
              readonly
              label="设备状态"
              placeholder="请选择状态"
              @click="showStatusPicker = true"
            />
            <van-field
              v-model="formData.note"
              rows="3"
              autosize
              type="textarea"
              label="备注"
              placeholder="请输入备注"
              show-word-limit
              :maxlength="200"
            />
          </van-cell-group>
        </div>

        <div class="form-actions">
          <van-button
            type="primary"
            block
            round
            size="large"
            :loading="submitting"
            native-type="submit"
            icon="success"
          >
            保存修改
          </van-button>
        </div>
      </van-form>
    </div>

    <van-popup
      v-model:show="showLabPicker"
      position="bottom"
    >
      <van-picker
        :columns="labColumns"
        @confirm="onLabConfirm"
        @cancel="showLabPicker = false"
      />
    </van-popup>

    <van-popup
      v-model:show="showCategoryPicker"
      position="bottom"
    >
      <van-picker
        :columns="categoryOptions"
        @confirm="onCategoryConfirm"
        @cancel="showCategoryPicker = false"
      />
    </van-popup>

    <van-popup
      v-model:show="showStatusPicker"
      position="bottom"
    >
      <van-picker
        :columns="statusOptions"
        @confirm="onStatusConfirm"
        @cancel="showStatusPicker = false"
      />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNavigation } from '@/core/utils/routeDecision'
import { equipmentService, labService } from '@/core/services/BaseService'
import { showSuccess, showError } from '@/core/utils/errorHandler'

const route = useRoute()
const router = useRouter()
const { goHome, smartBack } = useNavigation()

const deviceId = computed(() => route.params.id)

const loading = ref(false)
const submitting = ref(false)
const showLabPicker = ref(false)
const showCategoryPicker = ref(false)
const showStatusPicker = ref(false)
const labList = ref([])

const formData = ref({ code: '', name: '', category: '计算机', brand: '', model: '', config: '', laboratory: '', status: 'NORMAL', note: '' })

const categoryOptions = [
  { text: '计算机', value: '计算机' }, { text: '服务器', value: '服务器' },
  { text: '网络设备', value: '网络设备' }, { text: '投影设备', value: '投影设备' },
  { text: '多媒体设备', value: '多媒体设备' }, { text: '教学设备', value: '教学设备' }, { text: '其他', value: '其他' }
]
const statusOptions = [ { text: '正常', value: 'NORMAL' }, { text: '维护中', value: 'MAINTENANCE' }, { text: '损坏', value: 'DAMAGED' } ]

const labColumns = computed(() => [
  { values: labList.value.map(lab => ({ text: `${lab.code || ''} ${lab.name || ''}`.trim(), value: lab.id })) }
])

const laboratoryText = computed(() => {
  const lab = labList.value.find(l => l.id === formData.value.laboratory)
  return lab ? `${lab.code || ''} ${lab.name || ''}`.trim() : ''
})
const categoryText = computed(() => categoryOptions.find(o => o.value === formData.value.category)?.text || '')
const statusText = computed(() => statusOptions.find(o => o.value === formData.value.status)?.text || '正常')

const onLabConfirm = ({ selectedOptions }) => {
  formData.value.laboratory = selectedOptions[0].value
  showLabPicker.value = false
}
const onCategoryConfirm = ({ selectedOptions }) => {
  formData.value.category = selectedOptions[0].value
  showCategoryPicker.value = false
}
const onStatusConfirm = ({ selectedOptions }) => {
  formData.value.status = selectedOptions[0].value
  showStatusPicker.value = false
}

const goBack = () => router.go(-1)

const fetchDeviceData = async () => {
  if (!deviceId.value) return
  loading.value = true
  try {
    const res = await equipmentService.get(deviceId.value)
    if (res) {
      formData.value = {
        code: res.code || '',
        name: res.name || '',
        category: res.category || '计算机',
        brand: res.brand || '',
        model: res.model || '',
        config: res.config || '',
        laboratory: res.laboratory_id || res.laboratory || '',
        status: res.status || 'NORMAL',
        note: res.note || ''
      }
    }
  } catch (err) {
    showError(err.message || '获取设备信息失败')
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  submitting.value = true
  try {
    await equipmentService.update(deviceId.value, {
      ...formData.value,
      laboratory: formData.value.laboratory || undefined
    })
    showSuccess('修改成功')
    setTimeout(() => smartBack(), 1000)
  } catch (err) {
    showError(err.message || '修改失败')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  try {
    const res = await labService.list({ nopage: true })
    labList.value = res?.list || res?.data?.list || []
  } catch (err) {
    console.error('Failed to load lab list:', err)
  }
  await fetchDeviceData()
})
</script>

<style scoped>
.form-hero {
  background: #F7F8FA;
  padding: 28px 20px;
  margin: -12px -16px 20px;
  text-align: center;
}

.form-hero-icon {
  width: 60px; height: 60px;
  border-radius: 50%;
  background: rgba(255,255,255,0.25);
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 12px;
  color: white;
  backdrop-filter: blur(4px);
}

.form-hero h2 {
  margin: 0 0 6px;
  font-size: 20px;
  color: white;
  font-weight: 600;
}

.form-hero p {
  margin: 0;
  font-size: 14px;
  color: rgba(255,255,255,0.8);
}

.form-section {
  margin-bottom: 16px;
}

.section-label {
  padding: 0 16px;
  margin-bottom: 10px;
  font-size: 14px;
  font-weight: 600;
  color: var(--mobile-text-secondary);
  display: flex;
  align-items: center;
  gap: 6px;
}

.form-actions {
  padding: 20px 16px 40px;
}

.animate-fade-in-up {
  animation: fadeInUp 0.3s ease-out forwards;
  opacity: 0;
}

.animate-delay-1 { animation-delay: 0.1s; }
.animate-delay-2 { animation-delay: 0.2s; }
.animate-delay-3 { animation-delay: 0.3s; }

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(15px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
