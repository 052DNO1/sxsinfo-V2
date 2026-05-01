<template>
  <div class="mobile-page">
    <van-nav-bar
      title="添加用户"
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
      <div class="form-hero form-hero--hero">
        <div class="form-hero-icon">
          <van-icon
            name="user-o"
            size="28"
          />
        </div>
        <h2>新增用户</h2>
        <p>添加系统用户并分配角色</p>
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
            <span>👤</span> 基本信息
          </div>
          <van-cell-group inset>
            <van-field
              v-model="form.username"
              label="用户名"
              placeholder="请输入用户名"
              required
              clearable
              :rules="[{ required: true, message: '请输入用户名' }]"
            />
            <van-field
              v-model="form.nickname"
              label="昵称"
              placeholder="请输入昵称"
              clearable
            />
            <van-field
              v-model="form.email"
              type="email"
              label="邮箱"
              placeholder="请输入邮箱"
              clearable
            />
            <van-field
              v-model="form.phone"
              label="手机号"
              placeholder="请输入手机号"
              clearable
            />
          </van-cell-group>
        </div>

        <div class="form-section animate-fade-in-up animate-delay-2">
          <div class="section-label">
            <span>🛡️</span> 角色设置
          </div>
          <van-cell-group inset>
            <div class="role-grid">
              <div
                class="role-item"
                :class="{ active: roles.includes('teacher') }"
                @click="toggleRole('teacher')"
              >
                <van-icon
                  name="certificate"
                  size="20"
                />
                <span>教师</span>
              </div>
              <div
                class="role-item"
                :class="{ active: roles.includes('sxsadmin') }"
                @click="toggleRole('sxsadmin')"
              >
                <van-icon
                  name="manager-o"
                  size="20"
                />
                <span>实训室管理员</span>
              </div>
              <div
                class="role-item"
                :class="{ active: roles.includes('departadmin') }"
                @click="toggleRole('departadmin')"
              >
                <van-icon
                  name="hotel-o"
                  size="20"
                />
                <span>分院管理员</span>
              </div>
            </div>
          </van-cell-group>
        </div>

        <div class="form-section animate-fade-in-up animate-delay-3">
          <div class="section-label">
            <span>📝</span> 其他信息
          </div>
          <van-cell-group inset>
            <van-field
              v-model="deptText"
              is-link
              readonly
              label="所属部门"
              placeholder="选择部门(可选)"
              @click="showDeptPicker = true"
            />
            <van-field
              v-model="form.note"
              rows="2"
              autosize
              type="textarea"
              label="备注"
              placeholder="备注"
            />
          </van-cell-group>
        </div>

        <div class="form-actions">
          <van-button
            type="primary"
            block
            round
            size="large"
            native-type="submit"
            :loading="submitting"
            icon="success"
          >
            立即创建
          </van-button>
        </div>
      </van-form>
    </div>

    <van-popup
      v-model:show="showDeptPicker"
      position="bottom"
      round
    >
      <van-picker
        title="选择部门"
        :columns="deptOptions"
        @confirm="(o) => { form.department_id = o.selectedValues[0]; deptText = o.selectedOptions[0]?.text || ''; showDeptPicker = false }"
        @cancel="showDeptPicker = false"
      />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNavigation } from '@/core/utils/routeDecision'
import { userService, deptService } from '@/core/services/BaseService'
import { showSuccess, showError } from '@/core/utils/errorHandler'
import api from '@/core/api/client'

const router = useRouter()
const { goBack, goHome } = useNavigation()

const loading = ref(false)
const submitting = ref(false)
const showDeptPicker = ref(false)
const roles = ref([])
const deptOptions = ref([])
const deptText = ref('')

const form = ref({ username: '', nickname: '', email: '', phone: '', department_id: null, note: '' })

const toggleRole = (role) => {
  const idx = roles.value.indexOf(role)
  if (idx >= 0) roles.value.splice(idx, 1)
  else roles.value.push(role)
}

onMounted(async () => {
  loading.value = true
  try {
    const response = await api.get('/departments/options/')
    if (response && response.success && response.data) {
      deptOptions.value = (response.data.departments || response.data || []).map(d => ({ text: d.name, value: d.id }))
    } else {
      const depts = await deptService.list({ nopage: true })
      deptOptions.value = (depts?.list || depts || []).map(d => ({ text: d.name, value: d.id }))
    }
  } catch (err) {
    console.error('获取部门列表失败', err)
    try {
      const depts = await deptService.list({ nopage: true })
      deptOptions.value = (depts?.list || depts || []).map(d => ({ text: d.name, value: d.id }))
    } catch (e) {
      console.error('备用获取部门列表也失败', e)
    }
  }
  loading.value = false
})

const handleSubmit = async () => {
  if (!form.value.username) return showError('请输入用户名')
  submitting.value = true
  try {
    let role = 1
    if (roles.value.includes('sxsadmin')) role |= 2
    if (roles.value.includes('departadmin')) role |= 4
    await userService.create({ ...form.value, department: form.value.department_id || undefined, role })
    showSuccess('创建成功')
    setTimeout(() => goBack(), 1000)
  } catch (e) { showError('创建失败') }
  finally { submitting.value = false }
}
</script>

<style scoped>
.form-hero { background: #F7F8FA; padding: 28px 20px; margin: -12px -16px 20px; text-align: center; border-radius: 0 0 16px 16px; }
.form-hero-icon { width: 60px; height: 60px; border-radius: 50%; background: #EEF2FF; display: flex; align-items: center; justify-content: center; margin: 0 auto 12px; color: #4F6EF7; }
.form-hero h2 { margin: 0 0 6px; font-size: 20px; font-weight: 700; color: #1A1A1A; }
.form-hero p { margin: 0; font-size: 13px; color: #666666; }

.form-section { margin-bottom: 8px; }
.section-label { display: flex; align-items: center; gap: 8px; padding: 10px 16px 6px; font-size: 13px; font-weight: 600; color: var(--mobile-text-secondary); }
.section-label span { font-size: 16px; }

.role-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; padding: 14px 4px; }
.role-item {
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  padding: 14px 8px; border-radius: var(--mobile-radius-md);
  border: 2px solid var(--mobile-border);
  transition: all 0.25s ease; cursor: pointer;
}
.role-item .van-icon { color: var(--mobile-text-hint); }
.role-item span { font-size: 11px; color: var(--mobile-text-secondary); font-weight: 500; }
.role-item.active {
  border-color: var(--mobile-primary); background: var(--mobile-primary-bg);
}
.role-item.active .van-icon { color: var(--mobile-primary); }
.role-item.active span { color: var(--mobile-primary); font-weight: 600; }
</style>