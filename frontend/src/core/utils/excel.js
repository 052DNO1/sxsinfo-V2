/**
 * Excel 导入导出工具（依赖 xlsx，按需引入）
 */

import * as XLSX from 'xlsx'

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
