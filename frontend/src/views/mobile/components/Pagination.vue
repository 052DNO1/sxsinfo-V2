<template>
  <div class="pagination-wrapper" v-if="showPagination">
    <van-pagination
      v-model="currentPageValue"
      :total-items="totalCount"
      :items-per-page="pageSize"
      :show-page-size="5"
      force-ellipses
    />
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'Pagination',
  props: {
    show: {
      type: Boolean,
      default: true
    },
    currentPage: {
      type: Number,
      default: 1
    },
    pageSize: {
      type: Number,
      default: 10
    },
    totalCount: {
      type: Number,
      default: 0
    },
    pageSizes: {
      type: Array,
      default: () => [10, 20, 50, 100]
    },
    layout: {
      type: String,
      default: 'total, sizes, prev, pager, next, jumper'
    },
    background: {
      type: Boolean,
      default: true
    }
  },
  
  emits: [
    'update:currentPage',
    'update:pageSize',
    'size-change',
    'current-change'
  ],
  
  setup(props, { emit }) {
    const showPagination = computed(() => {
      return props.show && props.totalCount > 0
    })
    
    const currentPageValue = computed({
      get: () => props.currentPage,
      set: (val) => {
        emit('update:currentPage', val)
        emit('current-change', val)
      }
    })
    
    return {
      showPagination,
      currentPageValue
    }
  }
}
</script>

<style scoped>
.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 16px;
  margin-bottom: 16px;
  padding: 0 16px;
}
</style>
