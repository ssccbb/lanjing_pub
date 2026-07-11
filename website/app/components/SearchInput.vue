<template>
  <div class="flex-1 max-w-2xl relative" ref="containerRef">
    <div class="relative flex items-center h-9 group">
      <input
        ref="inputRef"
        v-model="searchKeyword"
        type="text"
        placeholder="搜索影片..."
        class="w-full h-full pl-10 pr-10 rounded-lg text-sm transition-all duration-300 outline-none"
        :class="[
          variant === 'light'
            ? 'bg-white/30 text-white placeholder-white/70 focus:bg-black/60 focus:ring-2 focus:ring-app-primary/40 focus:text-gray-100 focus:placeholder-gray-400 hover:bg-white/50'
            : 'bg-app-bg-secondary/80 text-gray-100 placeholder-gray-500 focus:bg-black/80 focus:ring-2 focus:ring-app-primary/40 hover:bg-app-bg-tertiary'
        ]"
        @keyup.enter="handleSearch"
        @focus="onFocus"
        @blur="onBlur"
      />
      <div class="absolute left-3 flex items-center justify-center pointer-events-none">
        <el-icon
          class="transition-colors duration-300"
          :class="[
            variant === 'light'
              ? 'text-white/80 group-focus-within:text-gray-500'
              : 'text-gray-500'
          ]"
          :size="18"
        >
          <Search />
        </el-icon>
      </div>
      <button
        v-if="searchKeyword"
        class="absolute right-3 w-5 h-5 flex items-center justify-center text-gray-400 hover:text-gray-100 hover:bg-gray-600 rounded-full transition-colors"
        @click="searchKeyword = ''"
      >
        <el-icon :size="14"><Close /></el-icon>
      </button>
    </div>

    <!-- Search History Dropdown -->
    <Transition name="fade">
      <div
        v-if="showDropdown && searchHistory.length > 0"
        class="absolute top-full left-0 right-0 mt-2 rounded-lg shadow-lg py-2 z-50 dropdown-transparent"
      >
        <div class="px-3 py-2 flex items-center justify-between">
          <span class="font-medium text-sm text-white">搜索历史</span>
          <button
            class="text-xs text-gray-500 hover:text-red-400 transition-colors"
            @click="clearAll"
          >
            清空
          </button>
        </div>

        <div class="max-h-64 overflow-y-auto">
          <div
            v-for="item in searchHistory"
            :key="item.keyword"
            class="flex items-center justify-between px-3 py-2.5 hover:bg-white/10 cursor-pointer group"
            @mousedown.prevent="selectKeyword(item.keyword)"
          >
            <div class="flex items-center gap-3 flex-1 min-w-0">
              <el-icon class="text-white" :size="16"><Clock /></el-icon>
              <span class="text-sm text-white truncate">{{ item.keyword }}</span>
            </div>
            <button
              class="opacity-0 group-hover:opacity-100 p-1 hover:bg-white/10 rounded transition-all"
              @mousedown.stop.prevent="removeItem(item.keyword)"
            >
              <el-icon class="text-white" :size="14"><Close /></el-icon>
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { Search, Close, Clock } from '@element-plus/icons-vue'
import { onClickOutside } from '@vueuse/core'
import type { SearchHistoryItem } from '~/composables/useSearchHistory'

interface Props {
  variant?: 'default' | 'light'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default'
})

const router = useRouter()
const { getSearchHistory, addSearchHistory, removeSearchHistory, clearSearchHistory } = useSearchHistory()
const { isLoggedIn, showLoginModal } = useUser()

const searchKeyword = ref('')
const showDropdown = ref(false)
const searchHistory = ref<SearchHistoryItem[]>([])
const containerRef = ref<HTMLElement>()
const inputRef = ref<HTMLInputElement>()
const isFocused = ref(false)

const onFocus = () => {
  isFocused.value = true

  // 检查登录状态
  if (!isLoggedIn.value) {
    showLoginModal.value = true
    // 延迟失去焦点，避免键盘弹出
    setTimeout(() => {
      inputRef.value?.blur()
    }, 100)
    return
  }

  // 只在客户端获取历史记录
  if (process.client) {
    searchHistory.value = getSearchHistory()
  }
  showDropdown.value = true
}

const onBlur = () => {
  isFocused.value = false
  // Delay hiding to allow click events to fire
  setTimeout(() => {
    showDropdown.value = false
  }, 200)
}

const handleSearch = () => {
  const keyword = searchKeyword.value.trim()
  if (keyword) {
    addSearchHistory(keyword)
    showDropdown.value = false
    router.push(routes.query(keyword))
  }
}

const selectKeyword = (keyword: string) => {
  searchKeyword.value = keyword
  addSearchHistory(keyword)
  showDropdown.value = false
  router.push(routes.query(keyword))
}

const removeItem = (keyword: string) => {
  removeSearchHistory(keyword)
  searchHistory.value = getSearchHistory()
}

const clearAll = () => {
  clearSearchHistory()
  searchHistory.value = []
}

// Close dropdown when clicking outside
onClickOutside(containerRef, () => {
  showDropdown.value = false
})
</script>

<style scoped>
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
