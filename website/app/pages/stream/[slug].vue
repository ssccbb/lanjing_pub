<template>
  <div class="h-[calc(100vh-60px)] bg-app-bg flex flex-col sm:flex-row overflow-hidden">
    <!-- Page Content -->
    <template v-if="movie">
      <!-- 播放器区域 -->
      <div class="flex-1 relative bg-app-bg h-full sm:h-full transition-all duration-300">
        <div v-if="playingEpisodeIndex >= 0 && playingEpisode" class="absolute inset-0 w-full h-full">
          <VideoPlayerWithDanmaku
            ref="videoPlayerRef"
            :src="playingEpisode.m3u8_link"
            :poster="coverUrl"
            :title="movie.title"
            :video-id="playingEpisode.id"
            :is-logged-in="isLoggedIn"
            show-input
            @ended="onEpisodeEnd"
            @timeupdate="onTimeUpdate"
            @switch-source="onSwitchSource"
            @login="handleGoToLogin"
          />
        </div>
        <!-- 未选择剧集时的占位 -->
        <div v-else class="absolute inset-0 flex flex-col items-center justify-center bg-app-bg">
          <p class="text-gray-500 text-sm">请选择要播放的剧集</p>
        </div>

        <!-- 收起/展开 Tab 按钮 - PC端 -->
        <button
          class="hidden sm:absolute sm:right-0 sm:top-1/2 sm:-translate-y-1/2 sm:z-30 sm:w-5 sm:h-10 sm:bg-app-bg sm:border-y sm:border-l sm:border-gray-700 sm:rounded-l sm:flex sm:items-center sm:justify-center sm:transition-all sm:duration-300 sm:hover:bg-gray-800"
          @click="togglePanel"
        >
          <img
            :src="isPanelCollapsed ? '/ic_arrow_left.png' : '/ic_arrow_right.png'"
            class="w-3 h-3 object-contain"
            alt=""
          />
        </button>
      </div>

      <!-- 信息区域（可滚动） - 移动端固定高度，PC端侧边栏 -->
      <div
        class="h-[65vh] sm:h-full bg-app-bg-secondary border-t sm:border-t-0 sm:border-l border-gray-800 flex flex-col transition-all duration-300 overflow-hidden"
        :class="isPanelCollapsed ? 'sm:w-0 sm:opacity-0' : 'w-full sm:w-[30vw] sm:min-w-[200px] sm:max-w-[300px] xl:w-[30vw] xl:min-w-[227px] xl:max-w-[340px] sm:opacity-100'"
      >
        <!-- 可滚动内容区域 -->
        <div class="flex-1 overflow-y-auto scrollbar-hide">
          <!-- 影片基本信息 -->
          <div class="p-4 border-b border-gray-800">
            <!-- 封面 + 信息 水平布局 -->
            <div class="flex gap-3">
              <!-- 左侧：封面 -->
              <div class="flex-shrink-0 h-[72px] sm:h-[80px]">
                <div class="relative h-full rounded-lg overflow-hidden bg-app-bg-tertiary" style="aspect-ratio: 3/4;">
                  <!-- 默认占位背景 -->
                  <div class="absolute inset-0 flex items-center justify-center bg-app-bg-tertiary">
                    <img
                      src="/ic_default_picture.png"
                      alt=""
                      class="w-8 h-8 object-contain opacity-50"
                    />
                  </div>
                  <!-- 封面图片 -->
                  <img
                    :src="getBestCover(movie?.covers || [], movie?.cover) || ''"
                    :alt="movie.title"
                    class="absolute inset-0 w-full h-full object-cover"
                  />
                </div>
              </div>

              <!-- 右侧：标题 + 标签 + 按钮 -->
              <div class="flex-1 min-w-0">
                <h1 class="text-lg font-bold leading-tight mb-2 text-white line-clamp-2">
                  {{ movie.title }}
                </h1>
                <div class="flex flex-wrap items-center gap-x-2 gap-y-1 text-xs mb-2">
                  <span
                    v-if="movie.score && movie.score > 0 && movie.category !== 6"
                    class="px-1 py-0 rounded text-[10px] font-bold bg-[#FFD700]/80 text-[#8B4513]"
                  >
                    {{ movie.score.toFixed(1) }}
                  </span>
                  <span v-if="movie.publish_year" class="text-gray-500">{{ movie.publish_year }}</span>
                  <NuxtLink
                    v-for="tag in tags"
                    :key="tag"
                    :to="routes.query(tag)"
                    target="_blank"
                    class="text-gray-500 hover:text-app-primary cursor-pointer transition-colors"
                  >
                    {{ tag }}
                  </NuxtLink>
                </div>
                <!-- 操作按钮 -->
                <div class="flex items-center gap-2 flex-wrap">
                  <button
                    class="flex items-center gap-1 px-2 py-1 text-xs rounded-lg bg-gray-800 text-gray-500 hover:bg-gray-700 hover:text-white transition-colors"
                    @click="showReportDialog = true"
                  >
                    <el-icon><Warning /></el-icon>
                    <span>报错</span>
                  </button>
                  <button
                    class="flex items-center gap-1 px-2 py-1 text-xs rounded-lg bg-gray-800 text-gray-500 hover:bg-gray-700 hover:text-white transition-colors"
                    @click="handleShare"
                  >
                    <el-icon><Share /></el-icon>
                    <span>分享</span>
                  </button>
                  <button
                    class="flex items-center gap-1 px-2 py-1 text-xs rounded-lg transition-all duration-200"
                    :class="hasRecommended
                      ? 'bg-app-primary/20 text-app-primary cursor-default'
                      : 'bg-gray-800 text-gray-500 hover:bg-app-primary hover:text-white'"
                    :disabled="hasRecommended"
                    @click="handleRecommend"
                  >
                    <el-icon :size="12"><CircleCheck v-if="hasRecommended" /><CircleCheckFilled v-else /></el-icon>
                    <span>{{ hasRecommended ? '已推荐' : '推荐' }}</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- 导演 -->
            <p v-if="directors.length" class="text-sm mb-2 mt-3">
              <span class="text-gray-500">导演：</span>
              <span class="text-gray-500">
                <template v-for="(director, index) in directors" :key="director">
                  <NuxtLink
                    :to="routes.query(director)"
                    target="_blank"
                    class="hover:text-app-primary hover:underline cursor-pointer transition-colors"
                  >
                    {{ director }}
                  </NuxtLink>
                  <span v-if="index < directors.length - 1" class="text-gray-500 mx-0.5">/</span>
                </template>
              </span>
            </p>

            <!-- 主演 -->
            <p v-if="actors.length" class="text-sm mb-3">
              <span class="text-gray-500">主演：</span>
              <span class="text-gray-500">
                <template v-for="(actor, index) in displayedActors" :key="actor">
                  <NuxtLink
                    :to="routes.query(actor)"
                    target="_blank"
                    class="hover:text-app-primary hover:underline cursor-pointer transition-colors"
                  >
                    {{ actor }}
                  </NuxtLink>
                  <span v-if="index < displayedActors.length - 1" class="text-gray-500 mx-0.5">/</span>
                </template>
                <button
                  v-if="actors.length > 3"
                  class="text-app-primary text-sm ml-1 hover:underline"
                  @click="showAllActors = !showAllActors"
                >
                  {{ showAllActors ? '收起' : '更多' }}
                </button>
              </span>
            </p>

            <!-- 简介 -->
            <div>
              <p
                class="text-sm text-gray-500 leading-relaxed"
                :class="{ 'line-clamp-3': !showFullSynopsis }"
              >
                {{ movie.contents || '暂无简介' }}
              </p>
              <button
                v-if="(movie.contents?.length || 0) > 60"
                class="text-app-primary text-sm mt-2 hover:underline"
                @click="showFullSynopsis = !showFullSynopsis"
              >
                {{ showFullSynopsis ? '收起' : '展开' }}
              </button>
            </div>
          </div>

          <!-- 选集区域 -->
          <div class="p-4 border-b border-gray-800">
            <!-- 播放源选择 -->
            <div v-if="episodeSources.length > 1" class="flex gap-2 mb-3 overflow-x-auto scrollbar-hide py-1">
              <button
                v-for="(source, index) in episodeSources"
                :key="source.source_name"
                class="relative px-3 py-1.5 text-xs rounded-lg transition-colors flex-shrink-0"
                :class="viewingSourceIndex === index
                  ? 'bg-app-primary text-white'
                  : 'bg-gray-800 text-gray-500 hover:bg-gray-700'"
                @click="switchSource(index)"
              >
                {{ formatSourceName(source.source_name) }}
                <!-- 4K标签 -->
                <span
                  v-if="has4kEpisodes(source)"
                  class="absolute -top-1.5 -right-1.5 px-1 py-0 text-[8px] font-bold bg-[#FFD700] text-[#8B4513] rounded tracking-wide border border-[#000000]"
                >
                  4K
                </span>
              </button>
            </div>

            <!-- 剧集列表 -->
            <div class="space-y-2">
              <h3 class="text-xs font-medium text-gray-500 mb-2">
                选集 ({{ viewingEpisodes.length }}集)
              </h3>
              <div class="flex flex-wrap gap-1.5">
                <button
                  v-for="(episode, index) in viewingEpisodes"
                  :key="episode.id"
                  class="px-3 py-1.5 min-w-[48px] rounded text-xs transition-colors flex items-center justify-center gap-1"
                  :class="isEpisodeActive(index)
                    ? 'bg-app-primary text-white'
                    : 'bg-gray-800 hover:bg-gray-700 text-gray-300'"
                  @click="playEpisode(index)"
                >
                  <span
                    v-if="getEpisodeLockType(episode) === 'lock' && !isLoggedIn"
                    class="px-1 text-[8px] font-bold bg-app-primary text-white rounded scale-75 origin-center"
                  >
                    登录
                  </span>
                  <img
                    v-else-if="getEpisodeLockType(episode) === 'crown'"
                    src="/ic_episodes_vip_lock.png"
                    alt="VIP"
                    class="w-4 h-4 object-contain"
                  />
                  {{ episode.title }}
                </button>
              </div>
            </div>
          </div>

          <!-- 推荐影片 -->
          <div class="p-4">
            <h3 class="text-sm text-gray-500 mb-3">相关推荐</h3>
            <div class="grid grid-cols-2 gap-3">
              <a
                v-for="m in relatedMovies"
                :key="m.id"
                :href="routes.stream(generateMovieSlug(m.id, m.title))"
                target="_blank"
                class="group block"
              >
                <div class="relative aspect-[2/3] rounded-lg overflow-hidden bg-gray-800 mb-1.5">
                  <img
                    :src="getBestCover(m.covers || [], m.cover)"
                    :alt="m.title"
                    class="w-full h-full object-cover group-hover:scale-105 transition-transform"
                    loading="lazy"
                  />
                  <div
                    v-if="m.score && m.score > 0 && m.category !== 6"
                    class="absolute top-1 right-1 px-1 py-0 rounded text-[10px] font-bold bg-[#FFD700]/80 text-[#8B4513]"
                  >
                    {{ m.score.toFixed(1) }}
                  </div>
                </div>
                <h4 class="text-xs text-gray-300 truncate group-hover:text-app-primary transition-colors">{{ m.title }}</h4>
              </a>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Loading -->
    <div v-else-if="loading" class="h-[calc(100vh-60px)] bg-app-bg flex flex-col sm:flex-row overflow-hidden">
      <!-- Player Skeleton -->
      <div class="flex-1 bg-app-bg" />
      <!-- Right Panel Skeleton - 移动端固定高度 -->
      <div class="h-[40vh] sm:h-full sm:w-[380px] xl:w-[420px] bg-app-bg p-4 space-y-4">
        <div class="space-y-3">
          <div class="h-7 bg-gray-800 rounded w-3/4 animate-pulse" />
          <div class="flex gap-2">
            <div class="h-3 bg-gray-800 rounded w-12 animate-pulse" />
            <div class="h-3 bg-gray-800 rounded w-10 animate-pulse" />
            <div class="h-3 bg-gray-800 rounded w-20 animate-pulse" />
          </div>
          <div class="flex gap-2">
            <div class="h-6 bg-gray-800 rounded w-14 animate-pulse" />
            <div class="h-6 bg-gray-800 rounded w-14 animate-pulse" />
            <div class="h-6 bg-gray-800 rounded w-14 animate-pulse" />
          </div>
        </div>
        <div class="h-12 bg-gray-800 rounded animate-pulse" />
        <div class="grid grid-cols-4 gap-1.5">
          <div v-for="i in 12" :key="i" class="aspect-video bg-gray-800 rounded animate-pulse" />
        </div>
        <div class="h-4 bg-gray-800 rounded w-20 animate-pulse" />
        <div class="grid grid-cols-2 gap-3">
          <div v-for="i in 4" :key="i" class="space-y-1.5">
            <div class="aspect-[2/3] bg-gray-800 rounded-lg animate-pulse" />
            <div class="h-3 bg-gray-800 rounded w-3/4 animate-pulse" />
          </div>
        </div>
      </div>
    </div>

    <!-- Not Found -->
    <div v-else class="flex-1 flex flex-col items-center justify-center bg-app-bg">
      <el-icon :size="64" class="text-gray-500 mb-4"><Film /></el-icon>
      <p class="text-gray-500">影片不存在或无法播放</p>
      <NuxtLink :to="routes.home()" class="mt-4 text-app-primary hover:underline">返回首页</NuxtLink>
    </div>

    <!-- 报错弹窗 -->
    <el-dialog
      v-model="showReportDialog"
      title="问题反馈"
      :width="isMobile ? '90%' : '400px'"
      align-center
      class="report-dialog"
    >
      <div class="space-y-4">
        <p class="text-sm text-gray-400">
          影片：{{ movie?.title }}<br>
          剧集：{{ playingEpisode?.title }}
        </p>
        <textarea
          v-model="reportForm.content"
          rows="4"
          class="w-full px-4 py-3 bg-[#222] border-0 rounded-lg text-sm text-gray-100 focus:outline-none focus:ring-2 focus:ring-app-primary/50 resize-none placeholder:text-gray-500"
          placeholder="请描述您遇到的问题，如：无法播放、画面模糊、音画不同步等"
        />
      </div>
      <template #footer>
        <div class="flex justify-end gap-2">
          <button
            class="px-4 py-2 bg-[#222] text-gray-300 rounded-lg text-sm hover:bg-[#2a2a2a] transition-colors"
            @click="showReportDialog = false"
          >
            取消
          </button>
          <button
            class="px-4 py-2 bg-app-primary text-white rounded-lg text-sm hover:bg-app-primary-hover transition-colors disabled:opacity-50"
            :disabled="submittingReport || !reportForm.content.trim()"
            @click="submitReport"
          >
            {{ submittingReport ? '提交中...' : '提交' }}
          </button>
        </div>
      </template>
    </el-dialog>

    <!-- 分享弹窗 -->
    <ShareDialog
      v-model:visible="shareVisible"
      :title="movie?.title || ''"
      :url="shareUrl"
      :cover="getBestCover(movie?.covers || [], movie?.cover) || ''"
      :year="Number(movie?.year || movie?.publish_year || 0)"
      :tags="movie?.tags"
      :score="movie?.score"
    />

    <!-- 权限提示弹窗 -->
    <el-dialog
      v-model="showPermissionDialog"
      :width="isMobile ? '85%' : '420px'"
      :show-close="false"
      align-center
      class="permission-dialog"
    >
      <div class="text-center py-6 px-4">
        <!-- 主文案 -->
        <div class="mb-6">
          <template v-if="permissionDialogType === 'login'">
            <p class="text-gray-100 text-base font-medium mb-3 leading-relaxed">
              您正在尝试观看「<span class="text-app-primary font-semibold">{{ permissionDialogEpisode?.title || '该剧集' }}</span>」
            </p>
            <p class="text-gray-500 text-sm leading-relaxed">
              该内容为登录专享，登录后即可免费观看全站海量高清影视资源，无需付费，没有广告打扰。
            </p>
          </template>
          <template v-else>
            <p class="text-gray-100 text-base font-medium mb-3 leading-relaxed">
              「<span class="text-amber-600 font-semibold">{{ permissionDialogEpisode?.title || '该剧集' }}</span>」为VIP专属内容
            </p>
            <p class="text-gray-500 text-sm leading-relaxed">
              该影片仅限VIP会员观看。升级VIP可解锁全站付费内容，享受高清画质、无广告观影、抢先观看最新大片等专属权益。
            </p>
          </template>
        </div>

        <!-- 权益说明 -->
        <div
          class="p-4 rounded-xl text-left border"
          :class="permissionDialogType === 'login' ? 'bg-blue-950/50 border-blue-900/50' : 'bg-amber-950/50 border-amber-900/50'"
        >
          <p class="text-sm font-medium mb-2" :class="permissionDialogType === 'login' ? 'text-blue-400' : 'text-amber-400'">
            {{ permissionDialogType === 'login' ? '登录即享权益' : 'VIP会员权益' }}
          </p>
          <div class="grid grid-cols-2 gap-2 text-xs" :class="permissionDialogType === 'login' ? 'text-blue-300' : 'text-amber-300'">
            <div class="flex items-center gap-1.5">
              <el-icon :size="14"><CircleCheck /></el-icon>
              <span>{{ permissionDialogType === 'login' ? '免费观看全站资源' : '全站内容无限制观看' }}</span>
            </div>
            <div class="flex items-center gap-1.5">
              <el-icon :size="14"><CircleCheck /></el-icon>
              <span>高清画质</span>
            </div>
            <div class="flex items-center gap-1.5">
              <el-icon :size="14"><CircleCheck /></el-icon>
              <span>无广告打扰</span>
            </div>
            <div class="flex items-center gap-1.5">
              <el-icon :size="14"><CircleCheck /></el-icon>
              <span>{{ permissionDialogType === 'login' ? '播放记录云端同步' : '新片抢先观看' }}</span>
            </div>
          </div>
        </div>

        <!-- 按钮 -->
        <div class="flex gap-3 mt-6">
          <button
            class="flex-1 py-3 bg-app-bg text-gray-300 rounded-xl text-sm font-medium hover:bg-app-bg-tertiary transition-colors"
            @click="closePermissionDialog"
          >
            稍后再说
          </button>
          <button
            v-if="permissionDialogType === 'login'"
            class="flex-1 py-3 bg-app-primary text-white rounded-xl text-sm font-medium hover:bg-app-primary-hover transition-colors"
            @click="handleGoToLogin"
          >
            立即登录
          </button>
          <button
            v-else
            class="flex-1 py-3 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-xl text-sm font-medium hover:from-amber-600 hover:to-orange-600 transition-colors"
            @click="handleGoToUpgrade"
          >
            升级VIP
          </button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<style scoped>
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}

/* 弹窗深色样式 - 统一风格 */
:deep(.el-dialog.report-dialog),
:deep(.el-dialog.permission-dialog) {
  background-color: #141414 !important;
}

:deep(.report-dialog .el-dialog__header),
:deep(.permission-dialog .el-dialog__header) {
  padding: 16px 20px;
  margin-right: 0;
  background-color: #141414;
}

:deep(.permission-dialog .el-dialog__header) {
  display: none;
}

:deep(.report-dialog .el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
  color: #f5f5f5;
}

:deep(.report-dialog .el-dialog__body),
:deep(.permission-dialog .el-dialog__body) {
  background-color: #141414;
}

:deep(.report-dialog .el-dialog__body) {
  padding: 20px;
}

:deep(.permission-dialog .el-dialog__body) {
  padding: 0;
}

:deep(.report-dialog .el-dialog__footer) {
  background-color: #141414;
  padding: 12px 20px;
}
</style>

<script setup lang="ts">
import { Film, Warning, Share, CircleCheck, CircleCheckFilled, Lock, Trophy } from '@element-plus/icons-vue'
import type { Movie, EpisodeSource, MovieItem, Episode } from '~/types'
import VideoPlayerWithDanmaku from '~/components/player/VideoPlayerWithDanmaku.vue'

definePageMeta({
  layout: 'player'
})

const route = useRoute()
const router = useRouter()
const { getMovieDetail, getRelatedMovies, updateWatchCount, updateRecommendCount } = useMovies()
const { addHistory } = useHistory()
const { addHistory: addPlayProgress, isLoggedIn } = useUser()
const { getBestCover } = useImageProxy()
const { nativeShare } = useShare()
const {
  requestPermission,
  getEpisodeLockType,
  showPermissionDialog,
  permissionDialogType,
  permissionDialogEpisode,
  closePermissionDialog,
  handleGoToLogin,
  handleGoToUpgrade
} = useEpisodePermission()

const slug = route.params.slug as string
const id = extractIdFromSlug(slug)

// 播放状态（控制播放器）
const playingSourceIndex = ref(0)
const playingEpisodeIndex = ref(-1)  // -1 表示未选择任何剧集
const videoPlayerRef = ref<InstanceType<typeof VideoPlayerWithDanmaku> | null>(null)

// 当播放器准备好时设置多源标志
watch(videoPlayerRef, (newRef) => {
  if (newRef) {
    newRef.setHasMultipleSources(episodeSources.value.length > 1)
  }
})

// 查看状态（控制右侧显示的剧集列表）
const viewingSourceIndex = ref(0)

const showFullSynopsis = ref(false)
const showAllActors = ref(false)
const showReportDialog = ref(false)
const isPanelCollapsed = ref(false)

const togglePanel = () => {
  isPanelCollapsed.value = !isPanelCollapsed.value
}

const shareVisible = ref(false)
const hasRecommended = ref(false)
const reportForm = reactive({
  content: ''
})

// 分享链接
const shareUrl = computed(() => {
  if (typeof window === 'undefined') return ''
  return window.location.href
})
const submittingReport = ref(false)

// ===== SSR 预取播放页数据 =====
const { data: pageData, pending: loading } = await useAsyncData(
  `stream-${id}`,
  async () => {
    const [detail, related] = await Promise.all([
      getMovieDetail(id),
      getRelatedMovies(id)
    ])
    return {
      movie: detail,
      relatedMovies: related,
      episodeSources: detail?.episode_sources || []
    }
  },
  {
    server: true,
    lazy: false,
    default: () => ({
      movie: null as Movie | null,
      relatedMovies: [] as MovieItem[],
      episodeSources: [] as EpisodeSource[]
    })
  }
)

const movie = computed(() => pageData.value?.movie ?? null)
const relatedMovies = computed(() => pageData.value?.relatedMovies ?? [])
const episodeSources = computed(() => pageData.value?.episodeSources ?? [])

// 当前正在播放的源
const playingSource = computed(() => {
  return episodeSources.value[playingSourceIndex.value]
})

// 当前正在播放的剧集
const playingEpisode = computed(() => {
  return playingSource.value?.episodes?.[playingEpisodeIndex.value]
})

// 当前查看的源的剧集列表
const viewingEpisodes = computed(() => {
  return episodeSources.value[viewingSourceIndex.value]?.episodes || []
})

// 判断源是否包含4K剧集
const has4kEpisodes = (source: EpisodeSource): boolean => {
  return source.episodes?.some(ep => ep.title?.toLowerCase().includes('4k')) ?? false
}

// 判断某个剧集是否应该显示为选中状态
const isEpisodeActive = (episodeIndex: number) => {
  return viewingSourceIndex.value === playingSourceIndex.value &&
         episodeIndex === playingEpisodeIndex.value
}

// SEO
const brandName = useBrandName()
useHead(() => ({
  title: movie.value ? `正在播放：${movie.value.title} - ${brandName}` : '播放页',
  link: [
    { rel: 'canonical', href: () => typeof window !== 'undefined' ? window.location.href : '' }
  ]
}))

// Computed
const coverUrl = computed(() => {
  // 优先使用横屏封面（适合播放器）
  const horizontalCover = movie.value?.extra?.horizontal_cover
  if (horizontalCover) return horizontalCover
  // 没有横屏封面时，使用原有逻辑获取竖屏封面
  return getBestCover(movie.value?.covers || [], movie.value?.cover) || ''
})

const tags = computed(() => {
  return (movie.value?.tags || []).slice(0, 8)
})

const directors = computed(() => {
  return movie.value?.directors || []
})

const actors = computed(() => {
  return movie.value?.actors || []
})

const displayedActors = computed(() => {
  if (showAllActors.value) {
    return actors.value
  }
  return actors.value.slice(0, 3)
})

const isMobile = computed(() => {
  return process.client ? window.innerWidth < 640 : false
})

const hasNextEpisode = computed(() => {
  return playingEpisodeIndex.value >= 0 &&
         playingEpisodeIndex.value < playingSource.value?.episodes?.length - 1
})

// Methods
const formatSourceName = (name: string): string => {
  if (!name) return ''
  return name
    .replace(/m3u8/gi, '')
    .replace(/地址/g, '')
    .replace(/资源/g, '')
    .trim()
}

// 切换查看的源
const switchSource = (sourceIndex: number) => {
  viewingSourceIndex.value = sourceIndex
}

// 播放器请求切换源（从播放器组件发出）
const onSwitchSource = async () => {
  // 找到下一个可用的源
  const nextIndex = (playingSourceIndex.value + 1) % episodeSources.value.length
  if (nextIndex !== playingSourceIndex.value) {
    // 切换到下一个源，尝试播放相同索引的剧集，如果没有则播放第一个
    viewingSourceIndex.value = nextIndex
    playingSourceIndex.value = nextIndex
    // 如果有剧集，尝试播放当前剧集索引，如果不存在则播放第一个
    const episodes = episodeSources.value[nextIndex]?.episodes || []
    if (episodes.length > 0) {
      const targetIndex = Math.min(playingEpisodeIndex.value, episodes.length - 1)
      await playEpisode(Math.max(0, targetIndex))
    }
  } else {
    ElMessage.warning('没有其他可用播放源')
  }
}

// 更新URL（使用新的参数名src和ep）
const updateUrl = () => {
  // 只有当选中了具体剧集时才更新 URL
  if (playingEpisodeIndex.value < 0) return
  const query = buildStreamQuery(playingSourceIndex.value, playingEpisodeIndex.value)
  window.history.replaceState(null, '', `/stream/${slug}${query ? '?' + query : ''}`)
}

// 播放指定剧集
const playEpisode = async (episodeIndex: number) => {
  // 获取要播放的剧集
  const targetEpisode = viewingEpisodes.value[episodeIndex]

  // 检查播放权限
  const hasPermission = await requestPermission(targetEpisode, {
    autoShowLogin: true,
    customMessages: {
      loginRequired: `「${targetEpisode?.title || '该剧集'}」需要登录后才能观看`,
      premiumRequired: `「${targetEpisode?.title || '该剧集'}」仅限付费会员观看`
    }
  })

  if (!hasPermission) {
    // 权限不足，不执行播放
    return
  }

  playingSourceIndex.value = viewingSourceIndex.value
  playingEpisodeIndex.value = episodeIndex

  updateUrl()

  if (movie.value) {
    // 异步记录播放历史（不阻塞）
    void addHistory({
      id: movie.value.id,
      title: movie.value.title,
      cover: coverUrl.value,
      covers: movie.value.covers || [],  // 传递 covers 数组供封面选择
      sourceName: playingSource.value?.source_name,
      episodeTitle: playingSource.value?.episodes?.[episodeIndex]?.title
    })
  }
}

const playNext = async () => {
  if (hasNextEpisode.value) {
    const nextIndex = playingEpisodeIndex.value + 1

    // 获取下一集
    const nextEpisode = playingSource.value?.episodes?.[nextIndex]

    // 检查下一集的播放权限
    const hasPermission = await requestPermission(nextEpisode, {
      autoShowLogin: true,
      customMessages: {
        loginRequired: `「${nextEpisode?.title || '下一集'}」需要登录后才能观看`,
        premiumRequired: `「${nextEpisode?.title || '下一集'}」仅限付费会员观看`
      }
    })

    if (!hasPermission) {
      // 权限不足，不自动播放下一集
      return
    }

    playingEpisodeIndex.value = nextIndex
    viewingSourceIndex.value = playingSourceIndex.value

    updateUrl()

    if (movie.value) {
      // 异步记录播放历史（不阻塞）
      void addHistory({
        id: movie.value.id,
        title: movie.value.title,
        cover: coverUrl.value,
        covers: movie.value.covers || [],  // 传递 covers 数组供封面选择
        sourceName: playingSource.value?.source_name,
        episodeTitle: playingSource.value?.episodes?.[nextIndex]?.title
      })
    }
  }
}

const onEpisodeEnd = () => {
  if (hasNextEpisode.value) {
    playNext()
  }
}

const onTimeUpdate = (time: number) => {
  if (movie.value) {
    addPlayProgress(movie.value.id, time)
  }
}

// 分享
const handleShare = async () => {
  const shared = await nativeShare({
    title: movie.value?.title || brandName,
    text: `我正在看《${movie.value?.title}》，一起来看吧！`,
    url: shareUrl.value
  })

  if (!shared) {
    shareVisible.value = true
  }
}

// 推荐此片
const handleRecommend = async () => {
  if (hasRecommended.value || !movie.value) return

  const success = await updateRecommendCount(movie.value.id, true)
  if (success) {
    hasRecommended.value = true
    const recommendedMovies = JSON.parse(localStorage.getItem('recommendedMovies') || '[]')
    if (!recommendedMovies.includes(movie.value.id)) {
      recommendedMovies.push(movie.value.id)
      localStorage.setItem('recommendedMovies', JSON.stringify(recommendedMovies))
    }
    ElMessage.success('感谢你的推荐！')
  } else {
    ElMessage.error('推荐失败，请稍后重试')
  }
}

// 提交报错
const submitReport = async () => {
  if (!reportForm.content.trim()) {
    ElMessage.warning('请填写报错内容')
    return
  }

  submittingReport.value = true
  try {
    const { submitFeedback } = useFeedback()
    const result = await submitFeedback({
      content: `播放页面报错 - 影片: ${movie.value?.title}(${id})\n剧集: ${playingEpisode.value?.title}\n问题描述: ${reportForm.content}`,
      feedback_type: 3
    })

    if (result.success) {
      ElMessage.success('报错已提交，我们会尽快处理')
      showReportDialog.value = false
      reportForm.content = ''
    } else {
      ElMessage.error(result.message)
    }
  } finally {
    submittingReport.value = false
  }
}

// 客户端初始化
onMounted(async () => {
  updateWatchCount(id)

  const recommendedMovies = JSON.parse(localStorage.getItem('recommendedMovies') || '[]')
  if (recommendedMovies.includes(id)) {
    hasRecommended.value = true
  }

  // 从URL参数获取播放源和剧集索引（使用新的参数名src和ep）
  const { source, episode } = parseStreamParams(route.query)
  if (source >= 0 && source < episodeSources.value.length) {
    playingSourceIndex.value = source
    viewingSourceIndex.value = source
  }

  const episodes = episodeSources.value[playingSourceIndex.value]?.episodes || []
  if (episode >= 0 && episode < episodes.length) {
    // 检查初始剧集的播放权限
    const initialEpisode = episodes[episode]
    const hasPermission = await requestPermission(initialEpisode, {
      autoShowLogin: true,
      customMessages: {
        loginRequired: `「${initialEpisode?.title || '该剧集'}」需要登录后才能观看`,
        premiumRequired: `「${initialEpisode?.title || '该剧集'}」仅限付费会员观看`
      }
    })

    if (hasPermission) {
      playingEpisodeIndex.value = episode
    }
    // 权限不足时 requestPermission 会显示弹窗，不设置 playingEpisodeIndex
    // 播放器不会加载任何剧集，等待用户操作
  }

  if (movie.value) {
    // 异步记录播放历史（不阻塞）
    void addHistory({
      id: movie.value.id,
      title: movie.value.title,
      cover: coverUrl.value,
      covers: movie.value.covers || [],  // 传递 covers 数组供封面选择
      sourceName: playingSource.value?.source_name,
      episodeTitle: playingEpisode.value?.title
    })
  }

  const { recordPageVisit } = useActivity()
  recordPageVisit(`/stream/${slug}`)
})
</script>
