<template>
  <div class="mobile-page">
    <van-nav-bar title="使用记录详情" left-arrow @click-left="goBack">
      <template #right>
        <van-icon name="home-o" size="20" @click="goHome" />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <van-skeleton v-if="loading" :row="6" animated />

      <template v-else-if="record">
        <van-cell-group inset title="基本信息">
          <van-cell title="实训室" :value="record.sxsname || '-'" />
          <van-cell title="使用日期" :value="record.sxsdate || '-'" />
          <van-cell title="使用节次" :value="record.sxsstart || '-'" />
          <van-cell title="课时数" :value="record.sxsclasshour || '-'" />
          <van-cell title="人数" :value="record.sxsnum || '-'" />
        </van-cell-group>

        <van-cell-group inset title="课程信息">
          <van-cell title="班级" :value="record.sxsclass || '-'" />
          <van-cell title="教师" :value="record.sxsteacher_name || '-'" />
          <van-cell title="课程内容" :value="record.sxscontent || '-'" />
        </van-cell-group>

        <van-cell-group inset title="设备状态">
          <van-cell title="设备状态">
            <template #value>
              <van-tag :type="record.sxsdevice_status === '正常' ? 'success' : 'danger'">
                {{ record.sxsdevice_status || '正常' }}
              </van-tag>
            </template>
          </van-cell>
          <van-cell title="实训室状态">
            <template #value>
              <van-tag :type="record.sxs_status === '正常' ? 'success' : 'warning'">
                {{ record.sxs_status || '正常' }}
              </van-tag>
            </template>
          </van-cell>
        </van-cell-group>

        <van-cell-group inset title="备注" v-if="record.sxsmemo">
          <div class="memo-content">{{ record.sxsmemo }}</div>
        </van-cell-group>
      </template>

      <van-empty v-else description="暂无数据" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNavigation } from '@/utils/routeDecision'
import { useApi } from '@/composables/useApi'
import { showError } from '@/utils/errorHandler'

const route = useRoute()
const router = useRouter()
const { goHome, smartBack } = useNavigation()

const loading = ref(false)
const record = ref(null)

const apiComposable = useApi('', { immediate: false })

const loadRecord = async () => {
  loading.value = true
  try {
    const recordId = route.params.id
    const response = await apiComposable.get({}, { url: `/sxs/editrecord/${recordId}/` })
    
    if (response && response.record) {
      record.value = response.record
    }
  } catch (err) {
    showError('加载记录失败')
  } finally {
    loading.value = false
  }
}

const goBack = () => router.go(-1)

onMounted(() => {
  loadRecord()
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
  padding-bottom: 20px;
}

.memo-content {
  padding: 12px 16px;
  font-size: 14px;
  color: #323233;
  line-height: 1.6;
  background: #fff;
}
</style>
