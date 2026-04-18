<template>
  <div class="mobile-info-container mobile-layout">
    <van-nav-bar
      :title="msg?.title || (isErrorMode ? '错误' : '成功')"
      left-arrow
      @click-left="goBack"
      class="mobile-nav-bar"
    >
      <template #left>
        <van-icon name="arrow-left" />
      </template>
    </van-nav-bar>

    <div class="mobile-info-content">
      <div :class="['info-title', isErrorMode ? 'error-title' : 'success-title']">
        <van-icon 
          :name="isErrorMode ? 'close' : 'success'" 
          size="20px" 
          :color="isErrorMode ? '#ee0a24' : '#07c160'"
          style="margin-right: 8px;"
        />
        {{ msg?.title || (isErrorMode ? '错误' : '成功') }}
      </div>
      
      <div class="info-message" style="white-space: pre-line;">
        {{ msg?.message || '' }}
      </div>

      <div v-if="msg?.links && msg.links.length > 0" class="info-actions">
        <van-button
          v-for="(link, index) in msg.links"
          :key="index"
          type="primary"
          block
          @click="() => window.location.href = link.url"
          style="margin-bottom: 12px;"
        >
          {{ link.text }}
        </van-button>
      </div>

      <div v-if="msg?.errdata && msg.errdata.length > 0" class="error-table-section">
        <div class="section-title">
          <van-icon name="description" size="16px" style="margin-right: 4px;" />
          错误详情
        </div>
        <van-cell-group inset>
          <van-cell
            v-for="(err, index) in msg.errdata"
            :key="index"
            :title="`行号: ${err[0]}`"
            :label="`错误: ${err[2]}`"
          >
            <template #value>
              <div style="font-size: 12px; color: #969799;">{{ err[1] }}</div>
            </template>
          </van-cell>
        </van-cell-group>
      </div>

      <div v-if="msg?.details && msg.details.length > 0" class="error-detail-section">
        <div class="section-title">
          <van-icon name="description" size="16px" style="margin-right: 4px;" />
          错误详情列表
        </div>
        <van-cell-group inset>
          <van-cell
            v-for="(detail, index) in msg.details"
            :key="index"
            :title="detail.name"
            :label="`${detail.type} - ${detail.extra}`"
            is-link
            @click="() => window.location.href = detail.url"
          />
        </van-cell-group>
        <div style="padding: 12px; color: #969799; font-size: 12px;">
          仅显示前10条，更多请通过上方的入口链接查看。
        </div>
      </div>

      <div class="info-actions" style="margin-top: 24px;">
        <template v-if="preUrl">
          <van-button
            type="primary"
            block
            @click="handleRouteBack"
            style="margin-bottom: 12px;"
          >
            <van-icon name="arrow-left" size="16px" style="margin-right: 4px;" />
            返回
          </van-button>
        </template>

        <van-button
          v-if="backUrl && !preUrl"
          type="primary"
          block
          @click="() => window.location.href = backUrl"
          style="margin-bottom: 12px;"
        >
          <van-icon name="arrow-left" size="16px" style="margin-right: 4px;" />
          返回
        </van-button>

        <template v-if="!preUrl && !backUrl">
          <van-button
            type="default"
            block
            @click="goBack"
            style="margin-bottom: 12px;"
          >
            <van-icon name="arrow-left" size="16px" style="margin-right: 4px;" />
            返回
          </van-button>
          <van-button
            type="primary"
            block
            @click="() => router.push('/')"
          >
            <van-icon name="home-o" size="16px" style="margin-right: 4px;" />
            回到首页
          </van-button>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/utils/api'
import { useMobile } from '@/composables/useMobile'

export default {
  name: 'Info',
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    const msg = ref({})
    const preUrl = ref('')
    const pama = ref('')
    const backUrl = ref('')

    const { loadVantComponents, init: initMobile } = useMobile()

    const isErrorMode = computed(() => {
      if (route.path === '/error') return true
      const title = msg.value?.title || ''
      return ['错误', '失败', '异常'].some(keyword => title.includes(keyword))
    })

    const goBack = () => router.go(-1)

    const handleRouteBack = () => {
      if (pama.value) {
        router.push({ name: preUrl.value, params: { id: pama.value } })
      } else {
        router.push({ name: preUrl.value })
      }
    }

    const loadData = async () => {
      try {
        const response = await api.get(route.path, { params: route.query })
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

    onMounted(() => {
      const cleanupMobile = initMobile()
      setTimeout(() => {
        loadVantComponents()
      }, 200)
      loadData()
    })

    return {
      msg,
      preUrl,
      pama,
      backUrl,
      isErrorMode,
      goBack,
      handleRouteBack,
      router
    }
  }
}
</script>


/* mobile.css 已在 main.js 中统一导入 */

.mobile-info-container {
  min-height: 100vh;
  background: #f7f8fa;
  padding-bottom: 20px;
}

.mobile-info-content {
  padding: 16px;
}

.info-title {
  font-size: 20px;
  font-weight: 600;
  text-align: center;
  margin-bottom: 16px;
  padding: 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.success-title {
  color: #07c160;
  background: #f0f9ff;
}

.error-title {
  color: #ee0a24;
  background: #fef2f2;
}

.info-message {
  font-size: 15px;
  line-height: 1.6;
  color: #323233;
  padding: 16px;
  background: #ffffff;
  border-radius: 8px;
  margin-bottom: 16px;
}

.info-actions {
  padding: 0;
}

.error-table-section,
.error-detail-section {
  margin-top: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #323233;
  margin-bottom: 12px;
  padding: 0 4px;
  display: flex;
  align-items: center;
}
