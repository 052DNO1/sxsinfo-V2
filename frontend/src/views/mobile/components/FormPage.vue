<template>
  <div class="mobile-form-container">
    <div class="mobile-form-panel">
      <div class="form-header">
        <van-icon
          v-if="showBackButton"
          name="arrow-left"
          size="20"
          class="back-icon"
          @click="$emit('back')"
        />
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
export default {
  name: 'FormPage',
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
.mobile-form-container {
  padding: 12px;
}

.mobile-form-panel {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  padding: 20px;
}

.form-header {
  text-align: center;
  margin-bottom: 20px;
  position: relative;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f2f5;
}

.back-icon {
  position: absolute;
  left: 0;
  top: 0;
  color: #969799;
}

.form-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.form-title {
  font-size: 18px;
  font-weight: 600;
  color: #323233;
  margin: 0 0 8px;
}

.form-description {
  font-size: 14px;
  color: #969799;
  margin: 0;
}

.form-content {
  padding-top: 8px;
}
</style>
