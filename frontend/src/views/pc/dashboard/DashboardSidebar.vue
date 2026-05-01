<!-- 侧边栏组件 -->
<template>
  <el-aside
    :width="isCollapse ? '64px' : '300px'"
    class="dashboard-sidebar"
    :class="{ 'is-collapsed': isCollapse }"
  >
    <div 
      class="collapse-toggle-switch" 
      :class="{ 'is-collapsed': isCollapse }"
      :title="isCollapse ? '展开侧边栏' : '折叠侧边栏'" 
      @click="toggleCollapse"
    >
      <div class="toggle-track">
        <div class="toggle-thumb">
          <el-icon :size="12">
            <component :is="isCollapse ? 'Expand' : 'Fold'" />
          </el-icon>
        </div>
      </div>
    </div>

    <el-card
      v-if="!isCollapse"
      class="user-card"
      shadow="hover"
      :body-style="{ padding: '20px' }"
    >
      <div class="user-profile">
        <h3 class="user-name">
          {{ user?.nickname || '用户' }}
        </h3>
        <div class="role-badge">
          <span class="role-dot" />
          {{ userDeptRole }}
        </div>
      </div>          
    </el-card>

    <div
      v-if="!isCollapse"
      class="search-wrapper"
    >
      <div
        class="modern-search-bar"
        :class="{ 'is-active': isSearchFocused }"
      >
        <el-input
          v-model="searchQuery"
          placeholder="搜索功能..."
          class="custom-search-input"
          clearable
          @focus="isSearchFocused = true"
          @blur="isSearchFocused = false"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon
              class="search-icon-input search-icon-clickable"
              @click="handleSearch"
            >
              <Search />
            </el-icon>
          </template>
        </el-input>
      </div>
    </div>

    <div
      v-if="isCollapse"
      class="quick-launch-bar"
    >
      <div class="quick-launch-header">
        <el-icon :size="14">
          <Grid />
        </el-icon>
      </div>
      <div class="quick-launch-items">
        <div
          v-for="(item, index) in pinnedShortcuts"
          :key="item.id"
          class="quick-launch-item"
          draggable="true"
          :title="item.label"
          @dragstart="handleDragStart($event, item)"
          @dragend="handleDragEnd"
          @click="handleNavigate(item.path)"
        >
          <el-icon :size="20">
            <component :is="item.icon" />
          </el-icon>
          <div class="item-indicator" />
        </div>
        <div
          class="quick-launch-item add-item"
          title="添加快捷方式"
          @click="showShortcutMenu = true"
        >
          <el-icon :size="20">
            <Plus />
          </el-icon>
        </div>
      </div>
    </div>

    <el-dialog
      v-model="showShortcutMenu"
      title="选择要固定的功能"
      width="360px"
      :append-to-body="true"
      class="shortcut-dialog"
    >
      <div class="shortcut-menu-content">
        <div class="shortcut-search">
          <el-input
            v-model="shortcutSearchQuery"
            placeholder="搜索功能..."
            prefix-icon="Search"
            clearable
            size="small"
          />
        </div>
        <div class="shortcut-list">
          <div
            v-for="item in filteredAllMenuItems"
            :key="item.id"
            class="shortcut-option"
            :class="{ 'is-pinned': isPinned(item.id) }"
            draggable="true"
            @dragstart="handleDragStart($event, item)"
            @dragend="handleDragEnd"
            @click="togglePin(item)"
          >
            <el-icon :size="18">
              <component :is="item.icon" />
            </el-icon>
            <span class="shortcut-label">{{ item.label }}</span>
            <el-icon
              v-if="isPinned(item.id)"
              class="pinned-icon"
            >
              <Check />
            </el-icon>
            <el-icon
              v-else
              class="pin-icon"
            >
              <Plus />
            </el-icon>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="showShortcutMenu = false">
          关闭
        </el-button>
      </template>
    </el-dialog>

    <el-card
      class="menu-card"
      shadow="hover"
      :body-style="{ padding: '0' }"
    >
      <el-menu
        ref="menuRef"
        class="sidebar-menu"
        :default-openeds="['user-ops', 'main-work']"
        :border="false"
        :collapse="isCollapse"
        :collapse-transition="false"
      >
        <el-sub-menu index="user-ops">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>用户操作</span>
          </template>
          <el-menu-item
            index="home"
            @click="handleNavigate('/')"
          >
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item
            index="pwd"
            @click="handleNavigate('/change-password')"
          >
            <el-icon><Lock /></el-icon>
            <span>修改密码</span>
          </el-menu-item>
          <el-menu-item
            index="info"
            @click="handleNavigate('/update-user')"
          >
            <el-icon><User /></el-icon>
            <span>修改用户信息</span>
          </el-menu-item>
          <el-menu-item
            index="logout"
            class="logout-item"
            @click="handleLogout"
          >
            <el-icon><SwitchButton /></el-icon>
            <span>退出登录</span>
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="main-work">
          <template #title>
            <el-icon><Briefcase /></el-icon>
            <span>主要工作</span>
          </template>

          <!-- 系统管理员（is_superuser=True）：显示用户管理和系统设置 -->
          <template v-if="user?.is_superuser">
            <el-menu-item
              index="user-mgmt"
              @click="handleNavigate('/userlist')"
            >
              <el-icon><UserFilled /></el-icon>
              <span>用户管理</span>
            </el-menu-item>
            <el-menu-item
              index="cache-config"
              @click="handleNavigate('/cache-config')"
            >
              <el-icon><Monitor /></el-icon>
              <span>缓存管理</span>
            </el-menu-item>
            <el-menu-item
              index="backup-manage"
              @click="handleNavigate('/backup-manage')"
            >
              <el-icon><Download /></el-icon>
              <span>数据备份与恢复</span>
            </el-menu-item>
            <el-menu-item
              index="operation-log"
              @click="handleNavigate('/operation-log')"
            >
              <el-icon><Document /></el-icon>
              <span>操作日志</span>
            </el-menu-item>
          </template>

          <!-- 管理员-校长（is_super_admin=True且is_superuser=False）：显示完整管理功能 -->
          <template v-if="user?.is_super_admin && !user?.is_superuser">
            <el-menu-item
              index="term"
              @click="handleNavigate('/term')"
            >
              <el-icon><Calendar /></el-icon>
              <span>学期管理</span>
            </el-menu-item>
            <el-menu-item
              index="archive-term"
              @click="handleNavigate('/archive-term')"
            >
              <el-icon><Box /></el-icon>
              <span>归档学期</span>
            </el-menu-item>
            <el-menu-item
              index="archived-terms"
              @click="handleNavigate('/archived-terms')"
            >
              <el-icon><Collection /></el-icon>
              <span>查看归档记录</span>
            </el-menu-item>
            <el-menu-item
              index="deptlist"
              @click="handleNavigate('/deptlist')"
            >
              <el-icon><OfficeBuilding /></el-icon>
              <span>查看分院信息</span>
            </el-menu-item>
            <el-menu-item
              index="deptadmin"
              @click="handleNavigate('/userlist/4')"
            >
              <el-icon><UserFilled /></el-icon>
              <span>查看分院管理员</span>
            </el-menu-item>
          </template>

          <template v-if="user?.is_departadmin && !user?.is_superuser">
            <el-menu-item
              index="user-mgmt"
              @click="handleNavigate('/user-management')"
            >
              <el-icon><User /></el-icon>
              <span>用户管理</span>
            </el-menu-item>
            <el-menu-item
              index="lab-mgmt"
              @click="handleNavigate('/lab-resource-management')"
            >
              <el-icon><OfficeBuilding /></el-icon>
              <span>全部实训室</span>
            </el-menu-item>
            <el-menu-item
              index="archived-terms"
              @click="handleNavigate('/archived-terms')"
            >
              <el-icon><Collection /></el-icon>
              <span>查看归档记录</span>
            </el-menu-item>
          </template>

          <template v-if="user?.is_sxsadmin && !user?.is_superuser && !user?.is_departadmin">
            <el-menu-item
              index="sxs-mgmt"
              @click="handleNavigate('/lab-resource-management')"
            >
              <el-icon><OfficeBuilding /></el-icon>
              <span>实训室与资源管理</span>
            </el-menu-item>
          </template>

          <template v-if="user?.is_teacher && !user?.is_superuser">
            <el-menu-item
              index="teaching"
              @click="handleNavigate('/personal-teaching')"
            >
              <el-icon><Reading /></el-icon>
              <span>个人教学中心</span>
            </el-menu-item>
          </template>

          <template v-if="!user?.is_superuser && (user?.is_departadmin || user?.is_sxsadmin || user?.is_teacher)">
            <el-menu-item 
              v-if="user?.is_departadmin || user?.is_sxsadmin"
              index="stats" 
              @click="handleNavigate('/comprehensive-stats')"
            >
              <el-icon><DataLine /></el-icon>
              <span>数据中心</span>
            </el-menu-item>
            <el-menu-item 
              v-if="user?.is_sxsadmin || user?.is_teacher"
              index="msg" 
              @click="handleNavigate('/workorder-center')"
            >
              <el-icon><Tickets /></el-icon>
              <span>工单中心</span>
            </el-menu-item>
          </template>
        </el-sub-menu>
      </el-menu>
    </el-card>
  </el-aside>
</template>

<script>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/core/hooks'
import { showConfirm } from '@/core/utils/errorHandler'
import {
  UserFilled, Search, Setting, HomeFilled, Lock, User, SwitchButton,
  Briefcase, Calendar, Box, Collection, OfficeBuilding, Reading,
  DataLine, Expand, Fold, Grid, Plus, Check, Download, Tickets, Monitor, Document
} from '@element-plus/icons-vue'

export default {
  name: 'DashboardSidebar',
  components: {
    UserFilled, Search, Setting, HomeFilled, Lock, User, SwitchButton,
    Briefcase, Calendar, Box, Collection, OfficeBuilding, Reading,
    DataLine, Expand, Fold, Grid, Plus, Check, Download, Tickets, Monitor, Document
  },
  props: {
    user: {
      type: Object,
      default: () => ({})
    },
    userRole: {
      type: String,
      default: ''
    }
  },
  emits: ['navigate', 'logout', 'search'],
  setup(props, { emit }) {
    const router = useRouter()
    const { logout } = useAuth()
    
    const searchQuery = ref('')
    const isSearchFocused = ref(false)
    
    const userDeptRole = computed(() => {
      const u = props.user || {}
      const deptName = u.department_name || ''
      const role = props.userRole || ''
      if (u.is_superuser) return role
      if (deptName && role) return `${deptName} - ${role}`
      if (!deptName && (u.is_department_admin || u.is_departadmin) && role) {
        return `无部门 - ${role}`
      }
      return role || '普通用户'
    })
    
    const getInitialCollapseState = () => {
      if (typeof window === 'undefined') return false
      const userId = props.user?.id || 'anonymous'
      const saved = localStorage.getItem(`sidebar_collapsed_${userId}`)
      return saved === 'true'
    }
    
    const isCollapse = ref(getInitialCollapseState())
    const menuRef = ref(null)

    const sidebarStorageKey = computed(() => {
      const userId = props.user?.id || 'anonymous'
      return `sidebar_collapsed_${userId}`
    })

    const showShortcutMenu = ref(false)
    const shortcutSearchQuery = ref('')
    const draggedItem = ref(null)

    const safeUser = computed(() => props.user || {})

    const allMenuItems = computed(() => {
      const items = []
      const u = safeUser.value
      
      items.push(
        { id: 'home', path: '/', icon: 'HomeFilled', label: '首页' },
        { id: 'pwd', path: '/change-password', icon: 'Lock', label: '修改密码' },
        { id: 'info', path: '/update-user', icon: 'User', label: '修改用户信息' }
      )

      if (u.is_systemadmin) {
        items.push(
          { id: 'cache-config', path: '/cache-config', icon: 'Monitor', label: '缓存管理' },
          { id: 'operation-log', path: '/operation-log', icon: 'Document', label: '操作日志' }
        )
      }

      if (u.is_superuser) {
        items.push(
          { id: 'term', path: '/term', icon: 'Calendar', label: '学期管理' },
          { id: 'archive-term', path: '/archive-term', icon: 'Box', label: '归档学期' },
          { id: 'archived-terms', path: '/archived-terms', icon: 'Collection', label: '查看归档记录' },
          { id: 'deptlist', path: '/deptlist', icon: 'OfficeBuilding', label: '查看分院信息' },
          { id: 'deptadmin', path: '/userlist/4', icon: 'UserFilled', label: '查看分院管理员' }
        )
      }
      
      if (u.is_departadmin && !u.is_superuser) {
        items.push(
          { id: 'user-mgmt', path: '/user-management', icon: 'UserFilled', label: '用户管理' },
          { id: 'lab-mgmt', path: '/lab-resource-management', icon: 'OfficeBuilding', label: '全部实训室' },
          { id: 'archived-terms', path: '/archived-terms', icon: 'Collection', label: '查看归档记录' }
        )
      }
      
      if (u.is_sxsadmin && !u.is_superuser && !u.is_departadmin) {
        items.push(
          { id: 'sxs-mgmt', path: '/lab-resource-management', icon: 'OfficeBuilding', label: '实训室与资源管理' }
        )
      }
      
      if (u.is_teacher && !u.is_superuser) {
        items.push(
          { id: 'teaching', path: '/personal-teaching', icon: 'Reading', label: '个人教学中心' }
        )
      }
      
      if (!u.is_superuser && (u.is_departadmin || u.is_sxsadmin || u.is_teacher)) {
        if (u.is_departadmin || u.is_sxsadmin) {
          items.push(
            { id: 'stats', path: '/comprehensive-stats', icon: 'DataLine', label: '数据中心' }
          )
        }
        items.push(
          { id: 'msg', path: '/workorder-center', icon: 'Tickets', label: '工单中心' }
        )
      }
      
      return items
    })

    const filteredAllMenuItems = computed(() => {
      if (!shortcutSearchQuery.value) return allMenuItems.value
      const query = shortcutSearchQuery.value.toLowerCase()
      return allMenuItems.value.filter(item => 
        item.label.toLowerCase().includes(query)
      )
    })

    const defaultShortcuts = computed(() => {
      const u = safeUser.value
      if (u.is_superuser) {
        return [
          { id: 'home', path: '/', icon: 'HomeFilled', label: '首页' },
          { id: 'term', path: '/term', icon: 'Calendar', label: '学期管理' },
          { id: 'deptlist', path: '/deptlist', icon: 'OfficeBuilding', label: '分院信息' }
        ]
      }
      if (u.is_teacher && !u.is_departadmin && !u.is_sxsadmin) {
        return [
          { id: 'home', path: '/', icon: 'HomeFilled', label: '首页' },
          { id: 'teaching', path: '/personal-teaching', icon: 'Reading', label: '教学中心' },
          { id: 'msg', path: '/workorder-center', icon: 'Tickets', label: '工单中心' }
        ]
      }
      return [
        { id: 'home', path: '/', icon: 'HomeFilled', label: '首页' },
        { id: 'msg', path: '/workorder-center', icon: 'Tickets', label: '工单中心' }
      ]
    })

    const pinnedShortcuts = ref([])

    const loadPinnedShortcuts = () => {
      try {
        const saved = localStorage.getItem('pinned_shortcuts')
        if (saved) {
          const parsed = JSON.parse(saved)
          const validItems = parsed.filter(item => {
            return allMenuItems.value.some(menuItem => menuItem.id === item.id)
          })
          pinnedShortcuts.value = validItems.length > 0 ? validItems : [...defaultShortcuts.value]
        } else {
          pinnedShortcuts.value = [...defaultShortcuts.value]
        }
      } catch {
        pinnedShortcuts.value = [...defaultShortcuts.value]
      }
    }

    const savePinnedShortcuts = () => {
      localStorage.setItem('pinned_shortcuts', JSON.stringify(pinnedShortcuts.value))
    }

    const isPinned = (id) => {
      return pinnedShortcuts.value.some(item => item.id === id)
    }

    const togglePin = (item) => {
      const isAllowed = allMenuItems.value.some(menuItem => menuItem.id === item.id)
      if (!isAllowed) return
      
      const index = pinnedShortcuts.value.findIndex(i => i.id === item.id)
      if (index > -1) {
        pinnedShortcuts.value.splice(index, 1)
      } else {
        pinnedShortcuts.value.push({ ...item })
      }
      savePinnedShortcuts()
    }

    const handleDragStart = (event, item) => {
      draggedItem.value = item
      event.dataTransfer.effectAllowed = 'move'
      event.dataTransfer.setData('text/plain', item.id)
    }

    const handleDragEnd = () => {
      draggedItem.value = null
    }

    const toggleCollapse = () => {
      isCollapse.value = !isCollapse.value
      localStorage.setItem(sidebarStorageKey.value, isCollapse.value)
      
      if (!isCollapse.value) {
        nextTick(() => {
          if (menuRef.value) {
            menuRef.value.open('user-ops')
            menuRef.value.open('main-work')
          }
        })
      }
    }

    const handleNavigate = (path) => {
      emit('navigate', path)
    }

    const handleSearch = () => {
      emit('search', searchQuery.value)
    }

    const handleLogout = async () => {
      const confirmed = await showConfirm(
        '确定要退出登录吗？',
        '退出确认',
        { confirmButtonText: '确定退出', cancelButtonText: '取消', type: 'warning' }
      )
      if (confirmed) {
        emit('logout')
        await logout()
      }
    }

    onMounted(() => {
      loadPinnedShortcuts()
    })

    watch(() => props.user?.id, () => {
      isCollapse.value = getInitialCollapseState()
    })

    return {
      searchQuery,
      isSearchFocused,
      isCollapse,
      toggleCollapse,
      menuRef,
      showShortcutMenu,
      shortcutSearchQuery,
      pinnedShortcuts,
      filteredAllMenuItems,
      isPinned,
      togglePin,
      handleDragStart,
      handleDragEnd,
      handleNavigate,
      handleSearch,
      handleLogout,
      userDeptRole
    }
  }
}
</script>

<style scoped>
.dashboard-sidebar {
  background: #ffffff;
  border-right: 1px solid #e6e6e6;
  display: flex;
  flex-direction: column;
  padding: 24px 0;
  box-shadow: 2px 0 8px rgba(0,0,0,0.02);
  height: 100vh;
  position: sticky;
  top: 0;
  overflow-y: auto;
  z-index: 1000;
  flex-shrink: 0;
}

.dashboard-sidebar::-webkit-scrollbar {
  width: 6px;
}
.dashboard-sidebar::-webkit-scrollbar-thumb {
  background: #e0e0e0;
  border-radius: 3px;
}
.dashboard-sidebar::-webkit-scrollbar-track {
  background: transparent;
}

.user-card {
  border: none;
  background: transparent;
  box-shadow: none !important;
  margin-bottom: 10px;
}

.user-profile {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 0 20px;
}

.user-name {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: #1a1a1a;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.role-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  background-color: #eef4ff;
  border-radius: 12px;
  color: #409eff;
  font-size: 12px;
  font-weight: 500;
  margin-top: 4px;
}

.role-dot {
  width: 6px;
  height: 6px;
  background-color: #409eff;
  border-radius: 50%;
  margin-right: 6px;
}

.search-wrapper {
  padding: 0 20px;
  margin-bottom: 24px;
}

.modern-search-bar {
  display: flex;
  align-items: center;
  background-color: #f7f8fa;
  border-radius: 8px;
  padding: 2px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid transparent;
}

.modern-search-bar:hover {
  background-color: #f2f3f5;
}

.modern-search-bar.is-active {
  background-color: #ffffff;
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
}

.custom-search-input {
  flex: 1;
}

:deep(.custom-search-input .el-input__wrapper) {
  background-color: transparent !important;
  box-shadow: none !important;
  padding-left: 8px;
}

:deep(.custom-search-input .el-input__inner) {
  color: #1a1a1a;
  height: 36px;
}

.search-icon-input {
  font-size: 16px;
  color: #a8abb2;
  margin-left: 4px;
}

.search-icon-clickable {
  cursor: pointer;
  transition: color 0.2s;
}

.search-icon-clickable:hover {
  color: #409eff;
}

.collapse-toggle-switch {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 10;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px;
}

.collapse-toggle-switch.is-collapsed {
  right: 50%;
  transform: translateX(50%);
  flex-direction: column;
  gap: 4px;
}

.toggle-track {
  width: 48px;
  height: 24px;
  background: #ffffff;
  border-radius: 12px;
  padding: 2px;
  transition: all 0.3s ease;
  border: 1px solid #e4e7ed;
  position: relative;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
}

.collapse-toggle-switch:hover .toggle-track {
  border-color: #c0c4cc;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.collapse-toggle-switch.is-collapsed .toggle-track {
  width: 24px;
  height: 24px;
  background: #ffffff;
  border-color: #e4e7ed;
}

.collapse-toggle-switch.is-collapsed:hover .toggle-track {
  border-color: #c0c4cc;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.toggle-thumb {
  width: 20px;
  height: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
  position: absolute;
  left: 2px;
  top: 50%;
  transform: translateY(-50%);
}

.collapse-toggle-switch:hover .toggle-thumb {
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  color: #1890ff;
  box-shadow: 0 2px 6px rgba(24, 144, 255, 0.2);
}

.collapse-toggle-switch.is-collapsed .toggle-thumb {
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
  color: #ffffff;
}

.collapse-toggle-switch.is-collapsed:hover .toggle-thumb {
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.4);
}

.collapse-toggle-switch:not(.is-collapsed) .toggle-thumb {
  left: calc(100% - 22px);
}

.quick-launch-bar {
  padding: 8px 4px;
  background: #f8f9fa;
  border-radius: 8px;
  margin: 0 8px 12px;
}

.quick-launch-header {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 0;
  color: #909399;
  border-bottom: 1px dashed #e4e7ed;
  margin-bottom: 8px;
}

.quick-launch-items {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.quick-launch-item {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.25s ease;
  position: relative;
  color: #606266;
  background: #ffffff;
  margin: 0 auto;
}

.quick-launch-item:hover {
  background: #e6f7ff;
  color: #1890ff;
  transform: scale(1.08);
}

.quick-launch-item:active {
  transform: scale(0.95);
}

.quick-launch-item .item-indicator {
  position: absolute;
  bottom: 4px;
  left: 50%;
  transform: translateX(-50%);
  width: 4px;
  height: 4px;
  background: #1890ff;
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.2s;
}

.quick-launch-item:hover .item-indicator {
  opacity: 1;
}

.quick-launch-item.add-item {
  background: transparent;
  border: 2px dashed #d9d9d9;
  color: #bfbfbf;
}

.quick-launch-item.add-item:hover {
  border-color: #1890ff;
  color: #1890ff;
  background: #e6f7ff;
}

.shortcut-dialog :deep(.el-dialog__body) {
  padding: 0;
}

.shortcut-menu-content {
  padding: 16px;
}

.shortcut-search {
  margin-bottom: 12px;
}

.shortcut-list {
  max-height: 320px;
  overflow-y: auto;
}

.shortcut-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 4px;
  background: #fafafa;
}

.shortcut-option:hover {
  background: #e6f7ff;
}

.shortcut-option.is-pinned {
  background: #e6f7ff;
  border: 1px solid #91d5ff;
}

.shortcut-label {
  flex: 1;
  font-size: 14px;
  color: #303133;
}

.shortcut-option .pin-icon,
.shortcut-option .pinned-icon {
  font-size: 16px;
  color: #bfbfbf;
  transition: all 0.2s;
}

.shortcut-option:hover .pin-icon {
  color: #1890ff;
}

.shortcut-option.is-pinned .pinned-icon {
  color: #52c41a;
}

.shortcut-option[draggable="true"] {
  cursor: grab;
}

.shortcut-option[draggable="true"]:active {
  cursor: grabbing;
}

.menu-card {
  flex: 1;
  border: none;
  box-shadow: none !important;
  background: transparent;
  overflow: visible;
}

.sidebar-menu {
  border-right: none;
  padding: 0 10px;
  background: transparent;
}

:deep(.el-menu-item), :deep(.el-sub-menu__title) {
  height: 48px;
  line-height: 48px;
  border-radius: 8px;
  margin: 4px 0;
  color: #606266;
}

:deep(.el-menu-item.is-active) {
  background-color: #e6f7ff;
  color: #1890ff;
  font-weight: 600;
}

:deep(.el-menu-item:hover), :deep(.el-sub-menu__title:hover) {
  background-color: #f5f7fa;
  color: #1890ff;
}

:deep(.el-menu-item .el-icon), :deep(.el-sub-menu__title .el-icon) {
  margin-right: 10px;
  font-size: 18px;
}

.logout-item {
  margin-top: 20px;
  border-top: 1px solid #f0f0f0;
  color: #f56c6c !important;
}
.logout-item:hover {
  background-color: #fef0f0 !important;
  color: #f56c6c !important;
}

.dashboard-sidebar.is-collapsed .user-profile {
  padding: 0 5px;
}

.dashboard-sidebar.is-collapsed .sidebar-menu {
  padding: 0;
  width: 100%;
}

@media (max-width: 1200px) {
  .dashboard-sidebar:not(.is-collapsed) {
    width: 240px !important;
  }
}
</style>
