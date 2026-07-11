<template>
  <el-dialog
    v-model="visible"
    :width="isMobile ? '92%' : '440px'"
    :show-close="false"
    align-center
    class="auth-dialog"
    :class="{ 'mobile-dialog': isMobile }"
  >
    <div class="p-8 sm:p-10">
      <!-- 关闭按钮 -->
      <button
        class="absolute top-5 right-5 p-2 text-gray-500 hover:text-gray-300 hover:bg-gray-700 rounded-full transition-all"
        @click="visible = false"
      >
        <el-icon :size="20"><Close /></el-icon>
      </button>

      <!-- Logo -->
      <div class="flex justify-center mb-8">
        <div class="w-16 h-16 rounded-2xl flex items-center justify-center text-white text-2xl font-bold" style="background-color: #2220d0;">
          影
        </div>
      </div>

      <!-- 标题和切换 -->
      <div class="text-center mb-8">
        <h2 class="text-2xl font-bold mb-3 text-gray-100">
          {{ formType === 'login' ? '欢迎回来' : formType === 'register' ? '创建账号' : '重置密码' }}
        </h2>
        <div class="flex items-center justify-center gap-2 text-sm">
          <span class="text-gray-400">
            {{ formType === 'login' ? '还没有账号？' : formType === 'register' ? '已有账号？' : '想起密码了？' }}
          </span>
          <button
            class="text-app-primary-light hover:text-[#3b82f6] font-semibold transition-colors"
            @click="formType = formType === 'login' ? 'register' : 'login'"
          >
            {{ formType === 'login' ? '立即注册' : formType === 'register' ? '立即登录' : '去登录' }}
          </button>
        </div>
      </div>

      <!-- 登录表单 -->
      <form v-if="formType === 'login'" class="space-y-4 sm:space-y-5" @submit.prevent="handleLogin">
        <div class="space-y-3 sm:space-y-4">
          <div class="flex items-center gap-2 sm:gap-3 px-3 sm:px-4 py-3 sm:py-3.5 bg-app-bg-secondary rounded-xl focus-within:ring-2 focus-within:ring-app-primary/20 transition-all">
            <el-icon :size="18" class="text-gray-500 flex-shrink-0">
              <User />
            </el-icon>
            <input
              v-model="loginForm.phone"
              type="tel"
              placeholder="手机号"
              class="flex-1 bg-transparent outline-none text-sm text-gray-100 placeholder-gray-500"
            />
          </div>
          <div class="flex items-center gap-2 sm:gap-3 px-3 sm:px-4 py-3 sm:py-3.5 bg-app-bg-secondary rounded-xl focus-within:ring-2 focus-within:ring-app-primary/20 transition-all">
            <el-icon :size="18" class="text-gray-500 flex-shrink-0">
              <Lock />
            </el-icon>
            <input
              v-model="loginForm.password"
              type="password"
              placeholder="密码"
              class="flex-1 bg-transparent outline-none text-sm text-gray-100 placeholder-gray-500"
            />
          </div>
        </div>

        <div class="flex items-center justify-between text-xs sm:text-sm">
          <label class="flex items-center gap-2 text-gray-400 cursor-pointer hover:text-gray-200 transition-colors">
            <input v-model="rememberMe" type="checkbox" class="w-4 h-4 rounded border-gray-600 text-app-primary focus:ring-app-primary bg-app-bg" />
            <span>记住我</span>
          </label>
          <button type="button" class="text-app-primary-light hover:text-[#3b82f6] font-medium transition-colors" @click="formType = 'reset'">忘记密码？</button>
        </div>

        <button
          type="submit"
          class="w-full py-3 sm:py-3.5 bg-gradient-to-r from-app-primary to-app-primary-hover text-white rounded-xl font-semibold hover:shadow-lg hover:shadow-blue-500/30 hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 disabled:hover:shadow-none text-sm sm:text-base"
          :disabled="loading"
        >
          {{ loading ? '登录中...' : '登 录' }}
        </button>
      </form>

      <!-- 注册表单 -->
      <form v-else-if="formType === 'register'" class="space-y-4 sm:space-y-5" @submit.prevent="handleRegister">
        <div class="space-y-3 sm:space-y-4">
          <div class="flex items-center gap-2 sm:gap-3 px-3 sm:px-4 py-3 sm:py-3.5 bg-app-bg-secondary rounded-xl focus-within:ring-2 focus-within:ring-app-primary/20 transition-all">
            <el-icon :size="18" class="text-gray-500 flex-shrink-0">
              <User />
            </el-icon>
            <input
              v-model="registerForm.username"
              type="text"
              placeholder="用户名"
              class="flex-1 bg-transparent outline-none text-sm text-gray-100 placeholder-gray-500"
            />
          </div>
          <div class="flex items-center gap-2 sm:gap-3 px-3 sm:px-4 py-3 sm:py-3.5 bg-app-bg-secondary rounded-xl focus-within:ring-2 focus-within:ring-app-primary/20 transition-all">
            <el-icon :size="18" class="text-gray-500 flex-shrink-0">
              <Iphone />
            </el-icon>
            <input
              v-model="registerForm.phone"
              type="tel"
              placeholder="手机号"
              class="flex-1 bg-transparent outline-none text-sm text-gray-100 placeholder-gray-500"
            />
          </div>
          <div class="flex gap-2 sm:gap-3">
            <div class="flex items-center gap-2 sm:gap-3 px-3 sm:px-4 py-3 sm:py-3.5 bg-app-bg-secondary rounded-xl focus-within:ring-2 focus-within:ring-app-primary/20 transition-all flex-1 min-w-0">
              <el-icon :size="18" class="text-gray-500 flex-shrink-0">
                <Message />
              </el-icon>
              <input
                v-model="registerForm.code"
                type="text"
                placeholder="验证码"
                class="flex-1 bg-transparent outline-none text-sm text-gray-100 placeholder-gray-500 min-w-0"
              />
            </div>
            <button
              type="button"
              class="px-4 sm:px-5 py-3 sm:py-3.5 bg-app-bg-secondary text-gray-300 rounded-xl font-medium hover:bg-app-primary hover:text-white active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-app-bg-secondary disabled:hover:text-gray-300 disabled:active:scale-100 whitespace-nowrap flex-shrink-0 text-sm"
              :disabled="codeCountdown > 0"
              @click="sendCode"
            >
              {{ codeCountdown > 0 ? `${codeCountdown}s` : '获取验证码' }}
            </button>
          </div>
          <div class="flex items-center gap-2 sm:gap-3 px-3 sm:px-4 py-3 sm:py-3.5 bg-app-bg-secondary rounded-xl focus-within:ring-2 focus-within:ring-app-primary/20 transition-all">
            <el-icon :size="18" class="text-gray-500 flex-shrink-0">
              <Lock />
            </el-icon>
            <input
              v-model="registerForm.password"
              :type="showRegisterPassword ? 'text' : 'password'"
              placeholder="设置密码"
              class="flex-1 bg-transparent outline-none text-sm text-gray-100 placeholder-gray-500"
              @input="onPasswordInput"
            />
            <button
              type="button"
              class="p-1 text-gray-500 hover:text-gray-300 transition-colors"
              @click="showRegisterPassword = !showRegisterPassword"
            >
              <el-icon :size="18">
                <View v-if="!showRegisterPassword" />
                <Hide v-else />
              </el-icon>
            </button>
          </div>
          <!-- 密码强度三段式指示器 -->
          <div v-if="registerForm.password" class="mt-2">
            <div class="flex items-center justify-between text-xs mb-1.5">
              <span class="text-gray-400">密码强度</span>
              <span :style="{ color: strengthConfig.color }">{{ strengthConfig.text }}</span>
            </div>
            <div class="flex gap-1.5">
              <div
                class="h-1.5 flex-1 rounded-full transition-all duration-300"
                :class="passwordStrength === 'weak' ? 'bg-red-500' : passwordStrength === 'medium' || passwordStrength === 'strong' ? 'bg-red-500' : 'bg-gray-700'"
              ></div>
              <div
                class="h-1.5 flex-1 rounded-full transition-all duration-300"
                :class="passwordStrength === 'medium' ? 'bg-yellow-500' : passwordStrength === 'strong' ? 'bg-yellow-500' : 'bg-gray-700'"
              ></div>
              <div
                class="h-1.5 flex-1 rounded-full transition-all duration-300"
                :class="passwordStrength === 'strong' ? 'bg-green-500' : 'bg-gray-700'"
              ></div>
            </div>
          </div>
          <!-- 确认密码输入框 -->
          <div class="flex items-center gap-2 sm:gap-3 px-3 sm:px-4 py-3 sm:py-3.5 bg-app-bg-secondary rounded-xl focus-within:ring-2 focus-within:ring-app-primary/20 transition-all">
            <el-icon :size="18" class="text-gray-500 flex-shrink-0">
              <Lock />
            </el-icon>
            <input
              v-model="registerForm.confirmPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              placeholder="确认密码"
              class="flex-1 bg-transparent outline-none text-sm text-gray-100 placeholder-gray-500"
              @input="onConfirmPasswordInput"
            />
            <button
              type="button"
              class="p-1 text-gray-500 hover:text-gray-300 transition-colors"
              @click="showConfirmPassword = !showConfirmPassword"
            >
              <el-icon :size="18">
                <View v-if="!showConfirmPassword" />
                <Hide v-else />
              </el-icon>
            </button>
          </div>
        </div>

        <div class="flex items-start gap-2 text-xs sm:text-sm">
          <input v-model="agreeTerms" type="checkbox" class="mt-0.5 w-4 h-4 rounded border-gray-600 text-app-primary focus:ring-app-primary bg-app-bg" />
          <span class="text-gray-400 leading-relaxed">
            我已阅读并同意
            <button type="button" class="text-app-primary-light hover:text-[#3b82f6] font-medium transition-colors" @click="openPolicy('terms')">用户协议</button>
            和
            <button type="button" class="text-app-primary-light hover:text-[#3b82f6] font-medium transition-colors" @click="openPolicy('privacy')">隐私政策</button>
          </span>
        </div>

        <button
          type="submit"
          class="w-full py-3 sm:py-3.5 bg-gradient-to-r from-app-primary to-app-primary-hover text-white rounded-xl font-semibold hover:shadow-lg hover:shadow-blue-500/30 hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 disabled:hover:shadow-none text-sm sm:text-base"
          :disabled="loading"
        >
          {{ loading ? '注册中...' : '注 册' }}
        </button>
      </form>

      <!-- 重置密码表单 -->
      <form v-else class="space-y-4 sm:space-y-5" @submit.prevent="handleResetPassword">
        <div class="space-y-3 sm:space-y-4">
          <div class="flex items-center gap-2 sm:gap-3 px-3 sm:px-4 py-3 sm:py-3.5 bg-app-bg-secondary rounded-xl focus-within:ring-2 focus-within:ring-app-primary/20 transition-all">
            <el-icon :size="18" class="text-gray-500 flex-shrink-0">
              <Iphone />
            </el-icon>
            <input
              v-model="resetForm.phone"
              type="tel"
              placeholder="手机号"
              class="flex-1 bg-transparent outline-none text-sm text-gray-100 placeholder-gray-500"
            />
          </div>
          <div class="flex items-center gap-2 sm:gap-3 px-3 sm:px-4 py-3 sm:py-3.5 bg-app-bg-secondary rounded-xl focus-within:ring-2 focus-within:ring-app-primary/20 transition-all">
            <el-icon :size="18" class="text-gray-500 flex-shrink-0">
              <Lock />
            </el-icon>
            <input
              v-model="resetForm.oldPassword"
              type="password"
              placeholder="旧密码"
              class="flex-1 bg-transparent outline-none text-sm text-gray-100 placeholder-gray-500"
            />
          </div>
          <div class="flex gap-2 sm:gap-3">
            <div class="flex items-center gap-2 sm:gap-3 px-3 sm:px-4 py-3 sm:py-3.5 bg-app-bg-secondary rounded-xl focus-within:ring-2 focus-within:ring-app-primary/20 transition-all flex-1 min-w-0">
              <el-icon :size="18" class="text-gray-500 flex-shrink-0">
                <Message />
              </el-icon>
              <input
                v-model="resetForm.code"
                type="text"
                placeholder="验证码"
                class="flex-1 bg-transparent outline-none text-sm text-gray-100 placeholder-gray-500 min-w-0"
              />
            </div>
            <button
              type="button"
              class="px-4 sm:px-5 py-3 sm:py-3.5 bg-app-bg-secondary text-gray-300 rounded-xl font-medium hover:bg-app-primary hover:text-white active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-app-bg-secondary disabled:hover:text-gray-300 disabled:active:scale-100 whitespace-nowrap flex-shrink-0 text-sm"
              :disabled="resetCodeCountdown > 0"
              @click="sendResetCode"
            >
              {{ resetCodeCountdown > 0 ? `${resetCodeCountdown}s` : '获取验证码' }}
            </button>
          </div>
          <div class="flex items-center gap-2 sm:gap-3 px-3 sm:px-4 py-3 sm:py-3.5 bg-app-bg-secondary rounded-xl focus-within:ring-2 focus-within:ring-app-primary/20 transition-all">
            <el-icon :size="18" class="text-gray-500 flex-shrink-0">
              <Lock />
            </el-icon>
            <input
              v-model="resetForm.newPassword"
              :type="showNewPassword ? 'text' : 'password'"
              placeholder="新密码"
              class="flex-1 bg-transparent outline-none text-sm text-gray-100 placeholder-gray-500"
              @input="onNewPasswordInput"
            />
            <button
              type="button"
              class="p-1 text-gray-500 hover:text-gray-300 transition-colors"
              @click="showNewPassword = !showNewPassword"
            >
              <el-icon :size="18">
                <View v-if="!showNewPassword" />
                <Hide v-else />
              </el-icon>
            </button>
          </div>
        </div>

        <button
          type="submit"
          class="w-full py-3 sm:py-3.5 bg-gradient-to-r from-app-primary to-app-primary-hover text-white rounded-xl font-semibold hover:shadow-lg hover:shadow-blue-500/30 hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 disabled:hover:shadow-none text-sm sm:text-base"
          :disabled="loading"
        >
          {{ loading ? '重置中...' : '重置密码' }}
        </button>
      </form>
    </div>
  </el-dialog>

  <!-- 用户协议/隐私政策弹窗 -->
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
</template>

<script setup lang="ts">
import { Close, User, Lock, Iphone, Message, View, Hide } from '@element-plus/icons-vue'
import { useSiteConfig } from '~/config/site'
import { validatePasswordChars, validatePasswordRule, getPasswordStrength } from '~/utils/password'

const siteConfig = useSiteConfig()
const visible = defineModel<boolean>({ default: false })

// 表单类型: 'login' | 'register' | 'reset'
type FormType = 'login' | 'register' | 'reset'
const formType = ref<FormType>('login')

// 暴露方法给父组件
const setFormType = (type: FormType) => {
  formType.value = type
}

defineExpose({
  setFormType
})
const loading = ref(false)
const rememberMe = ref(false)
const agreeTerms = ref(false)
const codeCountdown = ref(0)
const resetCodeCountdown = ref(0)

// 密码可见性控制
const showRegisterPassword = ref(false)
const showConfirmPassword = ref(false)
const showNewPassword = ref(false)

const loginForm = reactive({
  phone: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  phone: '',
  code: '',
  password: '',
  confirmPassword: ''
})

const resetForm = reactive({
  phone: '',
  oldPassword: '',
  newPassword: '',
  code: ''
})

const isMobile = computed(() => {
  return process.client ? window.innerWidth < 640 : false
})

// 密码强度
const passwordStrength = computed(() => {
  return getPasswordStrength(registerForm.password)
})

// 密码强度配置
const strengthConfig = computed(() => {
  const configs = {
    weak: { color: '#ef4444', text: '弱' },
    medium: { color: '#eab308', text: '中' },
    strong: { color: '#22c55e', text: '强' }
  }
  return configs[passwordStrength.value]
})

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

// 监听弹窗打开，重置表单
watch(visible, (val) => {
  if (val) {
    loginForm.phone = ''
    loginForm.password = ''
    registerForm.username = ''
    registerForm.phone = ''
    registerForm.code = ''
    registerForm.password = ''
    registerForm.confirmPassword = ''
    resetForm.phone = ''
    resetForm.oldPassword = ''
    resetForm.newPassword = ''
    resetForm.code = ''
    formType.value = 'login'
    // 重置密码可见性状态
    showRegisterPassword.value = false
    showConfirmPassword.value = false
    showNewPassword.value = false
  }
})

const config = useRuntimeConfig()
const { setUserInfo } = useUser()
const { syncLocalToCloud } = useHistory()

// 密码输入处理（过滤非法字符）
const onPasswordInput = (event: Event) => {
  const input = event.target as HTMLInputElement
  // 过滤非法字符
  const filtered = input.value.split('').filter(char => {
    return /[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{}|;:',.<>?\/`~]/.test(char)
  }).join('')
  registerForm.password = filtered
}

// 确认密码输入处理（过滤非法字符）
const onConfirmPasswordInput = (event: Event) => {
  const input = event.target as HTMLInputElement
  const filtered = input.value.split('').filter(char => {
    return /[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{}|;:',.<>?\/`~]/.test(char)
  }).join('')
  registerForm.confirmPassword = filtered
}

// 新密码输入处理（过滤非法字符）
const onNewPasswordInput = (event: Event) => {
  const input = event.target as HTMLInputElement
  const filtered = input.value.split('').filter(char => {
    return /[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{}|;:',.<>?\/`~]/.test(char)
  }).join('')
  resetForm.newPassword = filtered
}

const handleLogin = async () => {
  if (!loginForm.phone || !loginForm.password) {
    ElMessage.warning('请输入手机号和密码')
    return
  }

  loading.value = true
  try {
    const response = await $fetch(`${config.public.apiBase}/pub/user/login`, {
      method: 'POST',
      body: {
        account: loginForm.phone,
        password: loginForm.password
      }
    })

    if (response.code === 200) {
      ElMessage.success('登录成功')
      // 保存用户信息和 accessToken（从 user 对象中获取 accesstoken）
      // rememberMe: true 使用 localStorage，false 使用 sessionStorage
      const user = response.data.user
      setUserInfo(user, user?.accesstoken, rememberMe.value)
      visible.value = false

      // 同步本地播放记录到云端（不阻塞页面刷新）
      void syncLocalToCloud()

      // 刷新页面或更新状态
      window.location.reload()
    } else if (response.code === 9006) {
      // 用户被禁用
      ElMessageBox.alert(
        '您的账号已被禁用，如有疑问请联系客服。',
        '账号异常',
        {
          confirmButtonText: '我知道了',
          type: 'error',
          center: true
        }
      )
    } else {
      ElMessage.error(response.message || '登录失败')
    }
  } catch (error: any) {
    ElMessage.error(error?.data?.message || '登录失败，请检查账号密码')
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  if (!registerForm.username || !registerForm.phone || !registerForm.code || !registerForm.password || !registerForm.confirmPassword) {
    ElMessage.warning('请填写完整信息')
    return
  }

  // 校验密码字符合法性
  if (!validatePasswordChars(registerForm.password)) {
    ElMessage.warning('密码只能包含大小写字母、数字和英文标点符号')
    return
  }

  // 校验密码规则
  const ruleResult = validatePasswordRule(registerForm.password)
  if (!ruleResult.valid) {
    ElMessage.warning(ruleResult.message)
    return
  }

  // 校验两次密码一致
  if (registerForm.password !== registerForm.confirmPassword) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }

  if (!agreeTerms.value) {
    ElMessage.warning('请同意用户协议和隐私政策')
    return
  }

  loading.value = true
  try {
    const response = await $fetch(`${config.public.apiBase}/pub/user/register`, {
      method: 'POST',
      body: {
        account: registerForm.username,
        phone: registerForm.phone,
        password: registerForm.password,
        sms_code: registerForm.code,
        name: registerForm.username
      }
    })

    if (response.code === 200) {
      ElMessage.success('注册成功')
      // 保存用户信息（自动登录，从 user 对象中获取 accesstoken）
      // 注册默认记住登录状态
      const user = response.data.user
      setUserInfo(user, user?.accesstoken, true)
      visible.value = false

      // 同步本地播放记录到云端（不阻塞页面刷新）
      void syncLocalToCloud()

      // 刷新页面或更新状态
      window.location.reload()
    } else {
      ElMessage.error(response.message || '注册失败')
    }
  } catch (error: any) {
    ElMessage.error(error?.data?.message || '注册失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const sendCode = async () => {
  if (!registerForm.phone) {
    ElMessage.warning('请先输入手机号')
    return
  }

  try {
    const response = await $fetch(`${config.public.apiBase}/pub/user/sendSMSCode`, {
      method: 'POST',
      body: {
        account: registerForm.phone,
        sms_for: 'register'
      }
    })

    if (response.code === 200) {
      ElMessage.success('验证码已发送')
      codeCountdown.value = 60
      const timer = setInterval(() => {
        codeCountdown.value--
        if (codeCountdown.value <= 0) {
          clearInterval(timer)
        }
      }, 1000)
    } else {
      ElMessage.error(response.message || '发送失败')
    }
  } catch (error: any) {
    ElMessage.error(error?.data?.message || '发送验证码失败')
  }
}

const sendResetCode = async () => {
  if (!resetForm.phone) {
    ElMessage.warning('请先输入手机号')
    return
  }

  try {
    const response = await $fetch(`${config.public.apiBase}/pub/user/sendSMSCode`, {
      method: 'POST',
      body: {
        account: resetForm.phone,
        sms_for: 'register'
      }
    })

    if (response.code === 200) {
      ElMessage.success('验证码已发送')
      resetCodeCountdown.value = 60
      const timer = setInterval(() => {
        resetCodeCountdown.value--
        if (resetCodeCountdown.value <= 0) {
          clearInterval(timer)
        }
      }, 1000)
    } else {
      ElMessage.error(response.message || '发送失败')
    }
  } catch (error: any) {
    ElMessage.error(error?.data?.message || '发送验证码失败')
  }
}

const handleResetPassword = async () => {
  if (!resetForm.phone || !resetForm.oldPassword || !resetForm.newPassword || !resetForm.code) {
    ElMessage.warning('请填写完整信息')
    return
  }

  // 校验新密码字符合法性
  if (!validatePasswordChars(resetForm.newPassword)) {
    ElMessage.warning('新密码只能包含大小写字母、数字和英文标点符号')
    return
  }

  // 校验新密码规则
  const ruleResult = validatePasswordRule(resetForm.newPassword)
  if (!ruleResult.valid) {
    ElMessage.warning(ruleResult.message)
    return
  }

  loading.value = true
  try {
    const response = await $fetch(`${config.public.apiBase}/pub/user/resetPassword`, {
      method: 'POST',
      body: {
        phone: resetForm.phone,
        old_password: resetForm.oldPassword,
        new_password: resetForm.newPassword,
        sms_code: resetForm.code
      }
    })

    if (response.code === 200) {
      ElMessage.success('密码重置成功，请使用新密码登录')
      // 切换到登录表单
      formType.value = 'login'
      // 自动填充手机号
      loginForm.phone = resetForm.phone
    } else {
      ElMessage.error(response.message || '密码重置失败')
    }
  } catch (error: any) {
    ElMessage.error(error?.data?.message || '密码重置失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-dialog :deep(.el-dialog) {
  border-radius: 24px;
  overflow: hidden;
  background: rgba(20, 20, 20, 0.85) !important;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.auth-dialog :deep(.el-dialog__header) {
  display: none;
}

.auth-dialog :deep(.el-dialog__body) {
  padding: 0;
  background: transparent !important;
}

:deep(.auth-dialog .el-overlay-dialog) {
  backdrop-filter: blur(8px);
}

:deep(.mobile-dialog) {
  border-radius: 20px;
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

/* 覆盖浏览器自动填充的白色背景 */
input:-webkit-autofill,
input:-webkit-autofill:hover,
input:-webkit-autofill:focus,
input:-webkit-autofill:active {
  -webkit-box-shadow: 0 0 0 30px #1a1a1a inset !important;
  -webkit-text-fill-color: #f5f5f5 !important;
}
</style>
