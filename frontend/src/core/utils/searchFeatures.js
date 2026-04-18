/**
 * 全局搜索功能定义
 * 包含所有可搜索的功能项及其权限配置
 */

export const searchFeatures = [
  {
    id: 'home',
    title: '首页',
    subtitle: '返回系统首页',
    action_type: 'navigate',
    resource_type: 'home',
    aliases: ['主页', 'home', 'index'],
    roles: ['all']
  },
  {
    id: 'global_search',
    title: '全局搜索',
    subtitle: '搜索全站数据与功能',
    action_type: 'navigate',
    resource_type: 'global_search',
    aliases: ['搜索', '全站搜索', '查找'],
    roles: ['all']
  },
  {
    id: 'change_password',
    title: '修改密码',
    subtitle: '更新您的登录密码',
    action_type: 'navigate',
    resource_type: 'change_password',
    aliases: ['改密码', '重置密码', 'password', 'change password'],
    roles: ['all']
  },
  {
    id: 'update_user',
    title: '修改用户信息',
    subtitle: '更新个人资料',
    action_type: 'navigate',
    resource_type: 'update_user',
    aliases: ['修改个人信息', '个人信息', 'profile', 'update user'],
    roles: ['all']
  },
  {
    id: 'message',
    title: '工单中心',
    subtitle: '查看故障工单与维护记录',
    action_type: 'navigate',
    resource_type: 'workorder-center',
    aliases: ['工单', '故障', '维护', 'workorder', 'ticket'],
    roles: ['all']
  },
  {
    id: 'logout',
    title: '退出登录',
    subtitle: '安全退出当前账户',
    action_type: 'navigate',
    resource_type: 'logout',
    aliases: ['登出', '退出', 'logout', 'sign out'],
    roles: ['all']
  },

  {
    id: 'user_management',
    title: '用户管理',
    subtitle: '管理与分配用户角色',
    action_type: 'navigate',
    resource_type: 'user_management_dashboard',
    aliases: ['管理用户', '权限分配', 'user management'],
    roles: ['superuser', 'departadmin']
  },
  {
    id: 'all_labs',
    title: '全部实训室',
    subtitle: '查看分院全部实训室',
    action_type: 'navigate',
    resource_type: 'lab_resource_management_dashboard',
    aliases: ['实训室', '所有实训室', 'lab', 'labs'],
    roles: ['superuser', 'departadmin']
  },
  {
    id: 'stats',
    title: '综合统计',
    subtitle: '查看系统综合统计',
    action_type: 'navigate',
    resource_type: 'comprehensive_stats',
    aliases: ['统计', '数据统计', 'stats', 'dashboard'],
    roles: ['superuser', 'departadmin', 'sxsadmin']
  },
  {
    id: 'backup_manage',
    title: '数据备份与恢复',
    subtitle: '备份系统数据，防止数据丢失',
    action_type: 'navigate',
    resource_type: 'backup_manage',
    aliases: ['备份', '恢复', 'backup', '数据备份'],
    roles: ['superuser']
  },
  {
    id: 'import_schedule',
    title: '导入课表',
    subtitle: '批量导入学期课表',
    action_type: 'navigate',
    resource_type: 'import-class',
    aliases: ['导入课表', '课表导入', '我需要导入课表', 'import schedule'],
    roles: ['superuser', 'departadmin']
  },
  {
    id: 'report_fault',
    title: '故障报修',
    subtitle: '提交设备故障报修',
    action_type: 'navigate',
    resource_type: 'report-maintenance',
    aliases: ['报修', '故障报修', '我要报修', 'report fault', 'maintenance'],
    roles: ['teacher', 'sxsadmin', 'superuser', 'departadmin']
  },
  {
    id: 'send_notification',
    title: '故障上报',
    subtitle: '上报设备故障问题',
    action_type: 'navigate',
    resource_type: 'add-record',
    context: { type: 'fault' },
    aliases: ['故障上报', '报修', '上报故障', 'report fault'],
    roles: ['all']
  },

  {
    id: 'my_labs',
    title: '我管理的实训室',
    subtitle: '查看与管理我负责的实训室',
    action_type: 'navigate',
    resource_type: 'sxs_list',
    context: { qtype: 2 },
    aliases: ['我的实训室', '管理的实训室'],
    roles: ['sxsadmin'],
    exclude_roles: ['departadmin', 'superuser']
  },

  {
    id: 'teaching_center',
    title: '个人教学中心',
    subtitle: '查看我的实训记录',
    action_type: 'navigate',
    resource_type: 'personal_teaching_dashboard',
    aliases: ['个人中心', '教学中心', 'personal'],
    roles: ['teacher']
  }
]

/**
 * 根据用户权限过滤功能列表
 * @param {Object} user 用户对象
 * @returns {Array} 可访问的功能列表
 */
export function getAccessibleFeatures(user) {
  if (!user) return []

  return searchFeatures.filter(feature => {
    if (feature.exclude_roles) {
      if (feature.exclude_roles.includes('superuser') && user.is_superuser) return false
      if (feature.exclude_roles.includes('departadmin') && user.is_departadmin) return false
    }

    if (feature.roles.includes('all')) return true
    if (feature.roles.includes('superuser') && user.is_superuser) return true
    if (feature.roles.includes('departadmin') && user.is_departadmin) return true
    if (feature.roles.includes('sxsadmin') && user.is_sxsadmin) return true
    if (feature.roles.includes('teacher') && user.is_teacher) return true

    return false
  })
}
