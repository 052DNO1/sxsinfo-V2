<template>
  <!-- 移动端直接显示内容 -->
  <div class="mobile-import-page mobile-layout">
    <van-nav-bar
      :title="header || (importType === 'user' ? '导入用户' : '导入课表')"
      left-arrow
      @click-left="goBack"
      class="mobile-nav-bar"
    />

    <div class="mobile-content-wrapper">
      <!-- 导入说明 -->
      <van-cell-group inset style="margin-top: 12px;">
        <van-cell title="导入说明" />
        <van-cell v-if="importType === 'user'">
          <template #title>
            <div style="line-height: 1.6;">
              <div style="margin-bottom: 8px;"><strong>文件格式：</strong>支持 .xlsx、.xls 格式</div>
              <div style="margin-bottom: 8px;"><strong>批量创建：</strong>一次性导入多个教师用户</div>
              <div style="margin-bottom: 8px;"><strong>默认密码：</strong>新用户默认密码为用户名后6位</div>
              <div style="color: #ee0a24; margin-top: 12px; display: flex; align-items: center;">
                <van-icon name="warning-o" size="16px" style="margin-right: 4px;" />
                <strong>注意事项：</strong>
              </div>
              <div>• 请确保Excel文件格式正确</div>
              <div>• 手机号不要用科学计数法</div>
              <div>• 用户名不能重复</div>
            </div>
          </template>
        </van-cell>
        <van-cell v-else>
          <template #title>
            <div style="line-height: 1.6;">
              <div style="margin-bottom: 8px;"><strong>列名示例：</strong></div>
              <div>实训室、课程名称、星期、节次、周次、人数、任课教师、上课班级、备注</div>
              <div style="color: #ee0a24; margin-top: 12px; display: flex; align-items: center;">
                <van-icon name="warning-o" size="16px" style="margin-right: 4px;" />
                <strong>注意事项：</strong>
              </div>
              <div>• 第一行必须是表头</div>
              <div>• 系统会自动检测时间冲突</div>
              <div>• 导入的课表会自动关联当前学期</div>
            </div>
          </template>
        </van-cell>
      </van-cell-group>

      <!-- 文件上传 -->
      <van-form @submit="handleSubmitMobile" style="margin-top: 12px;">
        <van-cell-group inset>
          <van-field
            v-model="fileDisplayName"
            label="选择文件"
            placeholder="点击选择Excel文件"
            readonly
            is-link
            @click="triggerFileInput"
          />
          <input
            ref="fileInputRef"
            type="file"
            accept=".xlsx,.xls"
            @change="handleFileChange"
            style="display: none;"
          />
        </van-cell-group>

        <div style="padding: 16px;">
          <van-button
            type="primary"
            block
            native-type="submit"
            :loading="loading"
            :disabled="!selectedFile"
          >
            {{ loading ? '导入中...' : '开始导入' }}
          </van-button>
        </div>
      </van-form>

      <!-- 错误信息 -->
      <van-notice-bar
        v-if="error"
        :text="error"
        color="#ee0a24"
        background="#fff2f0"
        wrapable
        style="margin: 12px;"
      />
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/utils/api'
import { handleBusinessResponse } from '@/utils/routeDecision'
import { useMobile } from '@/composables/useMobile'

export default {
  name: 'Import',
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    // 根据路由判断导入类型
    const importType = computed(() => {
      // 如果路由路径包含 import-user，则是导入用户
      if (route.path.includes('import-user')) {
        return 'user'
      }
      // 否则是导入课表
      return 'class'
    })
    
    const header = ref(importType.value === 'user' ? '导入用户' : '导入课表')
    const selectedFile = ref(null)
    const error = ref('')
    const loading = ref(false)
    const backUrl = ref('')
    const fileInputRef = ref(null)
    const fileDisplayName = ref('')
    
    // 移动端初始化
    const { init: initMobile, loadVantComponents } = useMobile()
    
    const triggerFileInput = () => {
      fileInputRef.value?.click()
    }

    const handleFileChange = (file) => {
      // 原生input change事件
      if (file && file.target) {
        selectedFile.value = file.target.files[0]
        fileDisplayName.value = selectedFile.value ? selectedFile.value.name : ''
      } else if (file && file instanceof File) {
        selectedFile.value = file
        fileDisplayName.value = file.name
      }
    }
    
    // 移动端提交处理
    const handleSubmitMobile = async () => {
      if (!selectedFile.value) {
        const { showFailToast } = await import('@/utils/mobileDialog')
        showFailToast('请选择文件')
        return
      }
      await handleSubmit()
    }

    const handleSubmit = async () => {
      if (!selectedFile.value) {
        error.value = '请选择文件'
        return
      }

      loading.value = true
      error.value = ''

      const formData = new FormData()
      formData.append('excel_file', selectedFile.value)

      try {
        let apiUrl
        let defaultRoute
        
        if (importType.value === 'user') {
          // 导入用户
          apiUrl = '/import-user/'
          defaultRoute = '/user-management'
          formData.append('excel_file', selectedFile.value)
        } else {
          // 导入课表
          const sxsid = route.params.sxsid
          apiUrl = sxsid ? `/sxs/import_class/${sxsid}/` : '/sxs/import_class/'
          defaultRoute = '/lab-resource-management'
        }

        const response = await api.post(apiUrl, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          timeout: importType.value === 'user' ? 120000 : undefined  // 导入用户需要更长的超时时间
        })
        
        if (response.success) {
          let message = response.message || '导入成功'
          
          // 导入课表时显示调试信息
          if (importType.value === 'class' && response.debug_info) {
            const debug = response.debug_info
            message += `\n\n数据库验证信息：\n`
            message += `- 数据库中总记录数：${debug.total_in_database || 0}\n`
            message += `- 班级分组数量：${debug.class_groups_count || 0}\n`
            if (debug.class_groups && debug.class_groups.length > 0) {
              message += `- 班级列表：${debug.class_groups.slice(0, 5).join(', ')}${debug.class_groups.length > 5 ? '...' : ''}\n`
            }
            if (debug.recent_classes && debug.recent_classes.length > 0) {
              message += `\n最近导入的记录（前3条）：\n`
              debug.recent_classes.slice(0, 3).forEach((cls, idx) => {
                message += `${idx + 1}. ${cls.classname} (班级: ${cls.class_group || '未设置'}, 实训室: ${cls.sxsname__sxsname || '未知'})\n`
              })
            }
          }
          
          const { showSuccessToast, showFailToast } = await import('@/utils/mobileDialog')
          if (message.includes('成功') || message.includes('完成')) {
            await showSuccessToast(message)
          } else {
            await showFailToast(message)
          }
          
          // 完全前后端分离：根据业务数据自己决定路由
          const jumped = handleBusinessResponse(response, router, {
            currentContext: { defaultRoute }
          })
          if (!jumped) {
            router.push(defaultRoute)
          }
        } else {
          // 显示详细的错误信息，包括错误列表
          let errorMsg = response.message || '导入失败'
          if (response.errors && response.errors.length > 0) {
            errorMsg += '\n\n错误详情：\n' + response.errors.slice(0, 10).join('\n')
            if (response.errors.length > 10) {
              errorMsg += `\n...还有 ${response.errors.length - 10} 个错误`
            }
          }
          error.value = errorMsg
        }
      } catch (err) {
        console.error('导入错误:', err)
        let errorMsg = '导入失败：'
        
        // 处理不同类型的错误
        if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
          errorMsg += '请求超时，文件可能较大，请稍后重试或减少导入数据量'
        } else if (err.message === 'Network Error' || err.code === 'ERR_NETWORK') {
          errorMsg += '网络连接失败，请检查网络连接或稍后重试'
        } else if (err.response?.data?.message) {
          errorMsg += err.response.data.message
          if (err.response.data.errors && err.response.data.errors.length > 0) {
            errorMsg += '\n\n错误详情：\n' + err.response.data.errors.slice(0, 10).join('\n')
            if (err.response.data.errors.length > 10) {
              errorMsg += `\n...还有 ${err.response.data.errors.length - 10} 个错误`
            }
          }
        } else {
          errorMsg += err.message || '未知错误，请稍后重试'
        }
        
        error.value = errorMsg
      } finally {
        loading.value = false
      }
    }

    const goBack = () => {
      // 完全前后端分离：前端自己决定路由
      if (importType.value === 'user') {
        router.push('/user-management')
      } else {
        router.push('/lab-resource-management')
      }
    }

    const loadData = async () => {
      try {
        let apiUrl
        
        if (importType.value === 'user') {
          apiUrl = '/import-user/'
        } else {
          const sxsid = route.params.sxsid
          apiUrl = sxsid ? `/sxs/import_class/${sxsid}/` : '/sxs/import_class/'
        }
        
        const response = await api.get(apiUrl)
        header.value = response.header || (importType.value === 'user' ? '导入用户' : '导入课表')
        backUrl.value = response.back_url || ''
      } catch (err) {
        console.error('Load data error:', err)
      }
    }

    onMounted(() => {
      // 初始化移动端检测
      const cleanupMobile = initMobile()
      onUnmounted(() => {
        if (cleanupMobile) cleanupMobile()
      })
      
      // 预加载 Vant 组件
      setTimeout(() => {
        loadVantComponents()
      }, 200)
      
      loadData()
    })

    return {
      importType,
      header,
      selectedFile,
      error,
      loading,
      backUrl,
      fileInputRef,
      fileDisplayName,
      handleFileChange,
      handleSubmit,
      handleSubmitMobile,
      triggerFileInput,
      goBack
    }
  }
}
</script>

<style scoped>
/* mobile.css 已在 main.js 中统一导入 */
</style>


