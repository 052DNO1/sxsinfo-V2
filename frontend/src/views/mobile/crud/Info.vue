<template>
  <div class="mobile-page">
    <van-nav-bar
      :title="msg?.title || (isErrorMode ? '错误' : '成功')"
      left-arrow
      @click-left="goBack"
    >
      <template #right>
        <van-icon
          name="home-o"
          size="20"
          @click="goHome"
        />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <div class="result-container">
        <van-icon
          :name="isErrorMode ? 'cross' : 'passed'"
          :color="isErrorMode ? '#ee0a24' : '#07c160'"
          size="80"
        />
        <h2 class="result-title">
          {{ msg?.title || (isErrorMode ? '操作失败' : '操作成功') }}
        </h2>
        <p class="result-message">
          {{ msg?.message || '' }}
        </p>
      </div>

      <van-cell-group
        v-if="msg?.links && msg.links.length > 0"
        inset
      >
        <van-cell
          v-for="(link, index) in msg.links"
          :key="index"
          :title="link.text"
          is-link
          @click="() => window.location.href = link.url"
        />
      </van-cell-group>

      <van-cell-group
        v-if="msg?.errdata && msg.errdata.length > 0"
        inset
        title="错误详情"
      >
        <van-cell
          v-for="(item, index) in msg.errdata"
          :key="index"
          :title="`行 ${item[0]}`"
          :label="item[2]"
        >
          <template #value>
            <span class="error-preview">{{ item[1] }}</span>
          </template>
        </van-cell>
      </van-cell-group>

      <van-cell-group
        v-if="msg?.details && msg.details.length > 0"
        inset
        title="详情列表"
      >
        <van-cell
          v-for="(item, index) in msg.details"
          :key="index"
          :title="item.name"
          :label="item.extra"
          is-link
          @click="() => window.location.href = item.url"
        >
          <template #icon>
            <van-tag
              :type="item.type === 'error' ? 'danger' : 'primary'"
              size="small"
            >
              {{ item.type }}
            </van-tag>
          </template>
        </van-cell>
      </van-cell-group>

      <div class="form-actions">
        <van-button
          type="default"
          block
          @click="smartBack"
        >
          返回
        </van-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from '@/core/hooks'
import { useNavigation } from '@/core/utils/routeDecision'

const route = useRoute()
const router = useRouter()
const { get: fetchInfoApi } = useApi('', { immediate: false })
const { smartBack, goHome } = useNavigation()

const msg = ref({})
const preUrl = ref('')
const pama = ref('')
const backUrl = ref('')

const isErrorMode = computed(() => {
  if (route.path.includes('/error')) return true
  const title = msg.value?.title || ''
  return ['错误', '失败', '异常'].some(keyword => title.includes(keyword))
})

const loadData = async () => {
  try {
    let apiPath = route.path
    if (!apiPath.startsWith('/')) apiPath = '/' + apiPath
    const response = await fetchInfoApi(route.query, { url: apiPath })
    msg.value = response.msg || {}
    preUrl.value = response.preurl || ''
    pama.value = response.pama || ''
    backUrl.value = response.backurl || ''
  } catch (err) {
    msg.value = {
      title: '错误',
      message: '加载信息失败：' + (err.message || '未知错误')
    }
  }
}

const goBack = () => {
  if (preUrl.value) {
    if (pama.value) {
      router.push({ name: preUrl.value, params: { id: pama.value } })
    } else {
      router.push({ name: preUrl.value })
    }
  } else if (backUrl.value) {
    window.location.href = backUrl.value
  } else {
    smartBack()
  }
}

onMounted(loadData)
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

.result-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
  background: #fff;
  border-radius: 12px;
  margin-bottom: 16px;
}

.result-title {
  font-size: 20px;
  font-weight: 600;
  color: #323233;
  margin: 16px 0 8px;
}

.result-message {
  font-size: 14px;
  color: #969799;
  text-align: center;
  white-space: pre-line;
}

.error-preview {
  font-size: 12px;
  color: #969799;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.form-actions {
  padding: 16px;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
}
</style>
