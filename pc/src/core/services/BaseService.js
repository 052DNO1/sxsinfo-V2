import api from '../api/client'

/**
 * 基础服务类
 * 直接返回后端V2格式的数据，不做任何转换
 */
export class BaseService {
  constructor(resourcePath) {
    this.resourcePath = resourcePath.endsWith('/') ? resourcePath : `${resourcePath}/`
  }
  
  /**
   * 获取列表
   * @returns {Object} 后端返回格式: { success, data: { list, pagination: { total, page, page_size, total_pages } } }
   */
  async list(params = {}) { 
    return await api.get(this.resourcePath, params) 
  }
  
  /**
   * 获取详情
   * @returns {Object} 后端返回格式: { success, data: { ... } }
   */
  async get(id) { 
    return await api.get(`${this.resourcePath}${id}/`) 
  }
  
  /**
   * 创建
   * @returns {Object} 后端返回格式: { success, data: { id, ... }, message }
   */
  async create(data) { 
    return await api.post(this.resourcePath, data) 
  }
  
  /**
   * 更新
   * @returns {Object} 后端返回格式: { success, data: { id, ... }, message }
   */
  async update(id, data) { 
    return await api.put(`${this.resourcePath}${id}/`, data) 
  }
  
  /**
   * 部分更新
   * @returns {Object} 后端返回格式: { success, data: { ... }, message }
   */
  async patch(id, data) { 
    return await api.patch(`${this.resourcePath}${id}/`, data) 
  }
  
  /**
   * 删除
   * @returns {Object} 后端返回格式: { success, message }
   */
  async delete(id) { 
    return await api.delete(`${this.resourcePath}${id}/`) 
  }
  
  /**
   * 批量删除
   * @returns {Object} 后端返回格式: { success, data: { deleted_count, failed_count }, message }
   */
  async batchDelete(ids, paramName = 'ids') { 
    return await api.post(`${this.resourcePath}batch_delete/`, { [paramName]: ids }) 
  }
}

// ---------------- 业务子类 ----------------

class LaboratoryService extends BaseService {
  constructor() { super('laboratories') }
  async getEquipments(labId, params = {}) {
    return await api.get(`${this.resourcePath}${labId}/equipments/`, params)
  }
  async getSchedules(labId, params = {}) {
    return await api.get(`${this.resourcePath}${labId}/schedules/`, params)
  }
  async checkDeleteImpact(ids) {
    return await api.post(`${this.resourcePath}check_delete_impact/`, { ids })
  }
}

class UserService extends BaseService {
  constructor() { super('users') }
  async updateRole(id, roleId) { 
    return await api.post(`${this.resourcePath}${id}/update_role/`, { role_id: roleId }) 
  }
  async resetPassword(id) { 
    return await api.post(`${this.resourcePath}${id}/reset_password/`) 
  }
}

class SemesterService extends BaseService {
  constructor() { super('semesters') }
  async setCurrent(id) { 
    return await api.post(`${this.resourcePath}${id}/set_current/`) 
  }
  async archive(id) { 
    return await api.post(`${this.resourcePath}${id}/archive/`) 
  }
}

class ScheduleService extends BaseService {
  constructor() { super('schedules') }
  async checkConflict(data) { 
    return await api.post(`${this.resourcePath}check_conflict/`, data) 
  }
}

class NotificationService extends BaseService {
  constructor() { super('notifications') }
  async markRead(id) { 
    return await api.post(`${this.resourcePath}${id}/mark-read/`) 
  }
}

class DepartmentService extends BaseService {
  constructor() { super('departments') }
  async delete(id, cascade = false) {
    const config = cascade ? { params: { cascade: 'true' } } : {}
    return await api.delete(`${this.resourcePath}${id}/`, config)
  }
}

// ---------------- 实例导出 ----------------

export const labService = new LaboratoryService()
export const userService = new UserService()
export const deptService = new DepartmentService()
export const semesterService = new SemesterService()
export const recordService = new BaseService('records')
export const workOrderService = new BaseService('work-orders')
export const scheduleService = new ScheduleService()
export const equipmentService = new BaseService('equipments')
export const notificationService = new NotificationService()
