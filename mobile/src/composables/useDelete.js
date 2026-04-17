import { useApi } from '@/composables/useApi'
import { safeConfirm, showSuccess, showError, showWarning, extractFailedItems, formatBatchResult, safeAlert } from '@/utils/errorHandler'

export function useDelete(options = {}) {
  const {
    apiPathBuilder,
    apiPath,
    paramName = 'ids',
    getId = (row) => row.id || row[0],
    refresh,
    confirmMessageBuilder,
    method = 'POST',
    handleItemDelete
  } = options

  const apiComposable = useApi('', { immediate: false, autoHandleError: false })

  const handleDelete = async (item) => {
    if (!item) return

    const confirmMsg = confirmMessageBuilder 
      ? confirmMessageBuilder(item) 
      : `确定要删除 "${item.name || item.device_name || '该项目'}" 吗？`
    const confirmed = await safeConfirm(confirmMsg)
    if (!confirmed) return

    if (!apiPathBuilder || typeof apiPathBuilder !== 'function') {
      console.error('useDelete: apiPathBuilder is required')
      return
    }
    const url = apiPathBuilder(item)

    try {
      let response
      if (method.toUpperCase() === 'GET') {
        response = await apiComposable.get({}, { url })
      } else {
        response = await apiComposable.post({}, { url })
      }

      if (response && response.success !== false) {
        await showSuccess('删除成功')
        if (refresh && typeof refresh === 'function') {
          await refresh()
        }
      } else {
        await showError(response?.message || '删除失败')
      }
    } catch (err) {
      console.error('删除失败:', err)
      await showError(err)
    }
  }

  const handleBatchDelete = async (selection) => {
    if (!selection || selection.length === 0) {
      await showWarning('请至少选择一项进行删除')
      return
    }

    const count = selection.length
    const confirmMsg = confirmMessageBuilder 
      ? confirmMessageBuilder(selection)
      : `确定要删除选中的 ${count} 项吗？此操作不可恢复！`

    const confirmed = await safeConfirm(confirmMsg)
    if (!confirmed) return

    const ids = []
    for (const row of selection) {
      const id = getId(row)
      if (id !== null && id !== undefined && id !== '') {
        ids.push(id)
      }
    }

    if (ids.length === 0) {
      await showWarning('未能解析选中项的ID')
      return
    }

    if (handleItemDelete && typeof handleItemDelete === 'function') {
      const successItems = []
      const failedItems = []

      for (const id of ids) {
        try {
          await handleItemDelete(id)
          successItems.push(id)
        } catch (err) {
          let reason = '删除失败'
          if (err.response?.data?.message) {
            reason = err.response.data.message
          } else if (err.message) {
            reason = err.message
          }
          failedItems.push({ id, reason })
        }
      }

      const resultMessage = formatBatchResult({
        successItems,
        failedItems,
        successLabel: '项',
        failedLabel: '项'
      })

      if (resultMessage) {
        await safeAlert(resultMessage)
      }

      if (successItems.length > 0 && refresh && typeof refresh === 'function') {
        await refresh()
      }

    } else {
      if (!apiPath) {
        console.error('useDelete: apiPath is required for batch delete')
        return
      }

      try {
        const requestData = { [paramName]: ids }
        const response = await apiComposable.post(requestData, { url: apiPath })

        if (response && response.success) {
          const failedItems = extractFailedItems(response)
          const deletedCount = response.deleted_count || 0
          const failedCount = failedItems ? failedItems.length : 0
          
          if (deletedCount > 0 && failedCount > 0) {
            let warnMsg = `成功删除 ${deletedCount} 项，${failedCount} 项删除失败：\n\n`
            warnMsg += failedItems.slice(0, 5).join('\n')
            if (failedItems.length > 5) {
              warnMsg += `\n...等共 ${failedItems.length} 项`
            }
            await safeAlert(warnMsg)
          } else if (deletedCount > 0) {
            await showSuccess(response.message || `成功删除 ${deletedCount} 项`)
          } else if (failedCount > 0) {
            let warnMsg = response.message || '删除失败'
            warnMsg += '\n\n详情：\n' + failedItems.slice(0, 5).join('\n')
            if (failedItems.length > 5) {
              warnMsg += `\n...等共 ${failedItems.length} 项`
            }
            await safeAlert(warnMsg)
          } else {
            await showSuccess(response.message || '操作完成')
          }
          
          if (deletedCount > 0 && refresh && typeof refresh === 'function') {
            await refresh()
          }
        } else {
          const failedItems = extractFailedItems(response)
          let errorMsg = response?.message || '批量删除失败'
          if (failedItems && failedItems.length > 0) {
            errorMsg += '\n\n失败详情：\n' + failedItems.slice(0, 5).join('\n')
          }
          await showError(errorMsg)
        }
      } catch (err) {
        console.error('批量删除失败:', err)
        await showError(err)
      }
    }
  }

  return {
    handleDelete,
    handleBatchDelete
  }
}
