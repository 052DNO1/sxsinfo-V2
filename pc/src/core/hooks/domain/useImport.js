
import { ref } from 'vue'
import { useApi } from '@/core/hooks'
import { safeAlert } from '@/core/utils/errorHandler'
import { handleBusinessResponse } from '@/core/utils/routeDecision'
import { normalizeClassExcel } from '@/core/utils/io'
import { defaultCache } from '@/core/api/cache'

export function useImport(config, options = {}) {
  const {
    importType,
    route,
    router,
    onSuccess
  } = options

  const uploadProgress = ref(0)
  const backendProgress = ref(0)
  const isProcessing = ref(false)
  const error = ref('')
  const loading = ref(false)
  
  // Create API instance
  const apiComposable = useApi('', { immediate: false })

  const formatErrorMessage = (response) => {
    let errorMsg = response.message || '导入失败'
    
    // Header detection info
    if (response.detected_headers && Array.isArray(response.detected_headers)) {
      errorMsg += '\n\n识别到的表头：' + response.detected_headers.join(' | ')
    }
    if (response.header_row_index != null) {
      errorMsg += '\n推断的表头行：第 ' + (response.header_row_index) + ' 行'
    }
    if (response.header_map && typeof response.header_map === 'object') {
      const pairs = Object.entries(response.header_map).map(([k, v]) => `${k}→第${(v+1)}列`)
      if (pairs.length) errorMsg += '\n已匹配列：' + pairs.join(' | ')
    }
    
    // Validation info
    if (response.required && Array.isArray(response.required)) {
      errorMsg += '\n必填列：' + response.required.join(' | ')
    }
    if (response.hint) {
      errorMsg += '\n提示：' + response.hint
    }
    
    // Error summary
    if (response.error_summary) {
      const summary = Object.entries(response.error_summary)
        .slice(0, 5)
        .map(([k, v]) => `${k}: ${v}条`).join('\n')
      if (summary) errorMsg += '\n\n错误类型汇总：\n' + summary
    }
    
    // Detailed errors
    if (response.errors && response.errors.length > 0) {
      const lines = response.errors.slice(0, 10).map((e, i) => {
        const reason = typeof e === 'string' ? e : (e?.reason || JSON.stringify(e))
        return `${i + 1}. ${reason}`
      })
      errorMsg += '\n\n错误详情：\n' + lines.join('\n')
      if (response.errors.length > 10) {
        errorMsg += `\n...还有 ${response.errors.length - 10} 个错误`
      }
    }
    
    return errorMsg
  }

  const formatSuccessMessage = (response) => {
    let message = response.message || '导入成功'
    
    if (importType.value === 'class') {
      const imported = response.imported_count || 0
      const conflicts = response.skipped_conflicts || 0
      const errors = response.errors_count || 0
      
      message = `导入完成：成功导入 ${imported} 条，冲突 ${conflicts} 条，错误 ${errors} 条`
      
      if (imported === 0) {
        message += '\n未导入任何记录，请检查Excel列名或数据格式是否正确。'
      }
      
      if (response.debug_info) {
        const debug = response.debug_info
        message += `\n\n📊 数据库验证信息：\n`
        message += `- 数据库中总记录数：${debug.total_in_database || 0}\n`
        
        if (debug.recent_classes && debug.recent_classes.length > 0) {
          message += `\n最近导入的记录（前3条）：\n`
          debug.recent_classes.slice(0, 3).forEach((cls, idx) => {
            message += `${idx + 1}. ${cls.course_name} (班级: ${cls.class_name || '未设置'}, 实训项目: ${cls.laboratory__name || '未知'})\n`
          })
        }
      }
    }
    
    return message
  }

  const checkPartialErrors = (response) => {
    if (importType.value !== 'class' && response.errors && response.errors.length > 0) {
      let detailMsg = (response.message || '导入成功') + '\n\n⚠️ 虽然操作成功，但部分数据导入失败，详情如下：\n'
      const lines = response.errors.slice(0, 20).map((e, i) => {
        const reason = typeof e === 'string' ? e : (e?.reason || JSON.stringify(e))
        return `${i + 1}. ${reason}`
      })
      detailMsg += lines.join('\n')
      if (response.errors.length > 20) {
        detailMsg += `\n...还有 ${response.errors.length - 20} 条失败记录，请检查文件数据。`
      }
      return detailMsg
    }
    return null
  }

  const startPolling = () => {
    const taskMap = {
      'user': 'import_user',
      'device': 'import_equipment',
      'sxs': 'import_sxs',
      'class': 'import_class'
    }
    const taskType = taskMap[importType.value] || 'import_class'
    
    return setInterval(async () => {
      try {
        const res = await apiComposable.get({ type: taskType }, { url: '/common/progress/', quiet: true })
        if (res && res.data && res.data.percent !== undefined) {
          backendProgress.value = res.data.percent
        }
      } catch (e) {
        // ignore errors during polling
      }
    }, 500)
  }

  const submitImport = async (file) => {
    loading.value = true
    uploadProgress.value = 0
    backendProgress.value = 0
    isProcessing.value = false
    error.value = ''
    
    let progressTimer = null
    const formData = new FormData()

    try {
      let apiUrl = config.value.apiUrl
      const defaultRoute = config.value.defaultRoute

      if (importType.value === 'class') {
        const sxsid = route.params.sxsid
        apiUrl = sxsid ? `/common/import/schedules/?laboratory_id=${sxsid}` : '/common/import/schedules/'
        
        // Pre-process class excel if needed
        const uploadFile = await normalizeClassExcel(file)
        formData.append('file', uploadFile)
      } else {
        formData.append('file', file)
      }

      const response = await apiComposable.post(formData, {
        url: apiUrl,
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 120000,
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            uploadProgress.value = percent
            if (percent === 100 && !isProcessing.value) {
              isProcessing.value = true
              progressTimer = startPolling()
            }
          }
        }
      })

      if (progressTimer) clearInterval(progressTimer)
      progressTimer = null
      
      backendProgress.value = 100
      if (isProcessing.value) {
        await new Promise(resolve => setTimeout(resolve, 500))
      }

      if (response.success) {
        const cachePatterns = {
          'user': ['/users/', '/user-management/', '/auth/'],
          'device': ['/equipment/', '/devices/', '/lab-resource/'],
          'sxs': ['/laboratories/', '/sxs/', '/lab-resource/'],
          'class': ['/schedules/', '/classes/', '/lab-resource/']
        }
        
        const patterns = cachePatterns[importType.value] || []
        patterns.forEach(pattern => {
          defaultCache.clearPattern(new RegExp(`GET:${pattern}`, 'i'))
        })

        const partialErrorMsg = checkPartialErrors(response)
        if (partialErrorMsg) {
          error.value = partialErrorMsg
          await safeAlert('导入部分成功，请查看页面下方显示的失败详情。', 'warning')
          return
        }

        const successMsg = formatSuccessMessage(response)
        await safeAlert(successMsg)
        
        if (onSuccess) {
          onSuccess(response)
        } else {
          const jumped = handleBusinessResponse(response, router, {
            currentContext: { defaultRoute }
          })
          if (!jumped) {
            router.push(defaultRoute)
          }
        }
      } else {
        error.value = formatErrorMessage(response)
      }
    } catch (err) {
      let errorMsg = '导入失败：'
      
      if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
        errorMsg += '请求超时，文件可能较大，请稍后重试或减少导入数据。'
      } else if (err.message === 'Network Error' || err.code === 'ERR_NETWORK') {
        errorMsg += '网络连接失败，请检查网络连接或稍后重试'
      } else if (err.response?.data?.message) {
        // Reuse formatErrorMessage for backend errors if structure matches
        const backendErr = err.response.data
        errorMsg = formatErrorMessage(backendErr)
      } else {
        errorMsg += err.message || '未知错误，请稍后重试'
      }
      
      error.value = errorMsg
    } finally {
      if (progressTimer) clearInterval(progressTimer)
      loading.value = false
      isProcessing.value = false
    }
  }

  return {
    uploadProgress,
    backendProgress,
    isProcessing,
    error,
    loading,
    submitImport
  }
}
