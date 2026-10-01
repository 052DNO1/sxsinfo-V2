/**
 * 表格行右键：Tauri 原生菜单（B 缺口）
 *
 * 【为什么不直接 import】
 * `@tauri-apps/api` 这个 npm 包在工程里还没有安装。如果用静态 import，
 * 构建阶段就会直接失败。所以这里用**动态 import + 优雅降级**：
 *   ① 先看 withGlobalTauri 暴露的 window.__TAURI__.menu（Tauri 2 会把它挂上）
 *   ② 再尝试动态 import('@tauri-apps/api/menu')
 *   ③ 都拿不到就返回 false —— 调用方继续用 HTML 菜单，功能不受影响
 *
 * 【行数据怎么传到菜单回调里】
 * 不需要 Tauri 的 listen/IPC 往返：菜单项的 action 是 JS 回调，
 * 直接把当前行对象闭包捕获进去即可（最省事也最快，没有序列化开销）。
 *
 * 【Tauri 侧需要的配置】
 * src-tauri/capabilities/default.json 的 permissions 里加：
 *   "core:menu:default"
 * 若用 popupAt 指定坐标，还需（Tauri 2.2+）："core:menu:allow-popup-at"
 * 前端依赖（要用 ② 路径时才需要）：yarn add @tauri-apps/api
 */

/** 读取/写入"是否使用原生右键菜单"的开关（默认关闭，保持现有 HTML 菜单） */
const FLAG_KEY = 'lims_row_menu_native'

export function isNativeRowMenuEnabled() {
  try {
    return window.localStorage.getItem(FLAG_KEY) === '1'
  } catch {
    return false
  }
}

export function setNativeRowMenuEnabled(enabled) {
  try {
    window.localStorage.setItem(FLAG_KEY, enabled ? '1' : '0')
  } catch {
    /* 存储不可用时忽略：开关只是偏好，不影响功能 */
  }
}

/** 拿到菜单 API（可能为 null） */
async function getMenuApi() {
  const injected = typeof window !== 'undefined' ? window.__TAURI__?.menu : null
  if (injected?.Menu) return injected

  try {
    /**
     * 必须让 Vite 跳过静态分析：
     * Rollup 会把 `import('@tauri-apps/api/menu')` 这种**字面量**动态导入在构建期解析，
     * 而该包未安装时会直接导致 `Rollup failed to resolve import` 构建失败。
     * 用变量说明符 + @vite-ignore 后，构建期不再解析，运行时加载失败则走降级分支。
     */
    const moduleName = '@tauri-apps/api/menu'
    return await import(/* @vite-ignore */ moduleName)
  } catch {
    return null
  }
}

/**
 * 弹出原生行菜单
 *
 * @param {object}   options
 * @param {Array}    options.items      [{ id, text, danger, separator }]
 * @param {Function} options.onSelect   (id) => void，行数据由调用方闭包捕获
 * @returns {Promise<boolean>} 是否成功弹出（false 表示调用方应回退到 HTML 菜单）
 */
export async function popupNativeRowMenu({ items = [], onSelect } = {}) {
  if (!items.length) return false

  const api = await getMenuApi()
  if (!api?.Menu) return false

  try {
    const { Menu, PredefinedMenuItem } = api

    const menuItems = []
    for (const item of items) {
      if (item.separator) {
        menuItems.push(
          PredefinedMenuItem
            ? await PredefinedMenuItem.new({ item: 'Separator' })
            : { item: 'Separator' }
        )
        continue
      }

      menuItems.push({
        id: item.id,
        text: item.text,
        enabled: item.disabled !== true,
        // 关键：行数据通过闭包传入，无需 IPC 往返
        action: () => onSelect?.(item.id)
      })
    }

    const menu = await Menu.new({ items: menuItems })
    // popup() 在鼠标位置弹出；若需指定坐标，Tauri 2.2+ 可用 menu.popupAt({ x, y })
    await menu.popup()
    return true
  } catch (error) {
    console.warn('[nativeRowMenu] 原生菜单弹出失败，回退 HTML 菜单:', error)
    return false
  }
}
