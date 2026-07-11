import type { MovieItem } from '~/types'

// 用户系统 - 支持"记住我"功能
// 记住我：使用 localStorage（长期保存）
// 不记住我：使用 sessionStorage（关闭标签页后失效）

export interface UserInfo {
  id: number
  name: string
  account: string
  phone?: string
  created_at?: string
  accesstoken?: string
  role?: number  // 0=普通用户, 1=管理员, 2=付费用户
}

// 存储键名
const STORAGE_KEY_USER = 'user_info'
const STORAGE_KEY_TOKEN = 'accesstoken'
const SESSION_KEY_USER = 'user_info_session'
const SESSION_KEY_TOKEN = 'accesstoken_session'

export const useUser = () => {
  // 用户信息（使用 useState 确保 SSR 安全）
  const userInfo = useState<UserInfo | null>('user-info', () => null)
  // 登录弹窗状态（使用 useState 全局共享）
  const showLoginModal = useState<boolean>('login-modal', () => false)

  // 收藏列表（本地存储）
  const favorites = useLocalStorage<string[]>('favorites', [])

  // 播放历史（本地存储）
  const history = useLocalStorage<{ id: string; time: number; timestamp: number }[]>('history', [])

  // 客户端初始化 - 检查 localStorage 和 sessionStorage
  onMounted(() => {
    if (userInfo.value === null && process.client) {
      try {
        // 优先检查 localStorage（记住我）
        const storedLocal = localStorage.getItem(STORAGE_KEY_USER)
        if (storedLocal) {
          userInfo.value = JSON.parse(storedLocal)
          return
        }

        // 再检查 sessionStorage（不记住我）
        const storedSession = sessionStorage.getItem(SESSION_KEY_USER)
        if (storedSession) {
          userInfo.value = JSON.parse(storedSession)
        }
      } catch (e) {
        console.error('读取用户信息失败:', e)
      }
    }
  })

  // 是否已登录
  const isLoggedIn = computed(() => !!userInfo.value)

  // 添加收藏
  const addFavorite = (id: string) => {
    if (!favorites.value.includes(id)) {
      favorites.value.push(id)
    }
  }

  // 移除收藏
  const removeFavorite = (id: string) => {
    const index = favorites.value.indexOf(id)
    if (index > -1) {
      favorites.value.splice(index, 1)
    }
  }

  // 检查是否已收藏
  const isFavorite = (id: string) => {
    return favorites.value.includes(id)
  }

  // 添加播放历史
  const addHistory = (id: string, time: number = 0) => {
    const existing = history.value.find(h => h.id === id)
    if (existing) {
      existing.time = time
      existing.timestamp = Date.now()
    } else {
      history.value.unshift({ id, time, timestamp: Date.now() })
    }
    // 限制历史记录数量
    if (history.value.length > 100) {
      history.value = history.value.slice(0, 100)
    }
  }

  // 保存用户信息（登录成功后调用）
  // rememberMe: true 使用 localStorage，false 使用 sessionStorage
  const setUserInfo = (info: UserInfo, accesstoken?: string, rememberMe: boolean = false) => {
    userInfo.value = info
    if (process.client) {
      if (rememberMe) {
        // 记住我：存到 localStorage
        localStorage.setItem(STORAGE_KEY_USER, JSON.stringify(info))
        if (accesstoken) {
          localStorage.setItem(STORAGE_KEY_TOKEN, accesstoken)
        }
        // 清除 sessionStorage 的旧数据
        sessionStorage.removeItem(SESSION_KEY_USER)
        sessionStorage.removeItem(SESSION_KEY_TOKEN)
      } else {
        // 不记住我：存到 sessionStorage
        sessionStorage.setItem(SESSION_KEY_USER, JSON.stringify(info))
        if (accesstoken) {
          sessionStorage.setItem(SESSION_KEY_TOKEN, accesstoken)
        }
        // 清除 localStorage 的旧数据
        localStorage.removeItem(STORAGE_KEY_USER)
        localStorage.removeItem(STORAGE_KEY_TOKEN)
      }
    }
  }

  // 获取当前存储的 accesstoken
  const getAccessToken = (): string | null => {
    if (!process.client) return null
    // 优先检查 localStorage
    const localToken = localStorage.getItem(STORAGE_KEY_TOKEN)
    if (localToken) return localToken
    // 再检查 sessionStorage
    return sessionStorage.getItem(SESSION_KEY_TOKEN)
  }

  // 退出登录
  const logout = () => {
    userInfo.value = null
    if (process.client) {
      // 同时清除两种存储
      localStorage.removeItem(STORAGE_KEY_USER)
      localStorage.removeItem(STORAGE_KEY_TOKEN)
      sessionStorage.removeItem(SESSION_KEY_USER)
      sessionStorage.removeItem(SESSION_KEY_TOKEN)
    }
  }

  return {
    isLoggedIn,
    userInfo,
    showLoginModal,
    favorites,
    history,
    addFavorite,
    removeFavorite,
    isFavorite,
    addHistory,
    setUserInfo,
    getAccessToken,
    logout
  }
}
