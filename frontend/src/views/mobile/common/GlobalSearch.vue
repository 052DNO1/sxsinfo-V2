<template>
  <!-- 移动端直接显示内容 -->
  <div class="mobile-search-page mobile-layout">
    <van-nav-bar
      title="全局搜索"
      left-arrow
      @click-left="goBack"
      class="mobile-nav-bar"
    />

    <div class="mobile-content-wrapper">
      <!-- 搜索框 -->
      <van-search
        v-model="query"
        placeholder="搜索实训室、用户、课表、使用记录..."
        show-action
        @search="handleSearch"
        style="padding: 12px;"
      >
        <template #action>
          <div @click="handleSearch">搜索</div>
        </template>
      </van-search>

      <!-- 搜索结果 -->
      <div v-if="query" style="padding: 12px;">
        <van-cell-group inset>
          <van-cell title="搜索结果" :value="`找到 ${totalResults} 个相关结果`" />
        </van-cell-group>

        <div v-if="results && Object.keys(results).length > 0" style="margin-top: 12px;">
          <van-cell-group
            v-for="(items, category) in results"
            :key="category"
            inset
            style="margin-top: 12px;"
          >
            <van-cell :title="`${getCategoryIcon(category)} ${category} (${items.length})`" />
            <van-cell
              v-for="(item, index) in items"
              :key="`${category}-${index}`"
              :label="item.subtitle"
              is-link
              @click="handleItemClick(item)"
            >
              <template #title>
                <div style="display: flex; align-items: center;">
                  <van-icon :name="getItemIcon(category)" size="20px" :color="getItemIconColor(category)" style="margin-right: 12px;" />
                  <span>{{ item.title }}</span>
                </div>
              </template>
              <template #right-icon>
                <van-tag type="primary" size="small">{{ item.type }}</van-tag>
              </template>
            </van-cell>
          </van-cell-group>
        </div>

        <van-empty v-else description="没有找到相关结果" />
      </div>

      <van-empty v-else description="请输入搜索关键词" />
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi, useAuth } from '@/core/hooks'
import { decideRouteByActionType } from '@/utils/routeDecision'
import { useMobile } from '@/composables/useMobile'

export default {
  name: 'GlobalSearch',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const { user } = useAuth()
    
    const query = ref('')
    const results = ref({})
    const totalResults = ref(0)
    
    // 移动端初始化
    const { init: initMobile, loadVantComponents } = useMobile()

    const getCategoryIcon = (category) => {
      const icons = {
        实训室: '🏢',
        用户: '👥',
        课表: '📚',
        使用记录: '📋'
      }
      return icons[category] || '📄'
    }

    const getItemIcon = (category) => {
      const icons = {
        实训室: 'shop-o',
        用户: 'user-o',
        课表: 'orders-o',
        使用记录: 'records'
      }
      return icons[category] || 'description'
    }

    const getItemIconColor = (category) => {
      const colors = {
        实训室: '#1989fa',
        用户: '#7232dd',
        课表: '#07c160',
        使用记录: '#ff976a'
      }
      return colors[category] || '#969799'
    }

    // 完全前后端分离：根据业务标识决定路由
    const getItemUrl = (item) => {
      // 后端已经返回业务标识格式（action_type, resource_type, resource_id）
      if (item.action_type && item.resource_type) {
        const context = {
          resource_id: item.resource_id,
          id: item.resource_id,
          ...(item.context || {})
        }
        const route = decideRouteByActionType(item.action_type, item.resource_type, context, {})
        return route || '#'
      }
      
      // 完全前后端分离：不再需要向后兼容URL字段
      return '#'
    }

    const handleItemClick = (item) => {
      const url = getItemUrl(item)
      if (url && url !== '#') {
        router.push(url)
      }
    }

    const goBack = () => {
      router.go(-1)
    }

    const handleSearch = () => {
      router.push({ query: { q: query.value } })
      loadResults()
    }

    const loadResults = async () => {
      if (!query.value) return

      try {
        const { get: searchApi } = useApi('/sxs/global_search/', { immediate: false })
        const response = await searchApi({ q: query.value })
        results.value = response.results || {}
        totalResults.value = response.total_results || 0
      } catch (err) {
        console.error('❌ 搜索错误:', err)
        results.value = {}
        totalResults.value = 0
      }
    }

    onMounted(() => {
      // 初始化移动端检测
      const cleanupMobile = initMobile()
      onUnmounted(() => {
        if (cleanupMobile) cleanupMobile()
      })
      
      // 预加载 Vant 组件
      setTimeout(() => {
        loadVantComponents()
      }, 200)
      
      query.value = route.query.q || ''
      if (query.value) {
        loadResults()
      }
    })

    return {
      query,
      results,
      totalResults,
      getCategoryIcon,
      getItemIcon,
      getItemIconColor,
      getItemUrl,
      handleItemClick,
      handleSearch,
      goBack,
      user
    }
  }
}
</script>


