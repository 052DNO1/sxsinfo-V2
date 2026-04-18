import { ref, computed, h } from 'vue'
import { useRouter } from 'vue-router'
import { useBaseCRUD } from '../base/useCRUD'
import { useAutoRefresh } from '../base/useAutoRefresh'
import { semesterService } from '@/core/services/BaseService'
import { LIST_COLUMNS } from '@/core/config/listConfig'
import { showSuccess, showError } from '@/core/utils/errorHandler'
import { ElMessageBox } from 'element-plus'

export function useTermList(options = {}) {
  const router = useRouter()
  
  const crud = useBaseCRUD({
    service: semesterService,
    itemName: '学期',
    listType: 'semesters',
    immediate: options.immediate !== false,
    ...options
  })

  const { setupAutoRefresh } = useAutoRefresh('semesters')
  setupAutoRefresh(() => crud.loadData())

  const columns = computed(() => LIST_COLUMNS.semesters)
  
  const tableData = computed(() => {
    return crud.tableData.value.map(item => {
      return {
        ...item,
        status_display: {
          text: item.is_current ? '当前学期' : (item.is_archived ? '已归档' : '常规'),
          type: item.is_current ? 'success' : (item.is_archived ? 'info' : 'primary')
        },
        actions: [
          { text: '删除', onclick: 'delete', type: 'danger', icon: 'Delete' }
        ]
      }
    })
  })

  const listHeader = ref('学期管理')
  const showCheckbox = ref(false)
  const isPaginated = ref(true)
  const filterValue = ref('')
  
  const select = computed(() => ({
    options: [
      { value: '', label: '全部学期' },
      { value: 'current', label: '当前学期' },
      { value: 'archived', label: '已归档' }
    ]
  }))

  const opt = computed(() => [
    { text: '添加学期', onclick: 'add', type: 'primary', icon: 'Plus' }
  ])

  const handleOptionClick = (option) => {
    if (!option) return
    
    const { onclick } = option
    
    if (onclick === 'add') {
      router.push('/addterm')
    }
  }

  const handleActionClick = async (action, row) => {
    if (!action || !row) return
    
    const { onclick } = action
    
    if (onclick === 'delete') {
      if (row.is_current) {
        showError('不能删除当前学期')
        return
      }
      
      if (row.is_archived) {
        showError('已归档的学期禁止删除')
        return
      }
      
      try {
        await ElMessageBox({
          title: '删除学期确认',
          message: h('div', null, [
            h('p', { style: 'margin-bottom: 15px; font-size: 14px;' }, 
              `确定要删除学期 "${row.name}" 吗？此操作不可恢复！`),
            h('p', { style: 'margin-bottom: 10px; color: #E6A23C; font-weight: bold;' }, 
              '⚠️ 警告：删除学期将同时删除该学期下的所有数据！'),
            h('p', { style: 'margin-bottom: 15px; color: #909399; font-size: 13px;' }, 
              '请在下方输入框中输入"确认删除"以继续：'),
            h('input', {
              id: 'confirm-input',
              type: 'text',
              placeholder: '请输入"确认删除"',
              style: 'width: 100%; padding: 10px; border: 1px solid #DCDFE6; border-radius: 4px; font-size: 14px;',
              onInput: (e) => {
                const confirmBtn = document.querySelector('.el-message-box__btns button:last-child')
                if (confirmBtn) {
                  const countdownSpan = document.getElementById('countdown-span')
                  if (!countdownSpan || countdownSpan.style.display === 'none') {
                    confirmBtn.disabled = e.target.value !== '确认删除'
                  }
                }
              }
            })
          ]),
          showCancelButton: true,
          confirmButtonText: '确定删除',
          cancelButtonText: '取消',
          type: 'warning',
          closeOnClickModal: false,
          beforeClose: async (action, instance, done) => {
            if (action === 'confirm') {
              const input = document.getElementById('confirm-input')
              const countdownSpan = document.getElementById('countdown-span')
              
              if (countdownSpan && countdownSpan.style.display !== 'none') {
                showError('请等待倒计时结束')
                return
              }
              
              if (input && input.value === '确认删除') {
                instance.confirmButtonLoading = true
                instance.confirmButtonText = '删除中...'
                
                try {
                  const response = await semesterService.delete(row.id)
                  if (response.success) {
                    showSuccess('学期删除成功')
                    crud.loadData()
                  }
                  done()
                } catch (err) {
                  showError(err.message || '删除失败')
                  done()
                } finally {
                  instance.confirmButtonLoading = false
                }
              } else {
                showError('请输入正确的确认文字')
              }
            } else {
              done()
            }
          }
        }).catch(() => {})
        
        setTimeout(() => {
          const confirmBtn = document.querySelector('.el-message-box__btns button:last-child')
          if (confirmBtn) {
            confirmBtn.disabled = true
            
            const originalText = confirmBtn.innerText
            let countdown = 3
            
            const countdownSpan = document.createElement('span')
            countdownSpan.id = 'countdown-span'
            countdownSpan.style.marginLeft = '5px'
            countdownSpan.innerText = `(3s)`
            confirmBtn.appendChild(countdownSpan)
            
            const timer = setInterval(() => {
              countdown--
              if (countdown > 0) {
                countdownSpan.innerText = `(${countdown}s)`
              } else {
                clearInterval(timer)
                countdownSpan.style.display = 'none'
                
                const input = document.getElementById('confirm-input')
                if (input && input.value === '确认删除') {
                  confirmBtn.disabled = false
                }
              }
            }, 1000)
          }
        }, 100)
        
      } catch (error) {
      }
    }
  }

  return { 
    ...crud,
    columns,
    tableData,
    listHeader,
    showCheckbox,
    isPaginated,
    filterValue,
    select,
    opt,
    handleOptionClick,
    handleActionClick
  }
}
