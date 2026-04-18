<template>
  <!-- 移动端布局 -->
  <div class="mobile-assign-permission mobile-layout">
    <!-- 顶部导航栏 - 始终显示 -->
    <van-nav-bar
      title="分配权限"
      left-arrow
      @click-left="handleBack"
      class="mobile-nav-bar"
    />

    <!-- 表单内容 - 始终显示 -->
    <div style="padding: 16px; position: relative;">
      <!-- 加载状态覆盖层 -->
      <div v-if="isLoading" style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(255, 255, 255, 0.95); display: flex; align-items: center; justify-content: center; z-index: 100;">
        <div style="font-size: 16px; color: #969799;">加载中...</div>
      </div>
      <van-form @submit="handleSubmitMobile">
        <van-cell-group inset>
          <van-cell title="基本信息" />
          <van-field
            v-model="formData.username"
            label="用户名"
            readonly
          />
          <van-field
            v-model="formData.nikename"
            label="姓名"
            readonly
          />
        </van-cell-group>

        <!-- 权限设置 -->
        <van-cell-group inset style="margin-top: 16px;">
          <van-cell title="权限设置" />
          <van-cell v-if="filteredPermissionOptions.length > 0">
            <template #title>
              <van-checkbox-group v-model="formData.permissions" direction="horizontal">
                <van-checkbox
                  v-for="option in filteredPermissionOptions"
                  :key="`permission-${option.value}-${option.label}`"
                  :name="option.value"
                  shape="square"
                >
                  {{ option.label }}
                </van-checkbox>
              </van-checkbox-group>
            </template>
          </van-cell>
          <van-cell v-else>
            <template #title>
              <span style="font-size: 14px; color: #969799;">
                {{ isLoading ? '正在加载权限选项...' : '暂无权限选项' }}
              </span>
            </template>
          </van-cell>
          <van-cell>
            <template #title>
              <span style="font-size: 12px; color: #969799;">可以选择多个权限，用户将同时拥有所选的所有权限</span>
            </template>
          </van-cell>
          <div v-if="errors.permissions" style="padding: 8px 16px; color: #ee0a24; font-size: 12px;">
            {{ errors.permissions }}
          </div>
        </van-cell-group>

        <div style="margin-top: 24px; padding: 0;">
          <van-button
            round
            block
            type="primary"
            native-type="submit"
            :loading="loading"
          >
            {{ loading ? '提交中...' : '提交' }}
          </van-button>
        </div>
      </van-form>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onActivated, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/utils/api'
import { decideBackRoute } from '@/utils/routeDecision'
import { useMobile } from '@/composables/useMobile'

export default {
  name: 'MobileAssignPermission',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const formData = ref({
      username: '',
      nikename: '',
      permissions: []
    })
    const errors = ref({})
    const loading = ref(false)
    const isLoading = ref(true)
    const permissionOptions = ref([])
    const isDepartAdmin = ref(false)
    const originalTid = ref('')
    
    // 移动端检测
    const { init: initMobile, loadVantComponents } = useMobile()
    
    // 过滤权限选项（分院管理员不能选择分院管理员权限）
    const filteredPermissionOptions = computed(() => {
      const options = permissionOptions.value || []
      const filtered = options.filter(option => {
        // 确保 option 有 value 和 label 属性
        if (!option || typeof option !== 'object' || !option.hasOwnProperty('value')) {
          return false
        }
        if (isDepartAdmin.value && option.value === 4) {
          return false
        }
        return true
      })
      return filtered
    })
    
    // 返回处理
    const handleBack = () => {
      const backPath = decideBackRoute(route.path, route.query)
      router.push(backPath).catch(err => {
        console.error('导航失败:', err)
        router.go(-1)
      })
    }
    
    // 移动端提交处理
    const handleSubmitMobile = async () => {
      await handleSubmit()
    }

    const handleSubmit = async () => {
      loading.value = true
      errors.value = {}

      try {
        const userId = route.params.id
        if (!userId) {
          const msg = '缺少用户ID参数'
          const { showFailToast } = await import('@/utils/mobileDialog')
          await showFailToast(msg)
          return
        }
        
        const apiPath = `/userinfo/assign_permission/${userId}/`
        const submitData = {
          ...formData.value,
          original_tid: originalTid.value || route.query.tid || '1'
        }
        
        const response = await api.post(apiPath, submitData)
        if (response.success) {
          const { showSuccessToast } = await import('@/utils/mobileDialog')
          await showSuccessToast(response.message || '权限分配成功')
          const tid = originalTid.value || route.query.tid || '1'
          router.push(`/userlist/${tid}`)
        } else {
          const errorMsg = response.message || '权限分配失败'
          const { showFailToast } = await import('@/utils/mobileDialog')
          await showFailToast(errorMsg)
          if (response.errors) {
            errors.value = response.errors
          }
          // 检查是否是"不能给自己分配权限"的错误
          const isSelfAssignError = errorMsg.includes('不能给自己分配权限') || 
                                   errorMsg.includes('您不能给自己分配权限') ||
                                   errorMsg.includes('给自己分配权限')
          if (isSelfAssignError) {
            setTimeout(() => {
              router.push('/userlist/1').catch(err => {
                console.error('重定向失败:', err)
              })
            }, 2000)
          }
        }
      } catch (err) {
        console.error('提交失败:', err)
        const errorMsg = err.response?.data?.message || err.message || '权限分配失败，请检查网络连接'
        const { showFailToast } = await import('@/utils/mobileDialog')
        await showFailToast(errorMsg)
        if (err.response?.data?.errors) {
          errors.value = err.response.data.errors
        }
        // 检查是否是"不能给自己分配权限"的错误
        const isSelfAssignError = errorMsg.includes('不能给自己分配权限') || 
                                 errorMsg.includes('您不能给自己分配权限') ||
                                 errorMsg.includes('给自己分配权限')
        if (isSelfAssignError) {
          setTimeout(() => {
            router.push('/userlist/1').catch(err => {
              console.error('重定向失败:', err)
            })
          }, 2000)
        }
      } finally {
        loading.value = false
      }
    }

    const loadData = async () => {
      isLoading.value = true
      try {
        const userId = route.params.id
        if (!userId) {
          const errorMsg = '缺少用户ID参数，无法加载用户信息'
          const { showFailToast } = await import('@/utils/mobileDialog')
          await showFailToast(errorMsg)
          isLoading.value = false
          return
        }
        
        const apiPath = `/userinfo/assign_permission/${userId}/`
        const response = await api.get(apiPath, { params: route.query })
        
        if (response && response.user) {
          // 确保 permissions 是数组
          const currentPermissions = Array.isArray(response.current_permissions)             ? response.current_permissions 
            : (response.current_permissions ? [response.current_permissions] : [])
          
          formData.value.username = response.user.username || ''
          formData.value.nikename = response.user.nikename || ''
          formData.value.permissions = currentPermissions
          
          // 确保 permission_choices 是数组格式
          const choices = response.permission_choices || []
          let processedChoices = []
          
          if (Array.isArray(choices)) {
            processedChoices = choices.map(choice => {
              if (typeof choice === 'object' && choice.value !== undefined && choice.label !== undefined) {
                return choice
              } else if (Array.isArray(choice) && choice.length === 2) {
                // Django form choices 格式: (value, label)
                return { value: choice[0], label: choice[1] }
              }
              return null
            }).filter(Boolean)
          } else if (choices && typeof choices === 'object') {
            // 如果是对象，转换为数组格式
            processedChoices = Object.keys(choices).map(key => ({
              value: parseInt(key) || key,
              label: choices[key]
            }))
          }
          
          // 一次性更新所有数据，确保响应式更新
          permissionOptions.value = processedChoices
          isDepartAdmin.value = response.is_departadmin || false
          originalTid.value = response.original_tid || route.query.tid || '1'
          
          // 强制触发响应式更新，确保视图立即刷新
          await nextTick()
          await nextTick() // 双重 nextTick 确保完全更新
          
          // 如果权限选项为空，尝试重新设置
          if (filteredPermissionOptions.value.length === 0 && processedChoices.length > 0) {
            await nextTick()
          }
        } else {
          console.error('响应数据格式不正确:', response)
          const errorMsg = '加载用户信息失败：响应数据格式不正确'
          const { showFailToast } = await import('@/utils/mobileDialog')
          await showFailToast(errorMsg)
        }
      } catch (err) {
        console.error('加载数据失败:', err)
        const errorMsg = err.response?.data?.message || err.response?.statusText || err.message || '未知错误'
        const fullErrorMsg = `加载用户信息失败：${errorMsg}`
        
        // 检查是否是"不能给自己分配权限"的错误
        const isSelfAssignError = errorMsg.includes('不能给自己分配权限') || 
                                 errorMsg.includes('您不能给自己分配权限') ||
                                 errorMsg.includes('给自己分配权限')
        
        const { showFailToast } = await import('@/utils/mobileDialog')
        showFailToast(fullErrorMsg)
        setTimeout(() => {
          if (isSelfAssignError) {
            router.push('/userlist/1').catch(err => {
              console.error('重定向失败:', err)
            })
          } else {
            handleBack()
          }
        }, 2000)
      } finally {
        isLoading.value = false
      }
    }

    // 初始化移动端检测和数据加载的公共逻辑
    const initComponent = () => {
      // 初始化移动端检测
      const cleanupMobile = initMobile()
      // 预加载 Vant 组件（不阻塞）
      loadVantComponents().catch(err => {
        console.error('Vant 组件加载失败:', err)
      })
      
      // 加载数据
      loadData()
    }

    onMounted(() => {
      initComponent()
    })

    // 如果组件被 keep-alive 缓存，当组件激活时也需要重新加载数据
    onActivated(() => {
      // 组件激活时重新加载数据，确保显示最新内容
      loadData()
    })

    // 监听路由参数和查询参数变化，当变化时重新加载数据
    watch(
      () => [route.params.id, route.query.tid],
      ([newId, newTid], [oldId, oldTid]) => {
        // 只有当 id 真正变化时才重新加载（避免初始化时重复加载）
        if (newId && newId !== oldId) {
          loadData()
        }
      },
      { immediate: false }
    )

    return {
      formData,
      errors,
      loading,
      isLoading,
      permissionOptions,
      isDepartAdmin,
      originalTid,
      filteredPermissionOptions,
      handleSubmit,
      handleSubmitMobile,
      handleBack
    }
  }
}
</script>
/* mobile.css 已在 main.js 中统一导入 */

/* 移动端样式 */
.mobile-assign-permission {
  min-height: 100vh;
  background: #f7f8fa;
}


