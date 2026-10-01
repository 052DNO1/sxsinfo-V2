<!--
  通用数据表格（VS Code 风格）

  与旧版的区别（这次改造的核心）：
  1. 去掉白卡片与外层阴影：工具条 + 表格平铺在背景上，卡片感是"网页后台"的典型特征；
  2. 去掉表格外边框、斑马纹、底部整块分页组件与"每页条数"下拉：
     分页能力下沉到底部状态栏（区间 + 上一页/下一页，支持 PageUp/PageDown）；
  3. 行高压缩到 28px、整行悬浮高亮，信息密度接近 IDE 的列表；
  4. 去掉右侧"操作"列：行操作改为**右键上下文菜单**（组件见 desktop/ContextMenu.vue），
     横向空间让给数据列本身；
  5. 顶部操作改为扁平工具条图标按钮（无边框、32px、悬停着色，带 title 提示）。

  对外 API 与旧版保持一致：props/emits 名一个没改，
  因此 14 个列表页（CrudList 之下）无需改动即可获得新外观与新交互。
-->
<template>
  <div class="dt">
    <!-- 工具条：扁平、紧凑，不再是"卡片头" -->
    <div
      v-if="showHeader"
      class="dt-toolbar"
    >
      <div class="dt-toolbar__title">
        <el-icon
          v-if="icon"
          class="dt-toolbar__icon"
        >
          <component :is="icon" />
        </el-icon>
        <span class="dt-toolbar__text">{{ title }}</span>
        <span
          v-if="selectedCount > 0"
          class="dt-toolbar__badge"
        >已选 {{ selectedCount }}</span>
      </div>

      <div class="dt-toolbar__actions">
        <slot name="actions">
          <button
            v-if="showBatchDelete && !$slots.actions"
            class="dt-iconbtn is-danger"
            type="button"
            title="批量删除"
            :disabled="selectedCount === 0"
            @click="$emit('batch-delete')"
          >
            <el-icon><Delete /></el-icon>
          </button>

          <!-- 页面传入的业务动作：带文字的扁平按钮（图标 + 文案），
               不再是一排认不出功能的空白图标块 -->
          <el-button
            v-for="(o, index) in options || []"
            v-show="!$slots.actions"
            :key="index"
            class="dt-optionbtn"
            :type="buttonTypeOf(o)"
            :icon="iconFor(o)"
            @click="$emit('option-click', o)"
          >
            {{ o.text }}
          </el-button>
        </slot>

        <span
          v-if="$slots.actions"
          class="dt-toolbar__slotted"
        >
          <slot name="actions" />
        </span>

        <button
          v-if="shouldShowBackButton"
          class="dt-iconbtn"
          type="button"
          title="返回"
          @click="$emit('back')"
        >
          <el-icon><Back /></el-icon>
        </button>
        <button
          v-if="showHome"
          class="dt-iconbtn"
          type="button"
          title="首页"
          @click="$emit('home')"
        >
          <el-icon><House /></el-icon>
        </button>
      </div>
    </div>

    <!-- 表格本体：无边框、密排、整行高亮 -->
    <div class="dt-body">
      <div
        v-if="error"
        class="dt-error"
      >
        <el-empty
          :description="error"
          :image-size="64"
        />
      </div>

      <el-table
        v-else
        v-loading="loading"
        class="dt-table"
        :data="data"
        size="small"
        :border="false"
        :stripe="false"
        highlight-current-row
        @selection-change="val => $emit('selection-change', val)"
        @row-contextmenu="onRowContextMenu"
      >
        <el-table-column
          v-if="showCheckbox"
          type="selection"
          width="34"
          align="center"
        />

        <el-table-column
          v-for="(col, index) in visibleColumns"
          :key="index"
          :label="col.label"
          :prop="col.prop"
          :width="col.width"
          :min-width="Math.max(col.minWidth || 140, 130)"
          show-overflow-tooltip
        >
          <template #default="scope">
            <el-tag
              v-if="col.isStatus"
              :type="scope.row[col.prop]?.type || 'info'"
              size="small"
              effect="light"
            >
              {{ scope.row[col.prop]?.text || scope.row[col.prop] }}
            </el-tag>
            <span v-else>{{ formatValue(scope.row[col.prop]) }}</span>
          </template>
        </el-table-column>

        <!-- 页面自定义行操作（slot）时保留一个极窄的"更多"入口，兼容旧页面 -->
        <el-table-column
          v-if="$slots['row-actions']"
          width="44"
          align="center"
          class-name="dt-more-col"
        >
          <template #default="scope">
            <button
              class="dt-iconbtn dt-iconbtn--tiny"
              type="button"
              title="更多操作（也可直接右键本行）"
              @click.stop="openMenuForRow(scope.row, $event)"
            >
              <el-icon><More /></el-icon>
            </button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 右键菜单：视觉与交互都在 ContextMenu.vue 内 -->
    <ContextMenu
      v-model:visible="menu.visible"
      :items="menu.items"
      :x="menu.x"
      :y="menu.y"
      @select="onMenuSelect"
    />
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, reactive, watch } from 'vue'
import { Back, Delete, Download, Edit, House, More, Plus } from '@element-plus/icons-vue'
import { getButtonIcon, getButtonType } from '@/core/utils/tableHelpers'
import { useUserStore } from '@/core/store/user'
import { publishTable, registerPaging, registerReload } from '@/core/shell/statusStore'
import { isNativeRowMenuEnabled, popupNativeRowMenu } from '@/core/shell/nativeRowMenu'
import ContextMenu from '@/components/desktop/ContextMenu.vue'

/**
 * 业务动作的图标解析
 *
 * `getButtonIcon()` 返回的是**图标名字符串**（'Plus' / 'Delete' / …），
 * 而本工程没有全局注册 Element Plus 图标，`<component :is="'Plus'">` 会解析成空
 * —— 这正是之前工具栏出现"空白方框"的原因。这里显式映射到真实组件。
 */
const ICON_MAP = { Delete, Plus, Download, Edit, House, More, Back }

function iconFor(option) {
  const name = getButtonIcon(option)
  return (name && ICON_MAP[name]) || Plus
}

/** 主按钮 / 危险按钮 / 普通按钮 */
function buttonTypeOf(option) {
  const type = getButtonType(option)
  if (type === 'danger') return 'danger'
  if (type === 'primary') return 'primary'
  return 'default'
}

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
  showBack: { type: Boolean, default: true },
  showHome: { type: Boolean, default: true },
  total: { type: Number, default: 0 },
  currentPage: { type: Number, default: 1 },
  pageSize: { type: Number, default: 10 },
  isPaginated: Boolean,
  options: Array,
  selectedCount: { type: Number, default: 0 },
  excludeActionPatterns: { type: Array, default: () => [] }
})

const emit = defineEmits([
  'batch-delete',
  'option-click',
  'action-click',
  'selection-change',
  'size-change',
  'current-change',
  'back',
  'home',
  'update:currentPage',
  'update:pageSize'
])

const userStore = useUserStore()

/** 数据列：剔除旧的"操作"列（isAction），它已改为右键菜单 */
const visibleColumns = computed(() => (props.columns || []).filter((col) => !col.isAction))

const shouldShowBackButton = computed(() => {
  const user = userStore.user
  if (user?.is_superuser) return false
  if (user?.is_super_admin && !user?.is_superuser) return false
  return props.showBack
})

const formatValue = (val) => {
  if (val === null || val === undefined) return '-'
  return val
}

// ── 右键菜单 ─────────────────────────────────────────────
const menu = reactive({ visible: false, items: [], row: null, x: 0, y: 0 })

/** 从行数据里取出旧"操作列"定义的动作数组 */
function actionsOf(row) {
  const actionColumn = (props.columns || []).find((col) => col.isAction)
  if (!actionColumn) return []
  const list = row ? row[actionColumn.prop] : null
  if (!Array.isArray(list)) return []
  return list.filter((op) => op && op.text && !props.excludeActionPatterns.some((p) => op.text.includes(p)))
}

function openMenu(row, x, y) {
  const actions = actionsOf(row)
  if (!actions.length) return
  menu.items = actions.map((op) => ({
    text: op.text,
    danger: op.type === 'danger',
    raw: op
  }))
  menu.row = row
  menu.x = x
  menu.y = y
  menu.visible = true
}

function onRowContextMenu(row, _column, event) {
  // 行内没有可用操作时不弹菜单：空菜单比"没反应"更让人困惑
  if (!actionsOf(row).length) return
  event.preventDefault()

  // 开关打开时优先用 Tauri 原生菜单；拿不到（未装 @tauri-apps/api / 权限未开）
  // 会自动回退到下面的 HTML 菜单，功能不受影响
  if (isNativeRowMenuEnabled()) {
    const items = actionsOf(row).map((op) => ({
      id: op.text,
      text: op.text,
      danger: op.type === 'danger'
    }))
    popupNativeRowMenu({
      items,
      onSelect: (id) => {
        const op = actionsOf(row).find((candidate) => candidate.text === id)
        if (op) emit('action-click', op, row)
      }
    }).then((handled) => {
      if (!handled) openMenu(row, event.clientX, event.clientY)
    })
    return
  }

  openMenu(row, event.clientX, event.clientY)
}

/** 页面自定义了 row-actions 插槽时，用"更多"按钮打开同一个菜单 */
function openMenuForRow(row, event) {
  const rect = event.currentTarget.getBoundingClientRect()
  openMenu(row, rect.left, rect.bottom + 2)
}

function onMenuSelect(item) {
  emit('action-click', item.raw, menu.row)
}

// ── 状态栏联动：条数区间 + 翻页 ─────────────────────────────
function emitPage(page) {
  if (page < 1) return
  emit('update:currentPage', page)
  emit('current-change', page)
}

registerPaging({
  prev: () => emitPage(props.currentPage - 1),
  next: () => emitPage(props.currentPage + 1)
})

// Ctrl+R：只重新拉取当前页（复用分页事件，父组件据此重发请求），不刷新整个页面
registerReload(() => emitPage(props.currentPage))

function syncStatusBar() {
  if (!props.showPagination && !props.isPaginated) {
    // 不分页的列表只报条数，状态栏不显示翻页按钮
    publishTable({
      label: props.title,
      page: 1,
      pageSize: props.data.length || 1,
      total: props.data.length,
      loaded: props.data.length,
      pages: 1,
      canPrev: false,
      canNext: false,
      selectedCount: props.selectedCount
    })
    return
  }

  const pages = props.total > 0 ? Math.max(1, Math.ceil(props.total / Math.max(1, props.pageSize))) : 1
  publishTable({
    label: props.title,
    page: props.currentPage,
    pageSize: props.pageSize,
    total: props.total,
    loaded: props.data.length,
    pages,
    canPrev: props.currentPage > 1,
    canNext: props.currentPage < pages,
    selectedCount: props.selectedCount
  })
}

watch(
  () => [
    props.title,
    props.data,
    props.total,
    props.currentPage,
    props.pageSize,
    props.isPaginated,
    props.showPagination,
    props.selectedCount
  ],
  syncStatusBar,
  { immediate: true }
)

onBeforeUnmount(() => {
  publishTable(null)
  registerPaging(null)
  registerReload(null)
})
</script>

<style scoped>
.dt {
  display: flex;
  flex-direction: column;
}

/* ── 扁平工具条（尺寸与配色由 desktop-shell.css 统一，这里只管排布） ── */
.dt-toolbar {
  flex: 0 0 auto;
  min-height: 30px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  border-bottom: 1px solid var(--lims-border);
  padding-bottom: 16px;
  margin-bottom: 16px;
}

.dt-toolbar__title {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
  font-size: 13px;
  font-weight: 600;
  color: var(--lims-titlebar-fg);
}

.dt-toolbar__icon {
  color: #1890ff;
  font-size: 15px;
}

.dt-toolbar__text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dt-toolbar__badge {
  padding: 0 6px;
  border-radius: 8px;
  background: #e8f1fd;
  color: #1668dc;
  font-size: 11px;
  font-weight: 500;
  line-height: 16px;
}

.dt-toolbar__actions {
  display: flex;
  align-items: center;
  gap: 4px;
  flex: 0 0 auto;
}

.dt-toolbar__slotted {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

/* 扁平图标按钮：28×28，无边框，悬停才着色 */
.dt-iconbtn {
  width: 28px;
  height: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 0;
  border-radius: 4px;
  background: transparent;
  color: var(--lims-titlebar-fg);
  font-size: 15px;
  cursor: default;
  transition: background var(--lims-duration-fast) var(--lims-ease);
}

.dt-iconbtn:hover:not(:disabled) {
  background: var(--lims-titlebar-hover);
}

.dt-iconbtn:disabled {
  opacity: 0.35;
}

.dt-iconbtn.is-danger:hover:not(:disabled) {
  background: #fdeaea;
  color: #cd3131;
}

.dt-iconbtn--tiny {
  width: 22px;
  height: 22px;
  font-size: 14px;
}

/* ── 表格区域：高度由内容决定，页面整体滚动（不再内部裁切） ── */
.dt-body {
  flex: 1 1 auto;
}

.dt-error {
  padding: 32px 0;
}
</style>
