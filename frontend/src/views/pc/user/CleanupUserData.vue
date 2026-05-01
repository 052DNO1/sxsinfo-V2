<!-- 清理用户数据 -->
<template>
  <Index>
    <template #rightcontent>
      <div class="listheader">
        <el-icon><Tools /></el-icon> 数据清理工具 - {{ targetUser?.nickname || '' }}
        <div style="float: right;">
          <el-button
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
        <div style="clear: both;" />
      </div>

      <div class="cleanup-container">
        <div class="warning-section">
          <div class="warning-box">
            <h3><el-icon><WarningFilled /></el-icon> 重要提示</h3>
            <p>此工具用于处理用户删除前的数据关联问题。请谨慎操作，建议在删除用户前先处理相关数据。</p>
          </div>
        </div>

        <div class="data-sections">
          <div
            v-if="refSxs && refSxs.length> 0"
            class="data-section"
          >
            <h4><el-icon><OfficeBuilding /></el-icon> 管理的实训室 ({{ refSxs.length }})</h4>
            <div class="data-list">
              <div
                v-for="sxs in refSxs"
                :key="sxs.id"
                class="data-item"
              >
                <span class="item-name">{{ sxs.name }}</span>
                <span class="item-desc">{{ sxs.room_number }} - {{ sxs.department_name }}</span>
              </div>
            </div>
            <div class="action-section">
              <h5>重新分配管理员：</h5>
              <el-form
                :inline="true"
                class="reassign-form"
                @submit.prevent="handleReassignSxs"
              >
                <el-form-item>
                  <el-select
                    v-model="reassignData.new_admin_id"
                    placeholder="选择新的管理员"
                    style="width: 250px"
                    filterable
                  >
                    <el-option
                      v-for="admin in availableAdmins"
                      :key="admin.id"
                      :label="`${admin.nickname} (${admin.department_name})`"
                      :value="admin.id"
                    />
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-button
                    type="primary"
                    @click="handleReassignSxs"
                  >
                    重新分配
                  </el-button>
                </el-form-item>
              </el-form>
            </div>
          </div>

          <div
            v-if="refClasses && refClasses.length> 0"
            class="data-section"
          >
            <h4><el-icon><Reading /></el-icon> 课表记录 ({{ refClasses.length }}�?</h4>
            <div class="data-list">
              <div
                v-for="classItem in refClasses"
                :key="classItem.id"
                class="data-item"
              >
                <span class="item-name">{{ classItem.classname }}</span>
                <span class="item-desc">{{ classItem.laboratory_name }} - 周{{ classItem.weekday }} 第{{ classItem.time_slot }}节</span>
              </div>
            </div>
            <div class="action-section">
              <h5>重新分配教师：</h5>
              <el-form
                :inline="true"
                class="reassign-form"
                @submit.prevent="handleReassignClass"
              >
                <el-form-item>
                  <el-select
                    v-model="reassignData.new_teacher_id"
                    placeholder="选择新的任课教师"
                    style="width: 250px"
                    filterable
                  >
                    <el-option
                      v-for="teacher in availableTeachers"
                      :key="teacher.id"
                      :label="`${teacher.nickname} (${teacher.department_name})`"
                      :value="teacher.id"
                    />
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-button
                    type="primary"
                    @click="handleReassignClass"
                  >
                    重新分配
                  </el-button>
                </el-form-item>
              </el-form>
            </div>
          </div>
        </div>
      </div>
    </template>
  </Index>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNavigation } from '@/core/utils/routeDecision'
import { useApi } from '@/core/hooks'
import Index from '@/views/pc/dashboard/Index.vue'
import { showError, showSuccess } from '@/core/utils/errorHandler'
import { WarningFilled, OfficeBuilding, Reading, Tools } from '@element-plus/icons-vue'

export default {
  name: 'CleanupUserData',
  components: {
    Index
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    // 使用导航工具
    const { smartBack, goHome } = useNavigation()
    
    // 使用 useApi composable
    const userId = route.params.id || route.query.user_id
    const { get: fetchCleanupDataApi, post: submitCleanupApi } = useApi(`/users/${userId}/cleanup_data/`, { immediate: false })
    
    const targetUser = ref(null)
    const refSxs = ref([])
    const refClasses = ref([])
    const availableAdmins = ref([])
    const availableTeachers = ref([])
    const reassignData = ref({
      new_admin_id: '',
      new_teacher_id: ''
    })

    // 统一的重新分配处理函?
    const handleReassign = async (action, fieldName, successMsg = '重新分配成功') => {
      try {
        const response = await submitCleanupApi({
          action,
          [fieldName]: reassignData.value[fieldName]
        })
        
        if (response.success) {
          await showSuccess(successMsg)
          loadData()
        } else {
          await showError(response.message || '分配失败')
        }
      } catch (err) {
        await showError('分配失败：' + (err.message || '未知错误'))
      }
    }

    const handleReassignSxs = () => handleReassign('reassign_sxs_admin', 'new_admin_id')
    const handleReassignClass = () => handleReassign('reassign_class_teacher', 'new_teacher_id')

    const loadData = async () => {
      try {
        const response = await fetchCleanupDataApi(route.query)
        if (response && response.success && response.data) {
          targetUser.value = response.data.target_user
          refSxs.value = response.data.ref_sxs || []
          refClasses.value = response.data.ref_classes || []
          availableAdmins.value = response.data.available_admins || []
          availableTeachers.value = response.data.available_teachers || []
        }
      } catch (err) {
      }
    }

    onMounted(() => {
      loadData()
    })

    return {
      targetUser,
      refSxs,
      refClasses,
      availableAdmins,
      availableTeachers,
      reassignData,
      handleReassignSxs,
      handleReassignClass,
      smartBack,
      goHome
    }
  }
}
</script>

<style scoped>
/* @import '../../../assets/css/pages.css'; - Removed */
/* 20. 数据清理页面样式 */
.cleanup-container {
    max-width: 1000px;
    margin: 0 auto;
    padding: 20px;
}

.warning-section {
    margin-bottom: 30px;
}

.warning-box {
    background: var(--warning-bg, #fff3cd);
    border: 1px solid #ffeaa7;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 20px;
}

.warning-box h3 {
    color: var(--warning-color);
    margin: 0 0 10px 0;
    font-size: 20px;
}

.warning-box p {
    color: var(--warning-color);
    margin: 0;
    font-size: var(--font-size-sm);
}

.data-sections {
    display: grid;
    gap: 20px;
}

.data-section {
    background: var(--card-bg, white);
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    border: 1px solid #e1e8ed;
}

.data-section h4 {
    color: var(--text-primary, #333);
    margin: 0 0 15px 0;
    font-size: 20px;
    border-bottom: 2px solid #1c6cd4;
    padding-bottom: 8px;
}

.data-list {
    margin-bottom: 20px;
}

.data-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    background: var(--panel-bg, #f8f9fa);
    border-radius: 4px;
    margin-bottom: 8px;
    border-left: 3px solid #1c6cd4;
}

.item-name {
    font-weight: 600;
    color: var(--text-primary, #333);
}

.item-desc {
    color: var(--text-secondary, #666);
    font-size: 15px;
}

.action-section {
    background: var(--panel-bg, #f8f9fa);
    padding: 15px;
    border-radius: 6px;
    border: 1px solid var(--border-color);
}

.action-section h5 {
    margin: 0 0 10px 0;
    color: var(--text-primary, #333);
    font-size: var(--font-size-sm);
}

.reassign-form,
.archive-form {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
}

.reassign-form select {
    flex: 1;
    min-width: 200px;
    padding: 8px 12px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: var(--font-size-sm);
}

.archive-warning {
    color: var(--warning-color);
    font-size: 15px;
    margin: 0 0 10px 0;
    font-style: italic;
}

.action-buttons {
    display: flex;
    gap: 15px;
    justify-content: center;
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #e1e8ed;
}

.form-actions {
    display: flex;
    gap: 12px;
    margin-top: 24px;
    padding-top: 20px;
    border-top: 1px solid #e1e8ed;
}

.generation-history {
    background: var(--card-bg, white);
    border-radius: 8px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.generation-history h3 {
    color: var(--text-primary, #333);
    margin-bottom: 20px;
    font-size: 22.5px;
    font-weight: 600;
}

.history-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.history-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    border: 1px solid #e1e8ed;
    border-radius: 6px;
    transition: all 0.2s;
}

.history-item:hover {
    border-color: var(--primary-color);
    box-shadow: 0 2px 8px rgba(28, 108, 212, 0.1);
}

.history-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.history-name {
    font-weight: 500;
    color: var(--text-primary, #333);
}

.history-time {
    font-size: 15px;
    color: #999;
}

.history-actions {
    display: flex;
    gap: 8px;
}
</style>
