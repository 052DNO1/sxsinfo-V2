<!--
  统一更新/编辑组件（移动端版本）
  功能：支持多种资源的编辑和更新操作
  支持的路由：
    - /update-user: 修改当前用户自己的信息（姓名、邮箱、电话）
    - /update-user-role/:id?: 分配用户角色（多选权限）
    - /update/:id: 编辑其他资源（课表、实训室、使用记录、维护记录、用户等）
  
  支持的字段类型：
    - text/email/tel/number: 文本输入框
    - select: 下拉选择框
    - textarea: 多行文本输入框
    - checkbox: 复选框
    - permissions: 多选权限（特殊类型，用于角色分配）
-->
<template>
  <!-- 移动端直接显示内容 -->
  <div :class="['mobile-update-container', 'mobile-layout', { 'assign-role-page': isAssignRolePage }]">
    <!-- 顶部导航栏 -->
    <van-nav-bar
      :title="header"
      left-arrow
      @click-left="handleBack"
      class="mobile-nav-bar"
    />

    <!-- 表单 -->
    <van-form @submit="handleSubmitMobile" style="padding: 16px;">
      <van-cell-group inset>
        <template v-for="field in formFields" :key="field.name">
          <!-- 文本输入框 -->
          <van-field
            v-if="field && (field.type === 'text' || field.type === 'email' || field.type === 'tel' || field.type === 'number')"
            :model-value="formData[field.name]"
            @update:model-value="(val) => { formData[field.name] = val }"
            :name="field.name"
            :label="field.label"
            :placeholder="field.placeholder"
            :required="field.required"
            :readonly="field.readonly"
            :disabled="field.readonly"
            :type="field.type"
            :rules="[{ required: field.required, message: `请填写${field.label}` }]"
          />
          <div v-if="fieldErrors[field.name]" style="padding: 8px 16px; color: #ee0a24; font-size: 12px;">
            {{ fieldErrors[field.name] }}
          </div>

          <!-- 下拉选择框 -->
          <van-field
            v-else-if="field && field.type === 'select'"
            v-model="formData[field.name]"
            :name="field.name"
            :label="field.label"
            :placeholder="field.placeholder || '请选择'"
            is-link
            readonly
            :required="field.required"
            @click="showPicker(field)"
          />
          <van-popup v-if="field && field.type === 'select'" v-model:show="pickerFields[field.name]" position="bottom">
            <van-picker
              :columns="getPickerColumns(field)"
              @confirm="onPickerConfirm(field, $event)"
              @cancel="pickerFields[field.name] = false"
            />
          </van-popup>
          <div v-if="field && field.type === 'select' && fieldErrors[field.name]" style="padding: 8px 16px; color: #ee0a24; font-size: 12px;">
            {{ fieldErrors[field.name] }}
          </div>

          <!-- 多行文本 -->
          <van-field
            v-else-if="field.type === 'textarea'"
            v-model="formData[field.name]"
            :name="field.name"
            :label="field.label"
            :placeholder="field.placeholder"
            type="textarea"
            :rows="field.rows || 4"
            :required="field.required"
            :rules="[{ required: field.required, message: `请填写${field.label}` }]"
          />
          <div v-if="field.type === 'textarea' && fieldErrors[field.name]" style="padding: 8px 16px; color: #ee0a24; font-size: 12px;">
            {{ fieldErrors[field.name] }}
          </div>

          <!-- 复选框 -->
          <van-cell
            v-else-if="field.type === 'checkbox'"
            :title="field.label"
          >
            <template #right-icon>
              <van-switch v-model="formData[field.name]" />
            </template>
          </van-cell>

          <!-- 多选权限（移动端使用复选框组） -->
          <van-cell-group v-else-if="field && field.type === 'permissions'" inset class="permissions-group" :key="`permissions-group-${field.name}-${JSON.stringify(formData[field.name])}`">
            <van-cell :title="field.label" class="permissions-title-cell" />
            <div class="permissions-checkbox-wrapper">
              <van-checkbox-group 
                :model-value="Array.isArray(formData[field.name]) ? formData[field.name] : []"
                @update:model-value="(val) => {
                  // 确保更新 formData
                  if (Array.isArray(val)) {
                    formData[field.name] = [...val]
                  } else {
                    formData[field.name] = []
                  }
                }"
                class="permissions-checkbox-group"
                :key="`checkbox-group-${field.name}-${JSON.stringify(formData[field.name])}`"
              >
                <van-checkbox
                  v-for="option in getFilteredOptions(field)"
                  :key="`permission-${field.name}-${option.value}-${JSON.stringify(formData[field.name])}`"
                  :name="option.value"
                  shape="square"
                  class="permission-checkbox-item"
                >
                  {{ option.label }}
                </van-checkbox>
              </van-checkbox-group>
            </div>
          </van-cell-group>
        </template>
      </van-cell-group>

      <div class="submit-button-wrapper">
        <van-button
          round
          block
          type="primary"
          native-type="submit"
          :loading="loading"
          class="submit-button"
        >
          {{ loading ? '提交中...' : '提交' }}
        </van-button>
      </div>
    </van-form>

    <!-- 用户编辑页面的操作按钮区域 -->
    <div v-if="isUserEditPage" class="operations-section">
      <van-cell-group inset class="operations-group">
        <van-cell title="操作" class="operations-title-cell" />
        <van-cell
          title="重置密码"
          is-link
          @click="handleResetPassword"
          class="operation-cell reset-password-cell"
        >
          <template #right-icon>
            <van-icon name="lock" class="operation-icon reset-icon" />
          </template>
        </van-cell>
        <van-cell
          title="删除用户"
          is-link
          @click="handleDeleteUser"
          class="operation-cell delete-user-cell"
        >
          <template #right-icon>
            <van-icon name="delete-o" class="operation-icon delete-icon" />
          </template>
        </van-cell>
      </van-cell-group>
    </div>
  </div>
</template>

<script>
/**
 * 统一更新/编辑组件（移动端版本）
 * 
 * 功能说明：
 * 1. 修改当前用户信息：/update-user - 修改当前登录用户的基本信息（姓名、邮箱、电话）
 * 2. 分配用户角色：/update-user-role/:id? - 为用户分配多个角色权限
 * 3. 编辑其他资源：/update/:id - 根据resource_type编辑不同类型的资源
 *    - class/sxs_class: 编辑课表
 *    - sxs: 编辑实训室
 *    - record: 编辑使用记录
 *    - maintain: 编辑维护记录
 *    - user: 编辑用户信息
 */
import { ref, computed, onMounted, onUnmounted, watch, onActivated, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/utils/api'
import { handleBusinessResponse, decideRouteFromBusinessData, decideBackRoute } from '@/utils/routeDecision'
import { useMobile } from '@/composables/useMobile'

export default {
  name: 'Update',
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    // ==================== 响应式数据 ====================
    // 获取当前用户信息（从sessionStorage）
    const user = ref(JSON.parse(sessionStorage.getItem('user') || '{}'))
    
    // 页面标题
    const header = ref('')
    // 表单字段配置数组
    const formFields = ref([])
    // 表单数据对象
    const formData = ref({
      username: '',
      nikename: '',
      phone: '',
      permissions: [] // 确保 permissions 字段始终存在且是数组
    })
    // 字段错误信息对象
    const fieldErrors = ref({})
    // 加载状态
    const loading = ref(false)
    // 返回URL（已废弃，使用前端路由决策）
    const backUrl = ref('')
    // 原始类型ID（用于某些编辑操作）
    const originalTid = ref('')
    // 是否是分院管理员
    const isDepartAdmin = ref(false)
    
    // 移动端初始化
    const { loadVantComponents, init: initMobile } = useMobile()
    
    // 移动端状态
    const pickerFields = ref({})
    
    // 显示选择器（移动端）
    const showPicker = (field) => {
      pickerFields.value[field.name] = true
    }
    
    // 获取选择器列（移动端）
    const getPickerColumns = (field) => {
      if (!field.options) return []
      return field.options.map(opt => ({
        text: opt.label,
        value: opt.value
      }))
    }
    
    // 选择器确认（移动端）
    const onPickerConfirm = (field, { selectedOptions }) => {
      formData.value[field.name] = selectedOptions[0]?.value || ''
      pickerFields.value[field.name] = false
    }
    
    // ==================== 计算属性 ====================
    /**
     * 判断是否应该显示返回按钮
     * 超级管理员不显示返回按钮，其他用户显示
     * 例外：部门编辑页面（/update/:id?resource_type=dept）始终显示返回按钮
     */
    const showBackButton = computed(() => {
      // 部门编辑页面始终显示返回按钮
      if (route.path.startsWith('/update/') && route.query?.resource_type === 'dept') {
        return true
      }
      // 超级管理员不显示返回按钮，其他用户显示
      if (user.value?.is_superuser) {
        return false
      }
      return true
    })

    // 判断是否是分配角色页面（包括 /update-user-role/:id 和 /update/:id?resource_type=user）
    const isAssignRolePage = computed(() => {
      if (!route || !route.path) return false
      return route.path.startsWith('/update-user-role') || 
             (route.path.startsWith('/update/') && (route.query?.resource_type === 'user' || route.query?.opttype === 'user'))
    })

    // 判断是否是用户编辑页面（包括分配角色页面）
    const isUserEditPage = computed(() => {
      if (!route || !route.path) return false
      // 编辑用户页面：/update/:id?resource_type=user（统一显示分配角色页面）
      if (route.path.startsWith('/update/') && (route.query?.resource_type === 'user' || route.query?.opttype === 'user')) {
        return true
      }
      // 分配角色页面：/update-user-role/:id
      if (route.path.startsWith('/update-user-role')) {
        return true
      }
      return false
    })

    // 从路由中提取用户ID（用于分配角色页面）
    const getUserId = () => {
      if (!route || !route.path) return null
      // 从分配角色页面提取：/update-user-role/:id
      if (route.path.startsWith('/update-user-role')) {
        const match = route.path.match(/^\/update-user-role(?:\/(\d+))?$/)
        if (match && match[1]) {
          return match[1]
        }
      }
      // 从编辑用户页面提取：/update/:id?resource_type=user
      if (route.path.startsWith('/update/') && (route.query?.resource_type === 'user' || route.query?.opttype === 'user')) {
        const match = route.path.match(/^\/update\/(\d+)$/)
        if (match && match[1]) {
          return match[1]
        }
        // 如果路径中没有，尝试从 params 获取
        if (route.params.id) {
          return route.params.id
        }
      }
      return null
    }

    // 处理重置密码
    const handleResetPassword = async () => {
      if (!route || !route.path) {
        console.error('route 未初始化')
        return
      }
      const userId = getUserId()
      
      if (!userId) {
        const { showFailToast } = await import('@/utils/mobileDialog')
        await showFailToast('无法获取用户ID')
        return
      }

      try {
        const { showConfirmDialog, showSuccessToast, showFailToast } = await import('@/utils/mobileDialog')
        await showConfirmDialog({
          title: '确认重置密码',
          message: '确定要重置该用户的密码吗？密码将重置为用户名前6位。',
          type: 'info'
        })

        const url = `/userinfo/resetpassword/${userId}/`
        const response = await api.get(url)
        
        if (response && response.success) {
          await showSuccessToast(response.message || '密码重置成功')
        } else {
          await showFailToast(response?.message || '密码重置失败')
        }
      } catch (err) {
        if (err !== 'cancel') {
          console.error('重置密码失败:', err)
          const { showFailToast } = await import('@/utils/mobileDialog')
          const errorMsg = err.response?.data?.message || err.message || '密码重置失败'
          console.error('错误详情:', err.response)
          await showFailToast(errorMsg)
        }
      }
    }

    // 处理删除用户
    const handleDeleteUser = async () => {
      if (!route || !route.path) {
        console.error('route 未初始化')
        return
      }
      const userId = getUserId()
      
      if (!userId) {
        const { showFailToast } = await import('@/utils/mobileDialog')
        await showFailToast('无法获取用户ID')
        return
      }

      try {
        const { showConfirmDialog, showSuccessToast, showFailToast } = await import('@/utils/mobileDialog')
        
        await showConfirmDialog({
          title: '确认删除',
          message: '确定要删除该用户吗？此操作不可逆！',
          type: 'danger'
        })

        const url = `/userinfo/deluser/${userId}/`
        const response = await api.get(url)
        
        if (response && response.success) {
          await showSuccessToast(response.message || '用户删除成功')
          // 返回用户列表页面
          const tid = originalTid.value || route.query.tid || '1'
          router.push(`/userlist/${tid}`)
        } else {
          await showFailToast(response?.message || '用户删除失败')
        }
      } catch (err) {
        if (err !== 'cancel') {
          console.error('删除用户失败:', err)
          const { showFailToast } = await import('@/utils/mobileDialog')
          const errorMsg = err.response?.data?.message || err.message || '用户删除失败'
          console.error('错误详情:', err.response)
          await showFailToast(errorMsg)
        }
      }
    }

    // ==================== 工具函数 ====================
    /**
     * 过滤权限选项
     * 分院管理员不能给自己分配分院管理员权限
     * @param {Object} field - 表单字段对象
     * @returns {Array} 过滤后的选项数组
     */
    const getFilteredOptions = (field) => {
      if (!field || !field.options) {
        return []
      }
      return field.options.filter(option => {
        if (!option || option.value === undefined) return false
        // 分院管理员不能选择分院管理员选项（value === 4）
        if (isDepartAdmin.value && option.value === 4) return false
        return true
      })
    }

    // ==================== 表单提交处理 ====================
    /**
     * 处理表单提交
     * 根据路由路径确定API端点，提交表单数据，处理响应和错误
     */
    const handleSubmit = async () => {
      loading.value = true
      fieldErrors.value = {}

      try {
        const apiPath = getApiPath(route.path, route.query)
        
        // 检查是否尝试给自己分配权限（分配角色页面）
        const isAssignRoleRoute = route.path.startsWith('/update-user-role') || 
                                  (route.path.startsWith('/update/') && (route.query?.resource_type === 'user' || route.query?.opttype === 'user'))
        if (isAssignRoleRoute) {
          let targetUserId = null
          if (route.path.startsWith('/update-user-role')) {
            targetUserId = route.path.match(/^\/update-user-role(?:\/(\d+))?$/)?.[1]
          } else if (route.path.startsWith('/update/')) {
            targetUserId = route.path.match(/^\/update\/(\d+)$/)?.[1] || route.params.id
          }
          const currentUserId = user.value?.id?.toString()
          if (targetUserId && currentUserId && targetUserId === currentUserId) {
            const errorMsg = '您不能给自己分配权限'
            const { showFailToast } = await import('@/utils/mobileDialog')
            await showFailToast(errorMsg)
            loading.value = false
            // 重定向到教师用户列表（tid=1）
            setTimeout(() => {
              router.push('/userlist/1').catch(err => {
                console.error('重定向失败:', err)
              })
            }, 2000)
            return
          }
        }
        
        // 修改当前用户信息：只提交基本信息，不需要original_tid
        let submitData
        if (route.path === '/update-user') {
          submitData = formData.value
        } else {
          // 其他情况：添加original_tid到提交数据
          submitData = {
            ...formData.value,
            original_tid: originalTid.value || route.query.tid || '1'
          }
        }
        
        const response = await api.post(apiPath, submitData)
        if (response.success) {
          const { showSuccessToast } = await import('@/utils/mobileDialog')
          await showSuccessToast(response.message || '操作成功')
          
          // 修改当前用户信息：跳转到首页
          if (route.path === '/update-user') {
            router.push('/')
            return
          }
          
          // 完全前后端分离：根据业务数据自己决定路由
          // 优先处理编辑实训室的情况，返回到实训室列表页面（图二）
          if (route.path.startsWith('/update/') && apiPath.includes('editsxs')) {
            // 编辑实训室后返回到实训室列表页面（图二）
            // 使用业务数据决定路由，如果没有则使用默认值
            let redirectPath = decideRouteFromBusinessData(response.data, {
              defaultRoute: '/listsxs/2'
            })
            if (!redirectPath) {
              redirectPath = '/listsxs/2'
            }
            router.push(redirectPath)
          } else {
            // 其他情况使用业务数据决定路由
            let redirectPath = decideRouteFromBusinessData(response.data, {
              defaultRoute: originalTid.value ? `/userlist/${originalTid.value}` : '/userlist/1'
            })
            
            if (!redirectPath) {
              // 如果没有业务数据，使用默认路由
              redirectPath = originalTid.value ? `/userlist/${originalTid.value}` : '/userlist/1'
            }
            router.push(redirectPath)
          }
        } else {
          const { showFailToast } = await import('@/utils/mobileDialog')
          await showFailToast(response.message || '操作失败')
          if (response.errors) {
            fieldErrors.value = response.errors
          }
        }
      } catch (err) {
        console.error('提交失败:', err)
        const errorMsg = err.response?.data?.message || err.message || '操作失败，请检查网络连接'
        
        // 检查是否是"不能给自己分配权限"的错误（检查多种可能的错误消息格式和路径）
        const isAssignRoleRoute = route.path.startsWith('/update-user-role') || 
                                  (route.path.startsWith('/update/') && (route.query?.resource_type === 'user' || route.query?.opttype === 'user'))
        const isSelfAssignError = errorMsg.includes('不能给自己分配权限') || 
                                 errorMsg.includes('您不能给自己分配权限') ||
                                 errorMsg.includes('给自己分配权限')
        
        const { showFailToast } = await import('@/utils/mobileDialog')
        await showFailToast(errorMsg)
        // 延迟后处理返回逻辑
        setTimeout(() => {
          // 如果是分配角色/权限页面且是因为不能给自己分配权限，强制重定向到教师用户列表（tid=1）
          if (isAssignRoleRoute && isSelfAssignError) {
            router.push('/userlist/1').catch(err => {
              console.error('重定向失败:', err)
            })
          }
        }, 2000)
        if (err.response?.data?.errors) {
          fieldErrors.value = err.response.data.errors
        }
      } finally {
        loading.value = false
      }
    }

    // ==================== 表单字段转换 ====================
    /**
     * 转换表单字段格式（用于编辑页面）
     * 将后端返回的form_fields对象转换为前端需要的数组格式
     * 目前主要处理编辑课表的场景
     * 
     * @param {Object} fieldsData - 后端返回的表单字段数据对象
     * @param {String} routePath - 当前路由路径
     * @param {Object} response - 后端完整响应数据
     * @returns {Array} 转换后的表单字段数组
     */
    const convertFormFieldsForUpdate = (fieldsData, routePath, response) => {
      const fields = []
      
      // 处理编辑部门表单
      if (routePath.startsWith('/update/') && route.query.resource_type === 'dept') {
        const deptData = response.dept || {}
        const requiredFields = response.required_fields || []
        
        // 部门名称
        fields.push({
          name: 'departname',
          type: 'text',
          label: '部门名称',
          placeholder: '请输入部门名称',
          required: requiredFields.includes('departname'),
          icon: 'shop-o',
          default: deptData.departname || ''
        })
        
        // 部门描述
        fields.push({
          name: 'departdemo',
          type: 'text',
          label: '部门描述',
          placeholder: '请输入部门描述',
          required: requiredFields.includes('departdemo'),
          icon: 'edit',
          default: deptData.departdemo || ''
        })
        
        return fields
      }
      
      // 处理编辑课表表单
      if (routePath.startsWith('/update/') && (route.query.resource_type === 'class' || route.query.resource_type === 'sxs_class' || route.query.opttype === 'class')) {
        const classData = response.class || {}
        
        // 实训室选择
        if (fieldsData.sxs_list && fieldsData.sxs_list.length > 0) {
          fields.push({
            name: 'sxsname',
            type: 'select',
            label: '实训室',
            placeholder: '请选择实训室',
            required: true,
            icon: 'shop-o',
            default: classData.sxsname_id || '',
            options: fieldsData.sxs_list.map(sxs => ({
              value: sxs.id,
              label: `${sxs.sxsname} (${sxs.sxsno})`
            }))
          })
        }
        
        // 课程名称
        fields.push({
          name: 'classname',
          type: 'text',
          label: '课程名称',
          placeholder: '请输入课程名称',
          required: true,
          icon: 'book-o',
          default: classData.classname || ''
        })
        
        // 星期选择
        if (fieldsData.weekday_choices && fieldsData.weekday_choices.length > 0) {
          fields.push({
            name: 'classweekday',
            type: 'select',
            label: '星期',
            placeholder: '请选择星期',
            required: true,
            icon: 'calendar-o',
            default: classData.classweekday || 1,
            options: fieldsData.weekday_choices
          })
        }
        
        // 节次
        fields.push({
          name: 'classjc',
          type: 'text',
          label: '节次',
          placeholder: '例如：1-4',
          required: false,
          icon: 'clock-o',
          default: classData.classjc || '1-4'
        })
        
        // 周次
        fields.push({
          name: 'classweek',
          type: 'text',
          label: '周次',
          placeholder: '例如：1-18',
          required: false,
          icon: 'calendar-o',
          default: classData.classweek || '1-18'
        })
        
        // 人数
        fields.push({
          name: 'classnum',
          type: 'number',
          label: '人数',
          placeholder: '请输入上课人数',
          required: false,
          icon: 'friends-o',
          default: classData.classnum || 20
        })
        
        // 教师选择
        if (fieldsData.teachers && fieldsData.teachers.length > 0) {
          fields.push({
            name: 'classteacher',
            type: 'select',
            label: '任课教师',
            placeholder: '请选择任课教师（可选）',
            required: false,
            icon: 'manager-o',
            default: classData.classteacher_id || '',
            options: fieldsData.teachers.map(teacher => ({
              value: teacher.id,
              label: teacher.nikename || teacher.username
            }))
          })
        }
        
        // 上课班级
        fields.push({
          name: 'class_group',
          type: 'text',
          label: '上课班级',
          placeholder: '请输入上课班级（可选）',
          required: false,
          icon: 'graduation-cap-o',
          default: classData.class_group || ''
        })
        
        // 教师签名
        fields.push({
          name: 'teacher_signature',
          type: 'text',
          label: '教师签名',
          placeholder: '教师签名',
          required: false,
          icon: 'edit',
          default: classData.teacher_signature || '教师签名'
        })
        
        // 备注
        fields.push({
          name: 'classmemo',
          type: 'textarea',
          label: '备注',
          placeholder: '请输入备注信息（可选）',
          required: false,
          icon: 'edit',
          default: classData.classmemo || '',
          rows: 4
        })
        
        return fields
      }
      
      // 其他情况：返回空数组
      return []
    }

    // ==================== API路径构建 ====================
    /**
     * 根据路由路径和查询参数构建API路径
     * 完全前后端分离：不使用路径映射，直接从业务数据构建API路径
     * 
     * @param {String} routePath - 当前路由路径
     * @param {Object} queryParams - 路由查询参数
     * @returns {String} API路径
     */
    const getApiPath = (routePath, queryParams = {}) => {
      // 处理 /update-user 路由（修改当前用户自己的信息）
      if (routePath === '/update-user') {
        return '/userinfo/update_userinfo/'
      }
      
      // 处理 /update-user-role/:id? 路由（分配用户角色）
      if (routePath.startsWith('/update-user-role')) {
        // 尝试从路径中提取 id
        const match = routePath.match(/^\/update-user-role(?:\/(\d+))?$/)
        
        let userId = null
        if (match && match[1]) {
          userId = match[1]
        } else {
          // 如果路径中没有 id，尝试从 route.params 获取
          userId = route.params.id
        }
        
        if (userId) {
          return `/userinfo/updateuserrole/${userId}/`
        }
        
        // 如果没有用户ID，返回 null 让调用方处理
        return null
      }
      
      // 处理 /update/:id 路由 - 根据resource_type和resource_id构建API路径
      if (routePath.startsWith('/update/')) {
        const match = routePath.match(/^\/update\/(\d+)$/)
        if (match && match[1]) {
          const resourceId = match[1]
          
          // 从查询参数中获取resource_type
          // 优先使用resource_type，如果没有则尝试opttype（向后兼容）
          const resourceType = queryParams.resource_type || queryParams.opttype || ''
          
          // 根据resource_type构建对应的API路径
          switch (resourceType) {
            case 'class':
            case 'sxs_class':
              // 编辑课表
              return `/sxs/editclass/${resourceId}/`
            case 'sxs':
              // 编辑实训室
              return `/sxs/editsxs/${resourceId}/0/`
            case 'record':
              // 编辑使用记录
              return `/sxs/editrecord/${resourceId}/`
            case 'maintain':
              // 编辑维护记录
              return `/sxs/editmaintain/${resourceId}/`
            case 'user':
              // 编辑用户 - 统一使用分配角色API
              return `/userinfo/updateuserrole/${resourceId}/`
            case 'dept':
              // 编辑部门
              return `/userinfo/updatedept/${resourceId}/`
            default:
              // 默认尝试实训室编辑（向后兼容）
              return `/sxs/editsxs/${resourceId}/0/`
          }
        }
      }
      
      // 其他路由直接使用
      return routePath.startsWith('/') ? routePath.substring(1) : routePath
    }

    // ==================== 数据加载 ====================
    /**
     * 加载表单数据
     * 根据路由路径获取对应的API数据，转换为前端表单格式
     * 支持三种模式：
     * 1. 修改当前用户信息：显示简单的表单（姓名、邮箱、电话）
     * 2. 分配用户角色：显示多选权限表单
     * 3. 编辑其他资源：根据资源类型动态显示表单
     */
    const loadFormData = async () => {
      try {
        // 安全检查：确保 route 存在
        if (!route || !route.path) {
          console.error('route 未初始化')
          return
        }
        
        // 传递query参数给getApiPath函数
        const apiPath = getApiPath(route.path, route.query)
        
        // 验证API路径是否有效
        if (!apiPath || apiPath === null || apiPath === undefined) {
          // 如果是 update-user-role 路由但没有用户ID
          if (route.path.startsWith('/update-user-role')) {
            const errorMsg = '缺少用户ID参数，无法加载用户信息'
            console.error(errorMsg)
            const { showFailToast } = await import('@/utils/mobileDialog')
            await showFailToast(errorMsg)
            // 返回用户列表
            const tid = route.query.tid || route.query.typeid || '1'
            router.push(`/userlist/${tid}`)
            return
          }
          
          // 其他情况，显示错误并返回
          console.error('API路径无效:', apiPath)
          console.error('当前路由:', route.path, route.params, route.query)
          const errorMsg = '无法确定API路径，请检查路由配置'
          const { showFailToast } = await import('@/utils/mobileDialog')
          await showFailToast(errorMsg)
          return
        }
        
        // 确保apiPath是字符串且以/开头
        if (typeof apiPath !== 'string' || !apiPath.startsWith('/')) {
          console.error('API路径格式错误:', apiPath)
          const errorMsg = 'API路径格式错误'
          const { showFailToast } = await import('@/utils/mobileDialog')
          await showFailToast(errorMsg)
          return
        }
        
        const response = await api.get(apiPath, { params: route.query })
        
        header.value = response.header || '分配角色'
        
        // ========== 处理用户相关表单 ==========
        // 如果响应中包含user字段，说明是用户相关的操作
        if (response.user) {
          // 重置 formData，确保刷新后数据正确初始化
          formData.value = {
            username: '',
            nikename: '',
            phone: '',
            permissions: []
          }
          
          // 判断操作类型
          const isUpdateUser = route.path === '/update-user' // 修改当前用户信息
          // 分配用户角色：包括 /update-user-role/:id 和 /update/:id?resource_type=user
          const isUpdateUserRole = route.path.includes('/update-user-role') || 
                                   (route.path.startsWith('/update/') && (route.query?.resource_type === 'user' || route.query?.opttype === 'user'))
          
          // 修改当前用户信息页面：显示简单的表单（姓名、邮箱、电话）
          if (isUpdateUser) {
            formFields.value = [
              {
                name: 'nikename',
                type: 'text',
                label: '姓名',
                placeholder: '请输入姓名',
                required: true,
                icon: 'user-o',
                default: response.user.nikename || ''
              },
              {
                name: 'email',
                type: 'email',
                label: '邮箱',
                placeholder: '请输入邮箱',
                required: true,
                icon: 'envelope-o',
                default: response.user.email || ''
              },
              {
                name: 'phone',
                type: 'tel',
                label: '电话',
                placeholder: '请输入电话',
                required: false,
                icon: 'phone-o',
                default: response.user.phone || ''
              }
            ]
            
            formData.value = {
              nikename: response.user.nikename || '',
              email: response.user.email || '',
              phone: response.user.phone || ''
            }
            
            header.value = '修改用户信息'
          }
          // 分配角色页面：使用多选权限模式
          else if (isUpdateUserRole) {
            
            // 确保 permission_choices 是数组格式
            let permissionOptions = response.permission_choices || []
            
            // 处理不同格式的 permission_choices
            if (!Array.isArray(permissionOptions)) {
              // 如果是对象格式，转换为数组
              if (permissionOptions && typeof permissionOptions === 'object') {
                permissionOptions = Object.keys(permissionOptions).map(key => ({
                  value: parseInt(key) || key,
                  label: permissionOptions[key]
                }))
              } else {
                permissionOptions = []
              }
            }
            
            // 确保每个选项都有 value 和 label
            permissionOptions = permissionOptions.map(option => {
              if (Array.isArray(option) && option.length === 2) {
                // Django form choices 格式: [value, label]
                return { value: option[0], label: option[1] }
              } else if (typeof option === 'object' && option.value !== undefined && option.label !== undefined) {
                return option
              }
              return null
            }).filter(Boolean)
            
            // 如果没有返回选项，使用默认选项
            if (permissionOptions.length === 0) {
              permissionOptions = [
                { value: 1, label: '教师' },
                { value: 2, label: '实训室管理员' }
              ]
              // 如果是超级管理员，添加分院管理员选项
              if (response.is_departadmin === false) {
                permissionOptions.push({ value: 4, label: '分院管理员' })
              }
            }
            
            
            // 分配角色页面：使用多选权限
            formFields.value = [
              {
                name: 'username',
                type: 'text',
                label: '用户名',
                placeholder: '用户名',
                required: true,
                readonly: false,
                icon: 'user-o',
                default: response.user.username
              },
              {
                name: 'nikename',
                type: 'text',
                label: '姓名',
                placeholder: '姓名',
                required: true,
                readonly: false,
                icon: 'user-o',
                default: response.user.nikename
              },
              {
                name: 'phone',
                type: 'tel',
                label: '手机号',
                placeholder: '请输入手机号',
                required: false,
                readonly: false,
                icon: 'phone-o',
                default: response.user.phone || ''
              },
              {
                name: 'permissions',
                type: 'permissions',
                label: '角色',
                placeholder: '请选择角色',
                required: true,
                icon: 'friends-o',
                default: response.current_permissions || [],
                options: permissionOptions
              }
            ]
            
            // 确保 formData 中的 permissions 字段被初始化为数组
            const initialPermissions = Array.isArray(response.current_permissions) 
              ? response.current_permissions 
              : (response.current_permissions ? [response.current_permissions] : [])
            
            // 初始化 formData，确保所有字段都有默认值
            // 确保 permissions 是数组格式
            const permissionsArray = Array.isArray(initialPermissions) 
              ? [...initialPermissions] 
              : []
            
            // 使用响应式方式更新 formData，确保 permissions 始终是数组
            formData.value = {
              ...formData.value,
              username: response.user.username || '',
              nikename: response.user.nikename || '',
              phone: response.user.phone || '',
              permissions: permissionsArray
            }
            
            // 确保 permissions 字段存在且是数组（双重检查）
            if (!Array.isArray(formData.value.permissions)) {
              formData.value.permissions = []
            }
            
            // 强制触发响应式更新（使用 nextTick 确保 DOM 更新）
            await nextTick()
            await nextTick() // 双重 nextTick 确保完全更新
            
            // 强制更新 formData.permissions 的响应式引用，确保复选框组能正确识别选中状态
            const currentPermissions = [...(formData.value.permissions || [])]
            formData.value.permissions = []
            await nextTick()
            formData.value.permissions = [...currentPermissions]
            await nextTick()
            
          } else {
            // 其他页面：使用原来的单选角色
            formFields.value = [
              {
                name: 'username',
                type: 'text',
                label: '用户名',
                placeholder: '用户名',
                required: true,
                readonly: true,
                icon: 'user-o',
                default: response.user.username
              },
              {
                name: 'nikename',
                type: 'text',
                label: '姓名',
                placeholder: '姓名',
                required: true,
                readonly: true,
                icon: 'user-o',
                default: response.user.nikename
              },
              {
                name: 'role',
                type: 'select',
                label: '角色',
                placeholder: '请选择角色',
                required: true,
                icon: 'friends-o',
                default: response.current_role || 3,
                options: [
                  { value: 1, label: '教师' },
                  { value: 2, label: '实训室管理员' },
                  { value: 3, label: '普通用户' }
                ]
              }
            ]
            
            formData.value = {
              username: response.user.username || '',
              nikename: response.user.nikename || '',
              role: response.current_role || 3
            }
          }
        } 
        // ========== 处理其他资源表单 ==========
        else {
          // 如果没有 user 字段，说明是编辑其他资源（课表、实训室、部门等）
          // 处理部门编辑（特殊格式：返回 dept 对象和 fields 数组）
          if (route.path.startsWith('/update/') && route.query.resource_type === 'dept') {
            if (response.dept) {
              // 使用 convertFormFieldsForUpdate 转换部门表单字段
              formFields.value = convertFormFieldsForUpdate(response.fields || [], route.path, response)
              // 部门数据在 response.dept 中
              formData.value = {
                departname: response.dept.departname || '',
                departdemo: response.dept.departdemo || ''
              }
            } else {
              formFields.value = []
            }
          }
          // 根据路由路径转换form_fields对象为数组格式
          else if (response.form_fields) {
            if (Array.isArray(response.form_fields)) {
              formFields.value = response.form_fields
            } else if (typeof response.form_fields === 'object') {
              // 如果 form_fields 是对象，根据路由路径转换为数组
              formFields.value = convertFormFieldsForUpdate(response.form_fields, route.path, response)
            } else {
              formFields.value = []
            }
          } else {
            formFields.value = []
          }
          
          // 更新 formData，但保留 permissions 字段（如果是分配角色页面）
          // 部门编辑的数据已经在上面处理了，这里跳过
          if (!(route.path.startsWith('/update/') && route.query.resource_type === 'dept')) {
            const newFormData = response.form_data || response.class || {}
            // 如果是分配角色页面，确保 permissions 字段存在且是数组
            if (route.path.startsWith('/update-user-role')) {
              if (!newFormData.permissions) {
                newFormData.permissions = Array.isArray(formData.value.permissions) ? formData.value.permissions : []
              }
              // 确保 permissions 始终是数组
              if (!Array.isArray(newFormData.permissions)) {
                newFormData.permissions = []
              }
            }
            formData.value = { ...formData.value, ...newFormData }
          }
          
          // 如果 form_fields 也为空，至少显示一个提示
          if (!Array.isArray(formFields.value) || formFields.value.length === 0) {
            console.error('后端未返回表单字段数据:', response)
            console.error('formFields.value 类型:', typeof formFields.value, formFields.value)
            const { showFailToast } = await import('@/utils/mobileDialog')
            await showFailToast('加载表单失败：后端未返回表单字段数据')
            return // 提前返回，避免后续错误
          }
        }
        
        // 确保 formFields.value 是数组
        if (!Array.isArray(formFields.value)) {
          console.error('formFields.value 不是数组:', formFields.value)
          formFields.value = []
          const { showFailToast } = await import('@/utils/mobileDialog')
          await showFailToast('加载表单失败：表单字段数据格式错误')
          return
        }
        
        
        backUrl.value = response.back_url || ''
        originalTid.value = response.original_tid || route.query.tid || '1'
        isDepartAdmin.value = response.is_departadmin || false
        
        // 强制触发响应式更新，确保视图立即刷新
        await nextTick()
        await nextTick() // 双重 nextTick 确保完全更新
        
      } catch (err) {
        console.error('加载表单失败:', err)
        
        // 获取友好的错误消息
        let errorMsg = '加载表单失败'
        if (err.response?.data?.message) {
          errorMsg = err.response.data.message
        } else if (err.response?.data?.error) {
          errorMsg = err.response.data.error
        } else if (err.message) {
          errorMsg = err.message
        }
        
        // 在控制台打印详细错误信息（用于调试）
        console.error('错误详情:', {
          message: err.message,
          response: err.response,
          status: err.response?.status,
          data: err.response?.data
        })
        
        // 检查是否是"不能给自己分配权限"的错误（检查多种可能的错误消息格式和路径）
        const isAssignRoleRoute = route.path.startsWith('/update-user-role') || 
                                  (route.path.startsWith('/update/') && (route.query?.resource_type === 'user' || route.query?.opttype === 'user'))
        const isSelfAssignError = errorMsg.includes('不能给自己分配权限') || 
                                 errorMsg.includes('您不能给自己分配权限') ||
                                 errorMsg.includes('给自己分配权限')
        
        // 移动端统一使用 showFailToast
        const { showFailToast } = await import('@/utils/mobileDialog')
        await showFailToast(errorMsg)
        // 延迟后处理返回逻辑
        setTimeout(() => {
          // 如果是分配角色/权限页面且是因为不能给自己分配权限，强制重定向到教师用户列表（tid=1）
          if (isAssignRoleRoute && isSelfAssignError) {
            router.push('/userlist/1').catch(err => {
              console.error('重定向失败:', err)
            })
          } else {
            // 其他情况返回上一页
            handleBack()
          }
        }, 2000)
      }
    }

    // ==================== 返回处理 ====================
    /**
     * 处理返回按钮点击
     * 完全前后端分离：前端根据当前路由自己决定返回路径，不再依赖后端返回的back_url
     */
    const handleBack = () => {
      // 如果是分配角色页面，确保传递 tid 参数
      let queryParams = { ...route.query }
      if (route.path.startsWith('/update-user-role') && !queryParams.tid) {
        // 如果没有 tid，尝试从 originalTid 获取，或者使用默认值
        queryParams.tid = originalTid.value || route.query.tid || route.query.typeid || '1'
      }
      
      const backPath = decideBackRoute(route.path, queryParams)
      router.push(backPath).catch(err => {
        console.error('导航失败:', err)
        // 如果导航失败，使用浏览器后退
        router.go(-1)
      })
    }

    // 移动端提交处理
    const handleSubmitMobile = async () => {
      await handleSubmit()
    }

    // ==================== 生命周期 ====================
    /**
     * 初始化组件（移动端检测和数据加载的公共逻辑）
     */
    const initComponent = () => {
      // 初始化移动端检测
      const cleanupMobile = initMobile()
      onUnmounted(() => {
        if (cleanupMobile) cleanupMobile()
      })
      
      // 预加载 Vant 组件
      setTimeout(() => {
        loadVantComponents().catch(err => {
          console.error('Vant 组件加载失败:', err)
        })
      }, 200)
      
      // 加载表单数据
      loadFormData()
    }

    /**
     * 组件挂载时加载表单数据
     */
    onMounted(() => {
      initComponent()
    })

    // 如果组件被 keep-alive 缓存，当组件激活时也需要重新加载数据
    onActivated(() => {
      // 组件激活时重新加载数据，确保显示最新内容
      loadFormData()
    })

    // 监听路由参数变化，当 id 变化时重新加载数据
    // 这样可以解决组件复用时不重新加载数据的问题
    watch(
      () => {
        // 安全地获取路由信息
        if (!route) return [undefined, undefined, undefined]
        return [route.params?.id, route.path, route.query?.tid]
      },
      ([newId, newPath, newTid], [oldId, oldPath, oldTid]) => {
        // 只有当路径或参数真正变化时才重新加载
        if (newPath !== oldPath || newId !== oldId || newTid !== oldTid) {
          loadFormData()
        }
      },
      { immediate: false }
    )

    // ==================== 导出 ====================
    /**
     * 导出组件需要的数据和方法
     */

    return {
      header,
      formFields,
      formData,
      fieldErrors,
      loading,
      backUrl,
      originalTid,
      isDepartAdmin,
      getFilteredOptions,
      handleSubmit,
      handleSubmitMobile,
      handleBack,
      showBackButton,
      user,
      pickerFields,
      showPicker,
      getPickerColumns,
      onPickerConfirm,
      isAssignRolePage,
      isUserEditPage,
      handleResetPassword,
      handleDeleteUser
    }
  }
}
</script>

