/**
 * 移动端Hooks入口文件
 * 导出所有移动端专用的hooks
 */

export { useMobileList, createMobileList } from './useMobileList'
export { useMobileForm } from './useMobileForm'

// 同时导出所有PC端hooks供移动端直接使用
export { useApi } from '../base/useApi'
export { useForm } from '../base/useForm'
export { useAuth } from '../../auth/useAuth'
export { useDelete } from '../base/useDelete'

// 导出Services
export { 
  labService, 
  userService, 
  deptService, 
  semesterService, 
  recordService, 
  workOrderService, 
  scheduleService, 
  equipmentService, 
  notificationService 
} from '../../services/BaseService'

// 导出配置
export { LIST_COLUMNS, STATUS_MAP } from '../../config/listConfig'
