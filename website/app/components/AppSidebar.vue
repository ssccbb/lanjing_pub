<template>
  <div
    class="flex flex-col h-full"
    :class="transparent ? 'bg-transparent' : 'bg-black border-r border-gray-700'"
  >
    <!-- Logo Area - 可选择显示/隐藏 -->
    <div v-if="showLogo" class="h-16 px-4 flex items-center flex-shrink-0">
      <NuxtLink to="/" class="text-lg font-bold text-white">影视模版</NuxtLink>
    </div>

    <!-- Category Navigation -->
    <div class="flex-1 overflow-y-auto py-4 pb-20 min-h-0 scrollbar-hide">
      <!-- Section 1: 首页 -->
      <nav class="space-y-1">
        <NuxtLink
          to="/"
          class="w-full flex items-center px-5 py-3.5 text-left transition-colors relative"
          :class="$route.path === '/'
            ? 'text-white'
            : 'text-white/70 hover:text-white'"
          prefetch
        >
          <span
            v-if="$route.path === '/'"
            class="absolute left-0 top-0 bottom-0 w-1 bg-app-primary-hover"
          />
          <span
            v-if="$route.path === '/'"
            class="absolute left-1 top-0 bottom-0 right-0 bg-gradient-to-r from-gray-600/65 to-transparent"
          />
          <span class="font-medium text-base relative z-10">首页</span>
        </NuxtLink>
      </nav>

      <!-- Divider -->
      <div class="my-4 ml-5 border-t border-gray-600/50" />

      <!-- Section 2: 影片分类 -->
      <nav class="space-y-1">
        <NuxtLink
          v-for="item in videoCategories"
          :key="item.key"
          :to="item.link"
          class="w-full flex items-center px-5 py-3.5 text-left transition-colors relative"
          :class="$route.path.startsWith(item.path)
            ? 'text-white'
            : 'text-white/70 hover:text-white'"
          prefetch
        >
          <span
            v-if="$route.path.startsWith(item.path)"
            class="absolute left-0 top-0 bottom-0 w-1 bg-app-primary-hover"
          />
          <span
            v-if="$route.path.startsWith(item.path)"
            class="absolute left-1 top-0 bottom-0 right-0 bg-gradient-to-r from-gray-600/65 to-transparent"
          />
          <span class="font-medium text-base relative z-10">{{ item.label }}</span>
        </NuxtLink>
      </nav>

      <!-- Divider -->
      <div class="my-4 ml-5 border-t border-gray-600/50" />

      <!-- Section 3: 排行榜 & 片单广场 & 今日更新 -->
      <nav class="space-y-1">
        <NuxtLink
          :to="routes.tiers()"
          class="w-full flex items-center px-5 py-3.5 text-left transition-colors relative"
          :class="$route.path.startsWith('/tiers')
            ? 'text-white'
            : 'text-white/70 hover:text-white'"
          prefetch
        >
          <span
            v-if="$route.path.startsWith('/tiers')"
            class="absolute left-0 top-0 bottom-0 w-1 bg-app-primary-hover"
          />
          <span
            v-if="$route.path.startsWith('/tiers')"
            class="absolute left-1 top-0 bottom-0 right-0 bg-gradient-to-r from-gray-600/65 to-transparent"
          />
          <span class="font-medium text-base relative z-10">排行榜</span>
        </NuxtLink>
        <NuxtLink
          to="/watchlists"
          class="w-full flex items-center px-5 py-3.5 text-left transition-colors relative"
          :class="$route.path.startsWith('/watchlists')
            ? 'text-white'
            : 'text-white/70 hover:text-white'"
          prefetch
        >
          <span
            v-if="$route.path.startsWith('/watchlists')"
            class="absolute left-0 top-0 bottom-0 w-1 bg-app-primary-hover"
          />
          <span
            v-if="$route.path.startsWith('/watchlists')"
            class="absolute left-1 top-0 bottom-0 right-0 bg-gradient-to-r from-gray-600/65 to-transparent"
          />
          <span class="font-medium text-base relative z-10">片单广场</span>
        </NuxtLink>
        <NuxtLink
          to="/today"
          class="w-full flex items-center px-5 py-3.5 text-left transition-colors relative"
          :class="$route.path === '/today'
            ? 'text-white'
            : 'text-white/70 hover:text-white'"
          prefetch
        >
          <span
            v-if="$route.path === '/today'"
            class="absolute left-0 top-0 bottom-0 w-1 bg-app-primary-hover"
          />
          <span
            v-if="$route.path === '/today'"
            class="absolute left-1 top-0 bottom-0 right-0 bg-gradient-to-r from-gray-600/65 to-transparent"
          />
          <span class="font-medium text-base relative z-10">
            今日更新
            <span
              v-if="todayCount > 0"
              class="absolute -top-1 -right-5 min-w-[16px] h-4 px-1 text-[10px] flex items-center justify-center bg-red-500 text-white rounded-full"
            >
              {{ todayCount > 99 ? '99+' : todayCount }}
            </span>
          </span>
        </NuxtLink>
      </nav>

      <!-- Divider -->
      <div class="my-4 ml-5 border-t border-gray-600/50" />

      <!-- Section 4: APP下载 & 求片留言 -->
      <nav class="space-y-1">
        <a
          :href="routes.acquire()"
          target="_blank"
          class="w-full flex items-center px-5 py-3.5 text-left transition-colors relative"
          :class="$route.path.startsWith('/acquire')
            ? 'text-white'
            : 'text-white/70 hover:text-white'"
        >
          <span
            v-if="$route.path.startsWith('/acquire')"
            class="absolute left-0 top-0 bottom-0 w-1 bg-app-primary-hover"
          />
          <span
            v-if="$route.path.startsWith('/acquire')"
            class="absolute left-1 top-0 bottom-0 right-0 bg-gradient-to-r from-gray-600/65 to-transparent"
          />
          <span class="font-medium text-base relative z-10">下载APP</span>
        </a>
        <a
          :href="routes.echo()"
          target="_blank"
          class="w-full flex items-center px-5 py-3.5 text-left transition-colors relative"
          :class="$route.path.startsWith('/echo')
            ? 'text-white'
            : 'text-white/70 hover:text-white'"
        >
          <span
            v-if="$route.path.startsWith('/echo')"
            class="absolute left-0 top-0 bottom-0 w-1 bg-app-primary-hover"
          />
          <span
            v-if="$route.path.startsWith('/echo')"
            class="absolute left-1 top-0 bottom-0 right-0 bg-gradient-to-r from-gray-600/65 to-transparent"
          />
          <span class="font-medium text-base relative z-10">求片留言</span>
        </a>
      </nav>

      <!-- Section 5: 用户协议 & 隐私政策 & 备案号 -->
      <div class="mt-6 px-5 pb-4">
        <div class="flex flex-wrap items-center gap-x-2 gap-y-1 text-[10px] text-white/50">
          <button
            class="hover:text-app-primary-light transition-colors"
            @click="openPolicy('terms')"
          >
            用户协议
          </button>
          <button
            class="hover:text-app-primary-light transition-colors"
            @click="openPolicy('privacy')"
          >
            隐私政策
          </button>
        </div>
        <a
          v-if="icpNumber"
          href="https://beian.miit.gov.cn/"
          target="_blank"
          class="mt-1.5 block text-[10px] text-white/50 hover:text-[#60a5fa] transition-colors underline"
        >
          {{ icpNumber }}
        </a>
      </div>
    </div>

    <!-- 用户协议/隐私政策弹窗 - 使用 Teleport 移到 body -->
    <Teleport to="body">
      <el-dialog
        v-model="showPolicyDialog"
        :title="policyTitle"
        width="90%"
        :max-width="policyType === 'terms' ? '800px' : '600px'"
        align-center
        class="policy-dialog"
        destroy-on-close
      >
        <div class="policy-content">
          <iframe
            v-if="policyUrl"
            :src="policyUrl"
            class="w-full h-full border-0"
            sandbox="allow-same-origin allow-scripts"
          />
        </div>
      </el-dialog>
    </Teleport>
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
  Calendar,
  Trophy,
  Collection,
  Download,
  ChatDotRound
} from '@element-plus/icons-vue'
import { useSiteConfig } from '~/config/site'

const siteConfig = useSiteConfig()
const config = useRuntimeConfig()
const icpNumber = config.public.icpNumber

const { getTodayMovies } = useHome()

interface Props {
  transparent?: boolean
  showLogo?: boolean
}

withDefaults(defineProps<Props>(), {
  transparent: false,
  showLogo: true
})

// 今日更新数量
const { data: todayCountData } = useLazyAsyncData('today-count-sidebar', async () => {
  try {
    const result = await getTodayMovies(1, 1)
    return result.total || 0
  } catch (error) {
    console.error('获取今日更新数量失败:', error)
    return 0
  }
}, {
  server: false,
  default: () => 0
})

const todayCount = computed(() => todayCountData.value || 0)

// 视频分类
const videoCategories = [
  { key: 'movies', label: '电影', icon: Film, link: '/reels', path: '/reels' },
  { key: 'tv', label: '电视剧', icon: Monitor, link: '/tv', path: '/tv' },
  { key: 'variety', label: '综艺', icon: VideoCamera, link: '/variety', path: '/variety' },
  { key: 'animation', label: '动漫', icon: MagicStick, link: '/cels', path: '/cels' },
  { key: 'shorts', label: '短剧', icon: Lightning, link: '/shorts', path: '/shorts' }
]

// 协议弹窗
const showPolicyDialog = ref(false)
const policyType = ref('')
const policyUrl = ref('')

const policyTitle = computed(() => {
  return policyType.value === 'terms' ? '用户协议' : '隐私政策'
})

const openPolicy = (type: string) => {
  policyType.value = type
  if (type === 'terms') {
    policyUrl.value = siteConfig.policy.agreement
  } else {
    policyUrl.value = siteConfig.policy.privacy
  }
  showPolicyDialog.value = true
}
</script>

<style scoped>
/* 隐藏滚动条 */
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}

/* 协议弹窗样式 */
.policy-content {
  height: 60vh;
  min-height: 400px;
  max-height: 700px;
}

.policy-content iframe {
  width: 100%;
  height: 100%;
}

:deep(.el-dialog.policy-dialog) {
  background-color: #141414 !important;
}

:deep(.policy-dialog .el-dialog__body) {
  padding: 0;
  overflow: hidden;
  background-color: #141414;
}

:deep(.policy-dialog .el-dialog__header) {
  border-bottom: 1px solid #333333;
  padding: 16px 20px;
  margin-right: 0;
  background-color: #141414;
}

:deep(.policy-dialog .el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
  color: #f5f5f5;
}
</style>
