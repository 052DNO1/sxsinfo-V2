<!--
  Pagination.vue - 分页组件
  
  这是一个通用的分页组件，封装�?Element Plus �?el-pagination�?
  
  主要功能�?
  1. 显示分页导航
  2. 支持切换每页显示条数
  3. 支持跳转到指定页
  4. 显示总条�?
  
  对于新手�?
  - props 是父组件传递给子组件的数据
  - emits 是子组件向父组件发送的事件
  - computed 是计算属性，会根据依赖自动更�?
  - v-model 可以�?:currentPage �?@update:currentPage 实现
  
  使用示例�?
  ```vue
  <Pagination
    v-model:currentPage="page"
    v-model:pageSize="size"
    :total-count="total"
    @current-change="handlePageChange"
    @size-change="handleSizeChange"
  />
  ```
-->

<template>
  <div class="pagination-wrapper">
    <!-- Element Plus 分页组件 -->
    <!--
      属性说明：
      - current-page: 当前页码
      - page-size: 每页显示条数
      - page-sizes: 可选的每页条数选项
      - layout: 分页布局（total=总数, sizes=选择�? prev=上一�? pager=页码, next=下一�? jumper=跳转�?
      - total: 总条�?
      - background: 是否显示背景�?
    -->
    <el-pagination
      v-if="showPagination"
      :current-page="currentPage"
      :page-size="pageSize"
      :page-sizes="pageSizes"
      :layout="layout"
      :total="totalCount"
      :background="background"
      @size-change="handleSizeChange"
      @current-change="handlePageChange"
    />
  </div>
</template>

<script>
export default {
  name: 'Pagination',
  
  // ==================== 组件属�?====================
  props: {
    /** 是否显示分页 */
    show: {
      type: Boolean,
      default: true
    },
    /** 当前页码（支�?v-model�?*/
    currentPage: {
      type: Number,
      default: 1
    },
    /** 每页显示条数（支�?v-model�?*/
    pageSize: {
      type: Number,
      default: 10
    },
    /** 总条�?*/
    totalCount: {
      type: Number,
      default: 0
    },
    /** 可选的每页显示条数选项 */
    pageSizes: {
      type: Array,
      default: () => [10, 20, 50, 100]
    },
    /** 分页布局 */
    layout: {
      type: String,
      default: 'total, sizes, prev, pager, next, jumper'
    },
    /** 是否显示背景�?*/
    background: {
      type: Boolean,
      default: true
    }
  },
  
  // ==================== 组件事件 ====================
  emits: [
    'update:currentPage',   // 更新当前页码（v-model�?
    'update:pageSize',      // 更新每页条数（v-model�?
    'size-change',          // 每页条数变化事件
    'current-change'        // 页码变化事件
  ],
  
  // ==================== 计算属�?====================
  computed: {
    /**
     * 是否显示分页
     * 条件：show 属性为 true 且总条数大�?0
     */
    showPagination() {
      return this.show && this.totalCount > 0
    }
  },
  
  // ==================== 方法 ====================
  methods: {
    /**
     * 处理每页条数变化
     * @param {number} size - 新的每页条数
     */
    handleSizeChange(size) {
      this.$emit('update:pageSize', size)
      this.$emit('size-change', size)
    },
    
    /**
     * 处理页码变化
     * @param {number} page - 新的页码
     */
    handlePageChange(page) {
      this.$emit('update:currentPage', page)
      this.$emit('current-change', page)
    }
  }
}
</script>

<style scoped>
/* 分页容器样式：居中显示，上下边距 */
.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  margin-bottom: 20px;
}
</style>
