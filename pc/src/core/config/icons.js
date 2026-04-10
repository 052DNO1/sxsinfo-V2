/**
 * 常用图标映射 - 按需导入优化
 * 
 * 这个文件只导入项目中实际使用�?Element Plus 图标�?
 * 避免使用 `import * as Icons from '@element-plus/icons-vue'` 导入全部图标
 * 
 * 使用方法�?
 * import { iconMap } from '@/core/config/icons'
 * <component :is="iconMap[field.icon] || iconMap.Edit" />
 */

import {
  // 表单相关
  Document,
  User,
  Message,
  Iphone,
  PriceTag,
  OfficeBuilding,
  UserFilled,
  Reading,
  Calendar,
  Timer,
  Avatar,
  DataAnalysis,
  Grid,
  DataLine,
  School,
  Monitor,
  House,
  Edit,
  Tools,
  Cpu,
  Connection,
  SwitchButton,
  Discount,
  Files,
  Plus,
  InfoFilled,
  EditPen,
  QuestionFilled,
  WarningFilled,
  Warning,
  Delete,
  View,
  Download,
  Search,
  HomeFilled,
  ArrowRight,
  Setting,
  List,
  Key,
  Back,
  CircleClose,
  CircleCheck,
  ChatDotRound,
  Close,
  Position,
  Loading,
  Lock,
  Postcard,
  StarFilled,
  SetUp,
  Collection,
  ArrowLeft,
  UploadFilled,
} from '@element-plus/icons-vue'

// 图标名称到组件的映射
export const iconMap = {
  // 基础图标
  Document,
  Edit,
  Plus,
  Delete,
  View,
  Download,
  Search,
  Close,
  Loading,
  
  // 用户相关
  User,
  UserFilled,
  Avatar,
  
  // 通讯相关
  Message,
  Iphone,
  
  // 组织相关
  OfficeBuilding,
  School,
  Reading,
  
  // 时间日期
  Calendar,
  Timer,
  
  // 数据相关
  DataAnalysis,
  Grid,
  DataLine,
  Connection,
  
  // 设备相关
  Monitor,
  Cpu,
  House,
  Tools,
  SwitchButton,
  Discount,
  Files,
  
  // 表单图标
  PriceTag,
  Postcard,
  Lock,
  Key,
  SetUp,
  StarFilled,
  Collection,
  
  // 导航图标
  HomeFilled,
  ArrowRight,
  ArrowLeft,
  Back,
  List,
  Setting,
  
  // 状态图�?
  InfoFilled,
  EditPen,
  QuestionFilled,
  WarningFilled,
  Warning,
  CircleClose,
  CircleCheck,
  
  // 其他
  ChatDotRound,
  Position,
  UploadFilled,
}

// 默认导出
export default iconMap
