<template>
  <!-- PC端使用Index组件 -->
  <Index>
    <template #rightcontent>
      <div class="listheader custom-header">
        <span class="header-text"><el-icon><component :is="importType === 'user' ? 'UserFilled' : 'Download'" /></el-icon> {{ header || (importType === 'user' ? '导入用户' : '导入课表') }}</span>
        
        <!-- Dock Tabs moved to header -->
        <div
          v-if="importType !== 'user'"
          class="header-center"
        >
          <el-radio-group v-model="activeTab">
            <el-radio-button value="class">
              导入课表
            </el-radio-button>
            <el-radio-button value="device">
              导入设备
            </el-radio-button>
            <el-radio-button
              v-if="!isSxsAdmin"
              value="sxs"
            >
              导入实训室
            </el-radio-button>
          </el-radio-group>
        </div>

        <div class="listheader-actions">
          <el-button
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

      <div class="import-container">
        <!-- Unified Split Panel Layout -->
        <div class="unified-panel-layout">
          <div class="unified-panel">
            <!-- Left Side: Prep & Guide -->
            <div class="panel-side">
              <div class="side-header">
                <h3><el-icon><InfoFilled /></el-icon> 准备工作</h3>
                <p>请按照以下步骤准备数据</p>
              </div>
                 
              <div class="side-content">
                <!-- Download Template -->
                <div class="side-block">
                  <div class="block-title">
                    1. 下载模板
                  </div>
                  <p class="block-desc">
                    获取标准Excel格式，请勿修改表头
                  </p>
                  <el-button
                    type="primary"
                    plain
                    class="side-btn"
                    @click="downloadTemplate"
                  >
                    <el-icon><Download /></el-icon> 下载{{ summary.typeLabel }}模板
                  </el-button>
                </div>

                <!-- Requirements -->
                <div class="side-block">
                  <div class="block-title">
                    2. 数据要求
                  </div>
                  <div class="req-list">
                    <div class="req-item">
                      <span class="req-label">必填字段：</span>
                      <div class="req-tags">
                        <el-tag
                          v-for="c in summary.required"
                          :key="c"
                          size="small"
                          type="danger"
                          effect="plain"
                        >
                          {{ c }}
                        </el-tag>
                      </div>
                    </div>
                    <div
                      v-if="summary.optional.length"
                      class="req-item"
                    >
                      <span class="req-label">可选字段：</span>
                      <div class="req-tags">
                        <el-tag
                          v-for="c in summary.optional"
                          :key="c"
                          size="small"
                          type="info"
                          effect="plain"
                        >
                          {{ c }}
                        </el-tag>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Tips -->
                <div class="side-block tips-block">
                  <div class="block-title">
                    <el-icon><QuestionFilled /></el-icon> 常见问题
                  </div>
                  <ul class="tips-list">
                    <template v-if="importType === 'user'">
                      <li>手机号请勿使用科学计数法</li>
                      <li>用户名重复会自动检查</li>
                      <li>权限可选值：教师、实训室管理员、分院管理员（可组合）</li>
                      <li>部门需填写系统存在的完整名称</li>
                    </template>
                    <template v-else-if="importType === 'device'">
                      <li>电脑编号在实训室内不可重复</li>
                      <li>实训室名称必须已存在</li>
                    </template>
                    <template v-else-if="importType === 'sxs'">
                      <li>实训室门牌号不可重复</li>
                      <li>管理员需填写系统内存在的用户昵称或用户名</li>
                      <li>部门名称需准确填写</li>
                    </template>
                    <template v-else>
                      <li>任课教师必须是系统中已存在的用户</li>
                      <li>实训室名称/编号需与系统一致</li>
                      <li>系统会自动检测时间冲突</li>
                      <li>自动关联当前学期</li>
                    </template>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Right Side: Action -->
            <div class="panel-main">
              <div class="main-header">
                <h3><el-icon><UploadFilled /></el-icon> 上传文件</h3>
              </div>
                 
              <div class="main-content">
                <div class="upload-zone-wrapper">
                  <el-upload
                    class="upload-unified"
                    drag
                    :auto-upload="false"
                    :on-change="handleFileChange"
                    :show-file-list="false" 
                    accept=".xlsx,.xls"
                  >
                    <div
                      v-if="!selectedFile"
                      class="upload-placeholder"
                    >
                      <div class="upload-icon-box">
                        <el-icon><UploadFilled /></el-icon>
                      </div>
                      <h4>点击或拖拽上传</h4>
                      <p>支持 .xlsx, .xls 格式</p>
                    </div>
                    <div
                      v-else
                      class="file-preview-unified"
                    >
                      <div class="file-icon-unified">
                        <el-icon><Document /></el-icon>
                      </div>
                      <div class="file-info-unified">
                        <div class="fname">
                          {{ fileDisplayName }}
                        </div>
                        <div class="fstatus">
                          准备就绪
                        </div>
                      </div>
                      <el-button
                        type="primary"
                        link
                        @click.stop="triggerFileInput"
                      >
                        更换
                      </el-button>
                    </div>
                  </el-upload>
                </div>

                <div class="action-footer">
                  <div
                    v-if="loading && uploadProgress > 0"
                    class="progress-box"
                  >
                    <!-- 上传阶段 -->
                    <div v-if="!isProcessing">
                      <el-progress 
                        :percentage="uploadProgress" 
                        :stroke-width="18"
                        :text-inside="true"
                        class="upload-progress"
                      />
                      <div class="progress-tip">
                        正在上传文件...
                      </div>
                    </div>
                         
                    <!-- 处理阶段 -->
                    <div v-else>
                      <el-progress 
                        :percentage="backendProgress" 
                        :status="backendProgress === 100 ? 'success' : ''"
                        :stroke-width="18"
                        :text-inside="true"
                        class="upload-progress"
                      />
                      <div class="progress-tip">
                        <el-icon class="is-loading">
                          <Loading />
                        </el-icon>
                        <span>服务器正在处理数据... {{ backendProgress }}%</span>
                      </div>
                    </div>
                  </div>
                  <el-button
                    type="primary"
                    size="large"
                    :loading="loading"
                    :disabled="!selectedFile"
                    class="submit-btn-unified"
                    @click="handleSubmit"
                  >
                    {{ loading ? '正在导入...' : '开始导入数据' }}
                  </el-button>
                </div>

                <div
                  v-if="error"
                  class="error-box-unified"
                >
                  <el-alert
                    :title="error"
                    type="error"
                    :closable="true"
                    show-icon
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </Index>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { UploadFilled, Document, Download, InfoFilled, QuestionFilled, Loading, UserFilled } from '@element-plus/icons-vue'
import { useNavigation } from '@/core/utils/routeDecision'
import { useImport } from '@/core/hooks'
import Index from '@/views/pc/dashboard/Index.vue'
import { getImportConfig } from '@/core/config/importConfig'
import { createAndDownloadExcel } from '@/core/utils/io'
import { useUserStore } from '@/core/store/user'

export default {
  name: 'Import',
  components: {
    Index,
    UploadFilled,
    Document,
    Download,
    InfoFilled,
    QuestionFilled,
    Loading,
    UserFilled
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const userStore = useUserStore()
    
    const { smartBack, goHome } = useNavigation()
    const activeStep = ref(1) // Step control
    const navigateTo = (path) => {
      router.push(path)
    }

    const isSxsAdmin = computed(() => userStore.isSxsAdmin)

    // 根据路由判断导入类型
    const importType = computed(() => {
      if (route.path.includes('import-user')) return 'user'
      if (route.path.includes('import-device')) return 'device'
      if (route.path.includes('import-sxs')) return 'sxs'
      return 'class'
    })

    // 获取当前类型的配置策?
    const config = computed(() => getImportConfig(importType.value))

    const activeTab = computed({
      get: () => importType.value,
      set: (val) => {
        if (val === 'device') navigateTo('/import-device')
        else if (val === 'sxs') navigateTo('/import-sxs')
        else if (val === 'user') navigateTo('/import-user') // 虽然目前界面上没显示user tab，但支持
        else navigateTo('/import')
      }
    })
    
    const header = computed(() => `导入${config.value.label}`)
    
    const selectedFile = ref(null)
    const fileDisplayName = ref('')
    const fileList = ref([])
    
    // 使用新的 useImport composable
    const {
      uploadProgress,
      backendProgress,
      isProcessing,
      error,
      loading,
      submitImport
    } = useImport(config, {
      importType,
      route,
      router
    })
    
    // Summary derived from config
    const summary = computed(() => ({
      typeLabel: `导入${config.value.label}`,
      required: config.value.requiredFields,
      optional: config.value.optionalFields,
      tips: config.value.tips
    }))
    
    const triggerFileInput = () => {
      selectedFile.value = null
      fileDisplayName.value = ''
      fileList.value = []
    }

    const handleFileChange = (file) => {
      // Element Plus upload组件的on-change事件
      if (file && file.raw) {
        selectedFile.value = file.raw
        fileDisplayName.value = file.name
        fileList.value = [file]
      } else if (file && file instanceof File) {
        // 兼容原生input的change事件
        selectedFile.value = file
        fileDisplayName.value = file.name
        fileList.value = [{ name: file.name, raw: file }]
      } else if (file && file.target) {
        // 原生input change事件
        selectedFile.value = file.target.files[0]
        fileDisplayName.value = selectedFile.value ? selectedFile.value.name : ''
        if (selectedFile.value) {
          fileList.value = [{ name: selectedFile.value.name, raw: selectedFile.value }]
        }
      }
    }

    const handleSubmit = async () => {
      if (!selectedFile.value) {
        error.value = '请选择文件'
        return
      }
      await submitImport(selectedFile.value)
    }

    const downloadTemplate = () => {
      const tpl = config.value.templateData
      if (!tpl) return
      createAndDownloadExcel(tpl.headers, tpl.rows, config.value.templateName)
    }

    // 智能返回（根据导入类型决定返回路径）
    const handleGoBack = () => {
      if (importType.value === 'user') {
        router.push('/user-management')
      } else {
        router.push('/lab-resource-management')
      }
    }

    return {
      route,
      importType,
      header,
      selectedFile,
      uploadProgress,
      backendProgress,
      isProcessing,
      error,
      loading,
      fileDisplayName,
      fileList,
      handleFileChange,
      handleSubmit,
      triggerFileInput,
      navigateTo,
      smartBack,
      goHome,
      summary,
      downloadTemplate,
      activeStep,
      activeTab,
      isSxsAdmin
    }
  }
}
</script>

<style scoped>
/* @import '../../../assets/css/pages.css'; - Removed, using scoped styles */

/* Override the global container limit */
.import-container {
  max-width: 100% !important;
  padding: 20px;
}

.custom-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
}

.header-center {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  margin: 0 !important;
}

.header-text {
  font-weight: bold;
  font-size: 18px;
}

/* Unified Panel Layout */
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
  /* Constrain height to match typical sidebar, approx 600-700px */
  height: calc(100vh - 140px);
  max-height: 700px;
  min-height: 500px;
  margin-top: 10px;
}

/* Left Side: Prep & Guide */
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

.block-desc {
  font-size: 12px;
  color: #909399;
  margin: 0 0 12px;
}

.side-btn {
  width: 100%;
  justify-content: center;
}

.req-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.req-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.req-label {
  font-size: 12px;
  color: #909399;
}

.req-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
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

/* Right Side: Action */
.panel-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #fff;
}

.main-header {
  padding: 24px 32px;
  border-bottom: 1px solid #f5f7fa;
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
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center; /* Center content vertically */
}

.upload-zone-wrapper {
  width: 100%;
  max-width: 700px;
}

.upload-unified :deep(.el-upload-dragger) {
  width: 100%;
  height: 280px;
  border: 2px dashed #dcdfe6;
  border-radius: 16px;
  background-color: #fafbfc;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.upload-unified :deep(.el-upload-dragger:hover) {
  border-color: #409eff;
  background-color: #f0f7ff;
}

.upload-placeholder {
  text-align: center;
}

.upload-icon-box {
  width: 72px;
  height: 72px;
  background: #f2f3f5;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  color: #909399;
  margin: 0 auto 16px;
  transition: all 0.3s;
}

.upload-unified :deep(.el-upload-dragger:hover) .upload-icon-box {
  background: #d9ecff;
  color: #409eff;
}

.upload-placeholder h4 {
  margin: 0 0 6px;
  font-size: 16px;
  color: #303133;
}

.upload-placeholder p {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

.file-preview-unified {
  display: flex;
  align-items: center;
  padding: 0 20px;
  width: 100%;
}

.file-icon-unified {
  font-size: 42px;
  color: #67c23a;
  margin-right: 16px;
}

.file-info-unified {
  flex: 1;
  text-align: left;
}

.file-info-unified .fname {
  font-size: 15px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.file-info-unified .fstatus {
  font-size: 12px;
  color: #909399;
}

.action-footer {
  margin-top: 32px;
  width: 100%;
  max-width: 700px;
}

.progress-box {
  margin-bottom: 20px;
  width: 100%;
}

.progress-tip {
  margin-top: 8px;
  font-size: 13px;
  color: #909399;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.submit-btn-unified {
  width: 100%;
  height: 44px;
  font-size: 16px;
  border-radius: 22px;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.error-box-unified {
  margin-top: 20px;
  width: 100%;
  max-width: 700px;
}

@media (max-width: 900px) {
  .unified-panel {
    flex-direction: column;
    height: auto;
    max-height: none;
  }
  .panel-side {
    flex: none;
    border-right: none;
    border-bottom: 1px solid #eef0f5;
  }
}


</style>
