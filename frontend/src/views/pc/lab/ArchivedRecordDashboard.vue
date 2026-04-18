<!-- 归档记录面板 -->
<template>
  <div class="archived-dashboard-wrapper">
    <Index v-if="!currentType" class="pc-layout">
      <template #rightcontent>
        <div class="archive-page">
          <div class="page-header">
            <div class="header-content">
              <div class="header-icon">
                <el-icon :size="28"><FolderOpened /></el-icon>
              </div>
              <div class="header-text">
                <h1>{{ termName || '归档记录' }}</h1>
                <p class="header-desc">归档记录概览</p>
              </div>
            </div>
            <div class="header-actions">
              <el-select 
                v-model="selectedDepart" 
                :placeholder="departList && departList.length > 0 ? '全校数据' : '暂无分院数据'"
                clearable 
                style="width: 180px;"
                @change="handleDepartChange"
                size="large">
                <el-option label="全校数据" :value="''"></el-option>
                <el-option 
                  v-for="dept in departList" 
                  :key="dept.id" 
                  :label="dept.departname" 
                  :value="dept.id"></el-option>
              </el-select>
              <el-button type="primary" plain @click="smartBack">
                <el-icon><Back /></el-icon>
                返回归档列表
              </el-button>
            </div>
          </div>
          
          <div v-loading="loading" class="folders-container">
            <div class="folder-card" @click="openFolder('maintain')">
              <div class="folder-icon">
                <el-icon :size="28"><Tools /></el-icon>
              </div>
              <div class="folder-info">
                <h3>维护记录</h3>
                <p>{{ stats.maintain || 0 }} 条记录</p>
              </div>
              <el-icon class="folder-arrow" :size="20"><ArrowRight /></el-icon>
            </div>
            
            <div class="folder-card" @click="openFolder('usage')">
              <div class="folder-icon">
                <el-icon :size="28"><Document /></el-icon>
              </div>
              <div class="folder-info">
                <h3>纯使用记录</h3>
                <p>{{ stats.usage || 0 }} 条记录</p>
              </div>
              <el-icon class="folder-arrow" :size="20"><ArrowRight /></el-icon>
            </div>
            
            <div class="folder-card" @click="openFolder('fault')">
              <div class="folder-icon">
                <el-icon :size="28"><Warning /></el-icon>
              </div>
              <div class="folder-info">
                <h3>故障工单</h3>
                <p>{{ stats.fault || 0 }} 条记录</p>
              </div>
              <el-icon class="folder-arrow" :size="20"><ArrowRight /></el-icon>
            </div>
            
            <div class="folder-card" @click="openFolder('class')">
              <div class="folder-icon">
                <el-icon :size="28"><Reading /></el-icon>
              </div>
              <div class="folder-info">
                <h3>课表记录</h3>
                <p>{{ stats.class || 0 }} 条记录</p>
              </div>
              <el-icon class="folder-arrow" :size="20"><ArrowRight /></el-icon>
            </div>

            <div class="folder-card" @click="openFolder('lab_info')">
              <div class="folder-icon">
                <el-icon :size="28"><OfficeBuilding /></el-icon>
              </div>
              <div class="folder-info">
                <h3>实训室信息</h3>
                <p>{{ stats.lab || 0 }} 条记录</p>
              </div>
              <el-icon class="folder-arrow" :size="20"><ArrowRight /></el-icon>
            </div>

            <div class="folder-card" @click="openFolder('device_info')">
              <div class="folder-icon">
                <el-icon :size="28"><Monitor /></el-icon>
              </div>
              <div class="folder-info">
                <h3>设备信息</h3>
                <p>{{ stats.device || 0 }} 条记录</p>
              </div>
              <el-icon class="folder-arrow" :size="20"><ArrowRight /></el-icon>
            </div>

            <div class="folder-card" @click="openFolder('user_info')">
              <div class="folder-icon">
                <el-icon :size="28"><User /></el-icon>
              </div>
              <div class="folder-info">
                <h3>用户信息</h3>
                <p>{{ stats.user || 0 }} 条记录</p>
              </div>
              <el-icon class="folder-arrow" :size="20"><ArrowRight /></el-icon>
            </div>
          </div>
        </div>
      </template>
    </Index>

    <RecordList v-else :key="currentType" />
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from '@/core/hooks'
import { useNavigation } from '@/core/utils/routeDecision'
import RecordList from '@/views/pc/crud/list/RecordList.vue'
import Index from '@/views/pc/dashboard/Index.vue'
import { 
  FolderOpened, Back, ArrowRight, Tools, Document, Warning, 
  Reading, OfficeBuilding, Monitor, User
} from '@element-plus/icons-vue'

export default {
  name: 'ArchivedRecordDashboard',
  components: { 
    RecordList, Index,
    FolderOpened, Back, ArrowRight, Tools, Document, Warning, 
    Reading, OfficeBuilding, Monitor, User
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const { get } = useApi() 
    const { smartBack } = useNavigation() 
    
    const loading = ref(false)
    const stats = ref({})
    const termName = ref('')
    const departList = ref([])
    const selectedDepart = ref('')
    
    const currentType = computed(() => route.query.type)
    
    const fetchStats = async () => {
      loading.value = true
      try {
        const id = route.params.id
        const query = { ...route.query }
        const res = await get(query, { url: `/schedules/archived/${id}/` })
        if (res && res.success) {
          const data = res.data || res
          if (data.mode === 'dashboard') {
            stats.value = data.stats || {}
            termName.value = data.semester_name || data.term_name || ''
            departList.value = data.depart_list || []
            selectedDepart.value = data.current_depart_id ? Number(data.current_depart_id) : ''
          }
        }
      } catch (e) {
      } finally {
        loading.value = false
      }
    }
    
    const openFolder = (type) => {
      router.push({ query: { ...route.query, type } })
    }
    
    const closeFolder = () => {
      const query = { ...route.query }
      delete query.type
      router.push({ query })
    }
    
    const getFolderName = (type) => {
      const map = {
        'maintain': '维护记录',
        'usage': '纯使用记录',
        'fault': '故障工单',
        'class': '课表记录',
        'lab_info': '实训室信息',
        'device_info': '设备信息',
        'user_info': '用户信息'
      }
      return map[type] || '记录列表'
    }

    const handleDepartChange = async (val) => {
      const query = { ...route.query }
      if (val) {
        query.depart_id = val
      } else {
        delete query.depart_id
      }
      await router.replace({ query })
      fetchStats()
    }

    watch(currentType, (val) => {
      if (!val) {
        fetchStats()
      }
    }, { immediate: true })

    return {
      currentType,
      stats,
      termName,
      loading,
      departList,
      selectedDepart,
      handleDepartChange,
      openFolder,
      closeFolder,
      smartBack,
      getFolderName
    }
  }
}
</script>

<style scoped>
.archive-page {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: #409eff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.header-text h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.header-desc {
  margin: 4px 0 0;
  font-size: 14px;
  color: #909399;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.folders-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.folder-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  cursor: pointer;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.folder-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  border-color: #409eff;
  background: #f0f7ff;
}

.folder-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #409eff;
  color: white;
  margin-right: 16px;
  flex-shrink: 0;
}

.folder-info {
  flex: 1;
}

.folder-info h3 {
  margin: 0 0 6px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.folder-info p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.folder-arrow {
  opacity: 0;
  transform: translateX(-10px);
  transition: all 0.3s ease;
  color: #409eff;
}

.folder-card:hover .folder-arrow {
  opacity: 1;
  transform: translateX(0);
}

@media (max-width: 768px) {
  .archive-page {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-end;
    flex-wrap: wrap;
  }
  
  .folders-container {
    grid-template-columns: 1fr;
  }
}
</style>
