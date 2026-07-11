# Server Backend API 架构说明

## 项目概述

本项目是一个基于 FastAPI 的异步 Web API 服务，为影视内容平台提供后端支持。采用前后端分离架构，提供影片信息查询、用户认证、内容推荐等核心功能。

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| Web 框架 | FastAPI | 异步高性能 Python Web 框架 |
| ORM | SQLAlchemy 2.0 | 异步 ORM，支持类型注解 |
| 数据库 | MySQL | 通过 aiomysql 实现异步连接 |
| 缓存 | Redis | 用于热点数据缓存和会话管理 |
| 配置管理 | Pydantic Settings | 环境变量和配置文件加载 |
| 数据验证 | Pydantic | 请求/响应数据模型验证 |

## 目录结构

```
server/
├── app/
│   ├── main.py              # 应用入口，路由注册，中间件配置
│   ├── config.py            # 配置管理，环境变量加载
│   ├── database.py          # 数据库连接，Session 管理
│   ├── cache.py             # Redis 缓存操作封装
│   ├── models/
│   │   ├── entities.py      # SQLAlchemy 数据模型定义
│   │   ├── schemas/         # Pydantic 请求/响应模型
│   │   ├── search.py        # 搜索记录模型
│   │   └── user_activity.py # 用户活动模型
│   ├── routers/
│   │   ├── page.py          # 首页数据接口
│   │   ├── content.py       # 影片内容接口
│   │   ├── search.py        # 搜索接口
│   │   ├── user.py          # 用户认证接口
│   │   ├── danmaku.py       # 弹幕接口
│   │   ├── feedback.py      # 反馈留言接口
│   │   ├── user_activity.py # 用户活动记录接口
│   │   └── config.py        # 配置管理接口
│   ├── services/
│   │   ├── movie_service.py      # 影片业务逻辑
│   │   ├── user_service.py       # 用户认证逻辑
│   │   ├── sms_service.py        # 短信验证服务
│   │   ├── recommend_service.py  # 推荐算法服务
│   │   ├── danmaku_service.py    # 弹幕业务逻辑
│   │   └── home_service.py       # 首页数据服务
│   └── utils/
│       ├── response.py      # 统一响应格式
│       ├── auth.py          # 用户认证工具
│       ├── signature.py     # API 签名验证
│       ├── crypto.py        # 加密工具
│       ├── logger.py        # 日志配置
│       └── antibot.py       # 反爬虫检测
├── requirements.txt          # 依赖清单
└── .env.example              # 环境变量示例
```

## 核心模块说明

### 1. 应用入口 (main.py)

负责应用的初始化和生命周期管理：

**生命周期管理**：
- 启动时：初始化 Redis 连接、预热缓存、启动后台刷新任务
- 关闭时：清理 Redis 连接、停止后台任务

**中间件配置**：
- CORS 跨域配置
- GZip 响应压缩
- 性能监控（记录请求耗时）
- 反爬虫检测（高频访问限制）
- API 签名验证

**路由注册**：
- 公开路由（无需签名）：`/pub/*`
- 需签名路由：`/web/*`

### 2. 配置管理 (config.py)

使用 Pydantic Settings 实现分层配置加载：

```
.env.shared (公共配置) → .env (私有配置覆盖)
```

**主要配置项**：
- MySQL 连接参数（host, port, user, password, database）
- Redis 连接参数（host, port, db）
- CORS 允许的域名列表
- API 签名密钥

### 3. 数据库连接 (database.py)

异步数据库连接池管理：

| 配置项 | 值 | 说明 |
|--------|-----|------|
| `pool_size` | 20 | 常驻连接数 |
| `max_overflow` | 30 | 峰值时可扩展连接数 |
| `pool_recycle` | 3600 | 连接回收时间（秒） |

通过 `get_db` 依赖注入为每个请求提供独立的 AsyncSession，请求结束后自动关闭。

### 4. 缓存层 (cache.py)

Redis 缓存操作封装：

| 函数 | 用途 |
|------|------|
| `init_redis()` | 初始化 Redis 连接池 |
| `close_redis()` | 关闭连接池 |
| `cache_get(key)` | 获取缓存值 |
| `cache_set(key, value, ttl)` | 设置缓存（支持过期时间） |
| `cache_delete(key)` | 删除单个缓存 |
| `cache_delete_pattern(pattern)` | 批量删除匹配模式的缓存 |
| `cache_key(*parts)` | 生成标准化缓存键名 |

### 5. 数据模型 (models/entities.py)

**核心实体定义**：

#### Movie（影片表）
- 主键：id
- 核心字段：title, score, covers, tags, directors, actors
- 关系：与 Episode 一对多（通过 selectin 懒加载）
- 方法：`to_dict()` 提供 JSON 序列化，包含剧集分组

#### Episode（剧集表）
- 外键：movie_id → Movie.id
- 播放源字段：source_from（线路名称），source_limit（播放限制）

#### User（用户表）
- 认证字段：account, phone, password, accesstoken
- 状态字段：status（0=正常, 1=禁用），role（0=普通, 1=管理员, 2=付费）
- 时间字段：create_time, login_time（时间戳）

#### 其他模型
- Actor：演员信息
- Rank：排行榜
- Watchlist：用户片单
- HomePageData：首页配置数据
- AutoIndex：首页索引排序
- UserFeedback：用户反馈
- UserWatchHistory：观看历史
- UserSearch：搜索记录

## 路由层设计

### 公开路由（无需签名）`/pub/*`

| 路径 | 功能 | 说明 |
|------|------|------|
| `/pub/user/login` | 用户登录 | 手机号 + 密码认证 |
| `/pub/user/register` | 用户注册 | 手机号 + 验证码注册 |
| `/pub/user/sendSMSCode` | 发送验证码 | 登录/注册/绑定场景 |
| `/pub/user/verifySMSCode` | 验证验证码 | 验证码校验接口 |
| `/pub/user/resetPassword` | 重置密码 | 需旧密码 + 验证码 |
| `/pub/danmaku/{video_id}` | 获取弹幕列表 | 公开接口 |
| `/pub/danmaku/{video_id}/timeline` | 获取弹幕时间轴 | 热度分布 |

### 需签名路由 `/web/*`

| 路径 | 功能 |
|------|------|
| `/web/home` | 首页数据（Banner、分类推荐） |
| `/web/home/list/{category_id}` | 分类影片列表 |
| `/web/home/detail/{movie_id}` | 影片详情 |
| `/web/home/rank/{rank_id}` | 单个排行榜 |
| `/web/home/ranks/all` | 所有排行榜 |
| `/web/home/watchlists/all` | 片单列表 |
| `/web/home/today` | 今日更新 |
| `/web/movies/{movie_id}` | 影片信息 |
| `/web/movies/{movie_id}/episodes` | 影片剧集 |
| `/web/movies/{movie_id}/related` | 相关推荐 |
| `/web/movies/{movie_id}/count` | 更新计数（观看/推荐） |
| `/web/movies/actor/{actor_name}` | 演员详情 |
| `/web/movies/series/{series_title}` | 系列影片 |
| `/web/search` | 搜索影片 |
| `/web/search/suggest` | 搜索建议 |
| `/web/search/hot` | 热门搜索词 |
| `/web/search/hot-records` | 热门搜索记录 |
| `/web/search/record` | 记录搜索历史 |
| `/web/danmaku/{video_id}` | 发送弹幕 |
| `/web/danmaku/{danmaku_id}/like` | 点赞弹幕 |
| `/web/feedback/create` | 提交反馈 |
| `/web/feedback/list` | 反馈列表（管理后台） |
| `/web/feedback/stats` | 反馈统计 |
| `/web/history/visit` | 记录页面访问 |
| `/web/history/visit/list` | 访问记录列表 |
| `/web/history/watch-history` | 观看历史 |
| `/web/history/watch-history/{movie_id}` | 删除单条历史 |
| `/web/history/watch-history/all` | 清空历史 |
| `/web/config/info` | 配置信息 |
| `/web/config/cors` | CORS 配置 |
| `/web/config/reload` | 重载配置 |
| `/web/user/profile` | 用户信息 |

## 服务层设计

服务层封装业务逻辑，与路由层解耦：

### MovieService
- 影片查询（按ID、关键词、分类）
- 剧集信息处理
- 搜索结果排序和分页
- 首页数据获取

### UserService
- 用户注册、登录验证
- 密码加密校验
- 用户状态检查
- Token 管理

### SMSService
- 验证码发送
- 验证码校验（Redis 存储，有过期时间）

### DanmakuService
- 弹幕列表查询
- 弹幕发送（含权限检查）
- 弹幕点赞

### RecommendService
- 推荐算法
- 返回推荐影片列表

## 中间件与安全

### 1. API 签名验证

请求必须携带签名 header：
- `signature`：签名值

**验证逻辑**：
- 签名值解密
- 与 author-key 比对

### 2. 性能监控中间件

- 记录每个请求的处理耗时
- 响应头添加 `X-Process-Time`
- 超过阈值时记录警告日志
- 敏感参数过滤（password, token 等）

### 3. 反爬虫检测

- 检测爬虫 User-Agent
- 拦截已知的爬虫工具
- 返回 403 状态码

### 4. CORS 配置

从配置文件读取允许的域名列表，支持：
- 指定域名白名单
- 配置允许的方法和头
- 支持凭证携带

## 缓存策略

### 缓存预热
应用启动时预加载热点数据：
- 首页 Banner
- 最新上线
- 各分类推荐

### 缓存更新
- 后台任务每 3 分钟刷新首页缓存
- 缓存有效期 5 分钟
- 使用 `cache_delete_pattern` 批量清理

### 缓存键命名规范

| 格式 | 示例 |
|------|------|
| `{module}:{action}:{params}` | `movie:detail:123` |
| | `page:home` |
| | `search:hot` |

## 统一响应格式

所有接口返回统一 JSON 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | int | 状态码（200=成功，其他为错误） |
| `message` | string | 消息 |
| `data` | object | 实际数据 |

**常用状态码**：

| 码值 | 含义 |
|------|------|
| 200 | 成功 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |
| 9001 | 短信验证码错误 |
| 9002 | 密码未设置 |
| 9003 | 密码错误 |
| 9004 | 手机号已绑定 |
| 9005 | 账号已存在 |
| 9006 | 用户被禁用 |

## 后台任务

启动时创建后台任务用于：
- 定期刷新首页缓存（每 3 分钟）

任务通过 `asyncio.create_task` 在 lifespan 中管理。

## 部署建议

1. **环境变量**：使用 `.env` 文件配置敏感信息，不提交到代码仓库
2. **连接池**：根据并发量调整 `pool_size` 和 `max_overflow`
3. **Redis**：建议独立部署，配置持久化
4. **日志**：生产环境建议配置日志文件和日志级别
5. **监控**：可对接 Prometheus 等监控系统采集性能指标

## 扩展指南

### 新增接口
1. 在 `routers/` 下创建路由文件
2. 定义 Pydantic Request/Response 模型
3. 实现对应 Service 方法
4. 在 `main.py` 注册路由

### 新增数据模型
1. 在 `models/entities.py` 定义 SQLAlchemy 模型
2. 实现 `to_dict()` 方法
3. 如有外键关系，配置 `relationship`

### 新增中间件
1. 创建中间件函数
2. 通过 `@app.middleware("http")` 注册
3. 注意中间件执行顺序

---

**文档版本**: 1.1
**更新日期**: 2026-07-11
