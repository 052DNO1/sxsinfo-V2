import { ref, reactive, computed } from 'vue'

export function useForm(initialValues = {}, options = {}) {
  const { onSubmit } = options

  const form = reactive({ ...initialValues })
  const errors = reactive({})
  const isSubmitting = ref(false)

  const handleSubmit = async (event) => {
    if (event && event.preventDefault) {
      event.preventDefault()
    }

    isSubmitting.value = true

    try {
      if (onSubmit && typeof onSubmit === 'function') {
        await onSubmit(form)
      }
      return true
    } catch (error) {
      if (error.response && error.response.data) {
        const errorData = error.response.data
        if (errorData.errors && typeof errorData.errors === 'object') {
          Object.assign(errors, errorData.errors)
        } else if (errorData.message) {
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

  const clearFieldError = (field) => {
    if (errors[field]) {
      delete errors[field]
    }
  }

  return {
    form,
    errors,
    isSubmitting,
    handleSubmit,
    clearFieldError
  }
}
