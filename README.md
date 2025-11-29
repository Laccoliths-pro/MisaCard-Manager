# MisaCard 管理系统

一个功能完善的虚拟卡管理系统，用于管理 MisaCard 虚拟信用卡，支持卡片激活、查询、批量导入、退款管理等功能。

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.5-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ 功能特性

### 📋 核心功能
- **卡片管理** - 完整的 CRUD 操作（创建、读取、更新、删除）
- **自动激活** - 集成 MisaCard API，自动查询并激活虚拟卡
- **批量导入** - 支持 TXT/JSON 格式批量导入卡密
- **智能过期检测** - 自动检测并标记过期卡片
- **退款管理** - 跟踪和管理卡片退款申请
- **消费记录** - 查询卡片交易历史和余额信息

### 🎨 用户界面
- **现代化 Web 界面** - 基于 Tailwind CSS 的响应式设计
- **实时数据统计** - 卡片状态、额度、激活率等数据可视化
- **批量操作** - 支持批量标记退款、批量删除等操作
- **一键复制** - 快速复制已过期未退款卡号，并可自动标记

#### 界面预览
![系统概览](static/overview.png)
![卡片列表](static/list.png)

### 🔧 技术特性
- **RESTful API** - 标准的 REST API 设计
- **异步处理** - 基于 FastAPI 的异步请求处理
- **自动文档** - Swagger UI / ReDoc 自动生成 API 文档
- **数据验证** - Pydantic 模型验证
- **激活日志** - 完整的激活历史记录

## 📦 技术栈

- **后端框架**: FastAPI 0.115.5
- **数据库**: SQLite + SQLAlchemy 2.0.36 ORM
- **服务器**: Uvicorn (ASGI)
- **数据验证**: Pydantic 2.10.3
- **HTTP 客户端**: httpx 0.28.1
- **模板引擎**: Jinja2 3.1.4
- **前端样式**: Tailwind CSS

## 🚀 快速开始

### 环境要求

- Python 3.10 或更高版本
- pip (Python 包管理器)

### 安装步骤

#### 1. 克隆项目

```bash
git clone <repository-url>
cd backend
```

#### 2. 创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

#### 4. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env
```

> 默认配置已包含所有必要参数，通常无需修改。如需自定义端口或数据库路径，可编辑 `.env` 文件。

#### 5. 初始化数据库

```bash
# 创建数据库和表
python3 init_db.py init

# 检查数据库状态（可选）
python3 init_db.py check
```

#### 6. 启动服务

```bash
# 开发模式（自动重载）
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或使用提供的启动脚本
chmod +x run.sh
./run.sh
```

#### 7. 访问应用

- **Web 界面**: http://localhost:8000
- **API 文档 (Swagger)**: http://localhost:8000/docs
- **API 文档 (ReDoc)**: http://localhost:8000/redoc

## 📖 使用指南

### Web 界面功能

#### 1. 概览页面
- 查看系统统计数据（有效卡片、激活率、总额度等）
- 快速访问主要功能

#### 2. 卡片列表
- 查看所有卡片信息
- 搜索和筛选（按状态、退款状态）
- 批量操作（标记退款、删除）
- **一键复制已过期未退款卡号** - 点击后可选择自动标记为已申请退款

#### 3. 查询激活
- 输入卡密自动查询并激活
- 显示完整的卡片信息

#### 4. 批量导入
- 粘贴卡片数据批量导入
- 支持格式：`卡密: mio-xxx 额度: x 有效期: x小时`

### API 使用示例

#### 创建卡片

```bash
curl -X POST "http://localhost:8000/api/cards/" \
  -H "Content-Type: application/json" \
  -d '{
    "card_id": "mio-xxxxx-xxxxx",
    "card_nickname": "测试卡",
    "card_limit": 10.0,
    "validity_hours": 1
  }'
```

#### 激活卡片

```bash
curl -X POST "http://localhost:8000/api/cards/mio-xxxxx-xxxxx/activate"
```

#### 获取卡片列表

```bash
# 获取所有卡片
curl "http://localhost:8000/api/cards/"

# 筛选已激活的卡片
curl "http://localhost:8000/api/cards/?status=active"

# 筛选已过期的卡片
curl "http://localhost:8000/api/cards/?status=expired"

# 搜索卡片
curl "http://localhost:8000/api/cards/?search=mio-123"
```

#### 复制已过期未退款卡号

```bash
curl "http://localhost:8000/api/cards/batch/unreturned-card-numbers"
```

#### 查询消费记录

```bash
curl "http://localhost:8000/api/cards/mio-xxxxx-xxxxx/transactions"
```

更多 API 详情请查看 Swagger 文档：http://localhost:8000/docs

## 📁 项目结构

```
backend/
├── app/
│   ├── __init__.py           # 应用初始化
│   ├── main.py               # FastAPI 应用入口
│   ├── config.py             # 配置管理
│   ├── database.py           # 数据库连接
│   ├── models.py             # SQLAlchemy 模型
│   ├── schemas.py            # Pydantic 模型
│   ├── crud.py               # 数据库 CRUD 操作
│   ├── api/                  # API 路由
│   │   ├── cards.py          # 卡片管理接口
│   │   └── imports.py        # 批量导入接口
│   ├── utils/                # 工具函数
│   │   ├── activation.py     # 卡片激活逻辑
│   │   └── parser.py         # 文件解析
│   ├── templates/            # Jinja2 模板
│   │   └── index.html        # Web 界面
│   └── static/               # 静态文件
├── init_db.py                # 数据库初始化脚本
├── requirements.txt          # Python 依赖
├── .env.example              # 环境变量模板
├── .gitignore                # Git 忽略文件
├── run.sh                    # 启动脚本
└── README.md                 # 项目文档
```

## 🗄️ 数据模型

### Card（卡片表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| card_id | String | 卡密（唯一） |
| card_nickname | String | 卡片昵称 |
| card_number | String | 卡号（激活后） |
| card_cvc | String | CVC 安全码 |
| card_exp_date | String | 有效期（MM/YY） |
| billing_address | String | 账单地址 |
| card_limit | Float | 额度 |
| validity_hours | Integer | 有效时长（小时） |
| status | String | 状态（active/inactive/expired/deleted） |
| is_activated | Boolean | 是否已激活 |
| create_time | DateTime | 创建时间 |
| card_activation_time | DateTime | 激活时间 |
| exp_date | DateTime | 过期时间 |
| refund_requested | Boolean | 是否申请退款 |
| refund_requested_time | DateTime | 退款申请时间 |

### ActivationLog（激活日志表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| card_id | String | 卡密 |
| status | String | 激活状态（success/failed） |
| error_message | String | 错误信息 |
| activation_time | DateTime | 激活时间 |
| response_data | String | API 响应数据 |

## 🔧 数据库管理

### 初始化数据库

```bash
python3 init_db.py init
```

### 检查数据库状态

```bash
python3 init_db.py check
```

### 重置数据库（谨慎使用！）

```bash
python3 init_db.py reset
```

这将删除所有数据并重新创建表。

## 🛠️ 开发指南

### 添加新的 API 端点

1. 在 `app/schemas.py` 中定义 Pydantic 模型
2. 在 `app/crud.py` 中添加数据库操作函数
3. 在 `app/api/` 下创建或更新路由文件
4. 在 `app/main.py` 中注册路由

### 修改数据库模型

1. 更新 `app/models.py` 中的模型定义
2. 使用 Alembic 生成迁移脚本：
   ```bash
   alembic revision --autogenerate -m "描述修改内容"
   alembic upgrade head
   ```

### 运行测试

```bash
pytest
```

## 📝 常见问题

### 1. 数据库文件在哪里？

默认情况下，数据库文件 `cards.db` 位于项目根目录。你可以在 `.env` 文件中修改 `DATABASE_URL` 来更改位置。

### 2. 端口 8000 已被占用怎么办？

在 `.env` 文件中修改 `PORT` 配置，或启动时指定端口：
```bash
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8888
```

### 3. 时区问题

系统使用 UTC 时间存储，前端会根据浏览器时区自动转换显示。如果发现时间不正确，请检查：
- 确保系统时间正确
- MisaCard API 返回的时间格式（默认为 UTC+8）

### 4. 复制功能不工作

复制功能需要浏览器支持 Clipboard API，或在 HTTPS 环境下运行。本地开发时 localhost 默认是安全上下文，可以正常使用。如果仍有问题，系统会自动降级使用传统的复制方法。

### 5. "已过期+未申请退款"筛选不到数据

请确保：
1. 后端已重启，时区修复已生效
2. 数据库中的 `exp_date` 字段已正确设置
3. 刷新页面后重新筛选

## 🔒 安全注意事项

1. **不要提交 .env 文件到 Git** - .gitignore 已配置忽略此文件
2. **数据库备份** - 定期备份 `cards.db` 数据库文件，避免数据丢失
3. **生产环境配置** - 生产环境建议：
   - 设置 `DEBUG=false`
   - 使用更安全的数据库（PostgreSQL/MySQL）
   - 配置 HTTPS
   - 限制 CORS 来源
   - 添加身份验证

## 📜 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题或建议，请提交 GitHub Issue。

---

⭐ 如果这个项目对你有帮助，请给个 Star！
