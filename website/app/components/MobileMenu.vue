<template>
  <!-- 客户端渲染避免 Safari SSR 问题 -->
  <Teleport v-if="isClient" to="body">
    <Transition name="slide">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 md:hidden"
      >
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/1" @click="close" />

        <!-- Menu Panel -->
        <div class="absolute right-0 top-0 bottom-0 w-64 p-6 shadow-xl bg-app-bg/85 backdrop-blur-xl">
          <button
            class="absolute top-4 right-4 p-2 hover:bg-white/10 rounded-full text-gray-300"
            @click="close"
          >
            <el-icon :size="20"><Close /></el-icon>
          </button>

          <nav class="mt-12 space-y-4">
            <NuxtLink
              v-for="item in navItems"
              :key="item.path"
              :to="item.path"
              class="block text-lg py-2 hover:text-app-primary-light transition-colors text-gray-200"
              :class="{ 'text-app-primary-light': route.path === item.path }"
              @click="close"
            >
              {{ item.label }}
            </NuxtLink>
          </nav>

          <!-- Legal Links -->
          <div class="mt-8 pt-6 border-t border-gray-700 space-y-4">
            <button
              class="block w-full text-left text-lg py-2 hover:text-app-primary-light transition-colors text-gray-200"
              @click="openModal('terms')"
            >
              用户协议
            </button>
            <button
              class="block w-full text-left text-lg py-2 hover:text-app-primary-light transition-colors text-gray-200"
              @click="openModal('privacy')"
            >
              隐私政策
            </button>
          </div>

        </div>

        <!-- Policy Modal -->
        <el-dialog
          v-model="showModal"
          :title="modalTitle"
          width="90%"
          :max-width="modalType === 'terms' ? '800px' : '600px'"
          align-center
          class="policy-dialog"
          destroy-on-close
        >
          <div class="policy-content">
            <iframe
              v-if="modalUrl"
              :src="modalUrl"
              class="w-full h-full border-0"
              sandbox="allow-same-origin allow-scripts"
            />
          </div>
        </el-dialog>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { Close } from '@element-plus/icons-vue'
import { useSiteConfig } from '~/config/site'

const siteConfig = useSiteConfig()

// 客户端标识（用于模板）
const isClient = import.meta.client

interface NavItem {
  path: string
  label: string
}

const props = defineProps<{
  modelValue: boolean
  navItems: NavItem[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const route = useRoute()

const close = () => {
  emit('update:modelValue', false)
}

// ESC 关闭
onKeyStroke('Escape', () => {
  if (props.modelValue) close()
})

// Policy Modal
const showModal = ref(false)
const modalType = ref('')
const modalUrl = ref('')

const modalTitle = computed(() => {
  return modalType.value === 'terms' ? '用户协议' : '隐私政策'
})

const openModal = (type: string) => {
  modalType.value = type
  if (type === 'terms') {
    modalUrl.value = siteConfig.policy.agreement
  } else {
    modalUrl.value = siteConfig.policy.privacy
  }
  showModal.value = true
}
</script>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(100%);
}

.policy-content {
  height: 60vh;
  min-height: 400px;
  max-height: 700px;
}

.policy-content iframe {
  width: 100%;
  height: 100%;
}

:deep(.policy-dialog) {
  background-color: #000000;
}

:deep(.policy-dialog .el-dialog__body) {
  padding: 0;
  overflow: hidden;
}

:deep(.policy-dialog .el-dialog__header) {
  border-bottom: 1px solid #333333;
  padding: 16px 20px;
  margin-right: 0;
  background-color: #000000;
}

:deep(.policy-dialog .el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
  color: #f5f5f5;
}
</style>
