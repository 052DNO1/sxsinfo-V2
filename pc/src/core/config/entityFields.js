/**
 * 实体表单字段配置 (V2)
 * 用于统一定义各模块的表单字段、验证规则和选项
 */

const isLabAvailable = (l) => {
  if (l.disabled !== undefined) return !l.disabled
  if (l.is_available === false) return false
  if (l.status !== undefined && l.status !== 1) return false
  return true
}

const getStatusText = (l) => {
  if (l.status_text) return l.status_text
  if (l.status_display && typeof l.status_display === 'object') return l.status_display.text
  if (l.status_display && typeof l.status_display === 'string') return l.status_display
  if (l.is_available === true) return '可用'
  if (l.is_available === false) return '不可用'
  if (l.status === 1) return '可用'
  if (l.status === 2) return '使用中'
  if (l.status === 3) return '维护中'
  if (l.status === 4) return '不可用'
  return '未知'
}

export const formatLabOption = (l) => {
  const code = l.code || l.room_number || ''
  const name = l.name || l.laboratory_name || ''
  const isDisabled = !isLabAvailable(l)
  const statusText = getStatusText(l)
  
  return {
    value: l.id,
    label: l.text || `${code} ${name}`.trim(),
    statusLabel: `${code} ${name} - ${statusText}`.trim(),
    disabled: isDisabled
  }
}

export const VALIDATION_RULES = {
  required: (msg) => [{ required: true, message: msg, trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: ['blur', 'change'] }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的11位手机号', trigger: ['blur', 'change'] }
  ],
  numericCode: [
    { required: true, message: '请输入门牌号', trigger: 'blur' },
    { pattern: /^\d+$/, message: '门牌号只能包含数字', trigger: ['blur', 'change'] }
  ]
}

const field = (name, label, type = 'text', extra = {}) => ({
  name, label, type, 
  placeholder: extra.placeholder || `请输入${label}`,
  required: extra.required || false,
  icon: extra.icon || 'Document',
  ...extra
})

export const getUserFields = (data = {}) => [
  field('username', '用户名', 'text', { required: true, icon: 'User' }),
  field('nickname', '姓名', 'text', { required: true, icon: 'PriceTag' }),
  field('email', '邮箱', 'email', { icon: 'Message', rules: VALIDATION_RULES.email }),
  field('phone', '手机号', 'tel', { icon: 'Iphone', rules: VALIDATION_RULES.phone }),
  field('department', '所属部门', 'select', {
    required: true,
    icon: 'OfficeBuilding',
    options: (data.departments || []).map(d => ({ value: d.id, label: d.name }))
  }),
  field('role', '角色', 'select', {
    required: true,
    icon: 'UserFilled',
    options: data.role_choices || []
  })
]

export const getSxsFields = (data = {}) => [
  field('name', '实训室名称', 'text', { required: true, icon: 'OfficeBuilding' }),
  field('code', '门牌号', 'text', { required: true, icon: 'Document', placeholder: '请输入门牌号（仅限数字）', rules: VALIDATION_RULES.numericCode }),
  field('capacity', '工位数', 'number', { required: true, icon: 'Grid' }),
  field('admin', '管理员', 'select', {
    required: false,
    icon: 'User',
    options: data.admin_options || []
  }),
  field('status', '状态', 'select', {
    required: true,
    icon: 'DataLine',
    options: data.status_choices || [
      { value: 1, label: '可用' },
      { value: 2, label: '使用中' },
      { value: 3, label: '维护中' },
      { value: 4, label: '不可用' }
    ],
    default: 1
  }),
  field('note', '备注', 'textarea', { rows: 4 })
]

export const getDeviceFields = (data = {}) => [
  field('code', '设备编号', 'text', { required: true, icon: 'Document' }),
  field('name', '设备名称', 'text', { required: true, icon: 'Monitor' }),
  field('brand', '品牌', 'text', { icon: 'PriceTag' }),
  field('model', '型号', 'text', { icon: 'DataAnalysis' }),
  field('config', '配置', 'text', { 
    icon: 'Setting',
    placeholder: '如：i5-12500/16g/512g',
    help_text: '格式示例：CPU/内存/硬盘，如 i5-12500/16g/512g'
  }),
  field('laboratory', '所属实训室', 'select', {
    required: true,
    icon: 'OfficeBuilding',
    options: (data.lab_options || []).map(formatLabOption)
  }),
  field('status', '状态', 'select', {
    required: true,
    icon: 'DataLine',
    options: data.status_choices || [
      { value: 'NORMAL', label: '正常' },
      { value: 'MAINTENANCE', label: '维护中' },
      { value: 'DAMAGED', label: '损坏' }
    ],
    default: 'NORMAL'
  }),
  field('note', '备注', 'textarea', { rows: 4 })
]

export const getClassFields = (data = {}) => [
  field('laboratory', '实训室', 'select', {
    required: true,
    icon: 'OfficeBuilding',
    options: (data.lab_options || []).map(formatLabOption)
  }),
  field('weekday', '星期', 'select', {
    required: true,
    icon: 'Calendar',
    options: [
      { value: 1, label: '星期一' },
      { value: 2, label: '星期二' },
      { value: 3, label: '星期三' },
      { value: 4, label: '星期四' },
      { value: 5, label: '星期五' },
      { value: 6, label: '星期六' },
      { value: 7, label: '星期日' }
    ]
  }),
  field('time_slot', '节次', 'select', {
    required: true,
    icon: 'Timer',
    options: data.time_slot_options || [
      { value: '1-2', label: '1-2节（上午第1-2节）' },
      { value: '3-4', label: '3-4节（上午第3-4节）' },
      { value: '5-6', label: '5-6节（下午第1-2节）' },
      { value: '7-8', label: '7-8节（下午第3-4节）' },
      { value: '9-10', label: '9-10节（晚上）' },
      { value: '1-4', label: '1-4节（上午连课）' },
      { value: '5-8', label: '5-8节（下午连课）' },
      { value: '1-6', label: '1-6节（全天）' },
      { value: '1-8', label: '1-8节（全天含晚自习）' }
    ],
    help_text: '选择上课节次，支持连续节次'
  }),
  field('weeks', '周次', 'text', { 
    required: true, 
    icon: 'Calendar',
    placeholder: '如：1-16 或 1,3,5,7',
    help_text: '请输入周次，支持格式：1-16 或 1,3,5,7'
  }),
  field('class_name', '班级', 'text', { required: true, icon: 'School' }),
  field('course_name', '课程名称', 'text', { required: true, icon: 'Reading' }),
  field('teacher', '教师', 'select', {
    required: true,
    icon: 'Avatar',
    options: data.teacher_options || []
  }),
  field('note', '备注', 'textarea', { rows: 3 })
]

export const getRecordFields = (data = {}) => [
  field('laboratory', '实训室', 'select', { 
    required: true,
    icon: 'OfficeBuilding',
    options: (data.lab_options || data.sxs_list || []).map(formatLabOption)
  }),
  field('date', '使用日期', 'date', { required: true, icon: 'Calendar', default: new Date().toISOString().split('T')[0] }),
  field('time_slot', '节次', 'select', { required: true, icon: 'Timer', options: data.time_slot_choices || [] }),
  field('teacher', '教师', 'select', {
    required: true,
    icon: 'Avatar',
    options: (data.teacher_options || []).map(t => ({ value: t.id, label: t.nickname }))
  }),
  field('class_name', '上课班级', 'text', { required: true, icon: 'School' }),
  field('student_count', '使用人数', 'number', { default: 20, icon: 'User' }),
  field('content', '实训内容', 'textarea', { required: true, rows: 4, fullWidth: true })
]

export const getTermFields = (data = {}) => [
  field('name', '学期名称', 'text', { required: true, icon: 'Calendar', placeholder: '如：2024-2025第一学期' }),
  field('start_date', '开始日期', 'date', { required: true, icon: 'Calendar' }),
  field('end_date', '结束日期', 'date', { required: true, icon: 'Calendar' }),
  field('is_current', '设为当前学期', 'select', {
    icon: 'Star',
    options: [
      { value: true, label: '是' },
      { value: false, label: '否' }
    ],
    default: true
  })
]

export const getDeptFields = (data = {}) => [
  field('name', '部门名称', 'text', { required: true, icon: 'OfficeBuilding', placeholder: '如：计算机学院' }),
  field('code', '部门代码', 'text', { required: false, icon: 'Document', placeholder: '如：CS' }),
  field('managers', '部门管理员', 'select', {
    required: false,
    icon: 'User',
    multiple: true,
    options: (data.user_options || []).map(u => ({ value: u.id, label: u.nickname || u.username })),
    help_text: '可选择多个管理员，每个用户只能管理一个部门'
  }),
  field('description', '备注', 'textarea', { rows: 4, fullWidth: true, placeholder: '请输入部门简介或职责说明' })
]

export const getMaintainFields = (data = {}) => [
  field('laboratory', '实训实验室', 'select', {
    required: true,
    icon: 'OfficeBuilding',
    options: (data.laboratories || []).map(formatLabOption)
  }),
  field('maintainer', '维护人', 'select', {
    required: false,
    icon: 'User',
    options: data.maintainer_options || [],
    default: data.default_maintainer?.id
  }),
  field('content', '维护内容', 'textarea', {
    required: true,
    rows: 4,
    fullWidth: true,
    icon: 'Document'
  }),
  field('status', '状态', 'select', {
    required: true,
    icon: 'DataLine',
    options: [
      { value: 'maintained', label: '已维护' },
      { value: 'pending', label: '待维护' },
      { value: 'processing', label: '维护中' }
    ],
    default: 'maintained'
  }),
  field('maintenance_time', '维护时间', 'datetime', {
    required: true,
    icon: 'Calendar',
    default: new Date().toISOString()
  }),
  field('note', '备注', 'textarea', { rows: 3, fullWidth: true })
]

export const getFaultFields = (data = {}) => [
  field('laboratory', '实训室', 'select', {
    required: true,
    icon: 'OfficeBuilding',
    options: (data.laboratories || []).map(formatLabOption),
    disabled: data.current_laboratory ? true : false,
    default: data.current_laboratory?.id
  }),
  field('device_code', '设备编号', 'text', {
    required: true,
    icon: 'Monitor',
    placeholder: '请输入故障设备编号（如 01）'
  }),
  field('reporter', '上报人', 'text', {
    required: true,
    icon: 'User',
    default: data.current_user_name || ''
  }),
  field('reported_at', '上报时间', 'datetime', {
    required: true,
    icon: 'Calendar',
    default: new Date().toISOString()
  }),
  field('fault_type', '故障类型', 'select', {
    required: true,
    icon: 'Warning',
    options: data.fault_type_options || [
      { value: 'hardware', label: '硬件故障' },
      { value: 'software', label: '软件故障' },
      { value: 'network', label: '网络故障' },
      { value: 'other', label: '其他故障' }
    ],
    default: 'hardware'
  }),
  field('priority', '优先级', 'select', {
    required: true,
    icon: 'Star',
    options: [
      { value: 'low', label: '低' },
      { value: 'medium', label: '中' },
      { value: 'high', label: '高' },
      { value: 'urgent', label: '紧急' }
    ],
    default: 'medium'
  }),
  field('description', '故障描述', 'textarea', {
    required: true,
    rows: 4,
    fullWidth: true,
    icon: 'Document',
    placeholder: '请详细描述故障情况'
  }),
  field('status', '处理状态', 'select', {
    required: true,
    icon: 'DataLine',
    options: [
      { value: 'PENDING', label: '待处理' },
      { value: 'PROCESSING', label: '处理中' },
      { value: 'COMPLETED', label: '已完成' },
      { value: 'CLOSED', label: '已关闭' }
    ],
    default: 'PENDING'
  }),
  field('note', '备注', 'textarea', { rows: 3, fullWidth: true })
]
