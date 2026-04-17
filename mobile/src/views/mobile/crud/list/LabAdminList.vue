<template>
  <div class="mobile-page">
    <van-nav-bar title="管理员列表" left-arrow @click-left="goBack">
      <template #right>
        <van-icon name="home-o" size="20" @click="goHome" />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <van-empty v-if="admins.length === 0 && !loading" description="暂无管理员" />

      <div v-else class="list-container">
        <van-cell-group inset>
          <van-cell
            v-for="admin in admins"
            :key="admin.id"
            is-link
            @click="handleItemClick(admin)"
          >
            <template #title>
              <div class="admin-title">{{ admin.name || admin.username }}</div>
            </template>
            <template #label>
              <div class="admin-info">
                <span v-if="admin.role">{{ admin.role }}</span>
              </div>
            </template>
            <template #icon>
              <van-image
                round
                width="40"
                height="40"
                :src="admin.avatar || ''"
                icon="user-o"
                style="margin-right: 12px"
              />
            </template>
          </van-cell>
        </van-cell-group>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from '@/composables/useApi'
import { useNavigation, getApiPath } from '@/utils/routeDecision'

const route = useRoute()
const router = useRouter()
const { goHome, smartBack } = useNavigation()

const loading = ref(false)
const admins = ref([])

const apiComposable = useApi('', { immediate: false })

const loadData = async () => {
  if (loading.value) return
  loading.value = true
  try {
    const apiPath = getApiPath(route.path, route.query, route.params)
    const response = await apiComposable.get(route.query, { url: apiPath })
    
    if (response && response.object_list) {
      admins.value = response.object_list.map(item => ({
        id: item.id,
        username: item.username,
        name: item.nikename || item.username,
        role: item.role_name || '',
        avatar: ''
      }))
    }
  } catch (err) {
    console.error('Load admins error:', err)
  } finally {
    loading.value = false
  }
}

const handleItemClick = (admin) => {
  router.push(`/edit-user/${admin.id}`)
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

.admin-title {
  font-size: 15px;
  font-weight: 500;
  color: #323233;
}

.admin-info {
  font-size: 12px;
  color: #969799;
  margin-top: 4px;
}
</style>
