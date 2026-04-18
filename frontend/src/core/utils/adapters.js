/**
 * 数据适配器 - 处理不同格式的API响应
 */

/**
 * 适配电脑/设备列表数据
 * 统一处理多种API响应格式:
 * - { success: true, data: { list: [...] } }
 * - { data: { list: [...] } }
 * - { items: [...] }
 * - { list: [...] }
 * - [...] (直接数组)
 */
export function adaptComputerList(response) {
  if (!response) {
    return { data: [] }
  }

  let data = []

  if (response.success && response.data) {
    data = response.data.list || response.data.items || []
  } else if (response.items && Array.isArray(response.items)) {
    data = response.items
  } else if (response.list && Array.isArray(response.list)) {
    data = response.list
  } else if (response.data?.list && Array.isArray(response.data.list)) {
    data = response.data.list
  } else if (response.data && Array.isArray(response.data)) {
    data = response.data
  } else if (Array.isArray(response)) {
    data = response
  } else if (response.data?.items && Array.isArray(response.data.items)) {
    data = response.data.items
  } else {
    data = []
  }

  if (!Array.isArray(data)) {
    data = []
  }

  return {
    data,
    ...response
  }
}

/**
 * 适配通用列表数据
 */
export function adaptList(response) {
  if (!response) {
    return { list: [], pagination: null }
  }

  let list = []
  let pagination = null

  if (response.items && Array.isArray(response.items)) {
    list = response.items
  } else if (response.data?.list && Array.isArray(response.data.list)) {
    list = response.data.list
    pagination = response.data.pagination || null
  } else if (response.success && response.data?.list && Array.isArray(response.data.list)) {
    list = response.data.list
    pagination = response.data.pagination || null
  } else if (Array.isArray(response)) {
    list = response
  } else if (response.data && Array.isArray(response.data)) {
    list = response.data
  }

  if (response.page_obj?.paginator) {
    pagination = {
      total: response.page_obj.paginator.count,
      page: response.page_obj.number,
      page_size: response.page_obj.paginator.per_page
    }
  }

  return {
    list,
    pagination,
    raw: response
  }
}