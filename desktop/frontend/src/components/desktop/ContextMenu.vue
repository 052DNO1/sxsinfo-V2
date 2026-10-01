<!--
  右键上下文菜单（VS Code 风格）

  用途：替代表格右侧的"操作"列。行内操作改由右键触发，
  腾出横向空间给数据列本身，也让界面更像原生桌面应用。

  刻意不依赖 Element Plus 的下拉组件：
  - 右键菜单需要"跟随鼠标、贴边翻转、键盘可达"，自己实现约 120 行且完全可控；
  - 组件库的下拉是挂在 body 上的浮层，和表格滚动/虚拟滚动的配合更麻烦。
-->
<template>
  <Teleport to="body">
    <div
      v-if="visible"
      class="ctx-mask"
      @mousedown="close"
      @contextmenu.prevent="close"
    >
      <ul
        ref="panelRef"
        class="ctx-panel"
        role="menu"
        :style="panelStyle"
        @mousedown.stop
        @contextmenu.prevent
      >
        <template v-for="(item, index) in items" :key="index">
          <li
            v-if="item.separator"
            class="ctx-sep"
            role="separator"
          />
          <li v-else>
            <button
              class="ctx-item"
              type="button"
              role="menuitem"
              :class="{
                'is-danger': item.danger,
                'is-active': index === activeIndex,
                'is-disabled': item.disabled
              }"
              :disabled="item.disabled"
              @mouseenter="activeIndex = index"
              @click="choose(item)"
            >
              <span class="ctx-item__label">{{ item.text }}</span>
              <span
                v-if="item.shortcut"
                class="ctx-item__shortcut"
              >{{ item.shortcut }}</span>
            </button>
          </li>
        </template>
      </ul>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  items: { type: Array, default: () => [] },
  /** 触发位置（视口坐标） */
  x: { type: Number, default: 0 },
  y: { type: Number, default: 0 }
})

const emit = defineEmits(['select', 'update:visible'])

const panelRef = ref(null)
const activeIndex = ref(0)
const size = ref({ width: 200, height: 0 })

/** 贴边翻转：靠近右下角时向左/向上展开，避免菜单被窗口裁掉 */
const panelStyle = computed(() => {
  const margin = 4
  const maxX = window.innerWidth - size.value.width - margin
  const maxY = window.innerHeight - size.value.height - margin
  return {
    left: `${Math.max(margin, Math.min(props.x, maxX))}px`,
    top: `${Math.max(margin, Math.min(props.y, maxY))}px`,
    minWidth: '180px'
  }
})

function close() {
  emit('update:visible', false)
}

function choose(item) {
  if (item.disabled) return
  emit('select', item)
  close()
}

/** 键盘可达：↑↓ 移动、Enter 触发、Esc 关闭 */
function onKeydown(event) {
  if (!props.visible) return
  const selectable = props.items
    .map((item, index) => ({ item, index }))
    .filter(({ item }) => !item.separator && !item.disabled)

  if (!selectable.length) return

  if (event.key === 'Escape') {
    event.preventDefault()
    close()
    return
  }

  const currentPos = selectable.findIndex(({ index }) => index === activeIndex.value)

  if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
    event.preventDefault()
    const delta = event.key === 'ArrowDown' ? 1 : -1
    const nextPos = (currentPos + delta + selectable.length) % selectable.length
    activeIndex.value = selectable[nextPos].index
  } else if (event.key === 'Enter') {
    event.preventDefault()
    if (currentPos >= 0) choose(selectable[currentPos].item)
  }
}

watch(
  () => props.visible,
  async (visible) => {
    if (!visible) return
    activeIndex.value = props.items.findIndex((item) => !item.separator && !item.disabled)
    if (activeIndex.value < 0) activeIndex.value = 0
    await nextTick()
    if (panelRef.value) {
      const rect = panelRef.value.getBoundingClientRect()
      size.value = { width: rect.width, height: rect.height }
    }
    window.addEventListener('keydown', onKeydown, true)
  }
)

onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown, true))
</script>

<style scoped>
.ctx-mask {
  position: fixed;
  inset: 0;
  z-index: 5000;
}

.ctx-panel {
  position: fixed;
  margin: 0;
  padding: 4px 0;
  list-style: none;
  background: #ffffff;
  border: 1px solid #d4d4d4;
  border-radius: 4px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.18);
  font-size: 13px;
}

.ctx-item {
  display: flex;
  align-items: center;
  gap: 16px;
  width: 100%;
  height: 26px;
  padding: 0 12px;
  border: 0;
  background: transparent;
  color: #1f1f1f;
  font-family: inherit;
  font-size: 13px;
  text-align: left;
  cursor: default;
}

.ctx-item__label {
  flex: 1;
}

.ctx-item__shortcut {
  color: #8a8a8a;
  font-size: 12px;
}

.ctx-item.is-active:not(.is-disabled) {
  background: #0067c0;
  color: #ffffff;
}

.ctx-item.is-active:not(.is-disabled) .ctx-item__shortcut {
  color: rgba(255, 255, 255, 0.75);
}

.ctx-item.is-danger {
  color: #cd3131;
}

.ctx-item.is-danger.is-active {
  background: #cd3131;
  color: #ffffff;
}

.ctx-item.is-disabled {
  color: #b0b0b0;
}

.ctx-sep {
  height: 1px;
  margin: 4px 0;
  background: #e5e5e5;
}

@media (prefers-color-scheme: dark) {
  .ctx-panel {
    background: #252526;
    border-color: #3c3c3c;
    color: #cccccc;
  }

  .ctx-item {
    color: #cccccc;
  }

  .ctx-item.is-active:not(.is-disabled) {
    background: #04395e;
  }

  .ctx-sep {
    background: #3c3c3c;
  }
}
</style>
