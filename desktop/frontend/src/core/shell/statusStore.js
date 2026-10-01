/**
 * 外壳状态（供底部状态栏消费）
 *
 * 为什么要单独一个模块：状态栏在最外层（App.vue），而"当前用户/列表条数/连接状态"
 * 分别产生在侧边栏、列表页、请求层。用响应式单例做单向汇集，
 * 比层层 props 透传干净，也不必为此新增 Pinia store。
 *
 * 约定：
 * - 各产生方只调 setXxx / publishTable；
 * - 状态栏只读 state，翻页通过 registerPaging 注册的控制器回调触发，
 *   这样状态栏不需要知道列表页是谁、数据从哪来。
 */
import { reactive } from 'vue'

const state = reactive({
  /** { id, nickname, roleText } */
  user: null,
  /** { status: 'ok'|'fail'|'unknown', latency, baseUrl } */
  connection: { status: 'unknown', latency: null, baseUrl: '' },
  /** 列表上下文：{ label, page, pageSize, total, loaded, pages, canPrev, canNext, selectedCount } */
  table: null
})

/** 列表页注册的翻页控制器：{ prev(), next() } */
let pagingController = null

/** 列表页注册的"重新拉取当前页"回调（供 Ctrl+R 使用） */
let reloadHandler = null

export function setUser(user) {
  state.user = user || null
}

export function setConnection(connection) {
  state.connection = Object.assign({ status: 'unknown', latency: null, baseUrl: '' }, connection || {})
}

/** 列表页在数据/页码变化时调用；传 null 表示离开列表页 */
export function publishTable(info) {
  state.table = info || null
}

/**
 * 注册翻页控制器
 * @param {{ prev: Function, next: Function }|null} controller
 */
export function registerPaging(controller) {
  pagingController = controller || null
}

/** 状态栏点击上一页/下一页 */
export function requestPage(delta) {
  if (!pagingController) return
  const action = delta < 0 ? pagingController.prev : pagingController.next
  if (typeof action === 'function') action()
}

/**
 * 注册"重新拉取当前页"的回调
 *
 * 供 Ctrl+R 使用：只重发当前表格的请求，**不刷新整个页面**（整页刷新是网页的做法）。
 * @param {Function|null} handler
 */
export function registerReload(handler) {
  reloadHandler = handler || null
}

/** 重新拉取当前表格数据；没有表格时返回 false（调用方不要 fallback 成整页刷新） */
export function requestReload() {
  if (typeof reloadHandler === 'function') {
    reloadHandler()
    return true
  }
  return false
}

export function useShellStatus() {
  return state
}
