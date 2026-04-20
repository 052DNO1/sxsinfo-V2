<template>
  <div class="mobile-page">
    <van-nav-bar title="添加实训室" left-arrow @click-left="goBack">
      <template #right><van-icon name="home-o" size="20" color="#4F6EF7" @click="goHome" /></template>
    </van-nav-bar>

    <div class="page-content">
      <div class="form-hero form-hero--ocean">
        <div class="form-hero-icon"><van-icon name="home-o" size="28" /></div>
        <h2>新增实训室</h2>
        <p>创建新的教学实训空间</p>
      </div>

      <van-skeleton v-if="loading" :row="5" animated />

      <van-form v-else @submit="handleSubmit">
        <div class="form-section animate-fade-in-up animate-delay-1">
          <div class="section-label"><span>🏫</span> 基本信息</div>
          <van-cell-group inset>
            <van-field v-model="form.code" label="编号" placeholder="如: LAB-001" required clearable :rules="[{required:true,message:'请输入编号'}]" />
            <van-field v-model="form.name" label="名称" placeholder="实训室名称" required clearable :rules="[{required:true,message:'请输入名称'}]" />
            <van-field v-model="form.location" label="位置" placeholder="如: 教学楼3楼301" clearable />
            <van-field v-model="form.description" rows="2" autosize type="textarea" label="描述" placeholder="描述" show-word-limit :maxlength="200" />
          </van-cell-group>
        </div>

        <div class="form-section animate-fade-in-up animate-delay-2">
          <div class="section-label"><span>👤</span> 管理员</div>
          <van-cell-group inset>
            <van-field v-model="adminText" is-link readonly label="管理员" placeholder="选择管理员(可选)" @click="showAdminPicker = true" />
          </van-cell-group>
        </div>

        <div class="form-actions">
          <van-button type="primary" block round size="large" native-type="submit" :loading="submitting" icon="success">立即创建</van-button>
        </div>
      </van-form>
    </div>

    <van-popup v-model:show="showAdminPicker" position="bottom" round>
      <van-picker title="选择管理员" :columns="adminOptions" @confirm="(o) => { form.admin_id = o.selectedValues[0]; adminText = o.selectedOptions[0]?.text || ''; showAdminPicker = false }" @cancel="showAdminPicker = false" />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNavigation } from '@/core/utils/routeDecision'
import { labService, userService } from '@/core/services/BaseService'
import { showSuccess, showError } from '@/core/utils/errorHandler'

const router = useRouter()
const { goBack, goHome } = useNavigation()

const loading = ref(false)
const submitting = ref(false)
const showAdminPicker = ref(false)
const adminList = ref([])

const form = ref({ code: '', name: '', location: '', description: '', admin_id: null })
const adminText = ref('')
const adminOptions = computed(() => [{ text: '不指定', value: '' }, ...adminList.value.map(a => ({ text: `${a.nickname||a.username}`, value: a.id }))])

onMounted(async () => {
  loading.value = true
  const res = await userService.list({ nopage: true, role: '2' })
  adminList.value = res?.data?.list || []
  loading.value = false
})

const handleSubmit = async () => {
  if (!form.value.name) return showError('请输入名称')
  submitting.value = true
  try {
    const data = { ...form.value, admin: form.value.admin_id || undefined }
    await labService.create(data)
    showSuccess('创建成功')
    setTimeout(() => goBack(), 1000)
  } catch (e) { showError('创建失败') }
  finally { submitting.value = false }
}
</script>

<style scoped>
.form-hero--ocean { background: #E8F8EE; }
.form-hero { background: #F7F8FA; padding: 28px 20px; margin: -12px -16px 20px; text-align: center; border-radius: 0 0 16px 16px; }
.form-hero-icon { width: 60px; height: 60px; border-radius: 50%; background: #E8F8EE; display: flex; align-items: center; justify-content: center; margin: 0 auto 12px; color: #07C160; }
.form-hero h2 { margin: 0 0 6px; font-size: 20px; font-weight: 700; color: #1A1A1A; }
.form-hero p { margin: 0; font-size: 13px; color: #666666; }
.form-section { margin-bottom: 8px; }
.section-label { display: flex; align-items: center; gap: 8px; padding: 10px 16px 6px; font-size: 13px; font-weight: 600; color: var(--mobile-text-secondary); }
.section-label span { font-size: 16px; }
</style>