<template>
  <!-- 客户端渲染避免 Safari SSR 问题 -->
  <Teleport v-if="isClient" to="body">
    <Transition name="fade">
      <div
        v-if="visible"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        @click.self="close"
      >
        <!-- 遮罩 -->
        <div class="absolute inset-0 bg-black/50" @click="close" />

        <!-- 弹窗内容 -->
        <div class="relative bg-[#141414] rounded-xl shadow-xl w-full max-w-sm overflow-hidden">
          <!-- 头部 -->
          <div class="flex items-center justify-between px-5 py-4">
            <h3 class="text-lg font-medium text-gray-100">分享影片</h3>
            <button
              class="text-gray-500 hover:text-gray-300 transition-colors"
              @click="close"
            >
              <el-icon :size="20"><Close /></el-icon>
            </button>
          </div>

          <!-- 内容 -->
          <div class="p-5 space-y-5">
            <!-- 影片信息 -->
            <div v-if="title" class="flex gap-3 pb-4">
              <div class="w-12 h-18 rounded-lg overflow-hidden bg-[#222] flex-shrink-0 relative">
                <!-- Default placeholder (always visible) -->
                <div class="absolute inset-0 flex items-center justify-center bg-[#222]">
                  <img
                    src="/ic_default_picture.png"
                    alt=""
                    class="w-10 h-10 object-contain opacity-30"
                  />
                </div>
                <img
                  v-if="cover"
                  :src="cover"
                  :alt="title"
                  class="absolute inset-0 w-full h-full object-cover"
                />
              </div>
              <div class="flex-1 min-w-0 flex flex-col justify-center">
                <h4 class="font-medium text-gray-100 truncate">{{ title }}</h4>
                <div class="flex items-center gap-2 mt-1 text-xs text-gray-400">
                  <span v-if="score" class="text-amber-400 font-bold">{{ score.toFixed(1) }}分</span>
                  <span v-if="score && year" class="text-gray-600">|</span>
                  <span v-if="year">{{ year }}</span>
                </div>
                <p v-if="tags?.length" class="mt-1 text-xs text-gray-500 truncate">
                  {{ tags.slice(0, 3).join(' · ') }}
                </p>
              </div>
            </div>

            <!-- 二维码 -->
            <div class="text-center">
              <div class="inline-block p-3 bg-white rounded-lg">
                <canvas ref="qrcodeRef" width="180" height="180" />
              </div>
              <p class="mt-2 text-sm text-gray-400">微信扫码分享</p>
            </div>

            <!-- 复制链接 -->
            <div class="flex gap-2">
              <div class="flex-1 px-3 py-2 bg-[#222] rounded-lg text-sm text-gray-400 truncate">
                {{ displayUrl }}
              </div>
              <button
                class="px-4 py-2 bg-app-primary text-white rounded-lg text-sm font-medium hover:bg-app-primary-hover transition-colors flex items-center gap-1"
                @click="copyLink"
              >
                <el-icon v-if="copied"><Check /></el-icon>
                <el-icon v-else><DocumentCopy /></el-icon>
                {{ copied ? '已复制' : '复制' }}
              </button>
            </div>

            <!-- 社交平台 -->
            <div class="flex justify-center gap-6 pt-2">
              <button
                class="flex flex-col items-center gap-1 text-gray-400 hover:text-[#e6162d] transition-colors"
                @click="shareWeibo"
              >
                <div class="w-10 h-10 rounded-full bg-[#e6162d]/20 flex items-center justify-center">
                  <svg class="w-5 h-5 text-[#e6162d]" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M10.098 20.323c-3.977.391-7.414-1.406-7.672-4.02-.259-2.609 2.759-5.047 6.74-5.441 3.979-.394 7.413 1.404 7.671 4.018.259 2.6-2.759 5.049-6.737 5.439l-.002.004zM9.05 17.219c-.384.616-1.208.884-1.829.602-.612-.279-.793-.991-.406-1.593.379-.595 1.176-.861 1.793-.601.622.263.82.972.442 1.592zm1.27-1.627c-.141.237-.449.353-.689.253-.236-.09-.313-.361-.177-.586.138-.227.436-.346.672-.24.239.09.315.36.18.573h.014zm.176-2.719c-1.893-.493-4.033.45-4.857 2.118-.836 1.704-.026 3.591 1.886 4.21 1.983.64 4.318-.341 5.132-2.179.8-1.793-.201-3.642-2.161-4.149zm7.563-1.224c-.346-.105-.579-.18-.405-.649.381-1.017.42-1.894-.003-2.521-.801-1.169-2.986-1.108-5.52-.034 0 0-.791.345-.589-.281.384-1.217.327-2.234-.27-2.82-1.355-1.33-4.954.045-8.042 3.067-2.308 2.258-3.648 4.656-3.648 6.731 0 3.978 5.107 6.396 10.101 6.396 6.551 0 10.916-3.803 10.916-6.829 0-1.822-1.538-2.855-2.54-3.06zM21.466 6.088c-1.043-1.187-2.59-1.842-4.354-1.842h-.023c-.275 0-.551.021-.822.063-.421.065-.705.458-.639.879.065.42.457.705.879.64.19-.03.383-.045.576-.045 1.264 0 2.382.461 3.146 1.332.764.867 1.117 2.025.992 3.261-.028.279.04.559.196.784.157.226.39.389.659.465.269.076.556.057.813-.055.256-.111.461-.306.581-.55.383-.773.565-1.61.54-2.487-.026-.879-.234-1.723-.608-2.497l-.336-.458z"/>
                  </svg>
                </div>
                <span class="text-xs">微博</span>
              </button>

              <button
                class="flex flex-col items-center gap-1 text-gray-400 hover:text-[#12b7f5] transition-colors"
                @click="shareQQ"
              >
                <div class="w-10 h-10 rounded-full bg-[#12b7f5]/20 flex items-center justify-center">
                  <svg class="w-5 h-5 text-[#12b7f5]" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12.003 2c-2.265 0-6.29 1.364-6.29 7.325v1.195S3.55 14.96 3.55 17.474c0 .665.17 1.025.281 1.025.114 0 .902-.484 1.748-2.072 0 0-.18 2.197 1.904 3.967 0 0-1.77.495-1.77 1.182 0 .686 4.078.43 6.29.43 2.21 0 6.29.257 6.29-.43 0-.687-1.77-1.182-1.77-1.182 2.085-1.77 1.904-3.967 1.904-3.967.846 1.588 1.634 2.072 1.748 2.072.111 0 .281-.36.281-1.025 0-2.514-2.164-6.954-2.164-6.954V9.325C18.293 3.364 14.268 2 12.003 2z"/>
                  </svg>
                </div>
                <span class="text-xs">QQ</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { Close, DocumentCopy, Check, Film, ArrowRight } from '@element-plus/icons-vue'
import QRCode from 'qrcode'

// 客户端标识（用于模板）
const isClient = import.meta.client
const brandName = useBrandName()

interface Props {
  visible: boolean
  title: string
  url: string
  cover?: string
  year?: number
  tags?: string[]
  score?: number
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:visible': [value: boolean]
}>()

const { copyToClipboard, shareToWeibo, shareToQQ } = useShare()

const qrcodeRef = ref<HTMLCanvasElement>()
const copied = ref(false)

// 显示缩短的URL
const displayUrl = computed(() => {
  if (props.url.length > 40) {
    return props.url.slice(0, 40) + '...'
  }
  return props.url
})

// 生成二维码
const generateQRCode = async () => {
  if (!qrcodeRef.value || !props.url) return

  try {
    await QRCode.toCanvas(qrcodeRef.value, props.url, {
      width: 180,
      margin: 2,
      color: {
        dark: '#000000',
        light: '#ffffff'
      }
    })

    // 绘制中心文字（替代 favicon）
    const canvas = qrcodeRef.value
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // 在二维码中心绘制文字标识
    const size = 22
    const x = (canvas.width - size) / 2
    const y = (canvas.height - size) / 2

    // 绘制白色圆角矩形背景
    ctx.save()
    ctx.beginPath()
    ctx.roundRect(x - 3, y - 3, size + 6, size + 6, 6)
    ctx.fillStyle = '#ffffff'
    ctx.fill()
    ctx.restore()

    // 绘制文字
    ctx.save()
    ctx.fillStyle = '#2220d0'
    ctx.font = 'bold 14px sans-serif'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText('影', canvas.width / 2, canvas.height / 2)
    ctx.restore()
  } catch (err) {
    console.error('生成二维码失败:', err)
  }
}

// 分享文案
const shareText = computed(() => {
  return `在${brandName}追《${props.title}》中，推荐给你~\n${props.url}`
})

// 复制链接
const copyLink = async () => {
  const success = await copyToClipboard(shareText.value)
  if (success) {
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  }
}

// 分享到微博
const shareWeibo = () => {
  shareToWeibo({
    title: props.title,
    url: props.url
  })
}

// 分享到QQ
const shareQQ = () => {
  shareToQQ({
    title: props.title,
    url: props.url
  })
}

// 关闭弹窗
const close = () => {
  emit('update:visible', false)
}

// 监听显示状态，生成二维码
watch(() => props.visible, (val) => {
  if (val) {
    nextTick(() => {
      generateQRCode()
    })
  }
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
