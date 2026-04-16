/**
 * Core TypeScript 类型定义
 */

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  errors?: Record<string, string[]>
}

export interface PaginatedResponse<T = any> {
  list: T[]
  pagination: Pagination
}

export interface Pagination {
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface User {
  id: number
  username: string
  name: string
  email?: string
  is_superuser: boolean
  is_systemadmin: boolean
  is_super_admin: boolean
  is_departadmin: boolean
  is_sxsadmin: boolean
  is_teacher: boolean
  department_id?: number
  department_name?: string
  role_id?: number
  role_name?: string
}

export interface Laboratory {
  id: number
  name: string
  location: string
  capacity: number
  status: string
  department_id?: number
  department_name?: string
}

export interface Schedule {
  id: number
  laboratory_id: number
  laboratory_name?: string
  class_name: string
  teacher_name: string
  start_time: string
  end_time: string
  day_of_week: number
  semester_id?: number
}

export interface Record {
  id: number
  laboratory_id: number
  laboratory_name?: string
  user_id: number
  user_name?: string
  start_time: string
  end_time: string
  status: string
  notes?: string
}

export interface WorkOrder {
  id: number
  laboratory_id: number
  laboratory_name?: string
  reporter_id: number
  reporter_name?: string
  title: string
  description: string
  status: string
  priority: string
  created_at: string
  updated_at?: string
}

export interface Department {
  id: number
  name: string
  code?: string
  parent_id?: number
  created_at?: string
}

export interface Semester {
  id: number
  name: string
  start_date: string
  end_date: string
  is_current: boolean
  is_archived: boolean
}

export interface Equipment {
  id: number
  laboratory_id: number
  laboratory_name?: string
  name: string
  model?: string
  serial_number?: string
  status: string
  purchase_date?: string
}

export interface Notification {
  id: number
  user_id: number
  title: string
  content: string
  type: string
  is_read: boolean
  created_at: string
}

export interface FormField {
  name: string
  label: string
  type: string
  required?: boolean
  default?: any
  options?: { label: string; value: any }[]
  rules?: any[]
  placeholder?: string
  disabled?: boolean
  hidden?: boolean
}

export interface TableColumn {
  prop: string
  label: string
  width?: number | string
  minWidth?: number | string
  fixed?: string
  sortable?: boolean | string
  formatter?: (row: any, column: any, cellValue: any) => string
}

export interface Action {
  action_type: 'edit' | 'view' | 'add' | 'delete' | 'navigate'
  resource_type: string
  resource_id?: number
  url?: string
  context?: Record<string, any>
}

export interface CacheItem<T = any> {
  data: T
  timestamp: number
  ttl: number
}

export interface RequestQueueStatus {
  activeCount: number
  queueLength: number
  pendingCount: number
  maxConcurrent: number
}

export interface CacheStatus {
  size: number
  maxSize: number
  expiredCount: number
  defaultTTL: number
}

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'

export interface RequestConfig {
  method?: HttpMethod
  url?: string
  params?: Record<string, any>
  data?: any
  headers?: Record<string, string>
  cache?: boolean
  cacheTime?: number
  dedupe?: boolean
  dedupeWindow?: number
  retry?: boolean
  retryTimes?: number
  timeout?: number
  responseType?: 'json' | 'blob' | 'text' | 'arraybuffer'
  signal?: AbortSignal
}

export interface UseApiOptions {
  immediate?: boolean
  defaultData?: any
  autoHandleError?: boolean
  onError?: (error: Error) => void
  cache?: boolean
  cacheTime?: number
  dedupe?: boolean
  dedupeWindow?: number
  retry?: boolean
  retryTimes?: number
  resourceType?: string
  autoRefresh?: boolean
}

export interface UseFormOptions {
  validator?: (form: Record<string, any>) => Record<string, string>
  onSubmit?: (form: Record<string, any>) => Promise<void>
}

export interface UseCRUDOptions {
  service?: BaseService<any>
  immediate?: boolean
  defaultParams?: Record<string, any>
  itemName?: string
  listType?: string
  onDataLoaded?: (response: any) => void
  skipAutoLoad?: boolean
}

export interface UseBaseListOptions {
  adapter?: (response: any) => { data: any[]; columns: TableColumn[] }
  baseApiPath?: string
  onDataLoaded?: (response: any) => void
  immediate?: boolean
  defaultParams?: Record<string, any>
}

export interface UseDeleteOptions {
  apiPathBuilder?: (item: any) => string
  apiPath?: string
  paramName?: string
  getId?: (row: any) => number | string
  refresh?: () => void
  confirmMessageBuilder?: (item: any) => string
  method?: 'GET' | 'POST'
  handleItemDelete?: (id: number | string) => Promise<void>
}

export interface UseEntityFormOptions {
  service?: BaseService<any>
  getFields?: (data: any, response: any) => FormField[]
  onSuccess?: (response: any, formData: any) => void
  listType?: string
  dataMapper?: (data: any) => any
  configTransformFn?: (fields: any, response: any) => FormField[]
}

export abstract class BaseService<T = any> {
  protected resourcePath: string
  
  constructor(resourcePath: string)
  
  list(params?: Record<string, any>): Promise<ApiResponse<PaginatedResponse<T>>>
  get(id: number | string): Promise<ApiResponse<T>>
  create(data: Partial<T>): Promise<ApiResponse<T>>
  update(id: number | string, data: Partial<T>): Promise<ApiResponse<T>>
  patch(id: number | string, data: Partial<T>): Promise<ApiResponse<T>>
  delete(id: number | string): Promise<ApiResponse>
  batchDelete(ids: (number | string)[], paramName?: string): Promise<ApiResponse>
}
