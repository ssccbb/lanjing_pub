# 技术说明文档

本文档详细说明了项目中使用的前端和后端技术栈，包括框架选型、核心依赖、技术特性和最佳实践。

---

## 一、前端技术栈 (Website)

### 1.1 核心框架

| 技术 | 版本 | 用途说明 |
|------|------|---------|
| **Nuxt** | 4.4.8 | Vue.js 元框架，支持 SSR/CSR/SSG |
| **Vue** | 3.5.38 | 渐进式 JavaScript 框架 |
| **Vue Router** | 5.1.0 | 官方路由管理器 |
| **TypeScript** | 6.0.3 | 类型安全的 JavaScript 超集 |

### 1.2 UI 框架与样式

| 技术 | 版本 | 用途说明 |
|------|------|---------|
| **Element Plus** | 2.14.2 | Vue 3 组件库，提供丰富的 UI 组件 |
| **@element-plus/icons-vue** | 2.3.2 | Element Plus 图标库 |
| **@element-plus/nuxt** | 1.1.5 | Element Plus 的 Nuxt 模块 |
| **Tailwind CSS** | 6.14.0 | 原子化 CSS 框架 |
| **@nuxtjs/tailwindcss** | 6.14.0 | Tailwind CSS 的 Nuxt 模块 |
| **Sass** | 1.101.0 | CSS 预处理器 |

### 1.3 媒体播放

| 技术 | 版本 | 用途说明 |
|------|------|---------|
| **ArtPlayer** | 5.4.0 | HTML5 视频播放器，高度可定制 |
| **HLS.js** | 1.6.16 | HTTP Live Streaming 播放支持 |
| **@nuxt/image** | 2.0.0 | 图片优化与懒加载 |

### 1.4 工具库

| 技术 | 版本 | 用途说明 |
|------|------|---------|
| **VueUse** | 14.3.0 | Vue Composition API 工具集 |
| **@vueuse/nuxt** | 14.3.0 | VueUse 的 Nuxt 模块 |
| **@vueuse/gesture** | 2.0.0 | 手势识别库 |
| **dayjs** | 1.11.21 | 轻量级日期处理库 |
| **qrcode** | 1.5.4 | 二维码生成库 |

### 1.5 PWA 支持

| 技术 | 版本 | 用途说明 |
|------|------|---------|
| **@vite-pwa/nuxt** | 1.1.1 | PWA 集成模块，支持 Service Worker |

### 1.6 构建工具

| 技术 | 版本 | 用途说明 |
|------|------|---------|
| **Vite** | 内置 | 新一代前端构建工具 |
| **Terser** | 5.48.0 | JavaScript 压缩器 |
| **cross-env** | 7.0.3 | 跨平台环境变量设置 |

---

## 二、后端技术栈 (Server)

### 2.1 核心框架

| 技术 | 用途说明 |
|------|---------|
| **FastAPI** | 现代、高性能的 Python Web 框架，支持异步 |
| **Uvicorn** | ASGI 服务器，用于运行 FastAPI 应用 |
| **Pydantic** | 数据验证和设置管理 |
| **pydantic-settings** | 环境变量和配置管理 |

### 2.2 数据库

| 技术 | 用途说明 |
|------|---------|
| **MySQL** | 关系型数据库，存储核心业务数据 |
| **SQLAlchemy** | Python ORM 框架，支持异步操作 |
| **aiomysql** | 异步 MySQL 驱动 |

### 2.3 缓存

| 技术 | 用途说明 |
|------|---------|
| **Redis** | 内存数据结构存储，用于缓存和会话管理 |
| **redis-py** | Redis Python 客户端（支持异步） |

### 2.4 其他服务

| 技术 | 用途说明 |
|------|---------|
| **短信服务** | 用户验证码发送（需配置短信服务商） |

---

## 三、前端架构详解

### 3.1 渲染模式

项目采用 **SSR（服务端渲染）** 为主，CSR（客户端渲染）为辅的混合渲染策略：

| 场景 | 渲染方式 | 说明 |
|------|---------|------|
| 首页数据 | CSR（server: false） | 确保数据实时性，禁用 SSR 缓存 |
| 影片详情 | SSR | 利于 SEO，首屏渲染 |
| 搜索结果 | CSR | 实时搜索体验 |
| 用户相关 | CSR | 动态交互数据 |

### 3.2 状态管理

采用 Vue 3 Composition API 进行状态管理：

- **SSR 安全的全局状态**：使用 `useState` 管理，如用户信息
- **本地持久化**：使用 `useLocalStorage` 管理，如收藏列表
- **响应式计算属性**：使用 `computed` 派生状态

**"记住我"功能实现**：
- 勾选：存储到 `localStorage`（长期有效）
- 不勾选：存储到 `sessionStorage`（关闭标签页失效）

### 3.3 组件设计原则

```
components/
├── common/          # 通用组件（可复用）
│   └── VideoCard.vue
├── home/            # 页面特定组件（按功能分组）
│   ├── HomeBanner.vue
│   ├── HomeCarousel.vue
│   └── HomeRank.vue
├── player/          # 功能模块组件
│   ├── VideoPlayer.vue
│   ├── DanmakuLayer.vue
│   ├── composables/  # 模块专用 Composable
│   └── adapters/     # 播放器适配器
└── AuthDialog.vue   # 全局组件
```

### 3.4 API 请求架构

```
composables/
├── useSignedFetch.ts    # 签名请求基础封装
├── useMovies.ts         # 影片相关 API
├── useHome.ts           # 首页数据 API
├── useDanmaku.ts        # 弹幕系统 API
├── useUser.ts           # 用户状态管理
└── ...
```

**请求签名机制**：
- 所有 API 请求携带签名头（signature）
- 登录接口额外携带 Authorization 头（accesstoken）

### 3.5 视频播放器

基于 **ArtPlayer** 构建的自定义播放器：

**核心特性**：
- HLS 流媒体播放支持
- 自定义控制栏 UI
- 弹幕系统集成
- 播放速率调节（0.5x - 2x）
- 画面比例切换（默认/4:3/16:9/满屏）
- 小窗模式（滚动时自动触发）
- 键盘快捷键（空格暂停，F 全屏）
- 加载超时处理（15 秒）
- 移动端全屏兼容（iOS Safari 特殊处理）

### 3.6 响应式设计

| 断点 | 设备 | 布局特点 |
|------|------|---------|
| < 640px | 手机 | 底部 Tab 导航，侧滑菜单 |
| 640px - 1023px | 平板 | 简化侧边栏 |
| >= 1024px | 桌面 | 完整侧边栏导航 |

---

## 四、后端架构详解

### 4.1 项目结构

```
server/app/
├── main.py              # 应用入口，路由注册，中间件
├── config.py            # 配置管理（环境变量）
├── database.py          # 数据库连接池
├── cache.py             # Redis 缓存封装
├── models/              # 数据模型
│   ├── entities.py      # SQLAlchemy 实体定义
│   ├── schemas/         # Pydantic 请求/响应模型
│   └── ...
├── routers/             # API 路由
│   ├── page.py          # 首页聚合接口
│   ├── content.py       # 影片内容接口
│   ├── search.py        # 搜索接口
│   ├── user.py          # 用户接口
│   ├── danmaku.py       # 弹幕接口
│   └── ...
├── services/            # 业务逻辑层
│   ├── movie_service.py # 影片服务
│   ├── user_service.py  # 用户服务
│   ├── danmaku_service.py
│   └── ...
└── utils/               # 工具函数
    ├── crypto.py        # 加解密工具
    ├── auth.py          # 认证工具
    ├── response.py      # 统一响应格式
    ├── antibot.py       # 反爬虫检测
    └── logger.py        # 日志工具
```

### 4.2 API 路由设计

| 路由前缀 | 用途 | 鉴权 |
|---------|------|------|
| `/pub/*` | 公开接口 | 仅签名验证 |
| `/web/*` | 业务接口 | 签名 + 登录验证 |

**主要接口**：

| 接口 | 方法 | 说明 |
|------|------|------|
| `/pub/user/login` | POST | 用户登录 |
| `/pub/user/register` | POST | 用户注册 |
| `/pub/danmaku/{video_id}` | GET | 获取弹幕列表 |
| `/web/home` | GET | 首页数据聚合 |
| `/web/home/list/{category_id}` | GET | 分类列表 |
| `/web/home/detail/{movie_id}` | GET | 影片详情 |
| `/web/search` | GET | 搜索影片 |
| `/web/danmaku/{video_id}` | POST | 发送弹幕（需登录） |

### 4.3 数据模型

**核心实体**：

| 表名 | 说明 |
|------|------|
| `lj_movies` | 影片主表 |
| `lj_episodes` | 剧集表 |
| `lj_ranks` | 排行榜 |
| `lj_watchlist` | 片单 |
| `user` | 用户表 |
| `home_page_data` | 首页配置表 |
| `danmaku` | 弹幕表 |

**实体关系**：
- Movie → Episode：一对多（按 `source_from` 分组为播放源）
- Rank → Movie：通过 JSON 字段存储排名映射
- Watchlist → Movie：通过 JSON 数组存储影片 ID

### 4.4 缓存策略

| 数据类型 | 缓存时间 | 说明 |
|---------|---------|------|
| 首页数据 | 5 分钟 | 后台任务每 3 分钟刷新 |
| 影片列表（第一页） | 10 分钟 | 分页数据仅缓存首页 |
| 影片详情（含剧集） | 1 小时 | 热点数据长期缓存 |
| 搜索结果 | 3 分钟 | 搜索词较短缓存 |
| 排行榜/片单 | 5 分钟 | 中等缓存时间 |

**缓存键格式**：`{module}:{action}:{params}`

### 4.5 性能优化

**数据库层面**：
- 连接池配置：基础 20 连接，最大溢出 30
- 异步查询：使用 `selectinload` 优化关联查询
- 轻量级字段查询：列表页仅查询必要字段

**缓存层面**：
- Redis 缓存热点数据
- 后台任务定期刷新首页缓存
- 避免缓存爆炸：仅缓存第一页数据

**SQL 优化**：
- LIKE 查询特殊字符转义（防注入）
- 批量查询解决 N+1 问题
- 索引优化：`category`, `update_time`, `recommend_num`

### 4.6 安全机制

**请求签名验证**：
- 前端发送加密签名
- 后端解密验证签名有效性

**反爬虫机制**：
- User-Agent 黑名单检测
- 搜索引擎白名单（百度、Google 等）
- 可疑爬虫拦截（返回 403）

**密码安全**：
- 哈希存储（算法已隐藏）
- 重置密码需短信验证

---

## 五、前后端交互

### 5.1 统一响应格式

```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

**错误码定义**：

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权/签名无效 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |
| 9001 | 短信验证码错误 |
| 9003 | 密码错误 |
| 9005 | 账号已存在 |
| 9006 | 用户被禁用 |

### 5.2 API 地址处理

| 环境 | 客户端 | 服务端 (SSR) |
|------|--------|-------------|
| 开发 | `DEBUG_API_BASE` 或空 | `http://127.0.0.1:8000` |
| 生产 | 空字符串（同域） | `http://127.0.0.1:8000` |

### 5.3 分页数据格式

```json
{
  "list": [...],
  "total": 100,
  "page": 1,
  "page_size": 30
}
```

---

## 六、部署与运维

### 6.1 环境变量

**共享配置** (`../.env.shared`)：
- `NUXT_PUBLIC_AUTHOR_KEY` - API 签名密钥
- `NUXT_PUBLIC_APP_NAME` - 应用名称
- `NUXT_PUBLIC_APP_SLOGAN` - 应用标语
- `NUXT_PUBLIC_ICP_NUMBER` - 备案号
- `NUXT_PUBLIC_POLICY_AGREEMENT` - 用户协议URL
- `NUXT_PUBLIC_POLICY_PRIVACY` - 隐私政策URL
- `ALLOW_ORIGINS_DEV` - 开发环境允许域名
- `ALLOW_ORIGINS_PROD` - 生产环境允许域名

**私有配置** (`website/.env`, `server/.env`)：
- 数据库连接信息
- Redis 连接信息
- 调试开关等

### 6.2 构建命令

**前端**：
- `pnpm dev` - 开发模式
- `pnpm build` - 生产构建
- `pnpm build:lowmem` - 低内存构建

**后端**：
- `uvicorn app.main:app --reload` - 开发模式
- `uvicorn app.main:app --host 0.0.0.0 --port 8000` - 生产模式

### 6.3 日志系统

**后端日志**：
- 应用日志：`logs/app.log`
- 访问日志：单独文件，格式化记录请求详情
- 性能监控：请求耗时自动记录
- 敏感参数过滤（password, token, signature 等）

**前端日志**：
- 生产环境移除 `console.log`
- 错误上报（可接入监控系统）

---

## 七、技术选型理由

### 7.1 为什么选择 Nuxt 4？

| 特性 | 优势 |
|------|------|
| SSR 支持 | 利于 SEO，首屏渲染快 |
| 文件系统路由 | 自动路由生成，减少配置 |
| 自动导入 | 组件、Composable 自动注册 |
| 模块生态 | Element Plus、Tailwind、PWA 开箱即用 |
| Vue 3 | Composition API，更好的类型支持 |

### 7.2 为什么选择 FastAPI？

| 特性 | 优势 |
|------|------|
| 异步支持 | 高并发性能，原生 async/await |
| 类型提示 | Pydantic 自动校验，减少运行时错误 |
| 自动文档 | OpenAPI 文档自动生成 |
| 性能优秀 | 接近 Go/Node.js 的性能水平 |
| 开发效率 | 声明式路由，依赖注入 |

### 7.3 为什么选择 Redis？

| 特性 | 优势 |
|------|------|
| 高性能 | 内存存储，毫秒级响应 |
| 丰富类型 | String、Hash、List、Set 等 |
| 过期策略 | 支持 TTL，适合缓存场景 |
| 持久化 | 可选 RDB/AOF，数据不丢失 |

---

## 八、最佳实践

### 8.1 前端开发规范

1. **使用 Composable 封装 API 调用**
2. **SSR 安全**：使用 `useState` 而非全局变量
3. **响应式设计优先**：移动端适配
4. **按需加载**：使用 `useLazyAsyncData` 延迟加载
5. **类型安全**：所有 Props 和 API 响应使用 TypeScript 类型

### 8.2 后端开发规范

1. **分层架构**：Router → Service → Model
2. **异步优先**：所有 I/O 操作使用 async/await
3. **缓存策略**：合理设置缓存时间，避免缓存穿透
4. **SQL 安全**：转义 LIKE 查询，防止注入
5. **日志规范**：敏感信息过滤，结构化日志

### 8.3 接口设计规范

1. **统一响应格式**：`{ code, message, data }`
2. **版本控制**：通过路由前缀区分
3. **分页参数**：`page`, `page_size` 统一命名
4. **错误码规范**：语义化错误码，便于前端处理

---

## 九、技术演进方向

### 9.1 性能优化

- [ ] 图片 CDN 加速
- [ ] 接口响应压缩（已实现 GZip）
- [ ] 首页骨架屏优化
- [ ] 弹幕 WebSocket 推送

### 9.2 功能扩展

- [ ] 用户收藏云端同步
- [ ] 个性化推荐算法
- [ ] 多语言支持
- [ ] 暗色/亮色主题切换

### 9.3 运维增强

- [ ] 监控告警接入
- [ ] 自动化测试覆盖
- [ ] CI/CD 流水线
- [ ] 容器化部署

---

**文档版本**: 1.1  
**更新日期**: 2026-07-11  
**维护者**: 开发团队
