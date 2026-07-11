# Server 数据库表定义文档

## 概述

本文档描述 Server 后端 API 服务所使用的数据库表结构。数据库使用 MySQL，通过 SQLAlchemy ORM 进行异步操作。

---

## 影片相关表

### lj_movies（影片主表）

存储影片的核心信息。

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| id | INT | AUTO | 主键，影片ID |
| category | INT | 0 | 分类ID（1=电影, 2=电视剧, 3=综艺, 4=动漫, 6=短剧） |
| title | VARCHAR(2550) | "" | 影片标题 |
| other_titles | TEXT | "" | 其他标题（JSON数组） |
| score | FLOAT | 0.0 | 评分 |
| covers | TEXT | "" | 封面图片列表（JSON数组） |
| cover_tag | VARCHAR(255) | "" | 封面标签 |
| contents | TEXT | "" | 影片简介/详情 |
| tags | TEXT | "" | 标签列表（JSON数组） |
| season | INT | 0 | 季数 |
| directors | TEXT | "" | 导演列表（JSON数组） |
| actors | TEXT | "" | 演员列表（JSON数组） |
| series_title | VARCHAR(255) | "" | 系列名称 |
| oneshot_desc | VARCHAR(255) | "" | 一句话简介 |
| douban_id | VARCHAR(255) | "" | 豆瓣ID |
| imdb_id | VARCHAR(255) | "" | IMDB ID |
| publish_year | VARCHAR(255) | "" | 上映年份 |
| upload_time | VARCHAR(255) | "" | 上传时间 |
| update_time | FLOAT | 0.0 | 更新时间戳 |
| search_keys | TEXT | "" | 搜索关键词 |
| extra | TEXT | "" | 扩展信息（JSON对象） |
| recommend_num | INT | 0 | 推荐数 |

---

### lj_episodes（剧集表）

存储影片的剧集信息。

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| id | INT | AUTO | 主键，剧集ID |
| movie_id | INT | 0 | 外键，关联 lj_movies.id |
| title | VARCHAR(2550) | "" | 剧集标题 |
| m3u8_link | VARCHAR(255) | "" | M3U8播放链接 |
| link_type | INT | 0 | 链接类型 |
| duration | INT | 0 | 时长（秒） |
| source_from | VARCHAR(255) | "" | 播放源/线路名称 |
| source_link | VARCHAR(255) | "" | 播放源链接 |
| source_limit | INT | 0 | 播放限制（0=无限制, 1=需登录, 2=需付费） |

---

### actors（演员表）

存储演员信息。

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| id | INT | AUTO | 主键 |
| name | VARCHAR(255) | "" | 姓名 |
| eng_name | VARCHAR(255) | "" | 英文名 |
| sex | VARCHAR(255) | "" | 性别 |
| birth | VARCHAR(255) | "" | 出生日期 |
| address | VARCHAR(255) | "" | 出生地 |
| link_imdb | VARCHAR(255) | "" | IMDB链接 |
| profassion | VARCHAR(255) | "" | 职业 |
| link | VARCHAR(255) | "" | 相关链接 |
| avatar | VARCHAR(255) | "" | 头像 |
| contents | TEXT | "" | 简介 |
| movies | TEXT | "" | 参演影片列表 |

---

### lj_ranks（排行榜表）

存储排行榜信息。

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| id | INT | AUTO | 主键 |
| name | VARCHAR(255) | "" | 排行榜名称 |
| description | TEXT | "" | 排行榜描述 |
| cover | VARCHAR(555) | "" | 封面图片 |
| movies | TEXT | "" | 影片ID列表（JSON） |
| rank_type | INT | 0 | 排行榜类型 |
| create_time | VARCHAR(555) | "" | 创建时间 |
| update_time | VARCHAR(555) | "" | 更新时间 |
| marks | VARCHAR(255) | "" | 标记 |

---

### lj_watchlist（片单表）

存储用户片单信息。

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| id | INT | AUTO | 主键 |
| name | VARCHAR(255) | "" | 片单名称 |
| description | TEXT | "" | 片单描述 |
| cover | TEXT | "" | 封面图片 |
| movies | TEXT | "" | 影片ID列表（JSON） |
| create_time | VARCHAR(555) | "" | 创建时间 |
| update_time | VARCHAR(555) | "" | 更新时间 |
| marks | VARCHAR(255) | "" | 标记 |

---

## 首页配置表

### home_page_data（首页数据配置表）

存储首页各板块的影片ID配置。

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| id | INT | AUTO | 主键 |
| type | INT | 0 | 数据类型（1=Banner, 2=最新上线, 3=热门电影, 4=热播电视剧, 5=热门综艺, 6=动漫推荐） |
| movie_ids | TEXT | "" | 影片ID列表（JSON） |
| update_time | BIGINT | 0 | 更新时间戳 |

---

### auto_index（首页索引配置表）

存储首页索引排序配置。

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| id | INT | AUTO | 主键 |
| item_key | VARCHAR(100) | "" | 配置项键名 |
| item_type | VARCHAR(20) | "" | 配置项类型（banner, category等） |
| data_json | TEXT | "" | 配置数据（JSON） |
| sort_order | INT | 0 | 排序顺序，越小越靠前 |

---

### home_page_config（首页推荐人工干预配置表）

存储首页推荐的人工干预配置。

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| id | INT | AUTO | 主键 |
| data_type | INT | 0 | 对应 home_page_data.type（1-6） |
| movie_id | INT | 0 | 影片ID |
| action | VARCHAR(20) | "" | 操作类型：pin=置顶, block=屏蔽, boost=加权, reduce=降权 |
| priority | INT | 0 | 优先级，越小越靠前 |
| weight_adjust | FLOAT | 1.0 | 权重调整值（0.5-2.0） |
| expire_time | BIGINT | 0 | 过期时间戳（0=永不过期） |
| create_time | BIGINT | 0 | 创建时间戳 |

---

## 用户相关表

### user（用户表）

存储用户账号信息。

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| uid | INT | AUTO | 主键，用户ID |
| account | VARCHAR(255) | "" | 账号（用户名） |
| accesstoken | VARCHAR(255) | "" | 访问令牌 |
| name | VARCHAR(255) | "" | 昵称 |
| password | VARCHAR(255) | "" | 密码（加密存储） |
| phone | VARCHAR(255) | "" | 手机号 |
| avatar | VARCHAR(255) | "" | 头像URL |
| status | INT | 0 | 状态（0=正常, 1=禁用） |
| role | INT | 0 | 角色（0=普通用户, 1=管理员, 2=付费用户） |
| create_time | BIGINT | 0 | 注册时间戳 |
| login_time | BIGINT | 0 | 最后登录时间戳 |

---

### user_watch_history（用户观看历史表）

存储用户的影片观看历史。

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| id | INT | AUTO | 主键 |
| accesstoken | VARCHAR(255) | "" | 用户访问令牌（索引） |
| movie_id | VARCHAR(50) | "" | 影片ID（索引） |
| episode_id | VARCHAR(50) | "" | 剧集ID |
| timestamp | BIGINT | 0 | 观看时间戳 |
| covers | JSON | [] | 封面列表 |
| title | VARCHAR(500) | "" | 影片标题 |
| tags | JSON | [] | 标签列表 |
| create_time | DATETIME | NOW | 创建时间 |

**唯一约束**：`(accesstoken, movie_id)` - 同一用户同一影片只有一条记录

---

### user_page_visit（用户页面访问记录表）

存储用户的页面访问记录。

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| id | INT | AUTO | 主键 |
| accesstoken | VARCHAR(255) | "" | 用户访问令牌（索引） |
| path | VARCHAR(500) | "" | 访问路径 |
| timestamp | BIGINT | 0 | 访问时间戳 |
| create_time | DATETIME | NOW | 创建时间 |

---

### user_feedback（用户反馈表）

存储用户提交的反馈和留言。

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| id | INT | AUTO | 主键 |
| accesstoken | VARCHAR(255) | "" | 用户访问令牌（索引） |
| content | TEXT | "" | 反馈内容 |
| email | VARCHAR(255) | "" | 邮箱 |
| contact | VARCHAR(255) | "" | 联系方式 |
| feedback_type | INT | 1 | 类型（1=求片留言, 2=意见反馈, 3=问题报告） |
| status | INT | 0 | 状态（0=待处理, 1=已处理, 2=已忽略） |
| client_ip | VARCHAR(100) | "" | 客户端IP |
| remark | TEXT | "" | 备注回复 |
| create_time | DATETIME | NOW | 创建时间 |
| update_time | DATETIME | NOW | 更新时间 |

---

### user_searchs（用户搜索记录表）

存储搜索历史统计。

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| id | INT | AUTO | 主键 |
| series_title | VARCHAR(500) | "" | 影片名称 |
| search_count | INT | 1 | 搜索次数 |
| update_time | BIGINT | 0 | 更新时间戳 |

---

## 弹幕相关表

### danmaku（弹幕主表）

存储视频弹幕数据。

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| id | VARCHAR(32) | - | 主键，弹幕ID |
| video_id | BIGINT | - | 视频ID（索引） |
| sender_user_id | VARCHAR(32) | NULL | 发送者用户ID（索引） |
| sender_name | VARCHAR(64) | - | 发送者昵称 |
| content_text | TEXT | - | 弹幕内容 |
| style_color | VARCHAR(8) | "#FFFFFF" | 弹幕颜色 |
| position_time | DECIMAL(10,3) | - | 出现时间（秒） |
| position_mode | SMALLINT | 1 | 弹幕类型（1=滚动, 2=顶部, 3=底部） |
| meta_timestamp | BIGINT | - | 发送时间戳 |
| meta_client_type | SMALLINT | 1 | 客户端类型 |
| status | SMALLINT | 1 | 状态（0=待审核, 1=通过, 2=拒绝, 3=删除） |
| likes | INT | 0 | 点赞数 |
| created_at | DATETIME | NOW | 创建时间 |
| updated_at | DATETIME | NOW | 更新时间 |

**索引**：
- `idx_video_time`：`(video_id, position_time)`
- `idx_video_status`：`(video_id, status)`

---

### danmaku_likes（弹幕点赞表）

存储弹幕点赞记录。

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| id | BIGINT | AUTO | 主键 |
| danmaku_id | VARCHAR(32) | - | 弹幕ID（索引） |
| user_id | VARCHAR(32) | - | 用户ID（索引） |
| created_at | DATETIME | NOW | 点赞时间 |

**唯一索引**：`(danmaku_id, user_id)` - 同一用户对同一弹幕只能点赞一次

---

### danmaku_stats（弹幕统计表）

存储视频弹幕统计信息。

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| video_id | BIGINT | - | 主键，视频ID |
| total_count | INT | 0 | 弹幕总数 |
| updated_at | DATETIME | NOW | 更新时间 |

---

## 索引说明

### 主要索引

| 表名 | 索引名 | 字段 | 类型 |
|------|--------|------|------|
| lj_episodes | - | movie_id | 外键索引 |
| user | - | account, phone | 查询索引 |
| user_watch_history | - | accesstoken, movie_id | 查询索引 |
| user_watch_history | uq_watch_history_accesstoken_movie | accesstoken, movie_id | 唯一索引 |
| danmaku | idx_video_time | video_id, position_time | 复合索引 |
| danmaku | idx_video_status | video_id, status | 复合索引 |
| danmaku_likes | uk_danmaku_user | danmaku_id, user_id | 唯一索引 |

---

## 数据类型说明

| 类型 | 说明 |
|------|------|
| INT | 32位整数 |
| BIGINT | 64位整数 |
| VARCHAR(n) | 可变长度字符串，最大n字符 |
| TEXT | 长文本 |
| JSON | JSON数据类型（MySQL 5.7+） |
| FLOAT | 单精度浮点数 |
| DECIMAL(10,3) | 精确小数，10位总长度，3位小数 |
| DATETIME | 日期时间 |
| SMALLINT | 小整数（-32768~32767） |

---

## 命名规范

1. **表名**：小写字母，单词间用下划线分隔（如 `user_watch_history`）
2. **字段名**：小写字母，单词间用下划线分隔（如 `create_time`）
3. **主键**：通常使用 `id` 或 `{table}_id` 作为主键名
4. **外键**：以关联表名的单数形式加 `_id`（如 `movie_id`）
5. **时间字段**：`create_time`、`update_time` 或 `*_at` 后缀
6. **索引命名**：`idx_{字段名}` 或 `uk_{字段名}`（唯一索引）

---

**文档版本**: 1.1
**更新日期**: 2026-07-11
