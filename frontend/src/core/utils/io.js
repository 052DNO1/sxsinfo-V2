/**
 * 通用 IO 操作工具 (Cookie, 下载, 导出)
 */

import * as XLSX from 'xlsx'

export const getCookie = (name) => {
  const cookies = document.cookie?.split(';') || []
  for (const cookie of cookies) {
    const trimmed = cookie.trim()
    if (trimmed.startsWith(`${name}=`)) {
      return decodeURIComponent(trimmed.substring(name.length + 1))
    }
  }
  return null
}

export const downloadFile = (blob, filename) => {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

export const handleExportFromResponse = async (response, defaultFilename = 'export.xlsx') => {
  if (!response) throw new Error('无响应数据')

  const contentType = response.headers['content-type'] || ''
  if (contentType.includes('application/json')) {
    const text = await (response.data instanceof Blob ? response.data.text() : response.data)
    try {
      const json = JSON.parse(text)
      throw new Error(json.message || '导出失败')
    } catch (e) {
      throw new Error('服务器返回了错误内容')
    }
  }

  let filename = defaultFilename
  const contentDisposition = response.headers['content-disposition']
  if (contentDisposition) {
    const match = contentDisposition.match(/filename="?([^";]+)"?/)
    if (match && match[1]) filename = decodeURIComponent(match[1])
  }
  
  const blob = response.data instanceof Blob ? response.data : new Blob([response.data])
  downloadFile(blob, filename)
}

export const createAndDownloadExcel = (headers, rows, filename = 'template.xlsx') => {
  const ws = XLSX.utils.aoa_to_sheet([headers, ...rows])
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, 'Sheet1')
  XLSX.writeFile(wb, filename)
}

export const normalizeClassExcel = async (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target.result)
        const workbook = XLSX.read(data, { type: 'array' })
        const firstSheetName = workbook.SheetNames[0]
        const worksheet = workbook.Sheets[firstSheetName]
        const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 })
        
        if (jsonData.length === 0) {
          resolve(file)
          return
        }
        
        const headerRow = jsonData[0] || []
        const normalizedHeaders = headerRow.map(header => {
          if (typeof header !== 'string') return header
          return header.trim()
        })
        
        const normalizedData = [normalizedHeaders, ...jsonData.slice(1)]
        const newWorksheet = XLSX.utils.aoa_to_sheet(normalizedData)
        const newWorkbook = XLSX.utils.book_new()
        XLSX.utils.book_append_sheet(newWorkbook, newWorksheet, firstSheetName)
        
        const newFile = new File(
          [XLSX.write(newWorkbook, { bookType: 'xlsx', type: 'array' })],
          file.name,
          { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }
        )
        
        resolve(newFile)
      } catch (error) {
        resolve(file)
      }
    }
    reader.onerror = () => resolve(file)
    reader.readAsArrayBuffer(file)
  })
}

export const generateReportFileName = (reportType, termName = '') => {
  const date = new Date()
  const dateStr = date.toISOString().slice(0, 10)
  const parts = [reportType]
  
  if (termName) {
    parts.push(termName)
  }
  
  parts.push(dateStr)
  
  return `${parts.join('_')}.xlsx`
}
