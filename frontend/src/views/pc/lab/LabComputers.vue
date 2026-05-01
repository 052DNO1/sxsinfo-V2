<!-- 机房电脑管理 -->
<template>
  <Index class="pc-layout">
    <template #rightcontent>
      <div class="page-container">
        <el-card
          class="header-card"
          shadow="hover"
        >
          <div class="listheader">
            <div class="header-title">
              <el-icon class="header-icon">
                <Monitor />
              </el-icon>
              <span>设备管理</span>
            </div>

            <div class="listheader-actions">
              <div class="filter-area">
                <el-select
                  v-model="filters.sxsid"
                  placeholder="请选择实训室"
                  clearable
                  filterable
                  class="filter-select"
                  @change="handleFilter"
                >
                  <el-option
                    v-for="item in labOptions"
                    :key="item.id"
                    :label="item.name"
                    :value="item.id"
                  />
                </el-select>
              </div>

              <div class="action-buttons">
                <el-button
                  type="success"
                  plain
                  @click="handleExportAll"
                >
                  导出全部设备
                </el-button>
                <el-button
                  type="danger"
                  plain
                  @click="handleBatchDelete"
                >
                  批量/删除
                </el-button>
                <el-button
                  v-if="shouldShowBackButton"
                  class="nav-action-btn"
                  plain
                  @click="smartBack"
                >
                  返回
                </el-button>
                <el-button
                  class="nav-action-btn"
                  plain
                  @click="goHome"
                >
                  首页
                </el-button>
              </div>
            </div>
          </div>
        </el-card>

        <el-card
          class="table-card"
          shadow="hover"
        >
          <el-table
            v-loading="loading"
            :data="tableData"
            style="width: 100%"
            border
            stripe
            class="modern-table"
            @selection-change="handleSelectionChange"
          >
            <el-table-column
              type="selection"
              width="55"
              align="center"
            />

            <el-table-column
              prop="code"
              label="设备编号"
              width="120"
              sortable
            />

            <el-table-column
              prop="name"
              label="设备名称"
              min-width="150"
              show-overflow-tooltip
            />

            <el-table-column
              prop="brand"
              label="品牌"
              width="120"
              show-overflow-tooltip
            />

            <el-table-column
              prop="model"
              label="型号"
              width="120"
              show-overflow-tooltip
            />

            <el-table-column
              prop="category"
              label="类型"
              width="100"
            />

            <el-table-column
              label="配置"
              min-width="200"
              show-overflow-tooltip
            >
              <template #default="scope">
                <span>{{ scope.row.config || '暂无' }}</span>
              </template>
            </el-table-column>

            <el-table-column
              prop="laboratory_name"
              label="位置"
              min-width="150"
              show-overflow-tooltip
            />

            <el-table-column
              prop="status"
              label="状态"
              width="100"
              align="center"
            >
              <template #default="scope">
                <el-tag
                  :type="getStatusType(scope.row.status)"
                  effect="light"
                  size="small"
                >
                  {{ getStatusLabel(scope.row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column
              label="操作"
              width="150"
              fixed="right"
              align="center"
            >
              <template #default="scope">
                <el-button
                  type="primary"
                  link
                  size="small"
                  @click="openEdit(scope.row)"
                >
                  <el-icon><Edit /></el-icon> 编辑
                </el-button>
                <el-button
                  type="danger"
                  link
                  size="small"
                  @click="handleDelete(scope.row)"
                >
                  <el-icon><Delete /></el-icon> 删除
                </el-button>
              </template>
            </el-table-column>
            
            <template #empty>
              <el-empty description="暂无设备数据" />
            </template>
          </el-table>

          <Pagination
            v-if="totalCount > 0"
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total-count="totalCount"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </el-card>
      </div>
    </template>
  </Index>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Edit, Delete, Monitor } from '@element-plus/icons-vue'
import Index from '@/views/pc/dashboard/Index.vue'
import Pagination from '@/views/pc/components/Pagination.vue'
import { useApi, useDelete } from '@/core/hooks'
import { safeConfirm, showSuccess, showError } from '@/core/utils/errorHandler'
import { getStatusType } from '@/core/utils/format'
import { useNavigation } from '@/core/utils/routeDecision'
import { adaptComputerList } from '@/core/utils/adapters'
import { useUserStore } from '@/core/store/user'
import { useAppStore } from '@/core/store/app'
import { handleExportFromResponse } from '@/core/utils/io'

export default {
  name: 'LabComputers',
  components: {
    Index,
    Pagination,
    Edit,
    Delete,
    Monitor
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const { goHome, smartBack } = useNavigation()
    const userStore = useUserStore()
    const appStore = useAppStore()
    
    const shouldShowBackButton = computed(() => {
      const user = userStore.user
      if (user?.is_super_admin && !user?.is_superuser) {
        return false
      }
      return true
    })
    
    const loading = ref(false)
    const tableData = ref([])
    const totalCount = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(10)
    
    const { get: fetchApi } = useApi('', { immediate: false })
    const { get: fetchLabsApi } = useApi('/laboratories/', { immediate: false })
    const { get: fetchExportApi } = useApi('/equipments/', { immediate: false })
    const labOptions = ref([])
    
    const { handleBatchDelete: execBatchDelete, handleDelete: execDelete } = useDelete({
      apiPath: '/equipments/batch_delete/',
      apiPathBuilder: (item) => `/equipments/${item.id}/`,
      getId: (id) => id,
      refresh: () => loadData(1),
      confirmMessageBuilder: (itemOrSelection) => {
        if (Array.isArray(itemOrSelection)) {
          return `确定要删除选中的 ${itemOrSelection.length} 个设备吗？`
        }
        return `确定要删除设备 "${itemOrSelection.name}" 吗？`
      }
    })
    
    const filters = ref({
      sxsid: '',
      search: '',
      status: ''
    })
    const selectedIds = ref([])

    const getStatusLabel = (status) => {
      const statusMap = {
        'NORMAL': '正常',
        'MAINTENANCE': '维护中',
        'DAMAGED': '损坏',
        'SCRAPPED': '已报废',
        'BORROWED': '借用中'
      }
      return statusMap[status] || status
    }

    const loadData = async (page = 1) => {
      loading.value = true
      try {
        const params = {
          page,
          page_size: pageSize.value
        }

        if (filters.value.sxsid) {
          params.laboratory_id = filters.value.sxsid
        }
        if (filters.value.search) {
          params.search = filters.value.search
        }
        if (filters.value.status) {
          params.status = filters.value.status
        }

        const response = await fetchApi(params, { url: '/equipments/' })
        const adapted = adaptComputerList(response)

        if (Array.isArray(adapted.data)) {
          tableData.value = adapted.data
        } else if (Array.isArray(adapted.data?.list)) {
          tableData.value = adapted.data.list
        } else {
          tableData.value = []
        }

        if (response?.data?.total !== undefined) {
          totalCount.value = response.data.total
          currentPage.value = response.data.page || page
          pageSize.value = response.data.page_size || pageSize.value
        } else if (response?.total !== undefined) {
          totalCount.value = response.total
          currentPage.value = response.page || page
          pageSize.value = response.page_size || pageSize.value
        } else if (response?.data?.list?.length !== undefined) {
          totalCount.value = response.data.list.length
          currentPage.value = page
        } else {
          currentPage.value = page
          totalCount.value = adapted.data?.length || 0
        }
      } catch (err) {
        showError('加载数据失败')
      } finally {
        loading.value = false
      }
    }

    const loadLabs = async () => {
      try {
        const response = await fetchLabsApi({ nopage: 1 })
        
        if (response?.items) {
          labOptions.value = response.items
        } else if (response?.data?.list) {
          labOptions.value = response.data.list
        } else if (Array.isArray(response)) {
          labOptions.value = response
        }
      } catch (error) {
      }
    }

    const handleFilter = () => {
      router.push({ query: { ...filters.value } })
      loadData(1)
    }

    const handleSizeChange = (val) => {
      pageSize.value = val
      loadData(1)
    }

    const handleCurrentChange = (val) => {
      currentPage.value = val
      loadData(val)
    }

    const openEdit = (item) => {
      router.push(`/edit-device/${item.id}`)
    }

    const handleDelete = async (item) => {
      await execDelete(item)
    }

     const handleExportAll = async () => {
      try {
        const params = { ...filters.value, ...route.query }
        const response = await fetchExportApi(params, {
          url: '/common/export/equipment/',
          responseType: 'blob'
        })

        await handleExportFromResponse(response, `设备列表_${new Date().toISOString().slice(0,10)}.xlsx`)
      } catch (e) {
        if (e === 'cancel' || e === 'close') return
        showError('导出失败: ' + (e.message || '未知错误'))
      }
    }

    const handleBatchDelete = async () => {
      await execBatchDelete(selectedIds.value)
    }

    const handleSelectionChange = (selection) => {
      selectedIds.value = selection.map(item => item.id)
    }

    onMounted(() => {
      const query = { ...route.query }
      if (query.sxsid) query.sxsid = Number(query.sxsid)
      
      filters.value = { ...filters.value, ...query }
      loadLabs()
      loadData(1)
    })

    watch(() => route.query, (newQuery, oldQuery) => {
      if (JSON.stringify(newQuery) !== JSON.stringify(oldQuery)) {
        loadData(1)
      }
    }, { deep: true })

    watch(() => appStore.listRefreshTriggers.devices, (newVal, oldVal) => {
      if (newVal !== oldVal && newVal > 0) {
        loadData(currentPage.value)
      }
    })

    return {
      tableData,
      labOptions,
      filters,
      selectedIds,
      loading,
      totalCount,
      currentPage,
      pageSize,
      handleSizeChange,
      handleCurrentChange,
      handleFilter,
      handleSelectionChange,
      handleBatchDelete,
      handleDelete,
      handleExportAll,
      smartBack,
      goHome,
      shouldShowBackButton,
      getStatusType,
      getStatusLabel,
      openEdit
    }
  }
}
</script>

<style scoped>
.page-container {
  padding: 0;
  max-width: 100%;
}

.header-card {
  margin-bottom: 20px;
  border-radius: 12px;
  border: none;
}

.listheader {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.header-title {
  display: flex;
  align-items: center;
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
}

.header-icon {
  margin-right: 10px;
  color: #1890ff;
  font-size: 24px;
  display: flex;
  align-items: center;
}

.listheader-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.filter-area {
  display: flex;
  align-items: center;
}

.filter-select {
  width: 200px;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.table-card {
  border-radius: 12px;
  border: none;
  min-height: 500px;
}

.modern-table {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table th.el-table__cell) {
  background-color: #f5f7fa;
  color: #606266;
  font-weight: 600;
  height: 50px;
}

.pagination-container,
.pagination-wrapper {
  margin-top: 24px;
  padding-bottom: 10px;
  display: flex;
  justify-content: flex-end;
}
</style>
