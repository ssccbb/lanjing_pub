<template>
  <footer class="hidden md:block bg-black border-t border-gray-700 py-6 mt-8">
    <div class="px-4 md:px-6 lg:px-12 max-w-7xl mx-auto">
      <!-- Logo -->
      <div class="mb-3">
        <span class="text-lg font-bold text-blue-400">影视模版</span>
      </div>

      <!-- Links -->
      <div class="flex flex-wrap items-center gap-1 mb-4 text-sm text-gray-500">
        <NuxtLink to="/feedback" class="hover:text-gray-100 transition-colors px-3">求片留言</NuxtLink>
        <span class="text-gray-300">|</span>
        <button
          class="hover:text-gray-100 transition-colors px-3"
          @click="openModal('terms')"
        >
          用户协议
        </button>
        <span class="text-gray-300">|</span>
        <button
          class="hover:text-gray-100 transition-colors px-3"
          @click="openModal('privacy')"
        >
          隐私政策
        </button>
        <span class="text-gray-300">|</span>
        <NuxtLink to="/download" class="hover:text-gray-100 transition-colors px-3">APP下载</NuxtLink>
      </div>

      <!-- Copyright -->
      <div class="text-sm text-gray-500 space-y-2">
        <p>本站所有内容均来自网络收集，仅供学习交流，版权归原作者及原出处所有。如有侵犯您的权益，请发邮件至 <a :href="'mailto:' + contactEmail" class="text-app-primary hover:underline">{{ contactEmail }}</a></p>
      </div>
    </div>
  </footer>

  <!-- 用户协议/隐私政策弹窗 -->
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
</template>

<script setup>
import { useSiteConfig } from '~/config/site'

const siteConfig = useSiteConfig()
const config = useRuntimeConfig()
const contactEmail = config.public.contactEmail

const showModal = ref(false)
const modalType = ref('')
const modalUrl = ref('')

const modalTitle = computed(() => {
  return modalType.value === 'terms' ? '用户协议' : '隐私政策'
})

const openModal = (type) => {
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
.policy-content {
  height: 60vh;
  min-height: 400px;
  max-height: 700px;
}

.policy-content iframe {
  width: 100%;
  height: 100%;
}

:deep(.policy-dialog .el-dialog__body) {
  padding: 0;
  overflow: hidden;
}

:deep(.policy-dialog .el-dialog__header) {
  border-bottom: 1px solid #e5e7eb;
  padding: 16px 20px;
  margin-right: 0;
}

:deep(.policy-dialog .el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
}
</style>
