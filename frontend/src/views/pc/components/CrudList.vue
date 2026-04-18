<template>
  <Index class="pc-layout">
    <template #rightcontent>
      <div class="page-container">
        <DataTable
          :title="title"
          :icon="icon"
          :columns="columns"
          :data="data"
          :loading="loading"
          :error="error"
          :show-header="showHeader"
          :show-pagination="showPagination"
          :show-checkbox="showCheckbox"
          :show-batch-delete="showBatchDelete"
          :total="total"
          v-model:current-page="currentPageModel"
          v-model:page-size="pageSizeModel"
          :is-paginated="isPaginated"
          :options="options"
          :selected-count="selectedCount"
          @batch-delete="$emit('batch-delete')"
          @option-click="o => $emit('option-click', o)"
          @action-click="(op, row) => $emit('action-click', op, row)"
          @selection-change="val => $emit('selection-change', val)"
          @size-change="val => $emit('size-change', val)"
          @current-change="val => $emit('current-change', val)"
          @back="smartBack"
          @home="goHome"
        >
          <!-- 转发插槽 -->
          <template #actions v-if="$slots.actions">
            <slot name="actions"></slot>
          </template>
          <template #row-actions="slotProps">
            <slot name="row-actions" v-bind="slotProps"></slot>
          </template>
        </DataTable>
        
        <!-- 列表下方额外内容插槽 -->
        <slot name="extra"></slot>
      </div>
    </template>
  </Index>
</template>

<script setup>
import { computed } from 'vue'
import { useNavigation } from '@/core/utils/routeDecision'
import Index from '@/views/pc/dashboard/Index.vue'
import DataTable from './DataTable.vue'

const props = defineProps({
  title: String,
  icon: [String, Object],
  columns: { type: Array, default: () => [] },
  data: { type: Array, default: () => [] },
  loading: Boolean,
  error: String,
  showHeader: { type: Boolean, default: true },
  showPagination: { type: Boolean, default: true },
  showCheckbox: Boolean,
  showBatchDelete: Boolean,
  total: { type: Number, default: 0 },
  currentPage: { type: Number, default: 1 },
  pageSize: { type: Number, default: 10 },
  isPaginated: Boolean,
  options: Array,
  selectedCount: { type: Number, default: 0 }
})

const emit = defineEmits([
  'update:currentPage',
  'update:pageSize',
  'batch-delete',
  'option-click',
  'action-click',
  'selection-change',
  'size-change',
  'current-change'
])

const { goHome, smartBack } = useNavigation()

const currentPageModel = computed({
  get: () => props.currentPage,
  set: (val) => emit('update:currentPage', val)
})

const pageSizeModel = computed({
  get: () => props.pageSize,
  set: (val) => emit('update:pageSize', val)
})
</script>

<style scoped>
.page-container {
  padding: 0;
  max-width: 100%;
}
</style>
