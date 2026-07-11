<template>
  <div class="min-h-screen bg-app-bg">
    <!-- Top Navigation Bar -->
    <div class="sticky top-0 z-50 bg-app-bg/95 backdrop-blur-sm shadow-sm">
      <div class="flex items-center gap-4 px-4 py-3">
        <!-- Back Button -->
        <button
          class="flex items-center gap-1 text-white/70 hover:text-white transition-colors"
          @click="goBack"
        >
          <el-icon :size="20"><ArrowLeft /></el-icon>
          <span class="text-sm hidden sm:inline">返回</span>
        </button>

        <!-- Home Button - 只显示图标，移动端隐藏 -->
        <NuxtLink
          :to="routes.home()"
          class="hidden sm:flex items-center transition-colors group"
        >
          <img
            src="/ic_home.png"
            alt="首页"
            class="w-5 h-5 object-contain opacity-70 group-hover:opacity-100 group-hover:text-app-primary-light transition-all"
            style="filter: brightness(0) invert(1);"
          />
        </NuxtLink>

        <!-- Search Input -->
        <div class="flex-1 max-w-xl">
          <SearchInput variant="default" />
        </div>

        <!-- User Menu -->
        <div class="flex items-center gap-4 ml-auto">
          <!-- History Button - 保持默认样式 -->
          <HistoryDropdown variant="default" />

          <!-- User Menu (Logged In) -->
          <div v-if="isLoggedIn && userInfo" class="relative">
            <button
              ref="userButtonRef"
              class="flex items-center gap-2 text-sm transition-colors text-white/70 hover:text-white"
              @click="toggleUserDropdown"
            >
              <el-icon :size="18"><User /></el-icon>
              <span class="hidden sm:inline max-w-[80px] truncate">{{ userInfo.name || userInfo.account }}</span>
            </button>

            <!-- User Dropdown -->
            <Teleport v-if="isClient" to="body">
              <Transition name="fade">
                <div
                  v-if="showUserDropdown"
                  ref="userDropdownRef"
                  class="fixed z-50 rounded-lg shadow-lg py-2 w-52 dropdown-transparent"
                  :style="userDropdownStyle"
                >
                  <div class="px-3 py-2">
                    <div class="flex items-center gap-2">
                      <img
                        src="/ic_default_avatar.png"
                        alt="头像"
                        class="w-8 h-8 rounded-full object-cover flex-shrink-0 bg-gray-700"
                        onerror="this.style.display='none'"
                      />
                      <div class="flex-1 min-w-0">
                        <div class="flex items-center gap-2">
                          <p class="text-sm font-medium text-white truncate">{{ userInfo.name || userInfo.account }}</p>
                          <span
                            v-if="userInfo.role !== undefined"
                            class="text-[10px] px-1.5 py-0.5 rounded font-medium flex-shrink-0"
                            :class="{
                              'bg-blue-900/50 text-blue-300': userInfo.role === 0,
                              'bg-red-900/50 text-red-300': userInfo.role === 1,
                              'bg-amber-900/50 text-amber-300': userInfo.role === 2
                            }"
                          >
                            {{ userInfo.role === 1 ? '管理员' : userInfo.role === 2 ? '付费用户' : '普通用户' }}
                          </span>
                        </div>
                        <p class="text-xs text-white/70 truncate">{{ userInfo.phone || '' }}</p>
                      </div>
                    </div>
                  </div>

                  <!-- 管理员专用入口已移除 -->

                  <div class="flex pt-1">
                    <button
                      class="flex-1 flex items-center justify-center gap-1.5 px-3 py-2.5 text-sm text-white hover:bg-white/10 hover:text-app-primary-light transition-colors"
                      @click="openResetPassword"
                    >
                      <el-icon :size="14"><Lock /></el-icon>
                      <span>重设密码</span>
                    </button>
                    <button
                      class="flex-1 flex items-center justify-center gap-1.5 px-3 py-2.5 text-sm text-white hover:bg-white/10 hover:text-red-400 transition-colors"
                      @click="handleLogout"
                    >
                      <el-icon :size="14"><SwitchButton /></el-icon>
                      <span>退出登录</span>
                    </button>
                  </div>
                </div>
              </Transition>

              <!-- Backdrop -->
              <div
                v-if="showUserDropdown"
                class="fixed inset-0 z-40"
                @click="showUserDropdown = false"
              />
            </Teleport>
          </div>

          <!-- Login Button (Not Logged In) -->
          <button
            v-else
            class="flex items-center gap-2 text-sm transition-colors text-white/70 hover:text-white"
            @click="showLoginModal = true"
          >
            <el-icon :size="18"><User /></el-icon>
            <span class="hidden sm:inline">登录</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <main>
      <slot />
    </main>

    <!-- Auth Dialog -->
    <AuthDialog v-model="showLoginModal" />
  </div>
</template>

<script setup lang="ts">
import { ArrowLeft, User, SwitchButton, Lock } from '@element-plus/icons-vue'
import { onClickOutside } from '@vueuse/core'
import { nextTick } from 'vue'
import SearchInput from '~/components/SearchInput.vue'
import HistoryDropdown from '~/components/HistoryDropdown.vue'
import AuthDialog from '~/components/AuthDialog.vue'

const router = useRouter()
const { isLoggedIn, userInfo, logout: userLogout } = useUser()
const showLoginModal = ref(false)

// 客户端标识（用于模板）
const isClient = import.meta.client

// 用户下拉菜单
const showUserDropdown = ref(false)
const userButtonRef = ref<HTMLElement>()
const userDropdownRef = ref<HTMLElement>()
const userDropdownStyle = ref({ top: '0px', left: '0px' })

const toggleUserDropdown = async () => {
  showUserDropdown.value = !showUserDropdown.value
  if (showUserDropdown.value && userButtonRef.value) {
    await nextTick()
    const rect = userButtonRef.value.getBoundingClientRect()
    userDropdownStyle.value = {
      top: `${rect.bottom + 8}px`,
      left: `${rect.right - 208}px`
    }
  }
}

onClickOutside(userDropdownRef, () => {
  showUserDropdown.value = false
})

const handleLogout = () => {
  userLogout()
  showUserDropdown.value = false
  router.push('/')
}

const openResetPassword = () => {
  showUserDropdown.value = false
  showLoginModal.value = true
}

const goBack = () => {
  router.push(routes.home())
}
</script>

<style>
/* 下拉菜单过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
