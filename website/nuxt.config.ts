import { defineNuxtConfig } from 'nuxt/config'
import { readFileSync, existsSync } from 'fs'
import { resolve } from 'path'

// 手动加载共享配置（项目根目录的 .env.shared）
function loadEnvFile(filePath: string): Record<string, string> {
  const result: Record<string, string> = {}
  if (!existsSync(filePath)) return result

  const content = readFileSync(filePath, 'utf-8')
  content.split('\n').forEach(line => {
    line = line.trim()
    if (!line || line.startsWith('#')) return
    const [key, ...valueParts] = line.split('=')
    if (key) result[key.trim()] = valueParts.join('=').trim()
  })
  return result
}

// 加载共享配置和私有配置
const sharedEnv = loadEnvFile(resolve(__dirname, '../.env.shared'))
const localEnv = loadEnvFile(resolve(__dirname, './.env'))
const env = { ...sharedEnv, ...localEnv }

// 服务端 SSR 专用的 API 地址
// 客户端使用空字符串（同域请求），服务端需要完整地址
const SSR_API_BASE = 'http://127.0.0.1:8000'

// 确定 API Base URL
// 客户端：空字符串表示同域（通过 nginx 代理，避免跨域）
// 服务端 SSR：需要直接访问后端地址
// 开发环境：使用 DEBUG_API_BASE
const getApiBase = (): string => {
  // 开发环境使用 DEBUG_API_BASE
  if (process.env.NODE_ENV === 'development' && env.NUXT_PUBLIC_DEBUG_API_BASE) {
    return env.NUXT_PUBLIC_DEBUG_API_BASE
  }
  // 生产环境客户端：空字符串（同域）
  // 注意：服务端 SSR 需要在 composable 中单独处理
  return ''
}

// 从 ALLOW_ORIGINS 中提取域名列表（去掉协议前缀）
const extractHosts = (origins: string): string[] => {
  return origins.split(',').map(origin => {
    const trimmed = origin.trim()
    // 去掉 http:// 或 https:// 前缀
    return trimmed.replace(/^https?:\/\//, '')
  }).filter(h => h)
}

// Vite 开发服务器允许的 Hosts（从 CORS 配置中提取）
const devAllowedHosts = extractHosts(env.ALLOW_ORIGINS_DEV || '')

export default defineNuxtConfig({
  // 基础配置
  devtools: { enabled: false },

  // 实验性功能 - 优化内存
  experimental: {
    // 禁用 webpack 构建时的并行处理（减少内存峰值）
    parallelChunkBuilding: false
  },

  // 模块
  modules: [
    '@nuxtjs/tailwindcss',
    '@nuxt/image',
    '@vueuse/nuxt',
    '@element-plus/nuxt',
    '@vite-pwa/nuxt'
  ],

  // PWA 配置
  pwa: {
    manifest: {
      name: env.NUXT_PUBLIC_APP_NAME || '影视模版',
      short_name: env.NUXT_PUBLIC_APP_NAME || '影视模版',
      description: `${env.NUXT_PUBLIC_APP_NAME || '影视模版'} - ${env.NUXT_PUBLIC_APP_SLOGAN || '影视模版Slogan'}，${env.NUXT_PUBLIC_APP_SUB_SLOGAN || '影视模版SloganSub'}，畅享海量高清影视资源`,
      theme_color: '#141414',
      background_color: '#141414',
      display: 'standalone',
      orientation: 'portrait',
      scope: '/',
      start_url: '/',
      icons: []
    },
    meta: {
      mobileApp: true,
      mobileAppIOS: true,
      appleStatusBarStyle: 'black-translucent',
      apple: true,
      appleCapable: true,
      appleTitle: env.NUXT_PUBLIC_APP_NAME || '影视模版'
    },
    workbox: {
      globPatterns: ['**/*.{js,css,html,png,jpg,ico,svg,woff2}'],
      runtimeCaching: [
        {
          urlPattern: /^https:\/\/.*\.(?:png|jpg|jpeg|svg|gif|webp)$/i,
          handler: 'CacheFirst',
          options: {
            cacheName: 'images-cache',
            expiration: {
              maxEntries: 100,
              maxAgeSeconds: 60 * 60 * 24 * 30 // 30 days
            }
          }
        },
        {
          urlPattern: /^https:\/\/.*\.(?:js|css)$/i,
          handler: 'StaleWhileRevalidate',
          options: {
            cacheName: 'static-resources'
          }
        }
      ]
    },
    client: {
      installPrompt: false
    },
    devOptions: {
      enabled: true,
      // 开发环境下禁用 glob 警告
      suppressWarnings: true
    }
  },

  // CSS
  css: [
    '@/assets/styles/main.scss'
  ],

  // 组件自动导入
  components: [
    {
      path: '~/components',
      pathPrefix: false
    }
  ],


  // 运行时配置 - API 地址由环境变量或自动选择控制
  runtimeConfig: {
    // 服务端专用的 API 地址（SSR 时使用）
    apiBase: 'http://127.0.0.1:8000',
    public: {
      // 客户端使用的 API 地址（空字符串表示同域）
      apiBase: getApiBase(),
      // 请求签名密钥 - 用于 API 签名验证（前后端共用）
      authorKey: env.NUXT_PUBLIC_AUTHOR_KEY || '',
      // 联系邮箱
      contactEmail: env.NUXT_PUBLIC_CONTACT_EMAIL || '',
      // 备案号
      icpNumber: env.NUXT_PUBLIC_ICP_NUMBER || '',
      // 应用品牌
      appName: env.NUXT_PUBLIC_APP_NAME || '',
      appSlogan: env.NUXT_PUBLIC_APP_SLOGAN || '',
      appSubSlogan: env.NUXT_PUBLIC_APP_SUB_SLOGAN || '',
      // 协议页面
      policyAgreement: env.NUXT_PUBLIC_POLICY_AGREEMENT || '',
      policyPrivacy: env.NUXT_PUBLIC_POLICY_PRIVACY || ''
    }
  },

  // 路由配置
  router: {
    options: {
      scrollBehaviorType: 'smooth'
    }
  },

  // Element Plus 配置
  elementPlus: {
    icon: 'ElIcon'
  },

  // 构建配置
  build: {
    transpile: ['element-plus']
  },

  // Nitro 配置 - 优化服务端构建内存
  nitro: {
    // 减少并发构建数
    minify: true,
    // 启用流式压缩（减少内存占用）
    compressPublicAssets: {
      brotli: false,  // 禁用 Brotli（内存消耗大），只使用 gzip
      gzip: true
    },
    // 限制同时处理的文件数
    rollupConfig: {
      output: {
        // 减少 chunk 大小
        manualChunks: undefined
      }
    }
  },

  // Source Map 控制 - 生产环境禁用
  sourcemap: {
    server: false,
    client: false
  },

  // 插件配置（自动识别 .client.ts 和 .server.ts 后缀）
  plugins: ['~/plugins/performance.client.ts']
  ,

  // TypeScript
  typescript: {
    typeCheck: false
  },

  vite: {
    server: {
      allowedHosts: devAllowedHosts
    },
    optimizeDeps: {
      exclude: ['lodash-unified']
    },
    build: {
      minify: 'terser',
      // 限制并发数，减少内存峰值
      reportCompressedSize: false,  // 禁用 gzip 报告（节省内存）
      chunkSizeWarningLimit: 1000,  // 提高 chunk 大小警告阈值
      rollupOptions: {
        output: {
          // 控制代码分割，避免生成过多小 chunk
          manualChunks: {
            // 将 Element Plus 单独打包
            'element-plus': ['element-plus'],
            // 将视频播放器相关单独打包
            'player': ['artplayer', 'hls.js']
          }
        }
      },
      terserOptions: {
        compress: {
          drop_console: true,
          drop_debugger: true,
          pure_funcs: ['console.log', 'console.info', 'console.debug']
        },
        mangle: {
          safari10: true
        },
        format: {
          comments: false
        }
      }
    }
  },

  // 兼容性
  compatibilityDate: '2026-06-24'
})
