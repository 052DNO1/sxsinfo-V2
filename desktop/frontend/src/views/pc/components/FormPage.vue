<!-- 通用表单页面 -->
<template>
  <div class="modern-form-container">
    <div class="modern-form-panel">
      <div class="form-header">
        <div
          v-if="showBackButton"
          class="header-actions"
        >
          <el-button
            class="nav-action-btn"
            plain
            @click="$emit('back')"
          >
            <el-icon class="el-icon--left">
              <ArrowLeft />
            </el-icon> 返回
          </el-button>
        </div>
        
        <div
          v-if="icon"
          class="form-icon"
        >
          {{ icon }}
        </div>
        <h2 class="form-title">
          {{ title }}
        </h2>
        <p
          v-if="description"
          class="form-description"
        >
          {{ description }}
        </p>
        
        <div
          v-if="$slots.extra"
          class="form-extra"
        >
          <slot name="extra" />
        </div>
      </div>
      
      <div class="form-content">
        <slot />
      </div>
    </div>
  </div>
</template>

<script>
import { ArrowLeft } from '@element-plus/icons-vue'

export default {
  name: 'FormPage',
  components: {
    ArrowLeft
  },
  props: {
    title: {
      type: String,
      required: true
    },
    icon: {
      type: String,
      default: ''
    },
    description: {
      type: String,
      default: ''
    },
    showBackButton: {
      type: Boolean,
      default: true
    }
  },
  emits: ['back']
}
</script>

<!--
  桌面化重做（模板与 props 未改动）：
  - 去掉 1200px 居中悬浮的白卡片（16px 圆角 + 10px/40px 大阴影 + 悬停浮起）；
    表单直接铺在内容区白底上，与列表页、设置页保持同一种"平铺"观感；
  - 标题 28px 居中 → 16px 左对齐，描述 16px → 13px；
  - 返回按钮不再绝对定位浮在角落，改为标题上方的常规流程元素；
  - 那个 80px 的渐变圆形图标位（字符串图标）收成 20px 的行内小图标，不再抢视线；
  - extra 插槽由居中改为左对齐。
-->
<style scoped>
.modern-form-container {
  max-width: none;
  margin: 0;
  padding: 0;
  display: block;
}

.modern-form-panel {
  width: 100%;
  max-width: 880px;
  background: transparent;
  border: 0;
  border-radius: 0;
  box-shadow: none;
  padding: 0;
  transition: none;
  position: relative;
}

/* 头部：左对齐标题 + 1px 底边线，与列表页工具条同一节奏 */
.form-header {
  text-align: left;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--lims-border, #e5e7eb);
  position: relative;
}

.header-actions {
  position: static;
  margin-bottom: 10px;
  display: flex;
  gap: 8px;
}

/* 图标位：从 80px 渐变圆球收成行内小图标 */
.form-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  width: auto;
  height: auto;
  line-height: 1;
  margin: 0 8px 0 0;
  background: transparent;
  border-radius: 0;
  box-shadow: none;
  color: var(--el-color-primary, #1890ff);
  vertical-align: middle;
}

.form-title {
  display: inline-block;
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary, #1f2937);
  margin: 0 0 4px;
  letter-spacing: 0;
  vertical-align: middle;
}

.form-description {
  margin: 0;
  font-size: 13px;
  color: var(--el-text-color-secondary, #6b7280);
  line-height: 1.5;
}

.form-extra {
  margin-top: 12px;
  display: flex;
  justify-content: flex-start;
  gap: 8px;
}

.form-content {
  padding: 0;
}

@media (max-width: 768px) {
  .modern-form-panel {
    max-width: none;
    padding: 0;
  }

  .form-title {
    font-size: 15px;
  }
}
</style>
