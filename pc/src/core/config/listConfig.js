/**
 * 列表配置 - 直接对应后端V2字段
 */

export const LIST_COLUMNS = {
  laboratories: [
    { label: '名称', prop: 'name', minWidth: '120', show: true },
    { label: '编号', prop: 'code', minWidth: '100', show: true },
    { label: '设备数量', prop: 'equipment_count', minWidth: '100', show: true },
    { label: '课程数', prop: 'schedule_count', minWidth: '80', show: true },
    { label: '管理员', prop: 'admin_name', minWidth: '100', show: true },
    { label: '所属部门', prop: 'department_name', minWidth: '120', show: true },
    { label: '状态', prop: 'status_display', minWidth: '100', show: true, isStatus: true },
    { label: '备注', prop: 'note', minWidth: '150', show: true },
    { label: '操作', prop: 'actions', minWidth: '120', show: true, isAction: true }
  ],
  
  users: [
    { label: '用户名', prop: 'username', minWidth: '120', show: true },
    { label: '姓名', prop: 'nickname', minWidth: '120', show: true },
    { label: '邮箱', prop: 'email', minWidth: '180', show: true },
    { label: '手机号', prop: 'phone', minWidth: '120', show: true },
    { label: '角色', prop: 'role_display', minWidth: '150', show: true },
    { label: '管理的部门', prop: 'department_name', minWidth: '150', show: true },
    { label: '状态', prop: 'status_display', minWidth: '100', show: true, isStatus: true },
    { label: '操作', prop: 'actions', minWidth: '250', show: true, isAction: true }
  ],
  
  departments: [
    { label: '分院名称', prop: 'name', minWidth: '150', show: true },
    { label: '代码', prop: 'code', minWidth: '100', show: true },
    { label: '管理员', prop: 'manager_names', minWidth: '150', show: true },
    { label: '用户数', prop: 'user_count', minWidth: '100', show: true },
    { label: '备注', prop: 'description', minWidth: '200', show: true },
    { label: '操作', prop: 'actions', minWidth: '150', show: true, isAction: true }
  ],
  
  semesters: [
    { label: '学期名称', prop: 'name', minWidth: '150', show: true },
    { label: '学期代码', prop: 'code', minWidth: '120', show: true },
    { label: '开始日期', prop: 'start_date', minWidth: '120', show: true },
    { label: '结束日期', prop: 'end_date', minWidth: '120', show: true },
    { label: '状态', prop: 'status_display', minWidth: '120', show: true, isStatus: true },
    { label: '操作', prop: 'actions', minWidth: '150', show: true, isAction: true }
  ],
  
  records: [
    { label: '日期', prop: 'date', minWidth: '120', show: true },
    { label: '实训实验室', prop: 'laboratory_name', minWidth: '150', show: true },
    { label: '班级', prop: 'class_name', minWidth: '120', show: true },
    { label: '节次', prop: 'time_slot_display', minWidth: '100', show: true },
    { label: '教师', prop: 'teacher_name', minWidth: '120', show: true },
    { label: '内容', prop: 'content', minWidth: '200', show: true },
    { label: '操作', prop: 'actions', minWidth: '150', show: true, isAction: true }
  ],
  
  schedules: [
    { label: '星期', prop: 'weekday_display', minWidth: '100', show: true },
    { label: '节次', prop: 'time_slot_display', minWidth: '100', show: true },
    { label: '周次', prop: 'weeks_display', minWidth: '150', show: true },
    { label: '班级', prop: 'class_name', minWidth: '120', show: true },
    { label: '课程', prop: 'course_name', minWidth: '150', show: true },
    { label: '教师', prop: 'teacher_name', minWidth: '120', show: true },
    { label: '实训实验室', prop: 'laboratory_name', minWidth: '150', show: true },
    { label: '操作', prop: 'actions', minWidth: '150', show: true, isAction: true }
  ],
  
  work_orders: [
    { label: '工单编号', prop: 'order_number', minWidth: '150', show: true },
    { label: '实训实验室', prop: 'laboratory_name', minWidth: '150', show: true },
    { label: '报修人', prop: 'requester_name', minWidth: '120', show: true },
    { label: '内容', prop: 'content', minWidth: '200', show: true },
    { label: '状态', prop: 'status_display', minWidth: '100', show: true, isStatus: true },
    { label: '申请时间', prop: 'created_at', minWidth: '160', show: true },
    { label: '操作', prop: 'actions', minWidth: '200', show: true, isAction: true }
  ],
  
  maintenance_records: [
    { label: '工单编号', prop: 'order_number', minWidth: '150', show: true },
    { label: '实训实验室', prop: 'laboratory_name', minWidth: '150', show: true },
    { label: '维护人', prop: 'maintainer_name', minWidth: '120', show: true },
    { label: '内容', prop: 'content', minWidth: '200', show: true },
    { label: '状态', prop: 'status_display', minWidth: '100', show: true, isStatus: true },
    { label: '维护时间', prop: 'maintenance_time', minWidth: '160', show: true },
    { label: '操作', prop: 'actions', minWidth: '200', show: true, isAction: true }
  ],
  
  equipments: [
    { label: '设备编号', prop: 'code', minWidth: '120', show: true },
    { label: '设备名称', prop: 'name', minWidth: '150', show: true },
    { label: '所属实训室', prop: 'laboratory_name', minWidth: '150', show: true },
    { label: '状态', prop: 'status_display', minWidth: '100', show: true, isStatus: true },
    { label: '操作', prop: 'actions', minWidth: '150', show: true, isAction: true }
  ]
}

export const STATUS_MAP = {
  active: { text: '正常', type: 'success' },
  inactive: { text: '禁用', type: 'danger' },
  pending: { text: '待处理', type: 'warning' },
  processing: { text: '处理中', type: 'primary' },
  completed: { text: '已完成', type: 'success' },
  closed: { text: '已关闭', type: 'info' },
  maintained: { text: '已维护', type: 'success' },
  '待维护': { text: '待维护', type: 'warning' }
}
