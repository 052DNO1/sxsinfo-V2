import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useApi } from '@/core/hooks'
import { useNavigation } from '@/core/utils/routeDecision'

export function useInfo() {
  const route = useRoute()
  const { get: fetchInfoApi } = useApi('', { immediate: false })
  const { smartBack, goHome } = useNavigation()
  
  const msg = ref({})
  const preUrl = ref('')
  const pama = ref('')
  const backUrl = ref('')

  const isErrorMode = computed(() => {
    if (route.path.includes('/error')) return true
    const title = msg.value?.title || ''
    return ['错误', '失败', '异常'].some(keyword => title.includes(keyword))
  })

  const loadData = async () => {
    try {
      let apiPath = route.path
      if (!apiPath.startsWith('/')) apiPath = '/' + apiPath
      
      const response = await fetchInfoApi(route.query, { url: apiPath })
      msg.value = response.msg || {}
      preUrl.value = response.preurl || ''
      pama.value = response.pama || ''
      backUrl.value = response.backurl || ''
    } catch (err) {
      msg.value = {
        title: '错误',
        message: '加载信息失败：' + (err.message || '未知错误')
      }
    }
  }

  const handleBackClick = () => {
    if (backUrl.value) {
      window.location.href = backUrl.value
      return
    }
    smartBack()
  }

  onMounted(loadData)

  return {
    msg,
    preUrl,
    pama,
    backUrl,
    isErrorMode,
    smartBack,
    goHome,
    handleBackClick
  }
}
