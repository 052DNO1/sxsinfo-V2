<template>
  <!-- 移动端添加页面 - 使用与PC端相同的业务逻辑 -->
  <div class="mobile-add-page mobile-layout">
    <van-nav-bar
      :title="header || '添加'"
      left-arrow
      @click-left="goBack"
      class="mobile-nav-bar"
    />

    <!-- 加载状态 -->
    <div v-if="isLoading" class="mobile-loading-container">
      <van-loading size="24px" vertical>加载表单中...</van-loading>
    </div>

    <!-- 表单内容 -->
    <div v-else class="mobile-form-container">
      <van-form ref="formRef" @submit="handleSubmit" class="mobile-form">
        <van-cell-group inset>
          <!-- 动态渲染表单字段 -->
          <template v-for="(field, index) in formFields" :key="index">
            <!-- 文本输入 -->
            <van-field
              v-if="field.type === 'text' || field.type === 'input' || !field.type"
              v-model="formData[field.name]"
              :name="field.name"
              :label="field.label"
              :placeholder="field.placeholder || `请输入${field.label}`"
              :required="field.required"
              :rules="getFieldRules(field)"
              :type="field.inputType || 'text'"
              clearable
              class="custom-field"
            >
              <template #left-icon>
                <van-icon :name="getFieldIcon(field)" />
              </template>
            </van-field>

            <!-- 密码输入 -->
            <van-field
              v-else-if="field.type === 'password'"
              v-model="formData[field.name]"
              :name="field.name"
              :label="field.label"
              :type="showPassword ? 'text' : 'password'"
              :placeholder="field.placeholder || `请输入${field.label}`"
              :required="field.required"
              :rules="getFieldRules(field)"
              :right-icon="showPassword ? 'eye-o' : 'closed-eye'"
              @click-right-icon="showPassword = !showPassword"
              class="custom-field"
            >
              <template #left-icon>
                <van-icon name="lock" />
              </template>
            </van-field>

            <!-- 数字输入 -->
            <van-field
              v-else-if="field.type === 'number'"
              v-model.number="formData[field.name]"
              :name="field.name"
              :label="field.label"
              type="digit"
              :placeholder="field.placeholder || `请输入${field.label}`"
              :required="field.required"
              :rules="getFieldRules(field)"
              class="custom-field"
            />

            <!-- 选择器（单选） -->
            <van-field
              v-else-if="field.type === 'select' && !field.multiple"
              v-model="formData[field.name]"
              :name="field.name"
              :label="field.label"
              is-link
              readonly
              :placeholder="field.placeholder || `请选择${field.label}`"
              :required="field.required"
              :rules="getFieldRules(field)"
              @click="openPicker(field)"
              class="custom-field"
            >
              <template #left-icon>
                <van-icon name="arrow-down" />
              </template>
            </van-field>

            <!-- 选择器（多选） -->
            <van-field
              v-else-if="field.type === 'select' && field.multiple"
              :name="field.name"
              :label="field.label"
              is-link
              readonly
              :value="getMultipleSelectValue(field)"
              :placeholder="field.placeholder || `请选择${field.label}`"
              :required="field.required"
              :rules="getFieldRules(field)"
              @click="openPicker(field)"
              class="custom-field"
            />

            <!-- 文本域/多行文本 -->
            <van-field
              v-else-if="field.type === 'textarea'"
              v-model="formData[field.name]"
              :name="field.name"
              :label="field.label"
              type="textarea"
              rows="3"
              autosize
              :placeholder="field.placeholder || `请输入${field.label}`"
              :required="field.required"
              :rules="getFieldRules(field)"
              show-word-limit
              :maxlength="field.maxlength || 500"
              class="custom-field"
            />

            <!-- 开关 -->
            <van-cell
              v-else-if="field.type === 'switch'"
              :title="field.label"
            >
              <template #right-icon>
                <van-switch v-model="formData[field.name]" size="20" />
              </template>
            </van-cell>

            <!-- 日期选择 -->
            <van-field
              v-else-if="field.type === 'date'"
              v-model="formData[field.name]"
              :name="field.name"
              :label="field.label"
              is-link
              readonly
              :placeholder="field.placeholder || `请选择${field.label}`"
              :required="field.required"
              :rules="getFieldRules(field)"
              @click="openDatePicker(field)"
              class="custom-field"
            >
              <template #left-icon>
                <van-icon name="calendar-o" />
              </template>
            </van-field>

            <!-- 时间选择 -->
            <van-field
              v-else-if="field.type === 'time'"
              v-model="formData[field.name]"
              :name="field.name"
              :label="field.label"
              is-link
              readonly
              :placeholder="field.placeholder || `请选择${field.label}`"
              :required="field.required"
              :rules="getFieldRules(field)"
              @click="openTimePicker(field)"
              class="custom-field"
            >
              <template #left-icon>
                <van-icon name="clock-o" />
              </template>
            </van-field>
          </template>
        </van-cell-group>

        <!-- 提示信息区域 -->
        <div v-if="tips && tips.length > 0" class="form-tips">
          <div class="tips-title">💡 温馨提示</div>
          <ul class="tips-list">
            <li v-for="(tip, tipIndex) in tips" :key="tipIndex">{{ tip }}</li>
          </ul>
        </div>

        <!-- 提交按钮 -->
        <div class="form-submit-area">
          <van-button
            round
            block
            type="primary"
            native-type="submit"
            :loading="submitting"
            :disabled="!isFormValid"
            class="submit-button"
          >
            {{ submitting ? '提交中...' : submitButtonText }}
          </van-button>
          
          <van-button
            v-if="showResetButton"
            round
            block
            plain
            type="default"
            @click="handleReset"
            class="reset-button"
          >
            重置表单
          </van-button>
        </div>

        <!-- 消息提示 -->
        <div v-if="message" class="form-message" :class="'message-' + messageType">
          {{ message }}
        </div>
      </van-form>
    </div>

    <!-- 选择器弹窗 -->
    <van-popup v-model:show="pickerVisible" position="bottom" round>
      <van-picker
        :columns="currentPickerOptions"
        :title="currentField?.label || '请选择'"
        @confirm="onPickerConfirm"
        @cancel="pickerVisible = false"
      />
    </van-popup>

    <!-- 日期选择器 -->
    <van-popup v-model:show="datePickerVisible" position="bottom" round>
      <van-date-picker
        v-model="dateValue"
        :title="currentField?.label || '请选择日期'"
        @confirm="onDateConfirm"
        @cancel="datePickerVisible = false"
      />
    </van-popup>

    <!-- 时间选择器 -->
    <van-popup v-model:show="timePickerVisible" position="bottom" round>
      <van-time-picker
        v-model="timeValue"
        :title="currentField?.label || '请选择时间'"
        @confirm="onTimeConfirm"
        @cancel="timePickerVisible = false"
      />
    </van-popup>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi, useAuth } from '@/core/hooks'
import { useNavigation } from '@/core/utils/routeDecision'
import { useMobile } from '@/composables/useMobile'
import { showSuccessToast, showFailToast } from '@/utils/mobileDialog'

export default {
  name: 'MobileAdd',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const { user } = useAuth()
    const { smartBack } = useNavigation()
    
    // 移动端初始化
    const { init: initMobile, loadVantComponents } = useMobile()
    
    // API 实例
    const apiComposable = useApi('', { immediate: false })
    
    // UI 状态
    const formRef = ref(null)
    const loading = ref(false)
    const submitting = ref(false)
    const isLoading = ref(true)
    const header = ref('添加')
    const message = ref('')
    const messageType = ref('')
    const showPassword = ref(false)
    const pickerVisible = ref(false)
    const datePickerVisible = ref(false)
    const timePickerVisible = ref(false)
    const currentField = ref(null)
    const currentPickerOptions = ref([])
    const dateValue = ref([])
    const timeValue = ref([])

    // 表单数据 - 根据路由动态生成
    const formData = reactive({})
    const formFields = ref([])
    const fieldErrors = ref({})
    const tips = ref([])

    // 根据路由确定API路径和表单配置
    const getFormConfig = () => {
      const path = route.path
      
      if (path.includes('/adduser') || path.includes('/user/add')) {
        return {
          apiPath: '/users/',
          title: '添加用户',
          fields: [
            { name: 'username', label: '用户名', type: 'text', required: true, placeholder: '请输入用户名' },
            { name: 'nickname', label: '姓名', type: 'text', required: true, placeholder: '请输入姓名' },
            { name: 'email', label: '邮箱', type: 'text', placeholder: '请输入邮箱', rules: [{ pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: '请输入正确的邮箱格式' }] },
            { name: 'phone', label: '手机号', type: 'text', placeholder: '请输入手机号', rules: [{ pattern: /^1[3-9]\d{9}$/, message: '请输入正确的11位手机号' }] },
            { name: 'department', label: '所属部门', type: 'select', required: true, optionsUrl: '/departments/options/', optionLabel: 'name', optionValue: 'id' },
            { name: 'roles', label: '角色', type: 'select', multiple: true, required: true }
          ],
          tips: ['用户名建议使用工号或学号', '默认密码通常为用户名前6位']
        }
      }

      if (path.includes('/addsxs') || path.includes('/sxs/add')) {
        return {
          apiPath: '/laboratories/',
          title: '添加实训室',
          fields: [
            { name: 'sxsname', label: '实训室名称', type: 'text', required: true, placeholder: '请输入实训室名称' },
            { name: 'location', label: '位置', type: 'text', placeholder: '请输入位置信息' },
            { name: 'capacity', label: '容量', type: 'number', placeholder: '请输入容量' },
            { name: 'description', label: '描述', type: 'textarea', placeholder: '请输入描述信息' }
          ]
        }
      }

      if (path.includes('/adddept') || path.includes('/dept/add')) {
        return {
          apiPath: '/departments/',
          title: '添加部门',
          fields: [
            { name: 'name', label: '部门名称', type: 'text', required: true, placeholder: '请输入部门名称' },
            { name: 'description', label: '描述', type: 'textarea', placeholder: '请输入部门描述' }
          ]
        }
      }

      if (path.includes('/addclass') || path.includes('/class/add')) {
        return {
          apiPath: '/classes/',
          title: '添加班级',
          fields: [
            { name: 'classname', label: '班级名称', type: 'text', required: true, placeholder: '请输入班级名称' },
            { name: 'department', label: '所属部门', type: 'select', required: true, optionsUrl: '/departments/options/' },
            { name: 'grade', label: '年级', type: 'select', options: [
              { text: '2024级', value: '2024' },
              { text: '2023级', value: '2023' },
              { text: '2022级', value: '2022' }
            ]}
          ]
        }
      }

      if (path.includes('/addterm') || path.includes('/term/add')) {
        return {
          apiPath: '/terms/',
          title: '添加学期',
          fields: [
            { name: 'termname', label: '学期名称', type: 'text', required: true, placeholder: '如：2024-2025学年第一学期' },
            { name: 'start_date', label: '开始日期', type: 'date', required: true },
            { name: 'end_date', label: '结束日期', type: 'date', required: true },
            { name: 'is_current', label: '当前学期', type: 'switch' }
          ]
        }
      }

      // 默认配置 - 从API获取表单定义
      return {
        apiPath: getApiPathFromRoute(path),
        title: '添加',
        fields: []
      }
    }

    const getApiPathFromRoute = (path) => {
      // 将路由路径转换为API路径
      return path.replace(/^\/(m\/)?/, '').replace(/\/add$/, '/')
    }

    // 加载表单数据
    const loadFormData = async () => {
      try {
        const config = getFormConfig()
        header.value = config.title
        
        if (config.fields && config.fields.length > 0) {
          // 静态配置的字段
          formFields.value = config.fields
          tips.value = config.tips || []
          
          // 初始化表单数据
          config.fields.forEach(field => {
            if (field.multiple) {
              formData[field.name] = []
            } else if (field.type === 'switch') {
              formData[field.name] = false
            } else {
              formData[field.name] = ''
            }
            
            // 如果有选项URL，加载选项
            if (field.optionsUrl) {
              loadFieldOptions(field)
            }
          })
          
          // 处理角色选项
          const roleField = formFields.value.find(f => f.name === 'roles')
          if (roleField && !roleField.options) {
            roleField.options = getRoleOptions()
          }
        } else {
          // 动态从API获取表单定义
          await loadDynamicForm(config.apiPath)
        }
        
        isLoading.value = false
      } catch (err) {
        console.error('加载表单失败:', err)
        message.value = '加载表单失败'
        messageType.value = 'error'
        isLoading.value = false
      }
    }

    // 加载字段选项
    const loadFieldOptions = async (field) => {
      try {
        const response = await apiComposable.get({}, { url: field.optionsUrl })
        if (response && response.success && response.data) {
          let data = response.data
          
          // 提取选项数组
          if (Array.isArray(data)) {
            field.options = data.map(item => ({
              text: item[field.optionLabel || 'name'] || item.text,
              value: item[field.optionValue || 'id'] || item.value
            }))
          } else if (data.list || data.results || data.departments || data.options) {
            const list = data.list || data.results || data.departments || data.options
            field.options = Array.isArray(list) ? list.map(item => ({
              text: item[field.optionLabel || 'name'] || item.text,
              value: item[field.optionValue || 'id'] || item.value
            })) : []
          }
        }
      } catch (err) {
        console.error(`加载 ${field.label} 选项失败:`, err)
      }
    }

    // 动态加载表单
    const loadDynamicForm = async (apiPath) => {
      try {
        const response = await apiComposable.get({}, { url: apiPath, params: { action: 'form_config' } })
        
        if (response && response.success && response.data) {
          const config = response.data
          
          if (config.form_fields) {
            formFields.value = config.form_fields
          }
          
          if (config.title) {
            header.value = config.title
          }
          
          if (config.tips) {
            tips.value = config.tips
          }
          
          // 初始化表单数据
          formFields.value.forEach(field => {
            if (field.multiple) {
              formData[field.name] = []
            } else if (field.type === 'switch') {
              formData[field.name] = field.default || false
            } else {
              formData[field.name] = field.default || ''
            }
          })
        }
      } catch (err) {
        console.error('动态加载表单失败:', err)
        throw err
      }
    }

    // 获取角色选项
    const getRoleOptions = () => {
      if (!user.value) return []
      
      if (user.value.is_department_admin) {
        return [
          { text: '教师', value: 1 },
          { text: '实训室管理员', value: 2 }
        ]
      }
      
      if (user.value.is_superuser) {
        return [
          { text: '系统管理员', value: 32 },
          { text: '超级管理员', value: 16 }
        ]
      }
      
      if (user.value.is_super_admin) {
        return [
          { text: '部门管理员', value: 4 }
        ]
      }
      
      return [
        { text: '教师', value: 1 },
        { text: '实训室管理员', value: 2 },
        { text: '部门管理员', value: 4 }
      ]
    }

    // 获取字段验证规则
    const getFieldRules = (field) => {
      const rules = []
      
      if (field.required) {
        rules.push({ required: true, message: `请填写${field.label}`, trigger: 'blur' })
      }
      
      if (field.rules && Array.isArray(field.rules)) {
        rules.push(...field.rules)
      }
      
      return rules
    }

    // 获取字段图标
    const getFieldIcon = (field) => {
      const iconMap = {
        username: 'user-o',
        nickname: 'contact',
        email: 'envelop-o',
        phone: 'phone-o',
        sxsname: 'home-o',
        name: 'label-o',
        description: 'notes-o',
        classname: 'friends-o',
        termname: 'calendar-o'
      }
      return iconMap[field.name] || 'edit'
    }

    // 打开选择器
    const openPicker = (field) => {
      currentField.value = field
      
      if (field.options && field.options.length > 0) {
        currentPickerOptions.value = field.options
        pickerVisible.value = true
      } else if (field.optionsUrl) {
        // 动态加载选项
        loadFieldOptions(field).then(() => {
          currentPickerOptions.value = field.options || []
          pickerVisible.value = true
        })
      }
    }

    // 选择器确认
    const onPickerConfirm = ({ selectedOptions }) => {
      if (!currentField.value) return
      
      if (currentField.value.multiple) {
        // 多选模式
        const selectedValues = selectedOptions.map(opt => opt.value)
        formData[currentField.value.name] = selectedValues
      } else {
        // 单选模式
        formData[currentField.value.name] = selectedOptions[0]?.value || ''
      }
      
      pickerVisible.value = false
    }

    // 获取多选值显示
    const getMultipleSelectValue = (field) => {
      const values = formData[field.name]
      if (!values || !Array.isArray(values) || values.length === 0) return ''
      
      if (field.options) {
        return values
          .map(val => {
            const opt = field.options.find(o => o.value === val)
            return opt ? opt.text : val
          })
          .join(', ')
      }
      
      return values.join(', ')
    }

    // 日期选择器
    const openDatePicker = (field) => {
      currentField.value = field
      dateValue.value = []
      datePickerVisible.value = true
    }

    const onDateConfirm = ({ selectedValues }) => {
      if (currentField.value) {
        const [year, month, day] = selectedValues
        formData[currentField.value.name] = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`
      }
      datePickerVisible.value = false
    }

    // 时间选择器
    const openTimePicker = (field) => {
      currentField.value = field
      timeValue.value = []
      timePickerVisible.value = true
    }

    const onTimeConfirm = ({ selectedValues }) => {
      if (currentField.value) {
        const [hour, minute] = selectedValues
        formData[currentField.value.name] = `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`
      }
      timePickerVisible.value = false
    }

    // 表单验证状态
    const isFormValid = computed(() => {
      if (!formFields.value.length) return false
      
      return formFields.value.every(field => {
        if (!field.required) return true
        const value = formData[field.name]
        
        if (Array.isArray(value)) {
          return value.length > 0
        }
        
        if (typeof value === 'boolean') {
          return true
        }
        
        return value !== '' && value !== undefined && value !== null
      })
    })

    // 提交按钮文字
    const submitButtonText = computed(() => {
      return submitting.value ? '提交中...' : `立即创建`
    })

    // 是否显示重置按钮
    const showResetButton = computed(() => {
      return formFields.value.some(f => f.type !== 'switch')
    })

    // 表单提交
    const handleSubmit = async () => {
      if (submitting.value) return
      
      // 手动验证
      if (formRef.value) {
        try {
          await formRef.value.validate()
        } catch (err) {
          console.log('表单验证失败:', err)
          return
        }
      }
      
      submitting.value = true
      message.value = ''
      
      try {
        const config = getFormConfig()
        
        // 准备提交数据
        const submitData = { ...formData }
        
        // 处理特殊字段
        Object.keys(submitData).forEach(key => {
          // 将字符串布尔值转换为实际布尔值
          if (submitData[key] === 'True') submitData[key] = true
          if (submitData[key] === 'False') submitData[key] = false
          
          // 空字符串转为null或删除
          if (submitData[key] === '') {
            delete submitData[key]
          }
        })

        // 调用API提交
        const response = await apiComposable.post(submitData, {
          url: config.apiPath,
          resourceType: getResourceTypeFromPath(route.path)
        })

        if (response && response.success) {
          message.value = response.message || `${header.value}成功`
          messageType.value = 'success'
          
          await showSuccessToast(message.value)
          
          // 延迟返回上一页
          setTimeout(() => {
            smartBack()
          }, 1500)
        } else {
          message.value = response?.message || `${header.value}失败`
          messageType.value = 'error'
          
          if (response?.errors) {
            fieldErrors.value = response.errors
          }
          
          await showFailToast(message.value)
        }
      } catch (err) {
        console.error('提交错误:', err)
        message.value = err.message || '提交失败，请稍后重试'
        messageType.value = 'error'
        await showFailToast(message.value)
      } finally {
        submitting.value = false
      }
    }

    // 根据路径获取资源类型
    const getResourceTypeFromPath = (path) => {
      if (path.includes('user')) return 'users'
      if (path.includes('sxs')) return 'laboratories'
      if (path.includes('dept')) return 'departments'
      if (path.includes('class')) return 'classes'
      if (path.includes('term')) return 'terms'
      return ''
    }

    // 重置表单
    const handleReset = () => {
      formFields.value.forEach(field => {
        if (field.multiple) {
          formData[field.name] = []
        } else if (field.type === 'switch') {
          formData[field.name] = false
        } else {
          formData[field.name] = ''
        }
      })
      fieldErrors.value = {}
      message.value = ''
    }

    const goBack = () => {
      smartBack()
    }

    // 初始化
    onMounted(async () => {
      const cleanupMobile = initMobile()
      onUnmounted(() => {
        if (cleanupMobile) cleanupMobile()
      })
      
      await loadFormData()
      
      setTimeout(() => {
        loadVantComponents()
      }, 200)
    })

    return {
      // 数据状态
      formData,
      formFields,
      loading,
      submitting,
      isLoading,
      header,
      message,
      messageType,
      fieldErrors,
      tips,
      
      // UI 状态
      showPassword,
      pickerVisible,
      datePickerVisible,
      timePickerVisible,
      currentField,
      currentPickerOptions,
      dateValue,
      timeValue,
      
      // 计算属性
      isFormValid,
      submitButtonText,
      showResetButton,
      
      // 方法
      handleSubmit,
      handleReset,
      goBack,
      openPicker,
      onPickerConfirm,
      getMultipleSelectValue,
      openDatePicker,
      onDateConfirm,
      openTimePicker,
      onTimeConfirm,
      getFieldRules,
      getFieldIcon,
      
      // 引用
      formRef,
      
      // 用户信息
      user
    }
  }
}
</script>

<style scoped>
@import '@/assets/css/mobile.css';

.mobile-add-page {
  min-height: 100vh;
  background: #f7f8fa;
}

.mobile-loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 46px);
  padding: 40px 16px;
}

.mobile-form-container {
  padding-bottom: 80px;
}

.custom-field {
  margin-bottom: 4px;
}

.form-tips {
  margin: 16px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #e8f5e9 0%, #fff3e0 100%);
  border-radius: 10px;
  border-left: 4px solid #4caf50;
}

.tips-title {
  font-size: 14px;
  font-weight: 600;
  color: #2e7d32;
  margin-bottom: 8px;
}

.tips-list {
  margin: 0;
  padding-left: 18px;
  font-size: 13px;
  color: #555;
}

.tips-list li {
  margin-bottom: 4px;
  line-height: 1.6;
}

.form-submit-area {
  padding: 20px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.submit-button {
  height: 48px;
  font-size: 17px;
  font-weight: 600;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border: none;
  letter-spacing: 1px;
}

.reset-button {
  height: 44px;
  font-size: 15px;
  color: #969799;
}

.form-message {
  margin: 12px 16px;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
}

.message-success {
  background-color: #e8f5e9;
  color: #2e7d32;
  border-left: 4px solid #4caf50;
}

.message-error {
  background-color: #ffebee;
  color: #c62828;
  border-left: 4px solid #ef5350;
}

.message-info {
  background-color: #e3f2fd;
  color: #1565c0;
  border-left: 4px solid #42a5f5;
}
</style>
