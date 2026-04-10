<!-- 系统信息展示 -->
<template>
  <Index>
    <template #rightcontent>
      <div class="info-panel">
        <h3 
          :class="['info-title', isErrorMode ? 'error-title' : 'success-title']"
          class="text-center">
          <el-icon :size="28" :color="isErrorMode ? '#dc3545' : '#28a745'"><component :is="isErrorMode ? 'CircleClose' : 'CircleCheck'" /></el-icon> {{ msg?.title || (isErrorMode ? '错误' : '成功') }}
        </h3>
        
        <div class="info-message text-center" style="white-space: pre-line;">
          {{ msg?.message || '' }}
        </div>

        <div v-if="msg?.links && msg.links.length > 0" class="info-actions">
          <el-button
             v-for="(link, index) in msg.links"
            :key="index"
            type="primary"
            size="default"
            @click="() => window.location.href = link.url">
            {{ link.text }}
          </el-button>
        </div>

        <div v-if="msg?.errdata && msg.errdata.length > 0" class="warning text-center">
          <h4><el-icon><Document /></el-icon> 错误详情</h4>
          <el-table :data="msg.errdata" border stripe style="width: 100%">
            <el-table-column type="index" label="行号" width="80" align="center">
              <template #default="scope">
                 {{ scope.row[0] }}
              </template>
            </el-table-column>
            <el-table-column label="所在行示例数据" min-width="200" show-overflow-tooltip>
              <template #default="scope">
                 {{ scope.row[1] }}
              </template>
            </el-table-column>
            <el-table-column label="错误信息" min-width="300" show-overflow-tooltip>
               <template #default="scope">
                 {{ scope.row[2] }}
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div v-if="msg?.details && msg.details.length > 0" class="error-detail-list">
          <h4><el-icon><Document /></el-icon> 错误详情列表</h4>
          <el-table :data="msg.details" border stripe style="width: 100%">
            <el-table-column prop="type" label="类型" width="120" />
            <el-table-column prop="name" label="名称" width="150" show-overflow-tooltip />
            <el-table-column prop="extra" label="附加信息" min-width="200" show-overflow-tooltip />
            <el-table-column label="操作" width="120" align="center">
              <template #default="scope">
                <el-button type="primary" size="small" @click="() => window.location.href = scope.row.url">去处?/el-button>
              </template>
            </el-table-column>
          </el-table>
          <p class="text-muted">仅显示前10条，更多请通过上方的入口链接查看?/p>
        </div>

        <div class="info-actions">
          <template v-if="preUrl">
              <router-link
                v-if="pama"
                :to="{ name: preUrl, params: { id: pama } }"
                style="display: inline-block; text-decoration: none; color: inherit;">
                <el-button class="nav-action-btn" plain :icon="Back">返回</el-button>
              </router-link>
              <router-link v-else :to="{ name: preUrl }" style="display: inline-block; text-decoration: none; color: inherit;">
                <el-button class="nav-action-btn" plain :icon="Back">返回</el-button>
              </router-link>
          </template>

          <el-button v-if="backUrl" class="nav-action-btn" plain :icon="Back" @click="() => window.location.href = backUrl">返回</el-button>

          <template v-if="!preUrl && !backUrl">
            <el-button class="nav-action-btn" plain :icon="Back" @click="smartBack">返回</el-button>
            <el-button class="nav-action-btn" plain :icon="HomeFilled" @click="goHome">首页</el-button>
          </template>
        </div>
      </div>
    </template>
  </Index>
</template>

<script setup>
import { useInfo } from '@/core/hooks'
import Index from '@/views/pc/dashboard/Index.vue'
import { Back, HomeFilled, CircleClose, CircleCheck, Document } from '@element-plus/icons-vue'

const { msg, preUrl, pama, backUrl, isErrorMode, smartBack, goHome } = useInfo()
</script>

<style scoped>
.info-panel {
    margin: 50px auto;
    max-width: 1200px;
    padding: 20px;
}

.info-title {
    font-size: 30px;
    font-weight: bold;
    margin-bottom: 20px;
}

.success-title {
    color: #28a745;
}

.error-title {
    color: #dc3545;
}

.info-message {
    font-size: 20px;
    line-height: 1.6;
    margin-bottom: 30px;
    padding: 15px;
    background-color: #f8f9fa;
    border-radius: 8px;
}

.info-actions {
    margin: 30px auto;
    text-align: center;
    display: flex;
    gap: 10px;
    justify-content: center;
    flex-wrap: wrap;
}

.info-actions .table {
    width: 100%;
    margin: 20px 0;
    border-collapse: collapse;
}

.info-actions .table-bordered {
    border: 1px solid #dee2e6;
}

.info-actions .table-striped tbody tr:nth-of-type(odd) {
    background-color: rgba(0, 0, 0, 0.05);
}

.info-actions .table thead th,
.info-actions .table tbody td {
    padding: 12px;
    text-align: left;
    border: 1px solid #dee2e6;
}

.info-actions .table thead th {
    background-color: #f8f9fa;
    font-weight: bold;
}

.warning {
    margin: 30px 0;
    padding: 20px;
    background-color: #fff3cd;
    border: 1px solid #ffc107;
    border-radius: 8px;
}

.error-detail-list {
    margin: 30px 0;
    padding: 20px;
    background-color: #f8d7da;
    border: 1px solid #dc3545;
    border-radius: 8px;
}

.error-detail-list h4 {
    margin-bottom: 15px;
    color: #721c24;
}

.text-muted {
    color: #6c757d;
    font-size: 15px;
    margin-top: 10px;
}
</style>
