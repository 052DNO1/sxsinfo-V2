export function filterActionButtons(options, excludePatterns = []) {
    if (!options || !Array.isArray(options)) {
        return []
    }
    
    const defaultExcludePatterns = [
        '批量/删除',
        '导出维护记录',
        '切换到维护记录',
        '切换到使用记录',
        '返回学期管理'
    ]
    
    const patternsToExclude = [...defaultExcludePatterns, ...excludePatterns]
    
    return options.filter(option => {
        const text = option.text || ''
        return !patternsToExclude.some(pattern => text.includes(pattern))
    })
}

export function getDefaultActionExcludePatterns() {
    return [
        '批量/删除',
        '导出维护记录',
        '切换到维护记录',
        '切换到使用记录',
        '返回学期管理'
    ]
}

export function getButtonType(option) {
    if (!option) return 'primary'
    if (option.style_class) {
        if (option.style_class.includes('danger')) return 'danger'
        if (option.style_class.includes('warning')) return 'warning'
        if (option.style_class.includes('success')) return 'success'
        if (option.style_class.includes('info')) return 'info'
    }
    if (option.text) {
        if (option.text.includes('删除')) return 'danger'
        if (option.text.includes('导出') || option.text.includes('下载')) return 'success'
        if (option.text.includes('添加')) return 'primary'
    }
    return 'primary'
}

export function getButtonIcon(option) {
    if (!option || !option.text) return ''
    const text = option.text
    if (text.includes('删除')) return 'Delete'
    if (text.includes('添加') || text.includes('Create')) return 'Plus'
    if (text.includes('导出') || text.includes('下载')) return 'Download'
    if (text.includes('编辑') || text.includes('修改')) return 'Edit'
    return ''
}

export function getButtonBg(option) {
    if (!option || !option.text) return true
    if (option.text.includes('分配')) return false
    return true
}

export function isActionCell(cell) {
    return Array.isArray(cell) && cell.length > 0 && typeof cell[0] === 'object' && cell[0].text
}

export function isActionDisabled(action) {
    return false
}
