<template>
  <!-- PC端使用Index组件 -->
  <Index class="pc-layout">
    <template #rightcontent>
      <div class="dashboard-content">
        <!-- 头部 -->
        <el-card
          class="header-card"
          shadow="hover"
        >
          <div class="header-content">
            <div class="header-left">
              <el-icon class="header-icon">
                <Monitor />
              </el-icon>
              <h2>设备管理</h2>
            </div>
            <div class="header-right">
              <el-button
                type="primary"
                plain
                icon="HomeFilled"
                @click="goHome"
              >
                返回首页
              </el-button>
            </div>
          </div>
        </el-card>

        <!-- 功能卡片区域 -->
        <div class="cards-container">
          <el-row :gutter="24">
            <!-- 查看全部设备 -->
            <el-col
              v-if="user?.is_superuser || user?.is_departadmin || user?.is_sxsadmin"
              :xs="24"
              :sm="12"
              :md="8"
              :lg="8"
            >
              <el-card
                shadow="hover"
                class="function-card"
                @click="router.push('/device-list')"
              >
                <div class="card-content">
                  <div class="icon-wrapper device-icon">
                    <el-icon><Monitor /></el-icon>
                  </div>
                  <div class="text-content">
                    <h3>全部设备</h3>
                    <p>
                      查看和管理所有电脑设?/p>
                    </p>
                  </div>
                </div>
              </el-card>
            </el-col>

            <!-- 批量导入设备 -->
            <el-col
              v-if="user?.is_superuser || user?.is_departadmin || user?.is_sxsadmin"
              :xs="24"
              :sm="12"
              :md="8"
              :lg="8"
            >
              <el-card
                shadow="hover"
                class="function-card"
                @click="router.push('/import-device')"
              >
                <div class="card-content">
                  <div class="icon-wrapper import-icon">
                    <el-icon><Download /></el-icon>
                  </div>
                  <div class="text-content">
                    <h3>批量导入设备</h3>
                    <p>从Excel文件批量导入电脑设备</p>
                  </div>
                </div>
              </el-card>
            </el-col>

            <!-- 添加设备 -->
            <el-col
              v-if="user?.is_superuser || user?.is_departadmin || user?.is_sxsadmin"
              :xs="24"
              :sm="12"
              :md="8"
              :lg="8"
            >
              <el-card
                shadow="hover"
                class="function-card"
                @click="router.push('/add-device')"
              >
                <div class="card-content">
                  <div class="icon-wrapper add-icon">
                    <el-icon><Plus /></el-icon>
                  </div>
                  <div class="text-content">
                    <h3>添加设备</h3>
                    <p>手动添加单个电脑设备</p>
                  </div>
                </div>
              </el-card>
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
import { Monitor, Download, Plus, HomeFilled } from '@element-plus/icons-vue'

export default {
  name: 'DeviceManagementDashboard',
  components: {
    Index,
    Monitor, Download, Plus, HomeFilled
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
}

.header-card {
  margin-bottom: 24px;
  border-radius: 12px;
  border: none;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  font-size: 24px;
  color: #1890ff;
  background: #e6f7ff;
  padding: 8px;
  border-radius: 8px;
}

.header-left h2 {
  margin: 0;
  font-size: 20px;
  color: #1a1a1a;
  font-weight: 600;
}

.function-card {
  height: 100%;
  cursor: pointer;
  border-radius: 12px;
  border: 1px solid #f0f0f0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  margin-bottom: 24px;
}

.function-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
  border-color: transparent;
}

.card-content {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 10px;
}

.icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  flex-shrink: 0;
}

.device-icon {
  background: #e6f7ff;
  color: #1890ff;
}

.import-icon {
  background: #fff0f6;
  color: #eb2f96;
}

.add-icon {
  background: #f6ffed;
  color: #52c41a;
}

.text-content {
  flex: 1;
}

.text-content h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
}

.text-content p {
  margin: 0;
  font-size: 13px;
  color: #8c8c8c;
  line-height: 1.5;
}
</style>
