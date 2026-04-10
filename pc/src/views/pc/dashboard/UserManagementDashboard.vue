<template>
  <Index class="pc-layout">
    <template #rightcontent>
      <div class="dashboard-content">
        <div class="page-header">
          <div class="header-content">
            <div class="header-left">
              <div class="header-icon-wrapper">
                <el-icon><User /></el-icon>
              </div>
              <div class="header-info">
                <h2>用户管理</h2>
                <p>统一管理用户账户、角色与权限配置</p>
              </div>
            </div>
            <div class="header-right">
              <el-button class="nav-action-btn" plain @click="goHome">首页</el-button>
            </div>
          </div>
        </div>

        <div class="cards-container">
          <el-row :gutter="24">
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <div class="function-card blue-theme" @click="router.push('/userlist/1')">
                <div class="card-bg-decoration"></div>
                <div class="card-body">
                  <div class="icon-box">
                    <el-icon><Reading /></el-icon>
                  </div>
                  <div class="card-info">
                    <h3>查看教师信息</h3>
                    <p>管理所有教师账户信息</p>
                  </div>
                  <div class="card-arrow">
                    <el-icon><ArrowRight /></el-icon>
                  </div>
                </div>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8" :lg="6" v-if="user?.is_superuser || user?.is_departadmin">
              <div class="function-card green-theme" @click="router.push('/adduser/1')">
                <div class="card-bg-decoration"></div>
                <div class="card-body">
                  <div class="icon-box">
                    <el-icon><Plus /></el-icon>
                  </div>
                  <div class="card-info">
                    <h3>添加用户</h3>
                    <p>创建新的用户账户</p>
                  </div>
                  <div class="card-arrow">
                    <el-icon><ArrowRight /></el-icon>
                  </div>
                </div>
              </div>
            </el-col>

            <el-col :xs="24" :sm="12" :md="8" :lg="6" v-if="user?.is_superuser || user?.is_departadmin">
              <div class="function-card orange-theme" @click="router.push('/import-user')">
                <div class="card-bg-decoration"></div>
                <div class="card-body">
                  <div class="icon-box">
                    <el-icon><Download /></el-icon>
                  </div>
                  <div class="card-info">
                    <h3>导入用户</h3>
                    <p>从Excel文件批量导入用户</p>
                  </div>
                  <div class="card-arrow">
                    <el-icon><ArrowRight /></el-icon>
                  </div>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>
    </template>
  </Index>
</template>

<script>
import Index from '@/views/pc/dashboard/Index.vue'
import { useAuth } from '@/core/hooks'
import { useNavigation } from '@/core/utils/routeDecision'
import { useRouter } from 'vue-router'
import { User, Reading, Avatar, Plus, Download, ArrowRight } from '@element-plus/icons-vue'

export default {
  name: 'UserManagementDashboard',
  components: {
    Index,
    User, Reading, Avatar, Plus, Download, ArrowRight
  },
  setup() {
    const router = useRouter()
    const { user } = useAuth()
    const { goHome } = useNavigation()

    return {
      user,
      goHome,
      router
    }
  }
}
</script>

<style scoped>
.dashboard-content {
  padding: 0;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 32px;
  background: #fff;
  padding: 24px 32px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
  border: 1px solid rgba(0, 0, 0, 0.02);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-icon-wrapper {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  color: #1890ff;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  box-shadow: 0 4px 10px rgba(24, 144, 255, 0.15);
}

.header-info h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #1a1a1a;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.header-info p {
  margin: 0;
  font-size: 14px;
  color: #8c8c8c;
}

.cards-container {
  padding: 0 10px;
}

.function-card {
  position: relative;
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  height: 100%;
  border: 1px solid #f0f0f0;
  margin-bottom: 24px;
  display: flex;
  flex-direction: column;
}

.function-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 16px 32px rgba(0, 0, 0, 0.08);
  border-color: transparent;
}

.card-bg-decoration {
  position: absolute;
  top: -20px;
  right: -20px;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  opacity: 0.08;
  transition: all 0.3s ease;
}

.function-card:hover .card-bg-decoration {
  transform: scale(1.2);
  opacity: 0.12;
}

.card-body {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 20px;
}

.icon-box {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.function-card:hover .icon-box {
  transform: scale(1.05);
}

.card-info {
  flex: 1;
  padding-top: 2px;
}

.card-info h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
}

.card-info p {
  margin: 0;
  font-size: 13px;
  color: #8c8c8c;
  line-height: 1.5;
}

.card-arrow {
  opacity: 0;
  transform: translateX(-10px);
  transition: all 0.3s ease;
  color: #bfbfbf;
  font-size: 20px;
  display: flex;
  align-items: center;
}

.function-card:hover .card-arrow {
  opacity: 1;
  transform: translateX(0);
}

.blue-theme .icon-box {
  background: #e6f7ff;
  color: #1890ff;
}
.blue-theme .card-bg-decoration {
  background: #1890ff;
}
.blue-theme:hover {
  border-bottom: 2px solid #1890ff;
}
.blue-theme:hover .card-arrow {
  color: #1890ff;
}

.green-theme .icon-box {
  background: #f6ffed;
  color: #52c41a;
}
.green-theme .card-bg-decoration {
  background: #52c41a;
}
.green-theme:hover {
  border-bottom: 2px solid #52c41a;
}
.green-theme:hover .card-arrow {
  color: #52c41a;
}

.purple-theme .icon-box {
  background: #fff0f6;
  color: #eb2f96;
}
.purple-theme .card-bg-decoration {
  background: #eb2f96;
}
.purple-theme:hover {
  border-bottom: 2px solid #eb2f96;
}
.purple-theme:hover .card-arrow {
  color: #eb2f96;
}

.orange-theme .icon-box {
  background: #fff7e6;
  color: #fa8c16;
}
.orange-theme .card-bg-decoration {
  background: #fa8c16;
}
.orange-theme:hover {
  border-bottom: 2px solid #fa8c16;
}
.orange-theme:hover .card-arrow {
  color: #fa8c16;
}

@media (max-width: 768px) {
  .page-header {
    padding: 16px 20px;
    margin-bottom: 20px;
  }

  .header-icon-wrapper {
    width: 48px;
    height: 48px;
    font-size: 24px;
  }

  .header-info h2 {
    font-size: 20px;
  }

  .function-card {
    padding: 20px;
  }
}
</style>
