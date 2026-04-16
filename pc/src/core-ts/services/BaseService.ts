import api from '../api/client'
import type { ApiResponse, PaginatedResponse } from '../types'

export class BaseService<T = any> {
  protected resourcePath: string

  constructor(resourcePath: string) {
    this.resourcePath = resourcePath.endsWith('/') ? resourcePath : `${resourcePath}/`
  }

  async list(params: Record<string, any> = {}): Promise<ApiResponse<PaginatedResponse<T>>> {
    return await api.get(this.resourcePath, params)
  }

  async get(id: number | string): Promise<ApiResponse<T>> {
    return await api.get(`${this.resourcePath}${id}/`)
  }

  async create(data: Partial<T>): Promise<ApiResponse<T>> {
    return await api.post(this.resourcePath, data)
  }

  async update(id: number | string, data: Partial<T>): Promise<ApiResponse<T>> {
    return await api.put(`${this.resourcePath}${id}/`, data)
  }

  async patch(id: number | string, data: Partial<T>): Promise<ApiResponse<T>> {
    return await api.patch(`${this.resourcePath}${id}/`, data)
  }

  async delete(id: number | string): Promise<ApiResponse> {
    return await api.delete(`${this.resourcePath}${id}/`)
  }

  async batchDelete(ids: (number | string)[], paramName: string = 'ids'): Promise<ApiResponse> {
    return await api.post(`${this.resourcePath}batch_delete/`, { [paramName]: ids })
  }
}

export interface Laboratory extends Record<string, any> {
  id: number
  name: string
  location: string
  capacity: number
  status: string
}

export interface User extends Record<string, any> {
  id: number
  username: string
  name: string
}

export interface Semester extends Record<string, any> {
  id: number
  name: string
  is_current: boolean
}

export interface Schedule extends Record<string, any> {
  id: number
  laboratory_id: number
  class_name: string
}

export interface Notification extends Record<string, any> {
  id: number
  title: string
  is_read: boolean
}

export interface Department extends Record<string, any> {
  id: number
  name: string
}

class LaboratoryService extends BaseService<Laboratory> {
  constructor() {
    super('laboratories')
  }

  async getEquipments(labId: number, params: Record<string, any> = {}): Promise<ApiResponse> {
    return await api.get(`${this.resourcePath}${labId}/equipments/`, params)
  }

  async getSchedules(labId: number, params: Record<string, any> = {}): Promise<ApiResponse> {
    return await api.get(`${this.resourcePath}${labId}/schedules/`, params)
  }

  async checkDeleteImpact(ids: number[]): Promise<ApiResponse> {
    return await api.post(`${this.resourcePath}check_delete_impact/`, { ids })
  }
}

class UserService extends BaseService<User> {
  constructor() {
    super('users')
  }

  async updateRole(id: number, roleId: number): Promise<ApiResponse> {
    return await api.post(`${this.resourcePath}${id}/update_role/`, { role_id: roleId })
  }

  async resetPassword(id: number): Promise<ApiResponse> {
    return await api.post(`${this.resourcePath}${id}/reset_password/`)
  }
}

class SemesterService extends BaseService<Semester> {
  constructor() {
    super('semesters')
  }

  async setCurrent(id: number): Promise<ApiResponse> {
    return await api.post(`${this.resourcePath}${id}/set_current/`)
  }

  async archive(id: number): Promise<ApiResponse> {
    return await api.post(`${this.resourcePath}${id}/archive/`)
  }
}

class ScheduleService extends BaseService<Schedule> {
  constructor() {
    super('schedules')
  }

  async checkConflict(data: Record<string, any>): Promise<ApiResponse> {
    return await api.post(`${this.resourcePath}check_conflict/`, data)
  }
}

class NotificationService extends BaseService<Notification> {
  constructor() {
    super('notifications')
  }

  async markRead(id: number): Promise<ApiResponse> {
    return await api.post(`${this.resourcePath}${id}/mark-read/`)
  }
}

class DepartmentService extends BaseService<Department> {
  constructor() {
    super('departments')
  }

  async delete(id: number, cascade: boolean = false): Promise<ApiResponse> {
    const config = cascade ? { params: { cascade: 'true' } } : {}
    return await api.delete(`${this.resourcePath}${id}/`, config)
  }
}

export const labService = new LaboratoryService()
export const userService = new UserService()
export const deptService = new DepartmentService()
export const semesterService = new SemesterService()
export const recordService = new BaseService('records')
export const workOrderService = new BaseService('work-orders')
export const scheduleService = new ScheduleService()
export const equipmentService = new BaseService('equipments')
export const notificationService = new NotificationService()
