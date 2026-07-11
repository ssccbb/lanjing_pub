<template>
  <div
    v-if="showGuide"
    class="fixed inset-0 z-[100] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4"
    @click.self="closeGuide"
  >
    <div class="bg-app-bg-secondary rounded-2xl w-full max-w-md p-6 pb-8 max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="flex items-center justify-between mb-6">
        <h3 class="text-xl font-bold text-white">安装应用到桌面</h3>
        <button
          @click="closeGuide"
          class="w-8 h-8 flex items-center justify-center rounded-full bg-white/10 text-gray-400 hover:bg-white/20"
        >
          <el-icon :size="18"><Close /></el-icon>
        </button>
      </div>

      <!-- macOS Safari 步骤 -->
      <div v-if="!isIos" class="space-y-4">
        <!-- Step 1 -->
        <div class="flex items-start gap-4">
          <div class="w-8 h-8 rounded-full bg-app-primary flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
            1
          </div>
          <div class="flex-1">
            <p class="text-gray-200">点击菜单栏<strong class="text-white">"文件"</strong></p>
            <p class="text-sm text-gray-400 mt-1">或使用快捷键显示菜单</p>
          </div>
        </div>

        <!-- Step 2 -->
        <div class="flex items-start gap-4">
          <div class="w-8 h-8 rounded-full bg-app-primary flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
            2
          </div>
          <div class="flex-1">
            <p class="text-gray-200">选择<strong class="text-white">"将此页面添加到 Dock"</strong></p>
            <div class="mt-2 flex items-center gap-2 bg-white/5 rounded-lg p-3">
              <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-app-primary to-app-primary-hover flex items-center justify-center flex-shrink-0">
                <el-icon :size="20" class="text-white"><Plus /></el-icon>
              </div>
              <div>
                <p class="text-sm text-white">将此页面添加到 Dock</p>
                <p class="text-xs text-gray-400">{{ brandName }}将出现在 Dock 中</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 3 -->
        <div class="flex items-start gap-4">
          <div class="w-8 h-8 rounded-full bg-app-primary flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
            3
          </div>
          <div class="flex-1">
            <p class="text-gray-200">点击<strong class="text-white">"添加"</strong>完成安装</p>
            <p class="text-sm text-gray-400 mt-1">之后就可以像原生 App 一样使用了！</p>
          </div>
        </div>
      </div>

      <!-- iOS Safari 步骤 -->
      <div v-else class="space-y-4">
        <!-- Step 1 -->
        <div class="flex items-start gap-4">
          <div class="w-8 h-8 rounded-full bg-app-primary flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
            1
          </div>
          <div class="flex-1">
            <p class="text-gray-200">点击底部的<strong class="text-white">"分享"按钮</strong></p>
            <div class="mt-2 flex items-center gap-2">
              <div class="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center">
                <el-icon :size="24" class="text-white"><Share /></el-icon>
              </div>
              <span class="text-sm text-gray-400">或向上滑动显示分享菜单</span>
            </div>
          </div>
        </div>

        <!-- Step 2 -->
        <div class="flex items-start gap-4">
          <div class="w-8 h-8 rounded-full bg-app-primary flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
            2
          </div>
          <div class="flex-1">
            <p class="text-gray-200">在菜单中找到<strong class="text-white">"添加到主屏幕"</strong></p>
            <div class="mt-2 flex items-center gap-2 bg-white/5 rounded-lg p-3">
              <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-app-primary to-app-primary-hover flex items-center justify-center flex-shrink-0">
                <el-icon :size="20" class="text-white"><Plus /></el-icon>
              </div>
              <div>
                <p class="text-sm text-white">添加到主屏幕</p>
                <p class="text-xs text-gray-400">添加{{ brandName }}图标到主屏幕</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 3 -->
        <div class="flex items-start gap-4">
          <div class="w-8 h-8 rounded-full bg-app-primary flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
            3
          </div>
          <div class="flex-1">
            <p class="text-gray-200">点击<strong class="text-white">"添加"</strong>完成安装</p>
            <p class="text-sm text-gray-400 mt-1">之后就可以像原生 App 一样使用了！</p>
          </div>
        </div>
      </div>

      <!-- Benefits -->
      <div class="mt-6 p-4 bg-white/5 rounded-xl">
        <p class="text-sm text-gray-300 mb-3">安装后的好处：</p>
        <div class="grid grid-cols-2 gap-3">
          <div class="flex items-center gap-2">
            <el-icon class="text-app-primary" :size="16"><CircleCheckFilled /></el-icon>
            <span class="text-sm text-gray-200">独立窗口</span>
          </div>
          <div class="flex items-center gap-2">
            <el-icon class="text-app-primary" :size="16"><CircleCheckFilled /></el-icon>
            <span class="text-sm text-gray-200">离线可用</span>
          </div>
          <div class="flex items-center gap-2">
            <el-icon class="text-app-primary" :size="16"><CircleCheckFilled /></el-icon>
            <span class="text-sm text-gray-200">快速启动</span>
          </div>
          <div class="flex items-center gap-2">
            <el-icon class="text-app-primary" :size="16"><CircleCheckFilled /></el-icon>
            <span class="text-sm text-gray-200">无浏览器UI</span>
          </div>
        </div>
      </div>

      <!-- Don't show again -->
      <div class="mt-4 flex items-center gap-2">
        <input
          type="checkbox"
          id="dontShowAgain"
          v-model="dontShowAgain"
          class="w-4 h-4 rounded border-gray-600 bg-white/10 accent-app-primary"
        />
        <label for="dontShowAgain" class="text-sm text-gray-400">不再提示</label>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Close, Share, Plus, CircleCheckFilled } from '@element-plus/icons-vue'

const brandName = useBrandName()
const showGuide = ref(false)
const dontShowAgain = ref(false)
const isIos = ref(false)

onMounted(() => {
  // 检测设备类型
  const ua = navigator.userAgent
  isIos.value = /iPad|iPhone|iPod/.test(ua)

  // 检查是否已经安装过 PWA
  const isStandalone = window.matchMedia('(display-mode: standalone)').matches ||
    (window.navigator as any).standalone === true

  // 检查是否用户选择了不再提示
  const hideGuide = localStorage.getItem('hide-safari-pwa-guide')

  // 仅在 iOS 设备上自动显示引导
  if (isIos.value && !isStandalone && hideGuide !== 'true') {
    setTimeout(() => {
      showGuide.value = true
    }, 3000)
  }
})

// 关闭引导
const closeGuide = () => {
  showGuide.value = false
  if (dontShowAgain.value) {
    localStorage.setItem('hide-safari-pwa-guide', 'true')
  }
}

// 提供打开方法供外部调用
const openGuide = () => {
  showGuide.value = true
  dontShowAgain.value = false
}

defineExpose({
  openGuide
})
</script>