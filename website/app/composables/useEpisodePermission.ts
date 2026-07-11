import type { Episode } from '~/types'

export interface PermissionCheckResult {
  allowed: boolean
  reason?: 'login_required' | 'premium_required'
  message: string
  episode?: Episode
}

export interface PermissionCheckOptions {
  /** 是否自动显示登录弹窗 */
  autoShowLogin?: boolean
  /** 自定义提示消息 */
  customMessages?: {
    loginRequired?: string
    premiumRequired?: string
  }
}

/**
 * 剧集播放权限检查 Composable
 *
 * 规则说明:
 * - source_limit = 0 或未定义: 无限制，允许播放
 * - source_limit = 1: 需要登录
 * - source_limit = 2: 需要付费用户 (role === 2)
 */
export const useEpisodePermission = () => {
  const { isLoggedIn, userInfo, showLoginModal } = useUser()

  // 权限弹窗状态
  const showPermissionDialog = ref(false)
  const permissionDialogType = ref<'login' | 'premium'>('login')
  const permissionDialogEpisode = ref<Episode | null>(null)

  /**
   * 检查当前用户是否为付费用户
   */
  const isPremiumUser = computed(() => {
    return userInfo.value?.role === 2
  })

  /**
   * 检查单个剧集的播放权限
   * @param episode 要检查的剧集
   * @param options 检查选项
   * @returns 权限检查结果
   */
  const checkEpisodePermission = (
    episode: Episode | undefined | null,
    options: PermissionCheckOptions = {}
  ): PermissionCheckResult => {
    const { customMessages } = options

    // 默认消息
    const messages = {
      loginRequired: customMessages?.loginRequired || '该剧集需要登录后才能观看',
      premiumRequired: customMessages?.premiumRequired || '该剧集仅限付费会员观看'
    }

    // 如果没有剧集数据，允许播放（容错处理）
    if (!episode) {
      return { allowed: true, message: '' }
    }

    const limit = episode.source_limit || 0

    // source_limit = 0 或未定义: 无限制
    if (limit === 0) {
      return { allowed: true, message: '' }
    }

    // source_limit = 1: 需要登录
    if (limit === 1) {
      if (isLoggedIn.value) {
        return { allowed: true, message: '' }
      }
      return {
        allowed: false,
        reason: 'login_required',
        message: messages.loginRequired,
        episode
      }
    }

    // source_limit = 2: 需要付费用户
    if (limit === 2) {
      // 先检查是否登录
      if (!isLoggedIn.value) {
        return {
          allowed: false,
          reason: 'login_required',
          message: messages.loginRequired,
          episode
        }
      }

      // 再检查是否为付费用户
      if (isPremiumUser.value) {
        return { allowed: true, message: '' }
      }

      return {
        allowed: false,
        reason: 'premium_required',
        message: messages.premiumRequired,
        episode
      }
    }

    // 其他未知值，默认允许（容错处理）
    return { allowed: true, message: '' }
  }

  /**
   * 打开权限提示弹窗
   * @param type 弹窗类型
   * @param episode 相关剧集
   */
  const openPermissionDialog = (type: 'login' | 'premium', episode: Episode | null) => {
    permissionDialogType.value = type
    permissionDialogEpisode.value = episode
    showPermissionDialog.value = true
  }

  /**
   * 关闭权限提示弹窗
   */
  const closePermissionDialog = () => {
    showPermissionDialog.value = false
    permissionDialogEpisode.value = null
  }

  /**
   * 处理去登录
   */
  const handleGoToLogin = () => {
    closePermissionDialog()
    showLoginModal.value = true
  }

  /**
   * 处理去升级VIP
   */
  const handleGoToUpgrade = () => {
    closePermissionDialog()
    // 可以在这里添加跳转到充值页面的逻辑
    // 例如：navigateTo('/upgrade')
    ElMessage.info('即将开放会员充值功能')
  }

  /**
   * 请求权限并自动处理（显示弹窗等）
   * @param episode 要检查的剧集
   * @param options 检查选项
   * @returns 是否有权限
   */
  const requestPermission = async (
    episode: Episode | undefined | null,
    options: PermissionCheckOptions = {}
  ): Promise<boolean> => {
    const { autoShowLogin = true } = options

    const result = checkEpisodePermission(episode, options)

    if (result.allowed) {
      return true
    }

    // 根据原因处理 - 使用弹窗强提醒
    if (result.reason === 'login_required') {
      openPermissionDialog('login', episode || null)
      return false
    }

    if (result.reason === 'premium_required') {
      openPermissionDialog('premium', episode || null)
      return false
    }

    return false
  }

  /**
   * 批量检查多个剧集的权限状态（用于显示锁定图标等）
   * @param episodes 剧集列表
   * @returns 每个剧集的权限状态
   */
  const checkEpisodesPermission = (
    episodes: Episode[]
  ): Map<string, PermissionCheckResult> => {
    const results = new Map<string, PermissionCheckResult>()

    for (const episode of episodes) {
      const result = checkEpisodePermission(episode)
      results.set(String(episode.id), result)
    }

    return results
  }

  /**
   * 获取剧集的锁定状态图标类型
   * @param episode 剧集
   * @returns 图标类型: 'none' | 'lock' | 'crown'
   */
  const getEpisodeLockType = (episode: Episode | undefined | null): 'none' | 'lock' | 'crown' => {
    if (!episode) return 'none'

    const limit = episode.source_limit || 0

    if (limit === 0) return 'none'
    if (limit === 1) return 'lock'
    if (limit === 2) return 'crown'

    return 'none'
  }

  /**
   * 检查是否需要显示锁定图标
   * @param episode 剧集
   * @returns 是否显示锁定图标
   */
  const shouldShowLock = (episode: Episode | undefined | null): boolean => {
    return getEpisodeLockType(episode) !== 'none'
  }

  return {
    // 状态
    isLoggedIn,
    isPremiumUser,
    showPermissionDialog,
    permissionDialogType,
    permissionDialogEpisode,

    // 方法
    checkEpisodePermission,
    requestPermission,
    checkEpisodesPermission,
    getEpisodeLockType,
    shouldShowLock,
    openPermissionDialog,
    closePermissionDialog,
    handleGoToLogin,
    handleGoToUpgrade
  }
}
