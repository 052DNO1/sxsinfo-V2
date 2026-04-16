import { ElMessageBox, ElMessage } from 'element-plus'

export class AppError extends Error {
  code: string
  details: any
  type: string

  constructor(message: string, code: string = 'APP_ERROR', details: any = null) {
    super(message)
    this.name = 'AppError'
    this.code = code
    this.details = details
    this.type = 'app'
  }
}

export class ApiError extends AppError {
  status: number | null

  constructor(message: string, status: number | null = null, response: any = null) {
    super(message, status ? `API_ERROR_${status}` : 'API_ERROR', response)
    this.status = status
    this.type = 'api'
  }
}

export function normalizeError(error: unknown): AppError {
  if (error instanceof AppError) return error
  
  if (typeof error === 'string') return new AppError(error)
  
  if (error && typeof error === 'object' && 'response' in error) {
    const err = error as any
    const { status, data } = err.response || {}
    return new ApiError(data?.message || `请求失败 (${status})`, status, data)
  }
  
  if (error instanceof Error) return new AppError(error.message)
  
  return new AppError('未知错误，请稍后重试')
}

export const showSuccess = (message: string): void => {
  ElMessage.success(message)
}

export const showWarning = (message: string): void => {
  ElMessage.warning(message)
}

export const showInfo = (message: string): void => {
  ElMessage.info(message)
}

export const showError = (error: unknown): void => {
  const normalized = normalizeError(error)
  ElMessage.error(normalized.message)
}

export const safeConfirm = async (message: string, title: string = '提示', type: 'warning' | 'info' | 'error' | 'success' = 'warning'): Promise<boolean> => {
  try {
    await ElMessageBox.confirm(message, title, {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type
    })
    return true
  } catch (err) {
    return false
  }
}

export const safeAlert = async (message: string, title: string = '提示'): Promise<boolean> => {
  try {
    await ElMessageBox.alert(message, title, {
      confirmButtonText: '确定'
    })
    return true
  } catch (err) {
    return false
  }
}

export const safeConfirmWithInput = async (message: string, title: string = '提示', inputPlaceholder: string = '请输入"确认删除"'): Promise<boolean> => {
  try {
    const { value } = await ElMessageBox.prompt(message, title, {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPlaceholder,
      inputValidator: (val) => {
        if (val !== '确认删除') {
          return '请输入"确认删除"以继续'
        }
        return true
      }
    })
    return value === '确认删除'
  } catch (err) {
    return false
  }
}

export const showConfirm = safeConfirm

export const showConfirmDialog = async (msg: string): Promise<void> => {
  const ok = await safeConfirm(msg)
  return ok ? Promise.resolve() : Promise.reject('cancel')
}

interface BatchResultOptions {
  successItems?: any[]
  failedItems?: any[]
  successLabel?: string
  failedLabel?: string
}

export const formatBatchResult = ({ successItems = [], failedItems = [], successLabel = '项', failedLabel = '项' }: BatchResultOptions): string => {
  let msg = ''
  if (successItems.length) msg += `成功 ${successItems.length} ${successLabel}\n`
  if (failedItems.length) {
    msg += `失败 ${failedItems.length} ${failedLabel}\n`
    const details = failedItems.slice(0, 3).map(i => i.reason || i.message || String(i)).join('\n')
    msg += details + (failedItems.length > 3 ? '\n...' : '')
  }
  return msg
}

export const extractFailedItems = (response: any): any[] => {
  if (!response) return []
  
  if (response.failed_items && Array.isArray(response.failed_items)) {
    return response.failed_items
  }
  
  if (response.errors && Array.isArray(response.errors)) {
    return response.errors
  }
  
  if (response.data && response.data.failed_items && Array.isArray(response.data.failed_items)) {
    return response.data.failed_items
  }
  
  return []
}

interface HandleApiErrorOptions {
  showError?: boolean
  onError?: (error: AppError) => void | Promise<void>
}

export const handleApiError = async (error: unknown, options: HandleApiErrorOptions = {}): Promise<AppError> => {
  const { showError: shouldShowError = true, onError } = options
  const normalized = normalizeError(error)
  
  if (shouldShowError) {
    ElMessage.error(normalized.message)
  }
  
  if (onError && typeof onError === 'function') {
    await onError(normalized)
  }
  
  return normalized
}
