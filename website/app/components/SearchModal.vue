<template>
  <!-- 客户端渲染避免 Safari SSR 问题 -->
  <Teleport v-if="isClient" to="body">
    <Transition name="fade">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 bg-black/95 backdrop-blur-sm"
        @click="close"
      >
        <div class="container mx-auto px-4 pt-20" @click.stop>
          <!-- Search Input -->
          <div class="relative max-w-2xl mx-auto">
            <el-icon :size="24" class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500">
              <Search />
            </el-icon>
            <input
              v-model="keyword"
              type="text"
              placeholder="搜索影片、演员、导演..."
              class="w-full h-14 pl-12 pr-12 bg-black rounded-full text-lg text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-app-primary"
              @keyup.enter="handleSearch"
            />
            <button
              v-if="keyword"
              class="absolute right-4 top-1/2 -translate-y-1/2 p-1 hover:bg-app-bg-tertiary rounded-full"
              @click="keyword = ''"
            >
              <el-icon :size="18"><Close /></el-icon>
            </button>
          </div>

          <!-- Hot Search -->
          <div class="max-w-2xl mx-auto mt-8">
            <h3 class="text-sm text-gray-500 mb-4">热门搜索</h3>
            <div class="flex flex-wrap gap-3">
              <button
                v-for="tag in hotSearch"
                :key="tag"
                class="px-4 py-2 bg-black rounded-full text-sm hover:bg-app-bg-tertiary transition-colors text-gray-300"
                @click="quickSearch(tag)"
              >
                {{ tag }}
              </button>
            </div>
          </div>
        </div>

        <!-- Close Button -->
        <button
          class="absolute top-6 right-6 p-2 hover:bg-black rounded-full transition-colors"
          @click="close"
        >
          <el-icon :size="24"><Close /></el-icon>
        </button>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { Search, Close } from '@element-plus/icons-vue'

// 客户端标识（用于模板）
const isClient = import.meta.client

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const keyword = ref('')
const router = useRouter()

// 模拟热门搜索
const hotSearch = ['流浪地球', '狂飙', '三体', '漫长的季节', '消失的她', '八角笼中']

const close = () => {
  emit('update:modelValue', false)
  keyword.value = ''
}

const handleSearch = () => {
  if (keyword.value.trim()) {
    router.push(routes.query(keyword.value.trim()))
    close()
  }
}

const quickSearch = (tag: string) => {
  router.push(routes.query(tag))
  close()
}

// ESC 关闭
onKeyStroke('Escape', () => {
  if (props.modelValue) close()
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
