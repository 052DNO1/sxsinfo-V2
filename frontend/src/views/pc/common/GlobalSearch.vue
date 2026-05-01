<template>
  <!-- PC端使用Index组件 -->
  <Index class="pc-layout">
    <template #rightcontent>
      <div class="page-header">
        <div class="header-left">
          <h2 class="header-title">
            <el-icon class="header-icon">
              <Search />
            </el-icon>
            全局搜索
          </h2>
        </div>
        <div class="header-actions">
          <el-button
            class="nav-action-btn"
            plain
            @click="goHome"
          >
            <el-icon><HomeFilled /></el-icon>首页
          </el-button>
        </div>
      </div>

      <div class="search-container">
        <div class="search-box-section">
          <form
            class="search-form"
            @submit.prevent="handleSearch"
          >
            <div
              class="search-input-group"
              :class="{ 'is-focused': isInputFocused }"
            >
              <el-input
                v-model="query"
                placeholder="搜索实训室、用户、课表、使用记?.."
                class="search-input-el"
                size="large"
                clearable
                @input="onInput"
                @focus="isInputFocused = true"
                @blur="isInputFocused = false"
                @clear="handleSearch"
              >
                <template #prefix>
                  <el-icon class="search-input-icon">
                    <Search />
                  </el-icon>
                </template>
                <template #append>
                  <el-button
                    type="primary"
                    class="search-btn"
                    :loading="isLoading"
                    @click="handleSearch"
                  >
                    搜索
                  </el-button>
                </template>
              </el-input>
            </div>
          </form>
        </div>

        <div
          v-if="query"
          class="search-results"
        >
          <div class="search-summary">
            <h3>搜索结果</h3>
            <p>找到 <strong class="highlight-count">{{ totalResults }}</strong> 个相关结果</p>
          </div>

          <div
            v-if="results && Object.keys(results).length > 0"
            class="results-wrapper"
          >
            <div
              v-for="(items, category) in results"
              :key="category"
              class="result-category-card"
            >
              <div class="category-header">
                <el-icon class="category-icon">
                  <component :is="getCategoryIcon(category)" />
                </el-icon>
                <span class="category-name">{{ category }}</span>
                <span class="category-count">{{ items.length }}</span>
              </div>
              <div class="result-items">
                <div 
                  v-for="(item, index) in items" 
                  :key="`${category}-${index}`" 
                  class="result-item"
                  @click="handleItemClick(item)"
                >
                  <div class="result-content">
                    <h5 class="result-title">
                      <span
                        class="result-link"
                        v-html="highlightMatch(item.title)"
                      />
                    </h5>
                    <p
                      v-if="item.subtitle"
                      class="result-subtitle"
                    >
                      {{ item.subtitle }}
                    </p>
                  </div>
                  <div class="result-type">
                    <span class="type-badge">{{ item.type }}</span>
                    <el-icon class="arrow-icon">
                      <ArrowRight />
                    </el-icon>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div
            v-else
            class="no-results"
          >
            <div class="no-results-content">
              <el-icon class="no-results-icon">
                <Warning />
              </el-icon>
              <h3>没有找到相关结果</h3>
              <p>换个关键词试试看</p>
            </div>
          </div>
        </div>
        
        <div
          v-else
          class="empty-state"
        >
          <div class="empty-state-content">
            <el-icon class="empty-icon">
              <Grid />
            </el-icon>
            <h3>准备好搜索了吗？</h3>
            <p>输入关键词，探索实训室、用户、课程等信息</p>
          </div>
        </div>
      </div>
    </template>
  </Index>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi, useAuth } from '@/core/hooks'
import { decideRouteByActionType } from '@/core/utils/routeDecision'
import { getAccessibleFeatures } from '@/core/utils/searchFeatures'
import Index from '@/views/pc/dashboard/Index.vue'
import FlexSearch from 'flexsearch'
import { debounce } from 'lodash'
import { useNavigation } from '@/core/utils/routeDecision'

import { Search, HomeFilled, ArrowRight, OfficeBuilding, UserFilled, Reading, Document, Tools, Setting, Warning, Grid } from '@element-plus/icons-vue'

export default {
  name: 'GlobalSearch',
  components: {
    Index,
    Search,
    HomeFilled,
    ArrowRight,
    OfficeBuilding, UserFilled, Reading, Document, Tools, Setting, Warning, Grid
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const { goHome } = useNavigation()
    
    const { user, logout } = useAuth()
    const { get: searchApi } = useApi('/common/search/', { immediate: false })
    
    const query = ref('')
    const results = ref({})
    const totalResults = ref(0)
    const isLoading = ref(false)
    const isInputFocused = ref(false)

    // FlexSearch 索引实例
    let featureIndex = null

    // 初始化搜索索?
    const initSearchIndex = () => {
      if (!user.value) return

      // 创建 Document 索引
      featureIndex = new FlexSearch.Document({
        document: {
          id: 'id',
          index: ['title', 'subtitle', 'aliases'],
          store: true
        },
        tokenize: 'forward', // 前向匹配，支持部分输?
        cache: true
      })

      // 获取当前用户可访问的功能列表
      const features = getAccessibleFeatures(user.value)
      
      // 添加到索?
      features.forEach(feature => {
        featureIndex.add(feature)
      })
    }

    // 监听用户状态变化，重新初始化索?
    watch(user, () => {
      initSearchIndex()
    }, { immediate: true })

    // 执行前端功能搜索
    const searchFeatures = async (q) => {
      if (!featureIndex) initSearchIndex()
      if (!featureIndex) return [] // 如果还没有索引（例如未登录），返回空

      // 执行搜索
      const searchResult = await featureIndex.searchAsync(q, {
        limit: 10,
        enrich: true, // 获取完整文档内容
        bool: "or" // 任意字段匹配即可
      })

      // FlexSearch Document 搜索返回的是按字段分组的结果
      // 格式: [{ field: 'title', result: [...] }, { field: 'aliases', result: [...] }]
      // 需要合并去?
      const uniqueDocs = new Map()
      
      searchResult.forEach(fieldResult => {
        fieldResult.result.forEach(item => {
          // item.doc 是存储的文档对象
          if (!uniqueDocs.has(item.doc.id)) {
            uniqueDocs.set(item.doc.id, item.doc)
          }
        })
      })

      // 二次过滤：确保结果符合特定的业务规则（如单字符前缀匹配?
      // 解决 FlexSearch 有时返回不相关结果的问题
      const filteredResults = Array.from(uniqueDocs.values()).filter(item => {
        const qLower = q.toLowerCase()
        
        // 1. 特殊规则：如果是单个字母或数字，强制要求前缀匹配
        // 防止输入 "2" 显示 "修改密码" 这种不相关结?
        if (q.length === 1 && /^[a-zA-Z0-9]$/.test(q)) {
          // 检查标题前缀
          if (item.title && item.title.toLowerCase().startsWith(qLower)) return true
          // 检查别名前缀
          if (item.aliases && item.aliases.some(alias => alias.toLowerCase().startsWith(qLower))) return true
          
          return false
        }
        
        // 2. 常规规则：只?FlexSearch 匹配了，通常是相关的
        // 但为了保险，可以再次验证包含关系 (可选，FlexSearch �?tokenize: 'forward' 已经做得不错?
        // 这里我们信任 FlexSearch 的多字符匹配，只对单字符做严格限?
        return true
      })

      return filteredResults
    }

    const getCategoryIcon = (category) => {
      const icons = {
        '实训室': 'OfficeBuilding',
        '用户': 'UserFilled',
        '课表': 'Reading',
        '使用记录': 'Document',
        '维护记录': 'Tools',
        '功能': 'Setting'
      }
      return icons[category] || 'Grid'
    }


    // 完全前后端分离：根据业务标识决定路由
    const getItemUrl = (item) => {
      // 1. 处理 'navigate' 类型的功能导?
      if (item.action_type === 'navigate' && item.resource_type) {
        const route = decideRouteByActionType('navigate', item.resource_type, {}, {})
        return route || '#'
      }

      // 2. 处理后端返回的业务数?(action_type可能为空，默认为 'view' �?'detail')
      // 后端返回的结? { id, title, subtitle, resource_type, action_type, context: {...} }
      if (item.resource_type) {
        const actionType = item.action_type || 'view'
        // 合并 item 中的所有属性作?context，确?id/resource_id 等关键信息存?
        const context = {
          ...item,
          ...item.context,
          resource_id: item.id || item.resource_id
        }
        
        const route = decideRouteByActionType(actionType, item.resource_type, context, {})
        return route || '#'
      }
      
      return '#'
    }

    const handleItemClick = async (item) => {
      if (item?.resource_type === 'logout') {
        try {
          await logout({ redirectToLogin: true })
          return
        } catch (e) {
          router.push('/login')
          return
        }
      }
      
      const url = getItemUrl(item)
      
      if (url && url !== '#') {
        try {
          await router.push(url)
        } catch (err) {
          window.location.href = url
        }
      }
    }

    const handleSearch = () => {
      // 更新 URL query 参数，但不刷新页?
      router.replace({ query: { ...route.query, q: query.value } })
      loadResults()
    }

    // 实时搜索 (防抖)
    const onInput = debounce(() => {
      handleSearch()
    }, 300)

    // 关键词高?
    const highlightMatch = (text) => {
      if (!query.value || !text) return text
      
      // HTML 转义函数，防?XSS
      const escapeHtml = (unsafe) => {
        return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
      }

      // 先对整个文本进行转义
      const safeText = escapeHtml(text)
      
      // 对查询词也进行转义，以便匹配转义后的文本
      // 注意：这可能无法完美匹配原始HTML字符（如查询 '<'），但在纯文本搜索场景下通常足够
      const safeQuery = escapeHtml(query.value)
      
      const q = safeQuery.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') // escape regex
      return safeText.replace(new RegExp(`(${q})`, 'gi'), '<span class="highlight-text">$1</span>')
    }

    const loadResults = async () => {
      if (!query.value) {
        results.value = {}
        totalResults.value = 0
        return
      }

      isLoading.value = true
      try {
        // 并行执行：后端搜索（DB数据?+ 前端搜索（功能菜单）
        const [backendResponse, featureResults] = await Promise.all([
          searchApi({ keyword: query.value }),
          searchFeatures(query.value)
        ])

        let combinedResults = {}
        let count = 0

        // 1. 处理后端结果 (排除后端返回?功能'，改用前端FlexSearch结果)
        if (backendResponse && backendResponse.results) {
          const { 功能, ...otherResults } = backendResponse.results
          combinedResults = { ...otherResults }
          
          // 计算后端结果数量
          Object.values(combinedResults).forEach(arr => count += arr.length)
        }

        // 2. 添加前端FlexSearch的功能搜索结?
        if (featureResults && featureResults.length> 0) {
          combinedResults['功能'] = featureResults.map(item => ({
            ...item,
            type: '功能'
          }))
          count += featureResults.length
        }

        results.value = combinedResults
        totalResults.value = count

      } catch (err) {
        // 即使后端失败，如果前端搜索有结果，也可以显示
        try {
          const featureResults = await searchFeatures(query.value)
          if (featureResults && featureResults.length> 0) {
            results.value = {
              '功能': featureResults.map(item => ({ ...item, type: '功能' }))
            }
            totalResults.value = featureResults.length
          } else {
            results.value = {}
            totalResults.value = 0
          }
        } catch (e) {
          results.value = {}
          totalResults.value = 0
        }
      } finally {
        isLoading.value = false
      }
    }

    // 监听路由参数变化，实现与左侧侧边栏搜索框的同?
    watch(() => route.query.q, (newQ) => {
      if (newQ !== undefined && newQ !== query.value) {
        query.value = newQ
        loadResults()
      }
    })

    onMounted(() => {
      query.value = route.query.q || ''
      if (query.value) {
        loadResults()
      }
    })

    return {
      query,
      results,
      totalResults,
      isLoading,
      getCategoryIcon,
      getItemUrl,
      handleItemClick,
      handleSearch,
      onInput,
      goHome,
      user,
      isInputFocused,
      highlightMatch
    }
  }
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-title {
  font-size: 20px;
  font-weight: 600;
  color: #1f2d3d;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  letter-spacing: 0.5px;
}

.header-icon {
  font-size: 24px;
  color: #1890ff;
  animation: float 3s ease-in-out infinite;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.search-container {
    max-width: 900px;
    margin: 0 auto;
    padding: 20px 20px 60px;
}

.search-box-section {
    margin-bottom: 40px;
    position: sticky;
    top: 0;
    z-index: 100;
    padding-top: 20px;
    background: transparent;
}

.search-form {
    display: flex;
    justify-content: center;
}

.search-input-group {
    display: flex;
    width: 100%;
    max-width: 500px;
    background: white;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
    border-radius: 8px;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    border: 1px solid #dcdfe6;
}

.search-input-group.is-focused {
    box-shadow: 0 8px 24px rgba(24, 144, 255, 0.15);
    transform: translateY(-1px);
    border-color: #409eff;
}

.search-input-el :deep(.el-input__wrapper) {
    box-shadow: none !important;
    background: transparent;
    padding: 4px 12px;
    font-size: 14px;
}

.search-input-el :deep(.el-input__inner) {
    height: 40px;
    color: #303133;
}

.search-input-icon {
    font-size: 18px;
    color: #909399;
    margin-right: 6px;
}

.search-btn {
    height: 100% !important;
    padding: 0 20px !important;
    font-size: 14px !important;
    font-weight: 500;
    border-radius: 0 8px 8px 0 !important;
    background: var(--el-color-primary);
    border: none;
    transition: all 0.3s;
}

.search-btn:hover {
    opacity: 0.9;
    transform: scale(1.02);
}

.search-results {
    animation: fadeIn 0.5s ease;
}

.search-summary {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #ebeef5;
    padding-bottom: 15px;
    margin-bottom: 25px;
}

.search-summary h3 {
    margin: 0;
    font-size: 20px;
    color: #303133;
    font-weight: 600;
}

.search-summary p {
    margin: 0;
    color: #909399;
    font-size: 14px;
}

.highlight-count {
    color: #1890ff;
    font-size: 16px;
    margin: 0 2px;
}

.result-category-card {
    background: white;
    border-radius: 16px;
    padding: 0;
    margin-bottom: 30px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    border: 1px solid #f0f0f0;
    overflow: hidden;
    transition: all 0.3s;
}

.result-category-card:hover {
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
}

.category-header {
    display: flex;
    align-items: center;
    padding: 16px 24px;
    background: #fafafa;
    border-bottom: 1px solid #f0f0f0;
}

.category-icon {
  font-size: 24px;
  margin-right: 12px;
  color: #1890ff;
}

.category-name {
    font-size: 18px;
    font-weight: 600;
    color: #303133;
    flex: 1;
}

.category-count {
    background: #e6f7ff;
    color: #1890ff;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
}

.result-items {
    padding: 12px;
}

.result-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.2s ease;
    border: 1px solid transparent;
    margin-bottom: 8px;
}

.result-item:hover {
    background: #f0f9eb;
    transform: translateX(5px);
    border-color: #e1f3d8;
}

.result-content {
    flex: 1;
    min-width: 0; /* fix text overflow */
}

.result-title {
    margin: 0 0 6px 0;
    font-size: 16px;
    font-weight: 600;
    color: #303133;
}

.result-link {
    color: #303133;
    transition: color 0.2s;
}

.result-item:hover .result-link {
    color: #1890ff;
}

.result-subtitle {
    margin: 0;
    color: #909399;
    font-size: 13px;
    line-height: 1.4;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.result-type {
    margin-left: 20px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.type-badge {
    background: #f2f6fc;
    color: #909399;
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 500;
}

.arrow-icon {
    color: #c0c4cc;
    font-size: 16px;
    transition: transform 0.2s;
}

.result-item:hover .arrow-icon {
    transform: translateX(3px);
    color: #1890ff;
}

.no-results, .empty-state {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 400px;
    text-align: center;
}

.no-results-content, .empty-state-content {
    animation: fadeInUp 0.5s ease;
}

.no-results-icon, .empty-icon {
  font-size: 80px;
  margin-bottom: 24px;
  display: inline-block;
  color: #c0c4cc;
}

.no-results h3, .empty-state h3 {
    font-size: 24px;
    color: #303133;
    margin: 0 0 12px 0;
}

.no-results p, .empty-state p {
    color: #909399;
    font-size: 16px;
    margin: 0;
}

:deep(.highlight-text) {
    color: #f56c6c;
    font-weight: bold;
    background: rgba(245, 108, 108, 0.1);
    padding: 0 2px;
    border-radius: 2px;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes fadeInUp {
    from { 
        opacity: 0;
        transform: translateY(20px);
    }
    to { 
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-6px); }
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .page-header {
        padding: 0 20px;
        flex-direction: column;
        gap: 16px;
        align-items: flex-start;
    }
    
    .header-actions {
        width: 100%;
        justify-content: space-between;
    }
    
    .search-input-group {
        max-width: 100%;
    }
    
    .result-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 12px;
    }
    
    .result-type {
        margin-left: 0;
        width: 100%;
        justify-content: space-between;
    }
}
</style>
