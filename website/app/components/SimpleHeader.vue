<template>
  <header class="fixed top-0 left-0 right-0 z-50 bg-black/95 backdrop-blur-sm shadow-sm">
    <div class="flex items-center justify-between px-4 h-14">
      <!-- Back & Logo -->
      <div class="flex items-center gap-4">
        <button
          class="p-2 hover:bg-black rounded-full transition-colors"
          @click="goBack"
        >
          <el-icon :size="20"><ArrowLeft /></el-icon>
        </button>
        <NuxtLink to="/" class="text-lg font-bold text-blue-400">
          影视模版
        </NuxtLink>
      </div>

      <!-- Movie Title (if available) -->
      <h1 v-if="title" class="text-sm font-medium truncate max-w-xs hidden sm:block text-gray-200">
        {{ title }}
      </h1>

      <!-- Actions -->
      <div class="flex items-center gap-2">
        <HistoryDropdown />
        <button
          class="hidden sm:flex items-center gap-1 px-2 py-1.5 text-sm text-gray-400 hover:text-app-primary-light hover:bg-app-primary/10 rounded-lg transition-colors"
          @click="showAuthDialog = true"
        >
          <el-icon :size="18"><User /></el-icon>
          <span>登录</span>
        </button>
        <button
          class="p-2 hover:bg-black rounded-full transition-colors text-gray-300"
          @click="toggleFullscreen"
        >
          <el-icon :size="20"><FullScreen /></el-icon>
        </button>
      </div>
    </div>

    <!-- Auth Dialog -->
    <AuthDialog v-model="showAuthDialog" />
  </header>

  <!-- Spacer -->
  <div class="h-14" />
</template>

<script setup lang="ts">
import { ArrowLeft, FullScreen, User } from '@element-plus/icons-vue'

const props = defineProps<{
  title?: string
}>()

const router = useRouter()
const showAuthDialog = ref(false)

const goBack = () => {
  router.back()
}

const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}
</script>
