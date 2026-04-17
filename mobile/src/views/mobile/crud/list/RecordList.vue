<template>
  <div class="mobile-page">
    <van-nav-bar title="实训室记录" left-arrow @click-left="goBack">
      <template #right>
        <van-icon name="home-o" size="20" @click="goHome" />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <van-empty v-if="!canView" description="您没有权限查看记录" />

      <template v-else>
        <van-tabs v-model="activeTab" @change="handleTabChange">
          <van-tab title="使用记录" />
          <van-tab title="维护记录" />
        </van-tabs>

        <van-empty v-if="error" :description="error" />

        <van-empty v-else-if="!loading && objectList.length === 0" description="暂无数据" />

        <div v-else class="list-container">
          <van-cell-group inset>
            <van-cell
              v-for="item in objectList"
              :key="item.id"
              is-link
              @click="handleItemClick(item)"
            >
              <template #title>
                <div class="record-title">{{ item.sxsname || '记录' }}</div>
              </template>
              <template #label>
                <div class="record-info">
                  <template v-if="currentType === 'usage'">
                    <span v-if="item.sxsdate">{{ item.sxsdate }}</span>
                    <span v-if="item.sxsstart"> · {{ item.sxsstart }}</span>
                  </template>
                  <template v-else-if="currentType === 'maintain'">
                    <span v-if="item.maintainrecorddate">{{ item.maintainrecorddate }}</span>
                  </template>
                </div>
              </template>
              <template #value>
                <van-tag v-if="currentType === 'usage' && item.sxsdevice_status && item.sxsdevice_status !== '正常'" type="danger" size="small">
                  异常
                </van-tag>
              </template>
            </van-cell>
          </van-cell-group>
        </div>

        <Pagination 
          v-if="isPaginated"
          :show="isPaginated"
          :current-page="currentPage"
          :page-size="pageSize"
          :total-count="totalCount"
          @current-change="handleCurrentChange"
        />
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useNavigation } from '@/utils/routeDecision'
import { useApi } from '@/composables/useApi'
import Pagination from '@/views/mobile/components/Pagination.vue'

const route = useRoute()
const router = useRouter()
const { user } = useAuth()
const { goHome, smartBack } = useNavigation()

const loading = ref(false)
const objectList = ref([])
const error = ref('')
const listHeader = ref('')
const activeTab = ref(0)
const isPaginated = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const totalCount = ref(0)

const canView = computed(() => {
  const u = user.value
  return u?.is_departadmin || u?.is_sxsadmin
})

const currentType = computed(() => {
  return activeTab.value === 0 ? 'usage' : 'maintain'
})

const apiComposable = useApi('', { immediate: false })

const getQtype = () => {
  const u = user.value
  if (u?.is_superuser) return '0'
  if (u?.is_departadmin) return '4'
  if (u?.is_sxsadmin) return '2'
  return '4'
}

const loadData = async (options = {}) => {
  loading.value = true
  error.value = ''
  
  try {
    const qtype = route.params.id || route.query.qtype || getQtype()
    const type = options.type || currentType.value
    const page = options.page || currentPage.value
    
    const response = await apiComposable.get(
      { type, page, page_size: pageSize.value },
      { url: `/sxs/listsxsinfo/${qtype}/` }
    )
    
    if (response && response.success !== false) {
      listHeader.value = response.listheader || ''
      objectList.value = response.object_list || response.data || []
      
      if (response.paginator || response.page_obj) {
        isPaginated.value = true
        totalCount.value = response.paginator?.count || response.page_obj?.paginator?.count || 0
        currentPage.value = response.page_obj?.number || page
      }
    } else {
      objectList.value = []
      error.value = response?.message || '加载失败'
    }
  } catch (err) {
    error.value = '加载失败'
    objectList.value = []
    console.error('Load record list error:', err)
  } finally {
    loading.value = false
  }
}

const handleTabChange = async (tabIndex) => {
  currentPage.value = 1
  error.value = ''
  objectList.value = []
  const newType = tabIndex === 0 ? 'usage' : 'maintain'
  await loadData({ type: newType })
}

const handleCurrentChange = async (page) => {
  currentPage.value = page
  await loadData({ page })
}

const handleItemClick = (item) => {
  if (currentType.value === 'usage') {
    router.push(`/edit-record/${item.id}`)
  }
}

const goBack = () => router.go(-1)

onMounted(() => {
  if (canView.value) {
    loadData()
  }
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
  padding-bottom: 100px;
}

.list-container {
  min-height: 300px;
}

.record-title {
  font-size: 15px;
  font-weight: 500;
  color: #323233;
}

.record-info {
  font-size: 12px;
  color: #969799;
  margin-top: 4px;
}

:deep(.pagination-wrapper) {
  margin-bottom: 60px;
}
</style>
