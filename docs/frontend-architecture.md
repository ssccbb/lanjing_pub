# Website 前端架构说明文档

## 1. 项目概述

本项目是一个基于 **Nuxt 4** 的影视网站前端应用，采用 Vue 3 + TypeScript 开发，支持 SSR（服务端渲染）和 PWA（渐进式Web应用）。主要用于展示电影、电视剧、综艺、动漫、短剧等影视内容的在线观看平台。

### 技术栈

| 类别 | 技术 |
|------|------|
| 框架 | Nuxt 4.4.8 (Vue 3.5.38) |
| UI组件库 | Element Plus 2.14.2 |
| 样式 | Tailwind CSS 6.14.0 + SCSS |
| 视频播放器 | ArtPlayer 5.4.0 + HLS.js 1.6.16 |
| 状态管理 | Vue Composition API (useState, useLocalStorage) |
| 工具库 | VueUse 14.3.0, dayjs 1.11.21 |
| 构建工具 | Vite (内置), Terser |
| PWA | @vite-pwa/nuxt |

---

## 2. 项目结构

```
website/
├── app/                      # 应用主目录（Nuxt 4 目录结构）
│   ├── app.vue               # 应用根组件
│   ├── assets/
│   │   └── styles/
│   │       └── main.scss     # 全局样式入口
│   ├── components/           # Vue 组件
│   │   ├── common/           # 通用组件
│   │   ├── home/             # 首页相关组件
│   │   ├── list/             # 列页相关组件
│   │   ├── player/           # 播放器组件
│   │   │   ├── adapters/     # 播放器适配器
│   │   │   ├── composables/  # 播放器组合式函数
│   │   │   └── types.ts      # 播放器类型定义
│   │   └── ...               # 其他组件
│   ├── composables/          # 组合式函数（API封装、业务逻辑）
│   ├── config/               # 配置文件
│   ├── constants/            # 常量定义
│   ├── layouts/              # 布局组件
│   │   ├── default.vue       # 默认布局（首页等）
│   │   └── player.vue        # 播放器布局
│   ├── pages/                # 页面组件（路由自动生成）
│   ├── plugins/              # Nuxt 插件
│   ├── server/
│   │   └── api/              # 服务端API路由
│   └── utils/                # 工具函数
├── public/                   # 静态资源
├── server/                   # 后端服务（独立目录）
├── types/                    # TypeScript 类型定义
├── nuxt.config.ts            # Nuxt 配置
├── tailwind.config.ts        # Tailwind 配置
├── tsconfig.json             # TypeScript 配置
├── package.json              # 项目依赖
├── .env                      # 环境变量（私有）
└── pnpm-lock.yaml            # 依赖锁定文件
```

---

## 3. 核心架构模块

### 3.1 路由系统

采用 Nuxt **文件系统路由**，页面文件自动映射为路由：

| 页面文件 | 路由路径 | 功能 |
|---------|---------|------|
| `pages/index.vue` | `/` | 首页 |
| `pages/reels/index.vue` | `/reels` | 电影列表 |
| `pages/tv/index.vue` | `/tv` | 电视剧列表 |
| `pages/variety/index.vue` | `/variety` | 综艺列表 |
| `pages/cels/index.vue` | `/cels` | 动漫列表 |
| `pages/shorts/index.vue` | `/shorts` | 短剧列表 |
| `pages/detail/[id].vue` | `/detail/:id` | 影片详情（301重定向到播放页） |
| `pages/play/[id].vue` | `/play/:id` | 影片播放（旧版，301重定向） |
| `pages/stream/[slug].vue` | `/stream/:slug` | 影片播放（新版语义化URL） |
| `pages/search/index.vue` | `/search` | 搜索页 |
| `pages/tiers/index.vue` | `/tiers` | 排行榜 |
| `pages/watchlists/index.vue` | `/watchlists` | 片单广场 |
| `pages/today/index.vue` | `/today` | 今日更新 |
| `pages/ranks/index.vue` | `/ranks` | 排行榜 |
| `pages/feedback/index.vue` | `/feedback` | 用户反馈 |
| `pages/acquire/index.vue` | `/acquire` | APP下载 |
| `pages/echo/index.vue` | `/echo` | 求片留言 |

**路由辅助函数**（推荐使用）：
- `routes.home()` - 返回首页路径
- `routes.stream(slug)` - 返回播放页路径
- `routes.tiers()` - 返回排行榜路径

### 3.2 布局系统

#### Default Layout (`layouts/default.vue`)
- 固定顶部导航栏（滚动时渐进式背景变化）
- 左侧固定侧边栏导航（PC端）
- 主内容区域可滚动
- 移动端底部Tab导航
- 移动端侧滑菜单

#### Player Layout (`layouts/player.vue`)
- 简洁播放器布局
- 顶部返回按钮 + 搜索栏
- 无侧边栏干扰
- 适合沉浸式观看体验

### 3.3 组件层次结构

```
app.vue (根组件)
├── NuxtLayout (布局包装器)
│   ├── default.vue / player.vue
│   │   ├── AppHeader / AppSidebar (导航组件)
│   │   ├── AppFooter (页脚，可选)
│   │   ├── SearchInput (搜索输入)
│   │   ├── HistoryDropdown (历史记录下拉)
│   │   ├── AuthDialog (登录/注册对话框)
│   │   ├── MobileMenu (移动端菜单)
│   │   └── NuxtPage (页面内容)
│   │       ├── 页面组件
│   │       │   ├── HomeBanner (Banner轮播)
│   │       │   ├── HomeCarousel (内容轮播)
│   │       │   ├── HomeGrid (网格展示)
│   │       │   ├── HomeRank (排行榜)
│   │       │   ├── VideoCard (影片卡片)
│   │       │   ├── FilterBar (筛选栏)
│   │       │   ├── MovieGrid (影片网格)
│   │       │   ├── VideoPlayer (播放器)
│   │       │   ├── DanmakuLayer (弹幕层)
│   │       │   └── PlayerControls (播放器控制)
│   │       │   └── ...
```

---

## 4. 数据层架构

### 4.1 API 请求层

#### 签名机制
所有API请求都携带签名头，用于后端验证。签名值使用 authorKey 加密生成。

#### 认证机制
需要登录的接口额外携带 `Authorization` 头，从 localStorage/sessionStorage 获取 accesstoken。

#### SSR/客户端 API 地址处理
- SSR 环境：使用服务端 API 地址（如 http://127.0.0.1:8000）
- 客户端环境：使用空字符串（同域请求）

### 4.2 Composables（业务逻辑封装）

| Composable | 功能 | API路径 |
|------------|------|---------|
| `useMovies` | 影片列表、详情、搜索 | `/web/home/list/:id`, `/web/home/detail/:id`, `/web/search` |
| `useHome` | 首页数据、Banner、排行榜、片单 | `/web/home`, `/web/home/rank/:id` |
| `useDanmaku` | 弹幕加载、发送、点赞 | `/pub/danmaku/:id`, `/web/danmaku/:id` |
| `useUser` | 用户状态、登录信息、收藏、历史 | 本地存储 + `/pub/user/login` |
| `useFilters` | 筛选条件管理 | - |
| `useHistory` | 播放历史（本地 + 云端同步） | `/web/user/history` |
| `useSeo` | SEO元数据管理 | - |
| `useImageProxy` | 图片代理（防盗链处理） | `/api/proxy-image` |
| `useActivity` | 用户活动记录 | - |
| `useFeedback` | 用户反馈提交 | - |
| `useShare` | 分享功能 | - |
| `useSlug` | URL slug生成 | - |
| `usePerformance` | 性能监控 | - |

### 4.3 用户状态管理

采用 Vue 3 Composition API 的 `useState` 和 `useLocalStorage`：

- **全局状态（SSR安全）**：使用 `useState` 管理，如用户信息、登录弹窗状态
- **本地持久化**：使用 `useLocalStorage` 管理，如收藏列表、播放历史

**"记住我"功能**：
- 记住我：`localStorage` 存储（长期）
- 不记住我：`sessionStorage` 存储（关闭标签页后失效）

### 4.4 数据类型定义

核心类型定义在 `types/index.ts`：

- **Movie**：影片基础信息（id, title, covers, score, tags, directors, actors, episode_sources 等）
- **Episode**：剧集信息（id, title, m3u8_link, source_limit 等）
- **EpisodeSource**：播放源归类（source_name, episodes）
- **PaginatedData**：分页数据结构（list, total, page, pageSize）

---

## 5. 视频播放器架构

### 5.1 播放器组件结构

```
player/
├── VideoPlayer.vue          # 播放器主组件
├── VideoPlayerWithDanmaku.vue  # 播放器 + 弹幕集成
├── PlayerControls.vue       # 自定义控制栏
├── DanmakuLayer.vue         # 弹幕渲染层
├── adapters/
│   └── artplayer.ts         # ArtPlayer 适配器
├── composables/
│   └── usePlayer.ts         # 播放器逻辑封装
└── types.ts                 # 类型定义
```

### 5.2 播放器特性

- **ArtPlayer 核心**：支持 HLS 流媒体播放
- **自定义控制栏**：完全自定义 UI，支持弹幕集成
- **播放限制处理**：根据 `source_limit` 控制观看权限
- **全屏控制**：兼容 iOS Safari 的特殊处理
- **播放速率**：支持多档倍速播放
- **画面比例**：默认、4:3、16:9、满屏
- **小窗模式**：滚动离开播放页时自动进入小窗
- **键盘快捷键**：空格暂停/播放，F全屏
- **加载超时处理**：15秒超时提示，支持重试和换源

### 5.3 弹幕系统

- **弹幕类型**：滚动弹幕
- **发送弹幕**：需登录，实时显示
- **点赞弹幕**：需登录
- **弹幕颜色**：根据用户角色（管理员/付费用户/普通用户）显示不同颜色
- **弹幕开关**：用户可控制显示/隐藏

---

## 6. 样式系统

### 6.1 Tailwind CSS 配置

项目使用自定义主题色扩展：

- **app-bg**：主背景色（#141414）
- **app-bg-secondary**：次级背景色（#1a1a1a）
- **app-bg-tertiary**：三级背景色（#333333）
- **app-primary**：主题色（紫色）
- **app-primary-hover**：主题色悬停态
- **app-primary-light**：主题色浅色
- **app-scrollbar**：滚动条颜色

### 6.2 全局样式

- 暗色主题设计
- 滚动条自定义样式
- 图片懒加载骨架屏动画
- 文字多行省略
- Element Plus 暗色主题适配

---

## 7. 配置系统

### 7.1 运行时配置

从 `.env` 和 `.env.shared` 读取配置：

**SSR 专用配置**：
- `apiBase`：服务端 API 地址

**公共配置**：
- `apiBase`：客户端 API 地址（空字符串表示同域）
- `authorKey`：API 签名密钥
- `appName`：应用名称
- `appSlogan`：应用标语
- `icpNumber`：备案号
- `policyAgreement`：用户协议URL
- `policyPrivacy`：隐私政策URL

### 7.2 环境变量

| 变量名 | 说明 |
|--------|------|
| `NUXT_PUBLIC_APP_NAME` | 应用名称 |
| `NUXT_PUBLIC_APP_SLOGAN` | 应用标语 |
| `NUXT_PUBLIC_AUTHOR_KEY` | API签名密钥 |
| `NUXT_PUBLIC_ICP_NUMBER` | 备案号 |
| `NUXT_PUBLIC_POLICY_AGREEMENT` | 用户协议URL |
| `NUXT_PUBLIC_POLICY_PRIVACY` | 隐私政策URL |
| `NUXT_PUBLIC_DEBUG_API_BASE` | 开发环境API地址 |
| `ALLOW_ORIGINS_DEV` | 开发环境允许域名 |

---

## 8. PWA 配置

PWA 模块配置包含：

- **manifest**：应用名称、主题色、显示模式
- **workbox**：静态资源缓存策略
- **runtimeCaching**：图片和静态资源的运行时缓存规则

---

## 9. 构建优化

### 9.1 内存优化

提供两种构建命令：
- 标准构建：分配 3GB 内存
- 低内存构建：分配 2GB 内存

### 9.2 代码分割

手动分割大型依赖：
- `element-plus`：UI 组件库单独打包
- `player`：播放器相关依赖单独打包

### 9.3 生产优化

- Terser 压缩，删除 console.log
- Source Map 禁用
- Brotli 禁用（内存消耗大），仅用 gzip

---

## 10. SEO 优化

- SSR 渲染确保首屏 SEO
- 动态 meta 标签设置
- 301 重定向保持 SEO 权重（旧路由 -> 新路由）
- URL slug 语义化（`/stream/{id}-{title}`）

---

## 11. 安全机制

### 11.1 API 签名

前后端使用相同的 `authorKey` 生成签名，防止接口滥用。签名值为 32 位加密字符串。

### 11.2 密码验证

- 字符合法性验证（大小写字母、数字、英文标点）
- 强度验证（弱/中/强）
- 规则验证（长度、组合要求）

---

## 12. 响应式设计

### 12.1 断点

- Mobile: `< 640px`
- Tablet: `640px - 1023px`
- Desktop: `>= 1024px`

### 12.2 移动端特性

- 底部 Tab 导航
- 侧滑菜单
- 触摸手势支持
- iOS Safari 全屏特殊处理
- 安全区域适配（`env(safe-area-inset-bottom)`）

---

## 13. 关键业务流程

### 13.1 用户登录流程

```
用户点击登录按钮
  → AuthDialog 显示
  → 输入账号密码
  → 调用 /pub/user/login
  → 保存 userInfo + accesstoken（localStorage/sessionStorage）
  → 同步本地播放历史到云端
  → 刷新页面
```

### 13.2 视频播放流程

```
进入 /stream/:slug 页面
  → 解析 slug 获取 movieId
  → 获取影片详情
  → 获取剧集列表
  → 检查播放权限（source_limit）
    → 0: 直接播放
    → 1: 需登录，未登录显示登录弹窗
    → 2: 需付费，显示付费提示
  → 初始化播放器
  → 加载弹幕数据
  → 用户可发送弹幕（需登录）
```

### 13.3 首页数据加载

```
页面挂载
  → 禁用 SSR（server: false）
  → 客户端并行加载：
    - 首页区块数据（Banner、轮播等）
    - 今日更新
    - 热播榜/热搜榜
  → 渲染页面
```

---

## 14. 组件命名约定

| 类型 | 前缀 | 示例 |
|------|------|------|
| 页面组件 | 无 | `index.vue`, `[id].vue` |
| 布局组件 | 无 | `default.vue`, `player.vue` |
| 业务组件 | 功能前缀 | `HomeBanner`, `VideoCard` |
| 通用组件 | 无前缀或 `common/` | `VideoCard` |
| 组合式函数 | use前缀 | `useMovies`, `useUser` |

---

## 15. 最佳实践建议

1. **使用 Composables**：所有 API 调用应通过 Composables 封装
2. **签名请求**：所有请求必须携带签名头
3. **SSR 注意事项**：使用 `import.meta.server` / `import.meta.client` 区分环境
4. **状态持久化**：使用 `useState` 保证 SSR 安全，`useLocalStorage` 用于持久化
5. **路由跳转**：优先使用 `routes.xxx()` 辅助函数
6. **类型安全**：使用 `types/index.ts` 定义共享类型

---

## 16. 依赖关系图

```
┌─────────────────────────────────────────────────────────────┐
│                        nuxt.config.ts                        │
│  (模块配置: tailwindcss, element-plus, pwa, image, vueuse)   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                         app.vue                              │
│                    (根组件 + SEO配置)                         │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  layouts/       │ │  components/    │ │  composables/   │
│  default.vue    │ │  (业务组件)      │ │  (业务逻辑)      │
│  player.vue     │ │                 │ │                 │
└─────────────────┘ └─────────────────┘ └─────────────────┘
              │               │               │
              └───────────────┼───────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                         pages/                               │
│                    (路由页面组件)                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    server (后端API)                          │
│              http://127.0.0.1:8000 (SSR)                     │
│              同域请求 (Client)                                │
└─────────────────────────────────────────────────────────────┘
```

---

**文档版本**: 1.1
**更新日期**: 2026-07-11
