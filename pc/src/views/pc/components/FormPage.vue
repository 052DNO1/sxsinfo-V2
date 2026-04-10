<!-- 通用表单页面 -->
<template>
  <div class="modern-form-container">
    <div class="modern-form-panel">
      <div class="form-header">
        <div class="header-actions" v-if="showBackButton">
          <el-button class="nav-action-btn" plain @click="$emit('back')">
            <el-icon class="el-icon--left"><ArrowLeft /></el-icon> 返回
          </el-button>
        </div>
        
        <div class="form-icon" v-if="icon">{{ icon }}</div>
        <h2 class="form-title">{{ title }}</h2>
        <p class="form-description" v-if="description">{{ description }}</p>
        
        <div class="form-extra" v-if="$slots.extra">
           <slot name="extra"></slot>
        </div>
      </div>
      
      <div class="form-content">
        <slot></slot>
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

<style scoped>
.modern-form-container {
  max-width: 1600px;
  margin: 30px auto;
  padding: 0 20px;
  display: flex;
  justify-content: center;
}

.modern-form-panel {
  width: 100%;
  max-width: 1200px; /* Default max width, can be overridden by parent content */
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.04);
  padding: 40px;
  border: 1px solid rgba(0, 0, 0, 0.02);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  position: relative;
}

.modern-form-panel:hover {
  box-shadow: 0 15px 50px rgba(0, 0, 0, 0.06);
}

.form-header {
  text-align: center;
  margin-bottom: 40px;
  position: relative;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f2f5;
}

.header-actions {
  position: absolute;
  left: 0;
  top: 0;
}

.back-btn {
  font-size: 16px;
  color: #606266;
}

.back-btn:hover {
  color: #409eff;
}

.form-icon {
  font-size: 48px;
  margin-bottom: 16px;
  display: inline-block;
  background: #f0f7ff;
  width: 80px;
  height: 80px;
  line-height: 80px;
  border-radius: 50%;
  color: #1c6cd4;
  box-shadow: 0 4px 15px rgba(28, 108, 212, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: auto;
  margin-right: auto;
}

.form-title {
  font-size: 28px;
  color: #2c3e50;
  margin: 0 0 10px;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.form-description {
  color: #7f8c8d;
  font-size: 16px;
  margin: 0;
  line-height: 1.5;
}

.form-extra {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 15px;
}

.form-content {
  padding: 10px 0;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .modern-form-container {
    padding: 10px;
    margin: 10px auto;
  }
  
  .modern-form-panel {
    padding: 20px;
  }
  
  .form-icon {
    width: 60px;
    height: 60px;
    line-height: 60px;
    font-size: 32px;
  }
  
  .form-title {
    font-size: 24px;
  }
  
  .header-actions {
    position: relative;
    margin-bottom: 10px;
    text-align: left;
  }
}
</style>
