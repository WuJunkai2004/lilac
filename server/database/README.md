# 数据库设计思路

## 1. 数据库选择
选择了关系型数据库 SQLite 作为我们的数据库管理系统。SQLite 是一个轻量级的嵌入式数据库，适合小型应用程序和开发阶段使用。它不需要单独的服务器进程，数据存储在一个文件中，易于部署和维护。  
选择使用 peewee 作为 ORM 工具。

## 2. 数据库结构设计

### 图片表（images)
- **存储方式**：图片文件存储在服务器的文件系统中，所有传入的图片传入后，都需要转为webp格式进行存储，以节省空间和提升加载速度。
- **路径存储**：图片存储在文件系统中，具体路径是/datas/images/xxx.webp，数据库中仅储存xxx作为名称，访问时通过拼接路径获取完整路径。
```sql
CREATE TABLE images (
    img_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,  -- 存储图片的名称
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
);
```

### 用户表（users)
将登录凭证直接整合，优化鉴权性能。
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    avatar INTEGER,                  -- 头像id，通过关联 images 表获取完整路径
    -- Session 整合字段 (单设备登录模式)
    session_token TEXT UNIQUE,       -- 登录 Token (UUID)
    token_expires_at DATETIME,       -- Token 过期时间
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (avatar) REFERENCES images(img_id)
);
```


### 情绪定义表（mood_types)
- **element_type**: 作为描述，其实这个不是很重要，只需要在前端进行映射即可，但为了后续可能的扩展，还是放在数据库里比较好。
```sql
CREATE TABLE mood_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL, -- 活力, 喜悦, 宁静, 忧郁等
    color_code TEXT,           -- 十六进制颜色
    element_type TEXT          -- 对应主页展示的元素类型（如：粒子、流体、光斑）
);
```

### 信笺分享表（letters)
- **content**: 文字内容，允许为空，因为用户可能只想分享图片。
- **image**: 配图，允许为空，因为用户可能只想分享文字。
> 但是不允许两者都为空，至少要有文字或图片中的一个。
- **location**: 地点，校内四区域中的一个，不允许为空。
- **likes_count** 和 **view_count**: 这两个字段用于统计信笺的受欢迎程度，初始值为0。
- **is_public**: 是否公开，默认为1（公开），用户可以选择将信笺设为私密。
```sql
CREATE TABLE letters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    content TEXT,              -- 文字内容
    image INTEGER,             -- 配图
    mood_type INTEGER,         -- 情绪类型
    latitude REAL NOT NULL,    -- 纬度
    longitude REAL NOT NULL,   -- 经度
    location TEXT NOT NULL,    -- 地点名称
    likes_count INTEGER DEFAULT 0, 
    view_count INTEGER DEFAULT 0,  
    is_public BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (image) REFERENCES images(img_id),
    FOREIGN KEY (mood_type) REFERENCES mood_types(id),
    CHECK (content IS NOT NULL OR image IS NOT NULL)  -- 至少要有文字或图片中的一个
);

-- 为了优化查询性能，创建一个索引。
-- 场景：获取用户的信笺列表时；统计用户的信笺数量时；获取用户的公开信笺列表时。
CREATE INDEX idx_letters_user_id ON letters(user_id);
```

### 情绪记录表（mood_entries)
- **log_date**: 记录用户每天的情绪状态，确保每天只能有一条记录。
- **is_public**: 是否公开，默认为0（私密），用户可以选择将情绪记录设为公开，以便在主页展示。
```sql
CREATE TABLE mood_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    mood_type_id INTEGER NOT NULL,
    log_date DATE NOT NULL,
    is_public BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (mood_type_id) REFERENCES mood_types(id),
    UNIQUE(user_id, log_date)
);
```

### AI 反馈表 (ai_feedback)
```sql
CREATE TABLE ai_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mood_entry_id INTEGER UNIQUE NOT NULL,
    review_content TEXT NOT NULL,  -- AI 总结
    rec_activity TEXT,             -- 推荐活动
    rec_food TEXT,                 -- 推荐美食
    rec_location TEXT,             -- 推荐校内地点
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mood_entry_id) REFERENCES mood_entries(id)
);
```

### 聊天系统 (chat)
```sql
CREATE TABLE chat_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_type TEXT CHECK(session_type IN ('daily', 'long-term')) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    role TEXT CHECK(role IN ('user', 'assistant')) NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
);
```

### 全校实时心情聚合视图 (v_school_mood_summary)
- **summary_date**: 以日期为单位进行聚合，统计每天的情绪分布情况。
- **count**: 统计每种情绪的数量，便于前端展示全校的情绪分布图。
- **mood_name**: 情绪名称。
- **color_code**: 情绪颜色代码。
- **element_type**: 情绪对应的元素类型。
```sql
CREATE VIEW v_school_mood_summary AS
SELECT 
    mt.name AS mood_name,
    mt.color_code,
    mt.element_type,
    COUNT(me.id) AS count,
    DATE(me.log_date) AS summary_date
FROM mood_entries me
JOIN mood_types mt ON me.mood_type_id = mt.id
GROUP BY mt.id, summary_date;
```

### 公开信笺流视图 (v_public_letter_flow)
```sql
CREATE VIEW v_public_letter_flow AS
SELECT 
    l.id, l.content, l.image, l.latitude, l.longitude, l.mood_type AS mood_id,
    l.location, l.likes_count, l.view_count, l.created_at,
    u.username, u.avatar
FROM letters l
JOIN users u ON l.user_id = u.id
WHERE l.is_public = 1
ORDER BY l.created_at DESC;
```

### 用户信息统计视图 (v_user_profile)
```sql
CREATE VIEW v_user_profile AS
SELECT 
    u.id AS user_id,
    u.username,
    u.avatar,
    -- 统计信笺数
    (SELECT COUNT(*) FROM letters l WHERE l.user_id = u.id) AS letter_count,
    -- 统计总点赞数 (TOTAL 会在无记录时返回 0 而不是 NULL)
    (SELECT TOTAL(likes_count) FROM letters l WHERE l.user_id = u.id) AS total_likes,
    -- 统计心情记录天数
    (SELECT COUNT(*) FROM mood_entries me WHERE me.user_id = u.id) AS mood_day_count
FROM users u;
```