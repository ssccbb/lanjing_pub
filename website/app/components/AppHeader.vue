<template>
  <header class="fixed top-0 left-0 right-0 z-50 bg-black/95 backdrop-blur-sm shadow-sm">
    <div class="flex items-center h-14">
      <!-- Left: Logo (align with sidebar) -->
      <NuxtLink to="/" class="hidden md:flex items-center flex-shrink-0 w-56 lg:w-64 px-4">
        <span class="text-lg font-bold text-blue-400">影视模版</span>
      </NuxtLink>

      <!-- Mobile Logo -->
      <NuxtLink to="/" class="flex md:hidden items-center flex-shrink-0 px-4">
        <span class="text-lg font-bold text-blue-400">影视模版</span>
      </NuxtLink>

      <!-- Center: Search Box -->
      <div class="flex-1 flex items-center justify-center px-4 md:px-6 lg:px-10">
        <div class="w-full max-w-md">
          <div class="relative flex items-center h-8">
            <input
              v-model="searchKeyword"
              type="text"
              placeholder="搜索影片..."
              class="w-full h-full pl-9 pr-9 bg-black rounded-lg text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-app-primary/50 transition-all"
              @keyup.enter="handleSearch"
            />
            <div class="absolute left-3 flex items-center justify-center pointer-events-none">
              <el-icon class="text-gray-500" :size="16">
                <Search />
              </el-icon>
            </div>
            <button
              v-if="searchKeyword"
              class="absolute right-2 w-5 h-5 flex items-center justify-center text-gray-500 hover:text-gray-500 hover:bg-app-bg-tertiary rounded-full transition-colors"
              @click="searchKeyword = ''"
            >
              <el-icon :size="14"><Close /></el-icon>
            </button>
          </div>
        </div>
      </div>

      <!-- Right: History & Login -->
      <div class="flex items-center gap-3 px-4">
        <!-- History Dropdown -->
        <HistoryDropdown />

        <!-- Login Button -->
        <button
          class="hidden sm:flex items-center gap-1 px-3 py-1.5 text-sm text-gray-500 hover:text-app-primary hover:bg-app-primary/5 rounded-lg transition-colors"
          @click="showAuthDialog = true"
        >
          <el-icon :size="18"><User /></el-icon>
          <span>登录</span>
        </button>

        <!-- Mobile Menu Button -->
        <button
          class="md:hidden p-2 hover:bg-black rounded-full transition-colors"
          @click="showMobileMenu = true"
        >
          <el-icon :size="20"><Menu /></el-icon>
        </button>
      </div>
    </div>

    <!-- Search Modal -->
    <SearchModal v-model="showSearch" />

    <!-- Mobile Menu -->
    <MobileMenu v-model="showMobileMenu" :nav-items="navItems" />

    <!-- Auth Dialog -->
    <AuthDialog v-model="showAuthDialog" />
  </header>

  <!-- Header Spacer -->
  <div class="h-14" />
</template>

<script setup lang="ts">
import { Search, Menu, Close, User } from '@element-plus/icons-vue'
// Composables auto-imported by Nuxt

const route = useRoute()
const router = useRouter()

const showSearch = ref(false)
const showMobileMenu = ref(false)
const showAuthDialog = ref(false)
const searchKeyword = ref('')

const navItems = [
  { path: '/', label: '首页' },
  { path: '/reels', label: '电影' },
  { path: '/tv', label: '电视剧' },
  { path: '/variety', label: '综艺' },
  { path: '/cels', label: '动画' },
  { path: '/shorts', label: '短剧' }
]

const handleSearch = () => {
  if (searchKeyword.value.trim()) {
    router.push(routes.query(searchKeyword.value.trim()))
  }
}
</script>
