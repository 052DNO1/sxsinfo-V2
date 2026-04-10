
export const importConfig = {
  device: {
    label: '设备',
    icon: 'Monitor',
    apiUrl: '/import/equipments/',
    defaultRoute: '/device-list',
    templateName: '设备导入模板.xlsx',
    requiredFields: ['实训室名称', '电脑编号'],
    optionalFields: ['设备名称', '品牌', '型号', '类型', 'CPU', '内存', '硬盘', '状态'],
    tips: [
      '电脑编号在实训室内不可重复',
      '实训室名称必须已存在',
      '状态可选值：正常、故障、维修中'
    ],
    templateData: {
      headers: ['实训室名称', '电脑编号', '设备名称', '品牌', '型号', '类型', 'CPU', '内存', '硬盘', '状态'],
      rows: [['计算机实训室1', 'PC-01', '学生机1', '联想', 'M4000', '台式机', 'i5-12400', '16G', '512G SSD', '正常']]
    }
  },

  user: {
    label: '用户',
    icon: 'User',
    apiUrl: '/import/users/',
    defaultRoute: '/user-management',
    templateName: '用户导入模板.xlsx',
    requiredFields: ['用户名', '手机号'],
    optionalFields: ['昵称', '邮箱', '部门', '权限'],
    tips: [
      '手机号请勿使用科学计数法',
      '用户名重复会自动检测',
      '权限可选值：教师、实训室管理员、分院管理员（可组合）',
      '部门需填写系统存在的完整名称'
    ],
    templateData: {
      headers: ['用户名', '昵称', '手机号', '邮箱', '部门', '权限'],
      rows: [['zhangsan', '张三', '13800000000', 'zhangsan@example.com', '计算机学院', '教师']]
    }
  },

  sxs: {
    label: '实训室',
    icon: 'OfficeBuilding',
    apiUrl: '/import/laboratories/',
    defaultRoute: '/lab-resource-management',
    templateName: '实训室导入模板.xlsx',
    requiredFields: ['实训室名称', '门牌号', '所属部门'],
    optionalFields: ['工位', '管理员', '备注'],
    tips: [
      '实训室门牌号不可重复',
      '管理员需填写系统内存在的用户昵称或用户名',
      '部门名称需准确填写'
    ],
    templateData: {
      headers: ['实训室名称', '门牌号', '工位', '管理员', '所属部门', '备注'],
      rows: [['计算机实训室1', 'A101', '40', '张老师', '计算机学院', '普通实训室']]
    }
  },

  class: {
    label: '课表',
    icon: 'Calendar',
    apiUrl: '/import/schedules/',
    defaultRoute: '/lab-resource-management',
    templateName: '课表导入模板.xlsx',
    requiredFields: ['实训室名称', '课程名称', '星期', '节次', '周次'],
    optionalFields: ['人数', '任课教师', '上课班级', '备注'],
    tips: [
      '任课教师必须是系统中已存在的用户',
      '实训室名称需与系统一致',
      '系统会自动检测时间冲突',
      '自动关联当前学期'
    ],
    templateData: {
      headers: ['实训室名称', '课程名称', '星期', '节次', '周次', '人数', '任课教师', '上课班级', '备注'],
      rows: [['计算机实训室1', 'Java程序设计', '1', '1-4', '1-18', '30', '张老师', '软件3243', '正常']]
    }
  }
}

export const getImportConfig = (type) => {
  return importConfig[type] || importConfig.class
}
