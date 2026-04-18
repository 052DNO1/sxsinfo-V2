<template>
  <!-- 移动端布局 -->
  <div class="mobile-cleanup-user-data mobile-layout">
    <!-- 顶部导航栏 -->
    <van-nav-bar
      :title="`数据清理 - ${targetUser?.nikename || ''}`"
      left-arrow
      @click-left="goBack"
      class="mobile-nav-bar"
    />

    <div class="mobile-content-wrapper">
      <!-- 警告提示 -->
      <van-notice-bar
        left-icon="warning-o"
        color="#ff9800"
        background="#fff3cd"
        style="margin: 16px;"
      >
        此工具用于处理用户删除前的数据关联问题。请谨慎操作，建议在删除用户前先处理相关数据。
      </van-notice-bar>

      <!-- 管理的实训室 -->
      <van-cell-group inset v-if="refSxs && refSxs.length > 0" style="margin-top: 16px;">
        <van-cell title="管理的实训室" :value="`${refSxs.length}条`" />
        <van-cell
          v-for="sxs in refSxs"
          :key="sxs.id"
          :title="sxs.sxsname"
          :label="`${sxs.sxsno} - ${sxs.sxsdepart_name}`"
        />
        <van-cell title="重新分配管理员">
          <template #value>
            <van-field
              v-model="reassignData.new_admin_id"
              placeholder="选择新的管理员"
              readonly
              is-link
              @click="showAdminPicker = true"
            />
          </template>
        </van-cell>
        <van-popup v-model:show="showAdminPicker" position="bottom">
          <van-picker
            :columns="adminColumns"
            @confirm="onAdminConfirm"
            @cancel="showAdminPicker = false"
          />
        </van-popup>
        <van-cell>
          <van-button
            type="primary"
            block
            @click="handleReassignSxs"
            :disabled="!reassignData.new_admin_id"
          >
            重新分配
          </van-button>
        </van-cell>
      </van-cell-group>

      <!-- 课表记录 -->
      <van-cell-group inset v-if="refClasses && refClasses.length > 0" style="margin-top: 16px;">
        <van-cell title="课表记录" :value="`${refClasses.length}条`" />
        <van-cell
          v-for="classItem in refClasses"
          :key="classItem.id"
          :title="classItem.classname"
          :label="`${classItem.sxsname} - 周${classItem.classweekday} 第${classItem.classjc}节`"
        />
        <van-cell title="重新分配教师">
          <template #value>
            <van-field
              v-model="reassignData.new_teacher_id"
              placeholder="选择新的任课教师"
              readonly
              is-link
              @click="showTeacherPicker = true"
            />
          </template>
        </van-cell>
        <van-popup v-model:show="showTeacherPicker" position="bottom">
          <van-picker
            :columns="teacherColumns"
            @confirm="onTeacherConfirm"
            @cancel="showTeacherPicker = false"
          />
        </van-popup>
        <van-cell>
          <van-button
            type="primary"
            block
            @click="handleReassignClass"
            :disabled="!reassignData.new_teacher_id"
          >
            重新分配
          </van-button>
        </van-cell>
      </van-cell-group>

      <!-- 空状态 -->
      <van-empty
        v-if="(!refSxs || refSxs.length === 0) && (!refClasses || refClasses.length === 0)"
        description="该用户没有需要清理的数据"
        style="margin-top: 50px;"
      />
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/utils/api'
import { useMobile } from '@/composables/useMobile'

export default {
  name: 'MobileCleanupUserData',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const targetUser = ref(null)
    const refSxs = ref([])
    const refClasses = ref([])
    const availableAdmins = ref([])
    const availableTeachers = ref([])
    const reassignData = ref({
      new_admin_id: '',
      new_teacher_id: ''
    })
    const showAdminPicker = ref(false)
    const showTeacherPicker = ref(false)

    // 移动端检测
    const { init: initMobile, loadVantComponents } = useMobile()

    // 管理员选择器列
    const adminColumns = computed(() => {
      return availableAdmins.value.map(admin => ({
        text: `${admin.nikename} (${admin.depart_name})`,
        value: admin.id
      }))
    })

    // 教师选择器列
    const teacherColumns = computed(() => {
      return availableTeachers.value.map(teacher => ({
        text: `${teacher.nikename} (${teacher.depart_name})`,
        value: teacher.id
      }))
    })

    const goBack = () => {
      router.go(-1)
    }

    // 管理员选择确认
    const onAdminConfirm = ({ selectedOptions }) => {
      reassignData.value.new_admin_id = selectedOptions[0]?.value || ''
      showAdminPicker.value = false
    }

    // 教师选择确认
    const onTeacherConfirm = ({ selectedOptions }) => {
      reassignData.value.new_teacher_id = selectedOptions[0]?.value || ''
      showTeacherPicker.value = false
    }

    // 统一的重新分配处理函数
    const handleReassign = async (action, fieldName, successMsg = '重新分配成功') => {
      try {
        const response = await api.post('/cleanup-user-data/', {
          action,
          [fieldName]: reassignData.value[fieldName]
        })
        
        const { showSuccessToast, showFailToast } = await import('@/utils/mobileDialog')
        
        if (response.success) {
          await showSuccessToast(successMsg)
          loadData()
          // 重置选择
          reassignData.value[fieldName] = ''
        } else {
          const errorMsg = response.message || '分配失败'
          await showFailToast(errorMsg)
        }
      } catch (err) {
        const { showFailToast } = await import('@/utils/mobileDialog')
        const errorMsg = '分配失败：' + (err.message || '未知错误')
        await showFailToast(errorMsg)
      }
    }

    const handleReassignSxs = () => handleReassign('reassign_sxs_admin', 'new_admin_id', '管理员重新分配成功')
    const handleReassignClass = () => handleReassign('reassign_class_teacher', 'new_teacher_id', '教师重新分配成功')

    const loadData = async () => {
      try {
        const response = await api.get('/cleanup-user-data/', { params: route.query })
        targetUser.value = response.target_user
        refSxs.value = response.ref_sxs || []
        refClasses.value = response.ref_classes || []
        availableAdmins.value = response.available_admins || []
        availableTeachers.value = response.available_teachers || []
      } catch (err) {
        console.error('Load data error:', err)
        const { showFailToast } = await import('@/utils/mobileDialog')
        await showFailToast('加载数据失败：' + (err.message || '未知错误'))
      }
    }

    onMounted(() => {
      // 初始化移动端检测
      const cleanupMobile = initMobile()
      // 预加载 Vant 组件
      setTimeout(() => {
        loadVantComponents()
      }, 200)
      
      loadData()
    })

    return {
      targetUser,
      refSxs,
      refClasses,
      availableAdmins,
      availableTeachers,
      reassignData,
      showAdminPicker,
      showTeacherPicker,
      adminColumns,
      teacherColumns,
      onAdminConfirm,
      onTeacherConfirm,
      handleReassignSxs,
      handleReassignClass,
      goBack
    }
  }
}
</script>


/* mobile.css 已在 main.js 中统一导入 */

/* 移动端样式 */
.mobile-cleanup-user-data {
  min-height: 100vh;
  background: #f7f8fa;
}

