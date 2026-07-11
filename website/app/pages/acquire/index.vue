<template>
  <div class="min-h-screen bg-app-bg">
    <!-- iOS PWA 安装引导 -->
    <IosPwaGuide ref="iosPwaGuideRef" />

    <!-- Header -->
    <header class="sticky top-0 z-50 bg-app-bg/95 backdrop-blur-sm">
      <div class="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <NuxtLink :to="routes.home()" class="flex items-center gap-3">
          <span class="text-lg font-bold text-white">影视模版</span>
        </NuxtLink>
        <NuxtLink :to="routes.home()" class="flex items-center group">
          <img
            src="/ic_home.png"
            alt="首页"
            class="w-6 h-6 object-contain opacity-70 group-hover:opacity-100 group-hover:brightness-0 group-hover:invert-[1] group-hover:sepia-[1] group-hover:saturate-[400%] group-hover:hue-rotate-[199deg] transition-all duration-200"
            style="filter: brightness(0) invert(1);"
          />
        </NuxtLink>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-6xl mx-auto px-4 py-12">
      <!-- Hero Section -->
      <div class="text-center mb-12">
        <h1 class="text-4xl md:text-5xl font-bold text-gray-100 mb-3">
          从这里找到我们
        </h1>
        <p class="text-base text-gray-400">
          {{ appSubSlogan }}
        </p>
      </div>

      <!-- Platform Tabs -->
      <div class="flex justify-center mb-10">
        <div class="inline-flex bg-app-bg-secondary rounded-2xl p-2 shadow-lg border border-gray-700 gap-2">
          <button
            v-for="platform in platforms"
            :key="platform.key"
            class="flex items-center justify-center gap-3 w-28 py-3 rounded-xl transition-all duration-300"
            :class="activePlatform === platform.key
              ? 'bg-app-primary text-white shadow-md'
              : 'text-gray-400 hover:text-gray-200 hover:bg-black'"
            @click="activePlatform = platform.key"
          >
            <el-icon :size="20">
              <component :is="platform.icon" />
            </el-icon>
            <span class="font-medium">{{ platform.label }}</span>
          </button>
        </div>
      </div>

      <!-- Content Card -->
      <div class="bg-white/[0.03] backdrop-blur-sm rounded-3xl shadow-xl overflow-hidden">
        <!-- PC端 / 安卓端 - 单一视图 -->
        <div v-if="activePlatform !== 'ios'" class="grid md:grid-cols-2 gap-8 p-8 md:p-12">
          <!-- Left: Download Info -->
          <div class="flex flex-col justify-center">
            <div class="mb-6">
              <div class="inline-flex items-center gap-2 px-4 py-2 bg-app-primary/20 text-app-primary-light rounded-full text-sm font-medium mb-4">
                <el-icon><Check /></el-icon>
                <span>官方正版</span>
              </div>
              <h2 class="text-3xl font-bold text-white mb-2">
                {{ currentPlatform.title }}
              </h2>
              <p class="text-gray-200">{{ currentPlatform.description }}</p>
            </div>

            <!-- Features -->
            <div class="space-y-3 mb-8">
              <div
                v-for="feature in currentPlatform.features"
                :key="feature"
                class="flex items-center gap-3 text-gray-200"
              >
                <el-icon class="text-app-primary"><CircleCheckFilled /></el-icon>
                <span>{{ feature }}</span>
              </div>
            </div>

            <!-- Download Button -->
            <div class="space-y-4">
              <!-- Android 下载按钮 - 根据 buttonStatus 控制 -->
              <a
                v-if="currentPlatform.downloadUrl && !currentPlatform.isWeb && currentPlatform.buttonStatus === 1"
                :href="currentPlatform.downloadUrl"
                target="_blank"
                class="inline-flex items-center justify-center gap-2 w-full md:w-auto px-8 py-4 bg-app-primary text-white rounded-xl font-medium hover:bg-app-primary-hover transition-colors shadow-lg shadow-blue-500/30"
              >
                <el-icon :size="20"><Download /></el-icon>
                <span>{{ currentPlatform.downloadText }}</span>
              </a>

              <!-- 不可用状态的按钮 -->
              <button
                v-else-if="currentPlatform.downloadUrl && !currentPlatform.isWeb && currentPlatform.buttonStatus === 0"
                disabled
                class="inline-flex items-center justify-center gap-2 w-full md:w-auto px-8 py-4 bg-gray-700 text-gray-400 rounded-xl font-medium cursor-not-allowed"
              >
                <el-icon :size="20"><Download /></el-icon>
                <span>暂不提供下载</span>
              </button>

              <!-- PC 端按钮 - 根据 buttonStatus 控制 -->
              <NuxtLink
                v-if="currentPlatform.isWeb && currentPlatform.buttonStatus === 1"
                :to="routes.home()"
                class="inline-flex items-center justify-center gap-2 w-full md:w-auto px-8 py-4 bg-app-primary text-white rounded-xl font-medium hover:bg-app-primary-hover transition-colors shadow-lg shadow-blue-500/30"
              >
                <el-icon :size="20"><Monitor /></el-icon>
                <span>{{ currentPlatform.downloadText }}</span>
              </NuxtLink>

              <!-- PC 端安装PWA按钮 - 支持 beforeinstallprompt 的浏览器 -->
              <button
                v-if="currentPlatform.isWeb && currentPlatform.buttonStatus === 1 && canInstallPwa"
                @click="installPwa"
                class="inline-flex items-center justify-center gap-2 w-full md:w-auto px-8 py-4 text-white rounded-xl font-medium hover:text-blue-400 transition-colors"
              >
                <el-icon :size="20"><Download /></el-icon>
                <span>安装到桌面</span>
              </button>

              <!-- PC 端 Safari 手动安装引导按钮 -->
              <button
                v-if="currentPlatform.isWeb && currentPlatform.buttonStatus === 1 && !canInstallPwa && isSafari"
                @click="showSafariPwaGuide"
                class="inline-flex items-center justify-center gap-2 w-full md:w-auto px-8 py-4 text-white rounded-xl font-medium hover:text-blue-400 transition-colors"
              >
                <el-icon :size="20"><Download /></el-icon>
                <span>安装到桌面</span>
              </button>

              <!-- PC 端不可用状态的按钮 -->
              <button
                v-else-if="currentPlatform.isWeb && currentPlatform.buttonStatus === 0"
                disabled
                class="inline-flex items-center justify-center gap-2 w-full md:w-auto px-8 py-4 bg-gray-700 text-gray-400 rounded-xl font-medium cursor-not-allowed"
              >
                <el-icon :size="20"><Monitor /></el-icon>
                <span>暂不提供访问</span>
              </button>

              <!-- 版本信息 - 仅当 buttonStatus 为 1 时显示 -->
              <div v-if="!currentPlatform.isWeb && currentPlatform.buttonStatus === 1" class="text-sm text-gray-200">
                <p>当前版本：{{ currentPlatform.version }}</p>
                <p>更新日期：{{ currentPlatform.updateDate }}</p>
              </div>
            </div>
          </div>

          <!-- Right: QR Code - 仅当 buttonStatus 为 1 时显示（支持移动端和PC端） -->
          <div v-if="currentPlatform.qrCode && currentPlatform.buttonStatus === 1" class="flex flex-col items-center justify-center rounded-2xl p-8">
            <div class="bg-white/5 p-4 rounded-xl mb-4">
              <img
                :src="currentPlatform.qrCode"
                :alt="`${currentPlatform.label}下载二维码`"
                class="w-48 h-48 object-contain"
                @error="$event.target.style.display='none'"
              />
            </div>
            <p class="text-gray-200 text-center">
              扫描二维码<br />{{ currentPlatform.qrText }}
            </p>
          </div>

          <!-- 无二维码时的占位 -->
          <div v-else-if="!currentPlatform.qrCode && currentPlatform.buttonStatus === 1" class="flex flex-col items-center justify-center rounded-2xl p-8">
            <el-icon :size="64" class="text-gray-400 mb-4"><Cellphone /></el-icon>
            <p class="text-gray-200 text-center">
              点击上方按钮<br />{{ currentPlatform.isWeb ? '访问' : '下载' }}{{ currentPlatform.label }}版本
            </p>
          </div>

          <div v-else class="flex flex-col items-center justify-center rounded-2xl p-8">
            <el-icon :size="64" class="text-app-primary mb-4"><Monitor /></el-icon>
            <p class="text-gray-200 text-center">
              直接使用网页版<br />无需下载安装
            </p>
          </div>
        </div>

        <!-- 苹果端 - iPhone + iPad 双视图 -->
        <div v-else class="p-8 md:p-12">
          <div class="grid md:grid-cols-2 gap-8">
            <!-- iPhone -->
            <div class="flex flex-col">
              <div class="flex items-center gap-5 mb-6">
                <img src="/ic_iphone.png" alt="iPhone" class="w-8 h-8 object-contain opacity-70" />
                <div>
                  <h3 class="text-xl font-bold text-white">iPhone</h3>
                  <p class="text-sm text-gray-200">适用于 iPhone 设备</p>
                </div>
              </div>

              <!-- Features -->
              <div class="space-y-3 mb-6">
                <div
                  v-for="feature in iosConfig.iphone?.features || iosFeatures"
                  :key="feature"
                  class="flex items-center gap-3 text-gray-200 text-sm"
                >
                  <el-icon class="text-app-primary" :size="16"><CircleCheckFilled /></el-icon>
                  <span>{{ feature }}</span>
                </div>
              </div>

              <!-- Button - 根据 buttonStatus 控制 -->
              <a
                v-if="iosConfig.iphone?.buttonStatus === 1 && iosConfig.iphone?.downloadUrl"
                :href="iosConfig.iphone.downloadUrl"
                target="_blank"
                class="inline-flex items-center justify-center gap-2 px-6 py-3 bg-app-primary text-white rounded-xl font-medium hover:bg-app-primary-hover transition-colors shadow-lg shadow-blue-500/30 mb-3"
              >
                <el-icon :size="18"><Download /></el-icon>
                <span>前往 App Store</span>
              </a>

              <!-- 不可用状态的按钮 -->
              <button
                v-else
                disabled
                class="inline-flex items-center justify-center gap-2 px-6 py-3 bg-gray-700 text-gray-400 rounded-xl font-medium cursor-not-allowed mb-3"
              >
                <el-icon :size="18"><Download /></el-icon>
                <span>暂不提供下载</span>
              </button>

              <!-- iOS Safari 添加到主屏幕按钮 -->
              <button
                v-if="isIosSafari"
                @click="showIosPwaGuide"
                class="inline-flex items-center justify-center gap-2 px-6 py-3 bg-app-bg-secondary text-white rounded-xl font-medium hover:bg-app-bg-hover transition-colors border border-gray-600 mb-3"
              >
                <el-icon :size="18"><Plus /></el-icon>
                <span>添加到主屏幕</span>
              </button>

              <!-- 版本信息 - 仅当 buttonStatus 为 1 时显示 -->
              <div v-if="iosConfig.iphone?.buttonStatus === 1" class="text-sm text-gray-200">
                <p>当前版本：{{ iosConfig.iphone?.version || 'v2.1.0' }}</p>
                <p>更新日期：{{ iosConfig.iphone?.updateDate || '2025-06-27' }}</p>
              </div>

              <!-- QR Code - 仅当 buttonStatus 为 1 时显示 -->
              <div v-if="iosConfig.iphone?.qrCode && iosConfig.iphone?.buttonStatus === 1" class="mt-6 flex flex-col items-center justify-center rounded-2xl p-6">
                <div class="bg-white/5 p-3 rounded-xl mb-3">
                  <img
                    :src="iosConfig.iphone.qrCode"
                    alt="iPhone下载二维码"
                    class="w-32 h-32 object-contain"
                  />
                </div>
                <p class="text-sm text-gray-200">扫码下载 iPhone 版</p>
              </div>
            </div>

            <!-- iPad -->
            <div class="flex flex-col">
              <div class="flex items-center gap-5 mb-6">
                <img src="/ic_ipad.png" alt="iPad" class="w-8 h-8 object-contain opacity-70" />
                <div>
                  <h3 class="text-xl font-bold text-white">iPad</h3>
                  <p class="text-sm text-gray-200">专为 iPad 大屏优化</p>
                </div>
              </div>

              <!-- Features -->
              <div class="space-y-3 mb-6">
                <div
                  v-for="feature in iosConfig.ipad?.features || ipadFeatures"
                  :key="feature"
                  class="flex items-center gap-3 text-gray-200 text-sm"
                >
                  <el-icon class="text-app-primary" :size="16"><CircleCheckFilled /></el-icon>
                  <span>{{ feature }}</span>
                </div>
              </div>

              <!-- Button - 根据 buttonStatus 控制 -->
              <a
                v-if="iosConfig.ipad?.buttonStatus === 1 && iosConfig.ipad?.downloadUrl"
                :href="iosConfig.ipad.downloadUrl"
                target="_blank"
                class="inline-flex items-center justify-center gap-2 px-6 py-3 bg-app-primary text-white rounded-xl font-medium hover:bg-app-primary-hover transition-colors shadow-lg shadow-blue-500/30 mb-3"
              >
                <el-icon :size="18"><Download /></el-icon>
                <span>前往 App Store</span>
              </a>

              <!-- 不可用状态的按钮 -->
              <button
                v-else
                disabled
                class="inline-flex items-center justify-center gap-2 px-6 py-3 bg-gray-700 text-gray-400 rounded-xl font-medium cursor-not-allowed mb-3"
              >
                <el-icon :size="18"><Download /></el-icon>
                <span>暂不提供下载</span>
              </button>

              <!-- 版本信息 - 仅当 buttonStatus 为 1 时显示 -->
              <div v-if="iosConfig.ipad?.buttonStatus === 1" class="text-sm text-gray-200">
                <p>当前版本：{{ iosConfig.ipad?.version || 'v2.1.0 HD' }}</p>
                <p>更新日期：{{ iosConfig.ipad?.updateDate || '2025-06-27' }}</p>
              </div>

              <!-- QR Code - 仅当 buttonStatus 为 1 时显示 -->
              <div v-if="iosConfig.ipad?.qrCode && iosConfig.ipad?.buttonStatus === 1" class="mt-6 flex flex-col items-center justify-center rounded-2xl p-6">
                <div class="bg-white/5 p-3 rounded-xl mb-3">
                  <img
                    :src="iosConfig.ipad.qrCode"
                    alt="iPad下载二维码"
                    class="w-32 h-32 object-contain"
                  />
                </div>
                <p class="text-sm text-gray-200">扫码下载 iPad HD 版</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Additional Info -->
      <div class="mt-12 grid md:grid-cols-3 gap-6">
        <div class="bg-white/[0.03] backdrop-blur-sm rounded-2xl p-6 shadow-md text-center">
          <div class="w-14 h-14 mx-auto mb-4 bg-app-primary/20 rounded-2xl flex items-center justify-center">
            <el-icon :size="28" class="text-app-primary-light"><VideoPlay /></el-icon>
          </div>
          <h3 class="font-bold text-gray-100 mb-2">海量片源</h3>
          <p class="text-gray-400 text-sm">汇聚全网影视资源，每日更新热门大片</p>
        </div>

        <div class="bg-white/[0.03] backdrop-blur-sm rounded-2xl p-6 shadow-md text-center">
          <div class="w-14 h-14 mx-auto mb-4 bg-app-primary/20 rounded-2xl flex items-center justify-center">
            <el-icon :size="28" class="text-app-primary-light"><Film /></el-icon>
          </div>
          <h3 class="font-bold text-gray-100 mb-2">高清画质</h3>
          <p class="text-gray-400 text-sm">支持1080P/4K超清播放，流畅不卡顿</p>
        </div>

        <div class="bg-white/[0.03] backdrop-blur-sm rounded-2xl p-6 shadow-md text-center">
          <div class="w-14 h-14 mx-auto mb-4 bg-app-primary/20 rounded-2xl flex items-center justify-center">
            <el-icon :size="28" class="text-app-primary-light"><VideoPlay /></el-icon>
          </div>
          <h3 class="font-bold text-gray-100 mb-2">快速播放</h3>
          <p class="text-gray-400 text-sm">智能预加载技术，秒开播放不等待</p>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="bg-black py-8 mt-12">
      <div class="max-w-6xl mx-auto px-4">
        <div class="flex flex-col md:flex-row items-center md:items-start gap-6 md:gap-8">
          <!-- Left: Logo & Copyright -->
          <div class="flex flex-col items-center md:items-start">
            <div class="mb-3">
              <span class="text-lg font-bold text-white">影视模版</span>
            </div>
            <p class="text-gray-300 text-sm">
              © 2026 {{ appName }} 版权所有 | {{ appSlogan }}
            </p>
          </div>

          <!-- Right: Notice -->
          <div class="flex-1 text-center md:text-left space-y-2">
            <p class="text-xs text-gray-300">
              注：APP本身不存储任何视频/图片等内容，所有资源均由搜索引擎检索于公开网络，如有侵权请发送邮件至 {{ contactEmail }} 与我们联系，谢谢！
            </p>
            <p class="text-xs text-gray-300">
              注：我们承诺App绝对绿色、安全，且不会对您的数据和资产造成任何损害，请放心安装使用。
            </p>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import {
  Download,
  Check,
  CircleCheckFilled,
  VideoPlay,
  Cellphone,
  Apple,
  Monitor,
  Platform,
  Film,
  Warning,
  Plus
} from '@element-plus/icons-vue'

const config = useRuntimeConfig()
const contactEmail = config.public.contactEmail
const appName = config.public.appName
const appSlogan = config.public.appSlogan
const appSubSlogan = config.public.appSubSlogan

// 不使用默认布局，独立页面
definePageMeta({
  layout: false
})

// SEO
useHead({
  title: `${appName}客户端下载-${appSlogan}`,
  meta: [
    { name: 'description', content: `下载${appName}APP，${appSubSlogan}，畅享海量高清影视资源` }
  ]
})

// 获取版本配置
const { data: versionConfig } = await useFetch('/app-version.json', {
  server: false,
  key: 'app-version',
  default: () => ({
    android: {
      version: 'v2.1.0',
      updateDate: '2025-06-27',
      downloadUrl: '',
      qrCode: 'your_qr_code.png',
      buttonStatus: 1,
      changelog: ['优化播放体验', '修复已知问题']
    },
    iphone: {
      version: 'v2.1.0',
      updateDate: '2025-06-27',
      downloadUrl: '',
      qrCode: '',
      buttonStatus: 0,
      changelog: ['优化播放体验', '支持AirPlay投屏']
    },
    ipad: {
      version: 'v2.1.0 HD',
      updateDate: '2025-06-27',
      downloadUrl: '',
      qrCode: '',
      buttonStatus: 0,
      changelog: ['专为iPad优化', '支持分屏多任务']
    },
    pc: {
      description: '直接使用网页版，无需下载安装',
      url: '/',
      buttonStatus: 1,
      qrCode: ''
    }
  })
})

// iOS 配置（iPhone + iPad）
const iosConfig = computed(() => ({
  iphone: versionConfig.value?.iphone,
  ipad: versionConfig.value?.ipad
}))

// iPhone 默认特性
const iosFeatures = [
  '支持iOS 12.0及以上系统',
  '适配iPhone全系列机型',
  '支持AirPlay投屏',
  '小组件快捷入口'
]

// iPad 默认特性
const ipadFeatures = [
  '专为iPad大屏适配',
  '支持分屏多任务',
  '横竖屏自动切换',
  '画中画播放模式'
]

// PWA 安装相关
const deferredPrompt = ref<any>(null)
const canInstallPwa = ref(false)

// Safari 检测（包括 macOS Safari）
const isSafari = ref(false)
const isIosSafari = ref(false)
const iosPwaGuideRef = ref<{ openGuide: () => void } | null>(null)

// 监听 PWA 安装事件
onMounted(() => {
  window.addEventListener('beforeinstallprompt', (e: any) => {
    e.preventDefault()
    deferredPrompt.value = e
    canInstallPwa.value = true
  })

  // 检测 Safari（包括 macOS 和 iOS）
  const ua = navigator.userAgent
  const isIos = /iPad|iPhone|iPod/.test(ua)
  const safariCheck = /Safari/.test(ua) && !/Chrome|CriOS|FxiOS|Edg/.test(ua)
  isSafari.value = safariCheck
  isIosSafari.value = isIos && safariCheck
})

// 安装 PWA
const installPwa = async () => {
  if (!deferredPrompt.value) return

  deferredPrompt.value.prompt()
  const { outcome } = await deferredPrompt.value.userChoice

  if (outcome === 'accepted') {
    canInstallPwa.value = false
  }
  deferredPrompt.value = null
}

// 显示 Safari PWA 引导（macOS 和 iOS）
const showSafariPwaGuide = () => {
  iosPwaGuideRef.value?.openGuide()
}

// 显示 iOS PWA 引导
const showIosPwaGuide = () => {
  iosPwaGuideRef.value?.openGuide()
}

// 记录登录用户页面访问
const { recordPageVisit } = useActivity()

onMounted(() => {
  recordPageVisit('/acquire')
})

// 平台配置（合并配置文件数据）
const platforms = computed(() => {
  const config = versionConfig.value
  return [
    {
      key: 'pc',
      label: 'PC端',
      icon: Monitor,
      title: 'PC端使用',
      description: config?.pc?.description || '直接使用主站网页版，无需下载安装',
      downloadUrl: config?.pc?.url || '/',
      downloadText: '访问网页版',
      qrCode: config?.pc?.qrCode || '',
      qrText: '扫码访问网页版',
      version: '',
      updateDate: '',
      buttonStatus: config?.pc?.buttonStatus ?? 1,
      isWeb: true,
      features: [
        '支持Windows/macOS/Linux系统',
        '4K高清画质支持',
        '浏览器直接访问，无需安装',
        '多窗口播放模式'
      ]
    },
    {
      key: 'android',
      label: '安卓端',
      icon: Cellphone,
      title: '安卓版下载',
      description: '适用于大部分安卓手机和平板设备',
      downloadUrl: config?.android?.downloadUrl || '',
      downloadText: '立即下载 APK',
      qrCode: config?.android?.qrCode || 'your_qr_code.png',
      qrText: '手机扫码下载安卓版',
      version: config?.android?.version || 'v2.1.0',
      updateDate: config?.android?.updateDate || '2025-06-27',
      buttonStatus: config?.android?.buttonStatus ?? 1,
      isWeb: false,
      features: config?.android?.changelog || [
        '支持安卓5.0及以上系统',
        '适配手机和平板设备',
        '支持离线缓存下载',
        '投屏功能支持'
      ]
    },
    {
      key: 'ios',
      label: '苹果端',
      icon: Apple,
      title: 'iOS版下载',
      description: '适用于 iPhone 和 iPad 设备',
      downloadUrl: '',
      downloadText: '',
      qrCode: '',
      qrText: '',
      version: '',
      updateDate: '',
      isWeb: false,
      features: []
    }
  ]
})

const activePlatform = ref('pc')

const currentPlatform = computed(() => {
  return platforms.value.find(p => p.key === activePlatform.value) || platforms.value[0]
})
</script>

<style scoped>
.bg-gradient-to-br {
  background: linear-gradient(135deg, #f9fafb 0%, #eff6ff 100%);
}
</style>
