/**
 * 表单处理组合式函数
 */

import { ref, reactive, computed, type Ref, type UnwrapNestedRefs } from 'vue'
import type { UseFormOptions } from '../../types'

interface UseFormReturn<T extends Record<string, any>> {
  form: UnwrapNestedRefs<T>
  errors: Record<string, string>
  isSubmitting: Ref<boolean>
  isValid: Ref<boolean>
  setFieldValue: (field: keyof T, value: any) => void
  setFieldError: (field: keyof T, message: string) => void
  clearFieldError: (field: keyof T) => void
  validate: () => boolean
  validateField: (field: keyof T) => boolean
  handleSubmit: (event?: Event) => Promise<boolean>
  reset: () => void
  resetTo: (values: Partial<T>) => void
}

export function useForm<T extends Record<string, any> = Record<string, any>>(initialValues: T = {} as T, options: UseFormOptions = {}): UseFormReturn<T> {
  const { validator, onSubmit } = options

  const form = reactive<T>({ ...initialValues } as T) as UnwrapNestedRefs<T>
  const errors = reactive<Record<string, string>>({})
  const isSubmitting = ref(false)

  const isValid = computed(() => {
    return Object.keys(errors).length === 0 &&
      Object.values(form).some(value => value !== '' && value !== null && value !== undefined)
  })

  const setFieldValue = (field: keyof T, value: any): void => {
    (form as any)[field] = value
    if (errors[field as string]) {
      delete errors[field as string]
    }
  }

  const setFieldError = (field: keyof T, message: string): void => {
    errors[field as string] = message
  }

  const clearFieldError = (field: keyof T): void => {
    if (errors[field as string]) {
      delete errors[field as string]
    }
  }

  const validate = (): boolean => {
    Object.keys(errors).forEach(key => delete errors[key])

    if (validator && typeof validator === 'function') {
      const validationErrors = validator(form as T)
      if (validationErrors && typeof validationErrors === 'object') {
        Object.assign(errors, validationErrors)
      }
    }

    return Object.keys(errors).length === 0
  }

  const validateField = (field: keyof T): boolean => {
    clearFieldError(field)

    if (validator && typeof validator === 'function') {
      const validationErrors = validator(form as T)
      if (validationErrors && validationErrors[field as string]) {
        errors[field as string] = validationErrors[field as string]
        return false
      }
    }

    return true
  }

  const handleSubmit = async (event?: Event): Promise<boolean> => {
    if (event && event.preventDefault) {
      event.preventDefault()
    }

    if (!validate()) {
      return false
    }

    isSubmitting.value = true

    try {
      if (onSubmit && typeof onSubmit === 'function') {
        await onSubmit(form as T)
      }
      return true
    } catch (error: any) {
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

  const reset = (): void => {
    Object.keys(form).forEach(key => {
      (form as any)[key] = initialValues[key as keyof T] !== undefined ? initialValues[key as keyof T] : ''
    })
    Object.keys(errors).forEach(key => delete errors[key])
    isSubmitting.value = false
  }

  const resetTo = (values: Partial<T>): void => {
    Object.assign(form, values)
    Object.keys(errors).forEach(key => delete errors[key])
    isSubmitting.value = false
  }

  return {
    form,
    errors,
    isSubmitting,
    isValid,
    
    setFieldValue,
    setFieldError,
    clearFieldError,
    
    validate,
    validateField,
    
    handleSubmit,
    
    reset,
    resetTo
  }
}

export default useForm
