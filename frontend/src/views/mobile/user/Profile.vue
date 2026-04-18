<template>
  <div class="mobile-profile-page mobile-layout">
    <van-nav-bar
      title="个人资料"
      left-arrow
      @click-left="goBack"
      class="mobile-nav-bar"
    />

    <div v-if="loading" class="mobile-loading-container">
      <van-loading size="24px" vertical>加载中...</van-loading>
    </div>

    <div v-else class="profile-content">
      <!-- 用户头像和基本信息 -->
      <div class="profile-header">
        <div class="avatar-wrapper">
          <van-image
            round
            width="80px"
            height="80px"
            :src="user?.avatar || defaultAvatar"
            class="user-avatar"
          >
            <template #error>
              <van-icon name="user-o" size="40" color="#ccc" />
            </template>
          </van-image>
          <van-icon name="photograph" class="change-avatar-icon" />
        </div>
        <h3 class="user-name">{{ user?.nickname || user?.username || '用户' }}</h3>
        <p class="user-role">{{ roleDisplay }}</p>
      </div>

      <!-- 详细信息列表 -->
      <van-cell-group inset class="info-group">
        <van-cell title="用户名" :value="user?.username || '-'" icon="user-o" />
        <van-cell title="姓名" :value="user?.nickname || '-'" icon="contact" />
        <van-cell title="邮箱" :value="user?.email || '未设置'" icon="envelop-o" />
        <van-cell title="手机号" :value="user?.phone || '未设置'" icon="phone-o" />
        <van-cell 
          v-if="user?.department_name" 
          title="所属部门" 
          :value="user.department_name" 
          icon="office-building" 
        />
        <van-cell 
          v-if="user?.managed_laboratories && user.managed_laboratories !== '-'" 
          title="管理实训室" 
          :value="user.managed_laboratories" 
          :label="getLabNames(user.managed_laboratories)"
          icon="home-o" 
        />
        <van-cell 
          title="账户状态" 
          :value="user?.is_active ? '正常' : '已禁用'"
        >
          <template #right-icon>
            <van-tag :type="user?.is_active ? 'success' : 'danger'" size="medium">
              {{ user?.is_active ? '正常' : '禁用' }}
            </van-tag>
          </template>
        </van-cell>
      </van-cell-group>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <van-button 
          type="primary" 
          block 
          round 
          @click="editProfile"
          class="action-btn"
        >
          编辑资料
        </van-button>
        <van-button 
          type="default" 
          block 
          round 
          @click="changePassword"
          class="action-btn"
        >
          修改密码
        </van-button>
        <van-button 
          type="warning" 
          block 
          plain 
          round 
          @click="handleLogout"
          class="action-btn logout-btn"
        >
          退出登录
        </van-button>
      </div>

      <!-- 系统信息 -->
      <div class="system-info">
        <p>系统版本：v2.0.0</p>
        <p>最后登录：{{ lastLoginTime }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/core/hooks'
import { useMobile } from '@/composables/useMobile'

export default {
  name: 'MobileProfile',
  setup() {
    const router = useRouter()
    const { user, logout } = useAuth()
    
    // 移动端初始化
    const { init: initMobile, loadVantComponents } = useMobile()
    
    const loading = ref(false)
    const defaultAvatar = 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg'

    // 角色显示文本
    const roleDisplay = computed(() => {
      if (!user.value) return '-'
      
      const roles = []
      if (user.value.is_superuser) roles.push('系统管理员')
      if (user.value.is_super_admin) roles.push('超级管理员')
      if (user.value.is_department_admin) roles.push('部门管理员')
      
      // 根据角色值判断
      if (user.value.role) {
        const roleMap = {
          1: '教师',
          2: '实训室管理员',
          4: '部门管理员',
          16: '超级管理员',
          32: '系统管理员'
        }
        
        if (typeof user.value.role === 'number') {
          for (const [val, name] of Object.entries(roleMap)) {
            if (user.value.role & parseInt(val)) {
              roles.push(name)
            }
          }
        }
      }
      
      return roles.length > 0 ? roles.join('、') : '普通用户'
    })

    // 获取实训室名称（简化显示）
    const getLabNames = (labs) => {
      if (!labs) return ''
      if (Array.isArray(labs)) {
        return labs.length > 1 ? `共${labs.length}个实训室` : labs[0]
      }
      return String(labs).length > 20 ? String(labs).substring(0, 20) + '...' : labs
    }

    // 最后登录时间
    const lastLoginTime = computed(() => {
      if (!user.value) return '-'
      return user.value.last_login || new Date().toLocaleString()
    })

    // 编辑资料
    const editProfile = () => {
      router.push('/edit-profile')
    }

    // 修改密码
    const changePassword = () => {
      router.push('/change-password')
    }

    // 退出登录
    const handleLogout = async () => {
      try {
        await logout()
        router.push('/login')
      } catch (err) {
        console.error('登出失败:', err)
        // 即使失败也跳转到登录页
        router.push('/login')
      }
    }

    const goBack = () => {
      router.go(-1)
    }

    onMounted(() => {
      initMobile()
      loadVantComponents()
    })

    return {
      user,
      loading,
      defaultAvatar,
      roleDisplay,
      getLabNames,
      lastLoginTime,
      editProfile,
      changePassword,
      handleLogout,
      goBack
    }
  }
}
</script>

<style scoped>
@import '@/assets/css/mobile.css';

.mobile-profile-page {
  min-height: 100vh;
  background: #f7f8fa;
}

.profile-content {
  padding-bottom: 30px;
}

.profile-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px 30px;
  text-align: center;
  color: white;
}

.avatar-wrapper {
  position: relative;
  display: inline-block;
  margin-bottom: 12px;
}

.user-avatar {
  border: 4px solid rgba(255, 255, 255, 0.9);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.change-avatar-icon {
  position: absolute;
  bottom: 4px;
  right: 4px;
  background: white;
  border-radius: 50%;
  padding: 6px;
  font-size: 14px;
  color: #667eea;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.user-name {
  margin: 0 0 6px 0;
  font-size: 20px;
  font-weight: 600;
}

.user-role {
  margin: 0;
  font-size: 14px;
  opacity: 0.9;
}

.info-group {
  margin-top: -20px;
  position: relative;
  z-index: 10;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.action-buttons {
  padding: 20px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-btn {
  height: 46px;
  font-size: 15px;
  font-weight: 500;
}

.logout-btn {
  margin-top: 8px;
  color: #ee0a24;
}

.system-info {
  margin-top: 30px;
  padding: 16px;
  text-align: center;
  color: #969799;
  font-size: 12px;
}

.system-info p {
  margin: 4px 0;
}
</style>
