<template>
  <div class="px-4 md:px-6 lg:px-10 py-8">
    <div class="max-w-2xl mx-auto">
      <!-- Header -->
      <div class="text-center mb-8">
        <h1 class="text-2xl font-bold mb-2">求片留言</h1>
        <p class="text-gray-500">找不到想看的影片？告诉我们，我们会尽快添加</p>
      </div>

      <!-- Form -->
      <div class="bg-app-bg rounded-lg shadow-sm p-6">
        <!-- 内容 -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-300 mb-2">
            详细描述 <span class="text-red-500">*</span>
          </label>
          <textarea
            v-model="form.content"
            rows="5"
            class="w-full px-4 py-3 bg-app-bg-secondary rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-app-primary/50 resize-none"
            placeholder="请填写您想看的影片名称、年份、演员等信息，方便我们快速定位"
          />
          <p class="text-xs text-gray-500 mt-1">至少5个字符，最多1000个字符</p>
        </div>

        <!-- 联系邮箱 -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-300 mb-2">联系邮箱</label>
          <input
            v-model="form.email"
            type="email"
            class="w-full px-4 py-3 bg-app-bg-secondary rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-app-primary/50"
            placeholder="选填，方便我们回复您"
          />
        </div>

        <!-- 联系方式 -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-300 mb-2">其他联系方式</label>
          <input
            v-model="form.contact"
            type="text"
            class="w-full px-4 py-3 bg-app-bg-secondary rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-app-primary/50"
            placeholder="选填，手机号/微信/QQ等"
          />
        </div>

        <!-- Submit Button -->
        <button
          @click="handleSubmit"
          :disabled="submitting || !isValid"
          class="w-full py-3 bg-app-primary text-white rounded-lg font-medium hover:bg-app-primary-hover transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="submitting">提交中...</span>
          <span v-else>提交留言</span>
        </button>
      </div>

      <!-- Tips -->
      <div class="mt-6 text-center text-sm text-gray-500">
        <p>您的反馈对我们非常重要，我们会尽快处理</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'player'
})

const { submitFeedback } = useFeedback()

// SEO
usePageSeo('求片留言', '找不到想看的影片？提交求片留言，我们会尽快添加')

// 表单数据
const form = reactive({
  content: '',
  email: '',
  contact: ''
})

const submitting = ref(false)

// 表单校验
const isValid = computed(() => {
  return form.content.trim().length >= 5
})

// 提交
const handleSubmit = async () => {
  if (!isValid.value) {
    ElMessage.warning('请填写详细描述，至少5个字符')
    return
  }

  submitting.value = true
  try {
    const result = await submitFeedback({
      content: form.content,
      email: form.email,
      contact: form.contact,
      feedback_type: 1 // 求片留言
    })

    if (result.success) {
      ElMessage.success(result.message)
      // 重置表单
      form.content = ''
      form.email = ''
      form.contact = ''
    } else {
      ElMessage.error(result.message)
    }
  } finally {
    submitting.value = false
  }
}

// 记录登录用户页面访问
const { recordPageVisit } = useActivity()
onMounted(() => {
  recordPageVisit('/echo')
})
</script>
