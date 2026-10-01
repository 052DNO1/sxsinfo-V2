/**
 * 表单处理组合式函�?
 * 
 * 这是表单处理的通用解决方案，封装了表单的常见操作�?
 * 
 * 主要功能�?
 * 1. 表单数据管理（响应式�?
 * 2. 表单验证
 * 3. 错误信息管理
 * 4. 表单提交
 * 5. 表单重置
 * 
 * 对于新手�?
 * - reactive 用于创建响应式对象（适合表单这种多字段场景）
 * - ref 用于创建单个响应式�?
 * - 表单验证通过 validator 函数实现，返回错误对�?
 * 
 * 使用示例�?
 * ```js
 * // 定义初始值和验证函数
 * const initialValues = { username: '', password: '' }
 * const validator = (form) => {
 *   const errors = {}
 *   if (!form.username) errors.username = '请输入用户名'
 *   if (!form.password) errors.password = '请输入密�?
 *   return errors
 * }
 * 
 * // 创建表单
 * const { form, errors, handleSubmit, isValid } = useForm(initialValues, {
 *   validator,
 *   onSubmit: async (formData) => {
 *     await api.post('/login/', formData)
 *   }
 * })
 * 
 * // 在模板中使用
 * // <input v-model="form.username" />
 * // <span v-if="errors.username">{{ errors.username }}</span>
 * ```
 */
import { ref, reactive, computed } from 'vue'

/**
 * 表单组合式函�?
 * 
 * @param {Object} initialValues - 表单初始�?
 * @param {Object} options - 配置选项
 * @param {Function} options.validator - 验证函数，返回错误对�?{ field: '错误信息' }
 * @param {Function} options.onSubmit - 提交处理函数
 * @returns {Object} 表单相关的状态和方法
 */
export function useForm(initialValues = {}, options = {}) {
  const { validator, onSubmit } = options

  // ==================== 响应式状�?====================
  
  /**
   * 表单数据对象
   * 
   * 使用 reactive 创建，可以直接绑定到表单元素
   * 例如�?input v-model="form.username" />
   */
  const form = reactive({ ...initialValues })
  
  /**
   * 错误信息对象
   * 
   * 存储每个字段的错误信�?
   * 例如：{ username: '用户名不能为�?, password: '密码太短' }
   */
  const errors = reactive({})
  
  /**
   * 是否正在提交
   * 
   * 用于禁用提交按钮，防止重复提�?
   */
  const isSubmitting = ref(false)

  /**
   * 表单是否有效
   * 
   * 条件：没有错误信�?+ 至少有一个字段有�?
   */
  const isValid = computed(() => {
    return Object.keys(errors).length === 0 &&
      Object.values(form).some(value => value !== '' && value !== null && value !== undefined)
  })

  // ==================== 字段操作方法 ====================

  /**
   * 设置字段�?
   * 
   * @param {string} field - 字段�?
   * @param {*} value - 新�?
   * 
   * 设置值的同时会清除该字段的错误信�?
   */
  const setFieldValue = (field, value) => {
    form[field] = value
    // 清除该字段的错误
    if (errors[field]) {
      delete errors[field]
    }
  }

  /**
   * 设置字段错误
   * 
   * @param {string} field - 字段�?
   * @param {string} message - 错误消息
   */
  const setFieldError = (field, message) => {
    errors[field] = message
  }

  /**
   * 清除字段错误
   * 
   * @param {string} field - 字段�?
   */
  const clearFieldError = (field) => {
    if (errors[field]) {
      delete errors[field]
    }
  }

  // ==================== 验证方法 ====================

  /**
   * 验证整个表单
   * 
   * @returns {boolean} 是否通过验证
   * 
   * 流程�?
   * 1. 清除所有现有错�?
   * 2. 调用 validator 函数获取新错�?
   * 3. 返回是否通过验证
   */
  const validate = () => {
    // 清除所有错�?
    Object.keys(errors).forEach(key => delete errors[key])

    if (validator && typeof validator === 'function') {
      const validationErrors = validator(form)
      if (validationErrors && typeof validationErrors === 'object') {
        Object.assign(errors, validationErrors)
      }
    }

    return Object.keys(errors).length === 0
  }

  /**
   * 验证单个字段
   * 
   * @param {string} field - 字段�?
   * @returns {boolean} 是否通过验证
   */
  const validateField = (field) => {
    clearFieldError(field)

    if (validator && typeof validator === 'function') {
      const validationErrors = validator(form)
      if (validationErrors && validationErrors[field]) {
        errors[field] = validationErrors[field]
        return false
      }
    }

    return true
  }

  // ==================== 提交方法 ====================

  /**
   * 提交表单
   * 
   * @param {Object} event - 事件对象（可选，用于阻止默认行为�?
   * @returns {Promise<boolean>} 是否提交成功
   * 
   * 流程�?
   * 1. 阻止表单默认提交行为
   * 2. 验证表单
   * 3. 调用 onSubmit 回调
   * 4. 处理可能的错�?
   */
  const handleSubmit = async (event) => {
    // 阻止表单默认提交行为
    if (event && event.preventDefault) {
      event.preventDefault()
    }

    // 验证表单
    if (!validate()) {
      return false
    }

    isSubmitting.value = true

    try {
      if (onSubmit && typeof onSubmit === 'function') {
        await onSubmit(form)
      }
      return true
    } catch (error) {
      // 处理提交错误
      if (error.response && error.response.data) {
        const errorData = error.response.data
        // 如果是字段错误，设置�?errors �?
        if (errorData.errors && typeof errorData.errors === 'object') {
          Object.assign(errors, errorData.errors)
        } else if (errorData.message) {
          // 通用错误消息，存储在 _form 字段
          errors._form = errorData.message
        }
      } else if (error.message) {
        errors._form = error.message
      }
      return false
    } finally {
      isSubmitting.value = false
    }
  }

  // ==================== 重置方法 ====================

  /**
   * 重置表单到初始状�?
   */
  const reset = () => {
    Object.keys(form).forEach(key => {
      form[key] = initialValues[key] !== undefined ? initialValues[key] : ''
    })
    Object.keys(errors).forEach(key => delete errors[key])
    isSubmitting.value = false
  }

  /**
   * 重置表单到指定�?
   * 
   * @param {Object} values - 新的表单�?
   */
  const resetTo = (values) => {
    Object.assign(form, values)
    Object.keys(errors).forEach(key => delete errors[key])
    isSubmitting.value = false
  }

  return {
    // 状�?
    form,
    errors,
    isSubmitting,
    isValid,
    
    // 字段操作
    setFieldValue,
    setFieldError,
    clearFieldError,
    
    // 验证
    validate,
    validateField,
    
    // 提交
    handleSubmit,
    
    // 重置
    reset,
    resetTo
  }
}
