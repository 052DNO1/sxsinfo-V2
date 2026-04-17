<template>
  <div class="mobile-page">
    <van-nav-bar title="学期管理" left-arrow @click-left="goBack">
      <template #right>
        <van-icon name="home-o" size="20" @click="goHome" />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <van-empty v-if="error" :description="error" />

      <div v-else class="list-container">
        <van-cell-group inset>
          <van-cell
            v-for="item in objectList"
            :key="item.id"
          >
            <template #title>
              <div class="term-title">
                {{ item.termname }}
                <van-tag v-if="item.iscurrent" type="success" size="small">当前学期</van-tag>
              </div>
            </template>
            <template #label>
              <div class="term-info">
                <span v-if="item.startdate">{{ item.startdate }}</span>
                <span v-if="item.enddate"> ~ {{ item.enddate }}</span>
              </div>
            </template>
            <template #icon>
              <van-icon name="calendar-o" size="20" color="#1989fa" style="margin-right: 8px" />
            </template>
            <template #value>
              <van-tag v-if="item.islocked" type="default" size="small">已归档</van-tag>
            </template>
          </van-cell>
        </van-cell-group>
      </div>
    </div>

    <van-action-bar>
      <van-action-bar-button type="primary" text="添加学期" @click="handleAdd" />
    </van-action-bar>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNavigation } from '@/utils/routeDecision'
import { useTermList } from '@/composables/useTermList'

const router = useRouter()
const { goHome } = useNavigation()

const {
    tableData: objectList, error,
    loadData: loadListData,
} = useTermList()

const handleAdd = () => {
  router.push('/addterm')
}

const goBack = () => {
  router.go(-1)
}

onMounted(() => {
  loadListData()
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

.term-title {
  font-size: 15px;
  font-weight: 500;
  color: #323233;
  display: flex;
  align-items: center;
  gap: 8px;
}

.term-info {
  font-size: 12px;
  color: #969799;
  margin-top: 4px;
}
</style>
