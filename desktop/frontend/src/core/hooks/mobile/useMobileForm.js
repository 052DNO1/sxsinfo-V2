/**
 * 移动端表单Hook适配器
 * 
 * 复用PC端的Service进行表单提交
 */

import { ref, reactive, computed } from 'vue'
import { useForm } from '@/core/hooks/base/useForm'
import { showSuccess, showError } from '@/core/utils/errorHandler'

/**
 * 移动端通用表单Hook
 * @param {Object} options
 * @param {Object} options.service - BaseService实例
 * @param {Object} options.initialData - 初始表单数据
 * @param {Function} options.beforeSubmit - 提交前数据处理
 * @param {Function} options.afterSubmit - 提交后处理
 * @param {String} options.mode - 'create' | 'edit' | null(自动判断)
 * @param {Number|String} options.editId - 编辑模式的ID
 */
export function useMobileForm(options = {}) {
  const {
    service,
    initialData = {},
    beforeSubmit = null,
    afterSubmit = null,
    mode = null,
    editId = null,
    successMessage = '操作成功',
    errorMessage = '操作失败',
    successRoute = null
  } = options

  const isEditMode = computed(() => mode === 'edit' || !!editId)

  // 使用已有的 useForm hook
  const form = useForm(initialData, {
    onSubmit: async (data) => {
      try {
        let submitData = data
        
        // 提交前处理
        if (beforeSubmit) {
          submitData = await beforeSubmit(data, isEditMode.value)
        }

        let response
        
        if (isEditMode.value) {
          response = await service.update(editId, submitData)
        } else {
          response = await service.create(submitData)
        }

        if (response?.success !== false) {
          showSuccess(response?.message || successMessage)
          
          if (afterSubmit) {
            await afterSubmit(response, isEditMode.value)
          }
          
          return response
        } else {
          showError(response?.message || errorMessage)
          throw new Error(response?.message || errorMessage)
        }
      } catch (err) {
        showError(err.message || errorMessage)
        throw err
      }
    }
  })

  // 加载编辑数据
  const loadEditData = async (id) => {
    form.setLoading(true)
    try {
      const response = await service.get(id)
      if (response?.success !== false && response?.data) {
        form.setFormData(response.data)
        return response.data
      }
    } catch (err) {
      showError('加载数据失败')
    } finally {
      form.setLoading(false)
    }
  }

  // 重置表单
  const resetForm = () => {
    form.reset()
  }

  return {
    ...form,
    isEditMode,
    loadEditData,
    resetForm,
    successRoute
  }
}
