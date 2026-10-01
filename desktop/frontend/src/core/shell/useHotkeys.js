/**
 * 全局快捷键（桌面端）
 *
 * 桌面软件与网页的一个显著区别：快捷键是"应用级"的，而且**不会让整页重载**。
 * 这里只处理两件事：
 *   - Ctrl/Cmd + K ：唤出全局搜索（派发 window 事件，由搜索组件接）
 *   - Ctrl/Cmd + R ：只重新拉取当前表格数据（阻止 WebView 的整页刷新）
 *
 * 为什么用 window 事件而不是直接 import 搜索组件：
 * 搜索入口在页面深处（侧边栏搜索框 / GlobalSearch），这里只负责"广播意图"，
 * 谁在监听谁来响应，避免把布局组件和功能组件耦合在一起。
 */
import { onBeforeUnmount, onMounted } from 'vue'
import { requestReload } from '@/core/shell/statusStore'

/** 搜索组件监听这个事件即可被 Ctrl+K 唤起 */
export const EVENT_GLOBAL_SEARCH = 'lims:global-search'

export function useHotkeys() {
  function isEditingField(target) {
    if (!target) return false
    const tag = (target.tagName || '').toLowerCase()
    return tag === 'input' || tag === 'textarea' || tag === 'select' || target.isContentEditable === true
  }

  function onKeydown(event) {
    const mod = event.ctrlKey || event.metaKey
    if (!mod || event.altKey) return

    const key = (event.key || '').toLowerCase()

    if (key === 'k') {
      // 全局搜索：输入框里也允许（用户可能正想换关键词）
      event.preventDefault()
      window.dispatchEvent(new CustomEvent(EVENT_GLOBAL_SEARCH))
      return
    }

    if (key === 'r') {
      // 输入框里不抢 Ctrl+R，避免干扰输入法/浏览器原生行为
      if (isEditingField(event.target)) return
      event.preventDefault()

      // 当前页有表格 → 只刷新表格；没有表格（如表单页）→ 不动作，
      // 绝不 fallback 成整页 reload，那正是网页的做法
      const reloaded = requestReload()
      if (!reloaded) {
        window.dispatchEvent(new CustomEvent(EVENT_GLOBAL_SEARCH, { detail: { reason: 'no-table' } }))
      }
    }
  }

  onMounted(() => window.addEventListener('keydown', onKeydown, true))
  onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown, true))
}
