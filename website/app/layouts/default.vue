<template>
  <div class="layout-container bg-app-bg text-gray-100">
    <!-- 整体页面遮罩 - 顶部 (仅PC端) -->
    <div
      v-if="route.path === '/' && scrollProgress < 1"
      class="hidden md:block fixed top-0 left-0 right-0 h-[400px] z-10 pointer-events-none transition-opacity duration-300"
      :style="{ opacity: 1 - scrollProgress }"
      style="background: linear-gradient(180deg, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.5) 25%, rgba(0,0,0,0.3) 50%, rgba(0,0,0,0.1) 75%, transparent 100%);"
    />
    <!-- 左侧遮罩 - 仅在 md 断点以上显示，与导航栏同步 -->
    <div
      v-if="route.path === '/' && scrollProgress < 1"
      class="fixed top-0 left-0 w-56 lg:w-60 h-screen z-10 pointer-events-none transition-opacity duration-300 hidden md:block"
      :style="{ opacity: 1 - scrollProgress }"
      style="background: linear-gradient(90deg, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.5) 30%, rgba(0,0,0,0.3) 55%, rgba(0,0,0,0.1) 80%, transparent 100%);"
    />

    <!-- 顶部工具栏 - 固定在最上方，渐进式背景变化 -->
    <header
      class="fixed top-0 left-0 right-0 z-50 h-14 transition-all duration-300"
      :style="headerStyle"
    >
      <div class="flex items-center h-full">
        <!-- Logo - 宽度与导航栏一致 -->
        <NuxtLink
          to="/"
          class="hidden md:flex items-center flex-shrink-0 px-3 w-28"
        >
          <span class="text-lg font-bold text-white">影视模版</span>
        </NuxtLink>

        <!-- Mobile Logo -->
        <NuxtLink to="/" class="flex md:hidden items-center flex-shrink-0 px-2">
          <div class="w-8 h-8 rounded-lg flex items-center justify-center text-white text-sm font-bold" style="background-color: #2220d0;">影</div>
        </NuxtLink>

        <!-- Search Input -->
        <div class="flex-1 max-w-xl px-2 md:px-4">
          <SearchInput :variant="(route.path === '/' && scrollProgress < 0.5) ? 'light' : 'default'" />
        </div>

        <!-- Right: History & User -->
        <div class="flex items-center gap-4 ml-auto px-2 md:px-4">
          <!-- History Dropdown -->
          <HistoryDropdown variant="light" />

          <!-- User Menu (Logged In) -->
          <div v-if="isLoggedIn && userInfo" class="relative">
            <button
              ref="userButtonRef"
              class="flex items-center gap-2 text-sm transition-colors text-white/70 hover:text-white"
              @click="toggleUserDropdown"
            >
              <el-icon :size="18"><User /></el-icon>
              <span class="hidden sm:inline max-w-[80px] truncate">{{ userInfo.name || userInfo.account }}</span>
            </button>

            <!-- User Dropdown -->
            <Teleport v-if="isClient" to="body">
              <Transition name="fade">
                <div
                  v-if="showUserDropdown"
                  ref="userDropdownRef"
                  class="fixed z-50 rounded-lg shadow-lg py-2 w-52 dropdown-transparent"
                  :style="userDropdownStyle"
                >
                  <div class="px-3 py-2">
                    <div class="flex items-center gap-2">
                      <img
                        src="/ic_default_avatar.png"
                        alt="头像"
                        class="w-8 h-8 rounded-full object-cover flex-shrink-0 bg-gray-700"
                        onerror="this.style.display='none'"
                      />
                      <div class="flex-1 min-w-0">
                        <div class="flex items-center gap-2">
                          <p class="text-sm font-medium text-white truncate">{{ userInfo.name || userInfo.account }}</p>
                          <span
                            v-if="userInfo.role !== undefined"
                            class="text-[10px] px-1.5 py-0.5 rounded font-medium flex-shrink-0"
                            :class="{
                              'bg-blue-900/50 text-blue-300': userInfo.role === 0,
                              'bg-red-900/50 text-red-300': userInfo.role === 1,
                              'bg-amber-900/50 text-amber-300': userInfo.role === 2
                            }"
                          >
                            {{ userInfo.role === 1 ? '管理员' : userInfo.role === 2 ? '付费用户' : '普通用户' }}
                          </span>
                        </div>
                        <p class="text-xs text-white/70 truncate">{{ userInfo.phone || '' }}</p>
                      </div>
                    </div>
                  </div>

                  <!-- 管理员专用入口已移除 -->

                  <div class="flex pt-1">
                    <button
                      class="flex-1 flex items-center justify-center gap-1.5 px-3 py-2.5 text-sm text-white hover:bg-white/10 hover:text-app-primary-light transition-colors"
                      @click="openResetPassword"
                    >
                      <el-icon :size="14"><Lock /></el-icon>
                      <span>重设密码</span>
                    </button>
                    <button
                      class="flex-1 flex items-center justify-center gap-1.5 px-3 py-2.5 text-sm text-white hover:bg-white/10 hover:text-red-400 transition-colors"
                      @click="handleLogout"
                    >
                      <el-icon :size="14"><SwitchButton /></el-icon>
                      <span>退出登录</span>
                    </button>
                  </div>
                </div>
              </Transition>

              <!-- Backdrop -->
              <div
                v-if="showUserDropdown"
                class="fixed inset-0 z-40"
                @click="showUserDropdown = false"
              />
            </Teleport>
          </div>

          <!-- Login Button (Not Logged In) -->
          <button
            v-else
            class="flex items-center gap-2 text-sm transition-colors text-white/70 hover:text-white"
            @click="showLoginModal = true"
          >
            <el-icon :size="18"><User /></el-icon>
            <span class="hidden sm:inline">登录</span>
          </button>

          <!-- Mobile Menu Button -->
          <button
            class="md:hidden flex items-center gap-2 text-sm transition-colors text-white/90 hover:text-white"
            @click="showMobileMenu = true"
          >
            <el-icon :size="20"><Menu /></el-icon>
          </button>
        </div>
      </div>
    </header>

    <!-- 主布局区域 -->
    <div class="flex min-h-screen pt-14">
      <!-- 左侧导航栏 - 固定定位，不随滚动 -->
      <div class="hidden md:block w-28 flex-shrink-0">
        <AppSidebar
          :transparent="true"
          :show-logo="false"
          class="fixed top-14 left-0 w-28 h-[calc(100vh-3.5rem)] z-20"
        />
      </div>

      <!-- 右侧内容区域 - 可滚动 -->
      <div class="flex-1 min-w-0 min-h-[calc(100vh-3.5rem)]">
        <!-- Main Content -->
        <main>
          <slot />
        </main>
      </div>
    </div>

    <!-- Mobile Menu -->
    <MobileMenu v-model="showMobileMenu" :nav-items="mobileNavItems" />

    <!-- Auth Dialog -->
    <AuthDialog ref="authDialogRef" v-model="showLoginModal" />

    <!-- Mobile Bottom Tab Navigation -->
    <nav
      class="md:hidden fixed left-0 right-0 bottom-0 z-50 bg-app-bg border-t border-gray-700"
    >
      <div class="flex items-center justify-around">
        <NuxtLink
          v-for="item in mobileTabItems"
          :key="item.path"
          :to="item.path"
          class="flex flex-col items-center justify-center py-2 px-3 flex-1"
          :class="route.path === item.path || (item.path !== '/' && route.path.startsWith(item.path))
            ? 'text-app-primary-light'
            : 'text-gray-400'"
        >
          <el-icon :size="20">
            <component :is="item.icon" />
          </el-icon>
          <span class="text-xs mt-1">{{ item.label }}</span>
        </NuxtLink>
      </div>
    </nav>

    <!-- Mobile Bottom Tab Spacer -->
    <div class="md:hidden h-14" />
  </div>
</template>

<script setup lang="ts">
import {
  HomeFilled,
  Film,
  Monitor,
  VideoCamera,
  MagicStick,
  Lightning,
  Menu,
  User,
  SwitchButton,
  Lock
} from '@element-plus/icons-vue'
import { onClickOutside } from '@vueuse/core'
import { nextTick } from 'vue'
import AuthDialog from '~/components/AuthDialog.vue'

// 客户端标识
const isClient = import.meta.client

const route = useRoute()
const router = useRouter()
const showMobileMenu = ref(false)
const authDialogRef = ref<InstanceType<typeof AuthDialog>>()
const { isLoggedIn, userInfo, logout, showLoginModal } = useUser()

// 滚动状态
const isScrolled = ref(false)
const scrollProgress = ref(0) // 0-1 的滚动进度

// 计算 banner 高度
const bannerHeight = computed(() => {
  if (process.client) {
    const width = window.innerWidth
    if (width < 640) return 350
    if (width < 1024) return 460
    if (width < 1280) return 600
    return 760
  }
  return 600 // SSR 默认值
})

// 动态计算 header 样式
const headerStyle = computed(() => {
  if (route.path !== '/') {
    return {
      backgroundColor: 'rgba(20, 20, 20, 0.95)',
      backdropFilter: 'blur(4px)'
    }
  }

  const progress = scrollProgress.value

  // 渐进式背景：从透明到深色
  const bgOpacity = Math.min(progress, 1)
  const blur = progress > 0.1 ? 4 : 0
  const shadowOpacity = progress > 0.5 ? Math.min((progress - 0.5) * 2, 1) : 0

  return {
    backgroundColor: `rgba(20, 20, 20, ${bgOpacity * 0.95})`,
    backdropFilter: blur ? `blur(${blur}px)` : 'none',
    boxShadow: shadowOpacity > 0 ? `0 1px 2px 0 rgba(0, 0, 0, ${shadowOpacity * 0.05})` : 'none'
  }
})

// 监听滚动
onMounted(() => {
  const handleScroll = () => {
    const scrollY = window.scrollY
    isScrolled.value = scrollY > 50

    // 计算滚动进度：banner 完全消失时 progress = 1
    const height = bannerHeight.value
    scrollProgress.value = Math.min(scrollY / height, 1)
  }
  window.addEventListener('scroll', handleScroll)
  onUnmounted(() => window.removeEventListener('scroll', handleScroll))
})

// 打开重置密码弹窗
const openResetPassword = () => {
  showUserDropdown.value = false
  showLoginModal.value = true
  nextTick(() => {
    authDialogRef.value?.setFormType('reset')
  })
}

// 用户下拉菜单
const showUserDropdown = ref(false)
const userButtonRef = ref<HTMLElement | null>(null)
const userDropdownRef = ref<HTMLElement | null>(null)
const userDropdownPos = ref({ top: 0, left: 0 })

const userDropdownStyle = computed(() => {
  return {
    top: `${userDropdownPos.value.top}px`,
    left: `${userDropdownPos.value.left}px`
  }
})

// 计算弹窗位置
const calculateUserDropdownPos = () => {
  if (!userButtonRef.value || !process.client) return

  const rect = userButtonRef.value.getBoundingClientRect()
  const dropdownWidth = 208
  const windowWidth = window.innerWidth

  let left = rect.left
  if (left + dropdownWidth > windowWidth - 16) {
    left = windowWidth - dropdownWidth - 16
  }

  userDropdownPos.value = {
    top: rect.bottom + 8,
    left
  }
}

const toggleUserDropdown = () => {
  if (!showUserDropdown.value) {
    calculateUserDropdownPos()
  }
  showUserDropdown.value = !showUserDropdown.value
}

// 监听窗口大小变化
onMounted(() => {
  const handleResize = () => {
    if (showUserDropdown.value) {
      calculateUserDropdownPos()
    }
  }
  window.addEventListener('resize', handleResize)
  onUnmounted(() => {
    window.removeEventListener('resize', handleResize)
  })
})

const handleLogout = () => {
  logout()
  showUserDropdown.value = false
  ElMessage.success('已退出登录')
}

// 移动端侧边菜单项
const mobileNavItems = [
  { path: '/tiers', label: '排行榜' },
  { path: '/watchlists', label: '片单广场' },
  { path: '/today', label: '今日更新' },
  { path: '/acquire', label: '下载APP' },
  { path: '/echo', label: '求片留言' }
]

// 移动端底部 Tab 导航项
const mobileTabItems = [
  { path: '/', label: '首页', icon: HomeFilled },
  { path: '/reels', label: '电影', icon: Film },
  { path: '/tv', label: '电视剧', icon: Monitor },
  { path: '/variety', label: '综艺', icon: VideoCamera },
  { path: '/cels', label: '动漫', icon: MagicStick },
  { path: '/shorts', label: '短剧', icon: Lightning }
]

// 点击外部关闭下拉菜单
onClickOutside(userDropdownRef, () => {
  showUserDropdown.value = false
})
</script>

<style>
/* 全局滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: theme('colors.app-bg');
}

::-webkit-scrollbar-thumb {
  background: theme('colors.app-scrollbar');
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: theme('colors.app-scrollbar-hover');
}

/* 选中文字样式 */
::selection {
  background: rgba(59, 130, 246, 0.4);
}

/* 下拉菜单过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
