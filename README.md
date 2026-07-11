# 🎬 蓝鲸影视 - 开源影视网站全栈解决方案

![Vue.js](https://img.shields.io/badge/Vue.js-3.5-4FC08D?logo=vue.js)
![Nuxt](https://img.shields.io/badge/Nuxt-4-00DC82?logo=nuxt.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100-009688?logo=fastapi)
![TypeScript](https://img.shields.io/badge/TypeScript-6.0-3178C6?logo=typescript)
![License](https://img.shields.io/badge/License-LGPL%20v3-blue)

**一个功能完整的现代化影视网站模版，前后端分离架构，开箱即用。**

如果你觉得这个项目有帮助，请给一个 ⭐ **Star** 支持一下！这是开源项目最好的支持方式。

---

## 🌐 演示站

**在线体验**：[https://lanjingtv.cn:81/](https://lanjingtv.cn:81/)

演示站展示了项目的完整功能，包括：
- 🎬 HLS 流媒体播放
- 💬 实时弹幕互动
- 🔍 影片搜索与筛选
- 📱 响应式布局适配
- 👤 用户登录注册

> 演示站数据仅供展示，部分功能可能受限。

### 📹 演示视频

https://github.com/user-attachments/assets/demo.mov

---

## ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🎥 **HLS 流媒体播放** | 自适应码率，流畅播放体验 |
| 💬 **实时弹幕系统** | 轨道碰撞检测，Web Animations API 高性能渲染 |
| 🔍 **智能搜索** | 关键词搜索，热门推荐 |
| 📱 **响应式设计** | PC/平板/手机全适配，iOS Safari 全屏兼容 |
| 🚀 **SSR 服务端渲染** | SEO 优化，首屏快速加载 |
| 🔐 **API 签名验证** | 防接口滥用，请求加密 |
| 📊 **Redis 缓存** | 热点数据缓存，后台自动刷新 |
| 🎨 **自定义播放器** | 倍速播放、画面比例、小窗模式、快捷键 |

---

## 🛠 技术栈

### 前端 (Website)

| 技术 | 版本 | 用途 |
|------|------|------|
| **Nuxt** | 4.4 | Vue.js 元框架，SSR 支持 |
| **Vue 3** | 3.5 | Composition API |
| **TypeScript** | 6.0 | 类型安全 |
| **Element Plus** | 2.14 | UI 组件库 |
| **Tailwind CSS** | 6.14 | 原子化 CSS |
| **ArtPlayer** | 5.4 | 视频播放器 |
| **HLS.js** | 1.6 | HLS 流媒体 |
| **VueUse** | 14.3 | Composition 工具集 |

### 后端 (Server)

| 技术 | 版本 | 用途 |
|------|------|------|
| **FastAPI** | 0.100+ | 异步 Web 框架 |
| **SQLAlchemy** | 2.0 | 异步 ORM |
| **MySQL** | 8.0+ | 关系型数据库 |
| **Redis** | 7.0+ | 缓存/会话管理 |
| **Pydantic** | 2.0 | 数据验证 |

---

## 📐 架构设计

```
┌──────────────────────────────────────────────────────────────────────┐
│                           用户浏览器                                   │
└──────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    前端 (Nuxt 4 + Vue 3)                               │
│  ┌────────────────┐   ┌────────────────┐   ┌────────────────┐        │
│  │    Pages       │   │  Components    │   │  Composables   │        │
│  │  (SSR 路由)    │   │   (UI 层)      │   │  (业务逻辑)    │        │
│  └────────────────┘   └────────────────┘   └────────────────┘        │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────┐        │
│  │         播放器系统 (ArtPlayer + HLS.js)                     │        │
│  │         弹幕引擎 (轨道管理 + Web Animations API)            │        │
│  └───────────────────────────────────────────────────────────┘        │
└──────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    后端 API (FastAPI)                                  │
│  ┌────────────────┐   ┌────────────────┐   ┌────────────────┐        │
│  │    Routers     │   │   Services     │   │    Models      │        │
│  │  (路由层)      │   │  (业务逻辑)    │   │  (数据模型)    │        │
│  └────────────────┘   └────────────────┘   └────────────────┘        │
└──────────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┴───────────────┐
                ▼                               ▼
┌────────────────────────────┐   ┌────────────────────────────┐
│        MySQL 数据库         │   │        Redis 缓存          │
│  (影片/用户/弹幕/历史)      │   │  (热点数据/会话/验证码)    │
└────────────────────────────┘   └────────────────────────────┘
```

详细架构文档：
- [前端架构说明](./docs/frontend-architecture.md)
- [后端架构说明](./docs/server-architecture.md)
- [播放器与弹幕系统](./docs/player-danmaku-architecture.md)
- [数据库表结构](./docs/database-schema.md)
- [技术栈详情](./docs/technology-specification.md)

---

## 🚀 快速开始

### 前端启动

```bash
cd website
pnpm install
pnpm dev
```

访问 `http://localhost:3333`

### 后端启动

```bash
cd server
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API 服务运行在 `http://localhost:8000`

### 数据库准备

1. 创建 MySQL 数据库
2. 参考 [database-schema.md](./docs/database-schema.md) 创建表结构
3. 配置 `server/.env` 中的数据库连接

---

## ⚙️ 必须配置的项

### 环境变量

| 文件 | 配置项 | 说明 |
|------|--------|------|
| `.env.shared` | `NUXT_PUBLIC_AUTHOR_KEY` | API 签名密钥（16位随机字符串） |
| `.env.shared` | `NUXT_PUBLIC_CONTACT_EMAIL` | 联系邮箱 |
| `.env.shared` | `NUXT_PUBLIC_ICP_NUMBER` | 网站备案号 |
| `website/.env` | `NUXT_PUBLIC_POLICY_*` | 用户协议/隐私政策 URL |
| `server/.env` | `MYSQL_*` | MySQL 数据库连接信息 |

### 需自行实现的模块

出于安全考虑，以下核心模块已移除实现，保留接口框架：

| 模块 | 文件位置 | 说明 |
|------|---------|------|
| **加密算法** | `website/app/utils/crypto.ts`<br>`server/app/utils/crypto.py` | API 签名加解密 |
| **密码哈希** | `server/app/services/user_service.py` | 用户密码存储 |
| **短信服务** | `server/app/services/sms_service.py` | 验证码发送 |
| **推荐算法** | `server/app/services/recommend_service.py` | 影片推荐逻辑 |

代码中以 `your_algorithm_here` 标记，需自行填充实现。

---

## 📁 项目结构

```
lanjing_pub/
├── website/                    # 前端 (Nuxt 4)
│   ├── app/
│   │   ├── components/         # Vue 组件
│   │   ├── composables/        # 组合式函数
│   │   ├── pages/              # 页面路由
│   │   ├── layouts/            # 布局组件
│   │   └── utils/              # 工具函数
│   └── public/                 # 静态资源
│
├── server/                     # 后端 (FastAPI)
│   └── app/
│       ├── routers/            # API 路由
│       ├── services/           # 业务逻辑
│       ├── models/             # 数据模型
│       └── utils/              # 工具函数
│
├── docs/                       # 架构文档
│   ├── frontend-architecture.md
│   ├── server-architecture.md
│   ├── player-danmaku-architecture.md
│   ├── database-schema.md
│   └── technology-specification.md
│
├── .env.shared                 # 共享配置
└── LICENSE                     # LGPL v3
```

---

## 📜 许可证

本项目采用 **LGPL v3** 许可证开源。

- ✅ 可自由使用、修改、分发
- ✅ 可将本项目作为库链接到你的专有软件
- ⚠️ 修改了本项目并分发时，修改部分需以 LGPL 或兼容许可证开源

详见 [LICENSE](./LICENSE)。

---

## 🙏 致谢与第三方引用

本项目基于众多优秀的开源项目构建，感谢开源社区的贡献：

### 前端框架与工具

| 项目 | 许可证 | 说明 |
|------|--------|------|
| [Vue.js](https://vuejs.org/) | MIT | 渐进式 JavaScript 框架，本项目核心框架 |
| [Nuxt](https://nuxt.com/) | MIT | Vue.js 元框架，提供 SSR、文件路由等能力 |
| [TypeScript](https://www.typescriptlang.org/) | Apache-2.0 | JavaScript 的类型超集，提供类型安全 |
| [Vite](https://vitejs.dev/) | MIT | 下一代前端构建工具，极速开发体验 |

### UI 组件与样式

| 项目 | 许可证 | 说明 |
|------|--------|------|
| [Element Plus](https://element-plus.org/) | MIT | Vue 3 组件库，提供丰富的 UI 组件 |
| [Tailwind CSS](https://tailwindcss.com/) | MIT | 原子化 CSS 框架，快速构建响应式界面 |
| [Sass](https://sass-lang.com/) | MIT | CSS 预处理器，增强样式编写能力 |

### 媒体播放

| 项目 | 许可证 | 说明 |
|------|--------|------|
| [ArtPlayer](https://artplayer.org/) | MIT | 高度可定制的 HTML5 视频播放器 |
| [HLS.js](https://hlsjs.org/) | Apache-2.0 | JavaScript HLS 流媒体播放器 |

### 后端框架与数据库

| 项目 | 许可证 | 说明 |
|------|--------|------|
| [FastAPI](https://fastapi.tiangolo.com/) | MIT | 现代、高性能的 Python Web 框架 |
| [SQLAlchemy](https://www.sqlalchemy.org/) | MIT | Python SQL 工具包和 ORM |
| [Pydantic](https://pydantic-docs.helpmanual.io/) | MIT | 数据验证和设置管理 |
| [Uvicorn](https://www.uvicorn.org/) | MIT | ASGI 服务器 |

### 工具库

| 项目 | 许可证 | 说明 |
|------|--------|------|
| [VueUse](https://vueuse.org/) | MIT | Vue Composition API 工具集 |
| [day.js](https://day.js.org/) | MIT | 轻量级日期处理库 |
| [QRCode.js](https://github.com/davidshimjs/qrcodejs) | MIT | 二维码生成库 |

### 数据存储

| 项目 | 许可证 | 说明 |
|------|--------|------|
| [MySQL](https://www.mysql.com/) | GPL | 关系型数据库 |
| [Redis](https://redis.io/) | BSD-3-Clause | 内存数据结构存储 |

---

本项目尊重所有第三方项目的许可证，如有遗漏或错误，请提交 Issue 指正。

---

## ⭐ 支持

如果这个项目对你有帮助：

1. 给一个 **Star** ⭐ - 这是最好的支持方式
2. 分享给更多人知道
3. 提交 Issue 或 PR 参与贡献

---

## 📞 联系

如有问题或建议，欢迎提交 [Issue](../../issues)。

---

## ⚠️ 免责声明

### 使用限制

**本项目仅供学习、研究和技术交流使用。**

### 禁止用途

严禁将本项目用于以下用途：

| 禁止行为 | 说明 |
|---------|------|
| ❌ 盗版传播 | 未经授权传播受版权保护的影视内容 |
| ❌ 非法经营 | 未取得相关资质从事视频网站运营 |
| ❌ 侵权行为 | 侵犯他人知识产权、传播权等合法权益 |
| ❌ 违法内容 | 传播违法违规、低俗有害内容 |
| ❌ 商业欺诈 | 利用本项目进行诈骗等违法活动 |

### 法律责任

1. **使用者责任**：使用本项目搭建的网站，其内容、运营行为均与本项目作者无关
2. **内容合规**：使用者应确保网站内容符合当地法律法规，自行承担相关法律责任
3. **版权尊重**：使用者应尊重知识产权，不得利用本项目从事侵权活动
4. **资质要求**：从事视频网站运营需取得相应资质（如 ICP 许可证、信息网络传播视听节目许可证等）

### 知识产权声明

- 本项目源代码采用 LGPL v3 许可证开源
- 演示站中的影视内容、图片等素材版权归原作者所有
- 本项目不提供任何影视资源，仅提供技术框架

### 免责条款

1. 本项目作者不对使用本代码造成的任何直接或间接损失负责
2. 本项目作者不对基于本项目开发的网站内容负责
3. 本项目不提供任何明示或暗示的担保，包括但不限于适销性和特定用途适用性
4. 使用本项目即表示您已阅读、理解并同意本免责声明

### 违规举报

如发现有人利用本项目从事违法违规活动，请向当地网信、公安等部门举报。

---

**Made with ❤️ by 开源社区**

---

<!-- 
关键词（用于 GitHub 搜索优化）:
- video streaming platform
- movie website template
- nuxt fastapi
- vue3 typescript
- hls video player
- danmaku bullet comment
- 弹幕系统
- 影视网站源码
- 视频流媒体
- SSR 前端
- async python
- redis caching
-->