<template>
  <div class="mobile-page">
    <van-nav-bar :title="listHeader" left-arrow @click-left="goBack">
      <template #right>
        <van-icon name="home-o" size="20" @click="goHome" />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <van-skeleton v-if="loading" :row="5" animated />

      <van-empty v-else-if="error" :description="error" />

      <template v-else>
        <div class="list-container">
          <van-cell-group inset>
            <van-cell
              v-for="(item, index) in objectList"
              :key="index"
              is-link
              @click="viewDetail(item)"
            >
              <template #title>
                <div class="record-title">{{ item.title }}</div>
              </template>
              <template #label>
                <div class="record-info">
                  <span class="info-item">{{ item.sxsname }}</span>
                  <span class="info-item">{{ item.date }}</span>
                </div>
              </template>
              <template #value>
                <van-tag :type="getTypeColor(item.type)" size="small">
                  {{ item.type }}
                </van-tag>
              </template>
            </van-cell>
          </van-cell-group>
        </div>

        <Pagination 
          v-if="isPaginated && totalPages > 1"
          :show="isPaginated && totalPages > 1"
          :current-page="currentPage"
          :page-size="pageSize"
          :total-count="totalCount"
          @current-change="handlePageChange"
        />
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from '@/composables/useApi'
import { useNavigation } from '@/utils/routeDecision'
import Pagination from '@/views/mobile/components/Pagination.vue'

const route = useRoute()
const router = useRouter()
const { goHome } = useNavigation()

const loading = ref(false)
const error = ref('')
const objectList = ref([])
const listHeader = ref('归档记录')
const isPaginated = ref(false)
const currentPage = ref(1)
const totalPages = ref(1)
const totalCount = ref(0)
const pageSize = ref(10)

const apiComposable = useApi('', { immediate: false })

const getTypeColor = (type) => {
  const colorMap = {
    '使用': 'primary',
    '维护': 'success',
    '故障': 'danger',
    '课表': 'warning',
    '实训室': 'info',
    '设备': 'default',
    '用户': 'primary'
  }
  return colorMap[type] || 'default'
}

const loadData = async () => {
  if (loading.value) return
  loading.value = true
  try {
    const id = route.params.id
    const type = route.query.type
    const page = route.query.page || 1
    
    const response = await apiComposable.get({}, { 
      url: `/userinfo/view_archived_records/${id}/`,
      params: { type, page }
    })
    
    if (response) {
      listHeader.value = response.listheader || '归档记录'
      isPaginated.value = response.is_paginated || false
      
      if (response.page_obj) {
        currentPage.value = response.page_obj.number
        totalPages.value = response.page_obj.paginator.num_pages
        totalCount.value = response.page_obj.paginator.count
        pageSize.value = response.page_obj.paginator.per_page
      }
      
      if (response.object_list && Array.isArray(response.object_list)) {
        objectList.value = response.object_list.map(row => ({
          type: row[0],
          id: row[1],
          sxsname: row[2],
          content: row[3],
          date: row[4],
          title: row[3]
        }))
      } else {
        objectList.value = []
      }
    }
  } catch (err) {
    error.value = '加载失败'
    console.error('Load data error:', err)
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
  router.push({
    query: { ...route.query, page }
  })
  loadData()
}

const viewDetail = (item) => {
  router.push({
    name: 'ArchivedRecordDetail',
    params: { 
      id: route.params.id,
      recordId: item.id 
    },
    query: { type: route.query.type }
  })
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
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 6px;
}

.info-item {
  font-size: 12px;
  color: #969799;
}

:deep(.pagination-wrapper) {
  margin-bottom: 60px;
}
</style>
