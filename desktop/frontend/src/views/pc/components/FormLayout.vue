<template>
  <Index class="pc-layout">
    <template #rightcontent>
      <div class="page-container">
        <!-- 头部：与列表页工具条同一套节奏（左对齐标题 + 1px 底边线 + 16px 间距） -->
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

<!--
  桌面化重做（只改视觉，模板与 props 一个没动）：
  - 头部左对齐、16px 加粗、下方 1px 细线 —— 与列表页工具条同一套节奏；
  - 面板去掉 16px 大圆角与 8px/30px 大扩散阴影，改成 1px 细边框；
  - 去掉 height: calc(100vh - 140px) + max-height: 700px 这种"固定高度悬浮盒"，
    高度交给内容（页面自己滚动），这是网页后台最典型的做法；
  - 左侧指南栏收窄到 320px、灰底更浅、步骤序号改成小方牌；
  - 表单内容左对齐、限宽 760px（桌面表单的阅读宽度），不再居中悬浮。
-->
<style scoped>
.page-container {
  /* 外层 el-main 已有 24px 内边距，这里不再叠加 */
  padding: 0;
  max-width: 100%;
}

.custom-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding-bottom: 16px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--lims-border, #e5e7eb);
}

.header-text {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary, #1f2937);
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.listheader-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.unified-panel-layout {
  display: flex;
  justify-content: flex-start;
}

/* 面板：细边框 + 8px 圆角，不再"浮"在页面上 */
.unified-panel {
  width: 100%;
  max-width: none;
  background: var(--el-bg-color, #fff);
  border: 1px solid var(--el-border-color-lighter, #f3f4f6);
  border-radius: 8px;
  box-shadow: none;
  display: flex;
  overflow: hidden;
  /* 高度由内容决定；不再锁死 100vh-140px / max-height 700px */
  height: auto;
  min-height: 0;
  margin-top: 0;
}

.panel-side {
  flex: 0 0 320px;
  background-color: #fafbfc;
  border-right: 1px solid var(--el-border-color-lighter, #f3f4f6);
  display: flex;
  flex-direction: column;
}

.side-header {
  padding: 16px 20px 12px;
  border-bottom: 1px solid var(--el-border-color-lighter, #f3f4f6);
}

.side-header h3 {
  margin: 0 0 4px;
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary, #1f2937);
  display: flex;
  align-items: center;
  gap: 6px;
}

.side-header p {
  margin: 0;
  font-size: 12.5px;
  color: var(--el-text-color-secondary, #6b7280);
}

.side-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.side-block {
  display: flex;
  flex-direction: column;
}

.block-title {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.3px;
  color: var(--el-text-color-secondary, #6b7280);
  margin-bottom: 10px;
}

.guide-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.guide-item {
  display: flex;
  gap: 10px;
}

/* 步骤序号：小方牌（桌面工具里的编号样式），不再是灰色大圆点 */
.guide-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  border-radius: 4px;
  background: var(--el-fill-color-light, #f5f6f8);
  border: 1px solid var(--el-border-color-lighter, #f3f4f6);
  color: var(--el-text-color-secondary, #6b7280);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
}

.guide-text h4 {
  margin: 0 0 2px;
  font-size: 13px;
  font-weight: 500;
  color: var(--el-text-color-primary, #1f2937);
}

.guide-text p {
  margin: 0;
  font-size: 12.5px;
  color: var(--el-text-color-secondary, #6b7280);
  line-height: 1.5;
}

.tips-block {
  background: var(--el-bg-color, #fff);
  border: 1px solid var(--el-border-color-lighter, #f3f4f6);
  border-radius: 6px;
  padding: 12px 14px;
}

.tips-list {
  margin: 0;
  padding-left: 16px;
  font-size: 12.5px;
  color: var(--el-text-color-regular, #333);
}

.tips-list li {
  margin-bottom: 4px;
  line-height: 1.5;
}

.panel-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  background-color: var(--el-bg-color, #fff);
}

.main-header {
  padding: 14px 24px;
  border-bottom: 1px solid var(--el-border-color-lighter, #f3f4f6);
  flex-shrink: 0;
}

.main-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary, #1f2937);
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 表单内容：左对齐 + 760px 阅读宽度（桌面表单惯例，不再居中悬浮） */
.main-content {
  flex: 1;
  width: 100%;
  max-width: 760px;
  margin: 0;
  padding: 24px;
}

.loading-container {
  padding: 12px 0;
}

@media (max-width: 992px) {
  .unified-panel {
    flex-direction: column;
  }

  .panel-side {
    flex: none;
    width: 100%;
    border-right: none;
    border-bottom: 1px solid var(--el-border-color-lighter, #f3f4f6);
  }

  .guide-list {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .guide-item {
    flex: 1;
    min-width: 200px;
  }

  .main-content {
    padding: 16px;
  }
}
</style>
