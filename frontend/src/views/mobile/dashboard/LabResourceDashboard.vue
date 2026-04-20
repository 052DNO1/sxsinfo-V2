<template>
  <div class="mobile-page">
    <van-nav-bar title="实训室资源管理" left-arrow @click-left="goBack">
      <template #right>
        <van-icon name="home-o" size="20" @click="goHome" />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <van-pull-refresh v-model:refreshing="refreshing" @refresh="onRefresh">
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">{{ stats.total_laboratories || 0 }}</div>
            <div class="stat-label">实训室总数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.normal_count || 0 }}</div>
            <div class="stat-label">正常运行</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.maintenance_count || 0 }}</div>
            <div class="stat-label">维护中</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.total_equipments || 0 }}</div>
            <div class="stat-label">设备总数</div>
          </div>
        </div>

        <van-cell-group inset title="快捷操作">
          <van-grid :column-num="4" :border="false">
            <van-grid-item icon="cluster-o" text="实训室列表" @click="router.push('/listsxs')" />
            <van-grid-item icon="add-o" text="添加实训室" @click="router.push('/addsxs')" />
            <van-grid-item icon="setting-o" text="维护记录" @click="router.push('/maintain-list')" />
            <van-grid-item icon="edit" text="使用记录" @click="router.push('/listsxsinfo/1')" />
          </van-grid>
        </van-cell-group>

        <van-cell-group inset title="实训室列表">
          <van-empty v-if="sxsList.length === 0" description="暂无实训室" />
          <van-cell
            v-for="sxs in sxsList"
            :key="sxs.id"
            :title="sxs.name || sxs.laboratory_name"
            :label="sxs.location || sxs.sxslocation"
          >
            <template #value>
              <van-tag :type="sxs.status === 'NORMAL' ? 'success' : 'warning'" size="small">
                {{ getStatusLabel(sxs.status) }}
              </van-tag>
            </template>
          </van-cell>
        </van-cell-group>
      </van-pull-refresh>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { labService } from '@/core/services/BaseService'
import { useNavigation } from '@/core/utils/routeDecision'

const router = useRouter()
const { goHome, smartBack } = useNavigation()

const refreshing = ref(false)
const stats = ref({})
const sxsList = ref([])

const getStatusLabel = (status) => {
  const statusMap = {
    'NORMAL': '正常',
    'MAINTENANCE': '维护中',
    'DAMAGED': '损坏',
    '正常': '正常',
    '维护中': '维护中',
    '损坏': '损坏'
  }
  return statusMap[status] || status || '未知'
}

const loadData = async () => {
  try {
    const response = await labService.list({ nopage: true })
    const list = response?.list || response?.data?.list || []
    
    sxsList.value = list
    
    stats.value = {
      total_laboratories: list.length,
      normal_count: list.filter(s => s.status === 'NORMAL' || s.status === '正常').length,
      maintenance_count: list.filter(s => s.status === 'MAINTENANCE' || s.status === '维护中').length,
      total_equipments: list.reduce((sum, s) => sum + (s.equipment_count || 0), 0)
    }
  } catch (err) {
    console.error('Load data error:', err)
  }
}

const onRefresh = async () => {
  refreshing.value = true
  await loadData()
  refreshing.value = false
}

const goBack = () => router.go(-1)

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.mobile-page {
  min-height: 100vh;
  background: #f7f8fa;
  display: flex;
  flex-direction: column;
}

.page-content {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  padding-bottom: 60px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  margin-bottom: 12px;
}

.stat-item {
  background: #fff;
  border-radius: 8px;
  padding: 12px 8px;
  text-align: center;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #1989fa;
}

.stat-label {
  font-size: 12px;
  color: #969799;
  margin-top: 4px;
}
</style>