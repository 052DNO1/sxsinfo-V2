<template>
  <Index class="pc-layout">
    <template #rightcontent>
      <div class="page-container">
        <!-- 头部区域 -->
        <div class="listheader custom-header">
          <slot name="header">
            <span class="header-text">
              <el-icon v-if="icon"><component :is="icon" /></el-icon>
              {{ title || '填写信息' }}
            </span>
          </slot>
          
          <div
            v-if="$slots['header-center']"
            class="header-center"
          >
            <slot name="header-center" />
          </div>

          <div class="listheader-actions">
            <slot name="header-actions" />
            <el-button
              v-if="showBack"
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

        <!-- 主体面板布局 -->
        <div class="unified-panel-layout">
          <div class="unified-panel">
            <!-- 左侧指南区域 -->
            <div
              v-if="showSide"
              class="panel-side"
            >
              <div class="side-header">
                <h3><el-icon><InfoFilled /></el-icon> {{ guideTitle || '操作指南' }}</h3>
                <p>{{ guideSubTitle || '请按照提示进行操作' }}</p>
              </div>

              <div class="side-content">
                <div
                  v-if="guideSteps && guideSteps.length"
                  class="side-block"
                >
                  <div class="block-title">
                    流程步骤
                  </div>
                  <div class="guide-list">
                    <div
                      v-for="(step, index) in guideSteps"
                      :key="index"
                      class="guide-item"
                    >
                      <div class="guide-icon">
                        {{ index + 1 }}
                      </div>
                      <div class="guide-text">
                        <h4>{{ step.title }}</h4>
                        <p>{{ step.description }}</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div
                  v-if="tips && tips.length"
                  class="side-block tips-block"
                >
                  <div class="block-title">
                    <el-icon><QuestionFilled /></el-icon> {{ tipsTitle || '温馨提示' }}
                  </div>
                  <ul class="tips-list">
                    <li
                      v-for="(tip, index) in tips"
                      :key="index"
                    >
                      {{ tip }}
                    </li>
                  </ul>
                </div>
                
                <slot name="side-extra" />
              </div>
            </div>

            <!-- 右侧表单主区域 -->
            <div class="panel-main">
              <div
                v-if="showMainHeader"
                class="main-header"
              >
                <h3>
                  <el-icon v-if="mainIcon">
                    <component :is="mainIcon" />
                  </el-icon>
                  {{ mainTitle || title }}
                </h3>
              </div>

              <div class="main-content">
                <div
                  v-if="loading"
                  class="loading-container"
                >
                  <el-skeleton
                    :rows="8"
                    animated
                  />
                </div>
                <slot v-else />
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </Index>
</template>

<script setup>
import { useNavigation } from '@/core/utils/routeDecision'
import Index from '@/views/pc/dashboard/Index.vue'
import { InfoFilled, QuestionFilled } from '@element-plus/icons-vue'

const props = defineProps({
  title: String,
  icon: [String, Object],
  mainTitle: String,
  mainIcon: [String, Object],
  showSide: { type: Boolean, default: true },
  showMainHeader: { type: Boolean, default: true },
  showBack: { type: Boolean, default: true },
  guideTitle: String,
  guideSubTitle: String,
  guideSteps: { type: Array, default: () => [] },
  tipsTitle: String,
  tips: { type: Array, default: () => [] },
  loading: Boolean
})

const { goHome, smartBack } = useNavigation()
</script>

<style scoped>
.page-container {
  padding: 20px;
  max-width: 100%;
}

.custom-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0;
}

.header-text {
  font-weight: bold;
  font-size: 18px;
  color: #1a1a1a;
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.listheader-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.unified-panel-layout {
  display: flex;
  justify-content: center;
  padding: 0;
  min-height: auto;
}

.unified-panel {
  width: 100%;
  max-width: 1600px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.06);
  border: 1px solid #ebeef5;
  display: flex;
  overflow: hidden;
  height: calc(100vh - 140px);
  max-height: 700px;
  min-height: 500px;
  margin-top: 10px;
}

.panel-side {
  flex: 0 0 400px;
  background-color: #f8f9fb;
  border-right: 1px solid #eef0f5;
  display: flex;
  flex-direction: column;
}

.side-header {
  padding: 24px 24px 16px;
  border-bottom: 1px solid #eef0f5;
}

.side-header h3 {
  margin: 0 0 6px;
  font-size: 18px;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.side-header p {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

.side-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.side-block {
  display: flex;
  flex-direction: column;
}

.block-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 10px;
}

.guide-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.guide-item {
  display: flex;
  gap: 16px;
}

.guide-icon {
  width: 28px;
  height: 28px;
  background: #e6e8eb;
  color: #606266;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
}

.guide-text h4 {
  margin: 0 0 4px 0;
  font-size: 15px;
  color: #303133;
  font-weight: 600;
}

.guide-text p {
  margin: 0;
  font-size: 13px;
  color: #909399;
  line-height: 1.4;
}

.tips-block {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
}

.tips-list {
  margin: 0;
  padding-left: 18px;
  font-size: 13px;
  color: #606266;
}

.tips-list li {
  margin-bottom: 6px;
  line-height: 1.5;
}

.panel-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #fff;
  overflow-y: auto;
}

.main-header {
  padding: 24px 32px;
  border-bottom: 1px solid #f5f7fa;
  flex-shrink: 0;
}

.main-header h3 {
  margin: 0;
  font-size: 20px;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 10px;
}

.main-content {
  flex: 1;
  padding: 32px;
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
}

.loading-container {
  padding: 20px 0;
}

@media (max-width: 992px) {
  .unified-panel {
    flex-direction: column;
    height: auto;
    max-height: none;
  }
  
  .panel-side {
    flex: none;
    width: 100%;
    border-right: none;
    border-bottom: 1px solid #eef0f5;
  }
  
  .guide-list {
    flex-direction: row;
    flex-wrap: wrap;
    gap: 20px;
  }
  
  .guide-item {
    flex: 1;
    min-width: 200px;
  }
  
  .main-content {
    padding: 20px;
  }
}
</style>
