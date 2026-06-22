# 家庭 DIY 维修小记

记录家庭维修过程的轻量 Web 应用：问题描述、日期、工具、耗时与是否复发，支持基础 CRUD。

| 模块 | 技术栈 | 端口 |
|------|--------|------|
| 前端 | Vue 3 + Naive UI、date-fns、axios | **6101** |
| 后端 | FastAPI + SQLite (`./data/fixit.db`) | **6000** |

## 目录结构

```
├── backend/          # FastAPI 后端
├── frontend/         # Vue 3 前端
├── data/             # SQLite 数据库（首次启动自动创建）
└── README.md
```

## 环境要求

- Python 3.10+
- Node.js 18+（使用项目内 `npm`，无需全局 pnpm/yarn）

## 启动

### 1. 后端（一条命令）

在项目根目录执行：

```bash
cd backend && python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt && python -m uvicorn main:app --reload --host 127.0.0.1 --port 6000
```

macOS / Linux 将激活命令改为 `source .venv/bin/activate`。

Windows 也可双击 `backend/run.bat`（等效于上述流程）。

首次启动会自动创建 `data/fixit.db` 并写入 5 条示例记录。

API 文档：http://127.0.0.1:6000/docs

### 2. 前端

新开终端，在项目根目录执行：

```bash
cd frontend && npm install && npm run dev
```

浏览器访问：http://localhost:6101

## API 概览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/records` | 列表 |
| GET | `/api/records/{id}` | 详情 |
| POST | `/api/records` | 新建 |
| PUT | `/api/records/{id}` | 更新 |
| DELETE | `/api/records/{id}` | 删除 |

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| description | string | 问题描述 |
| repair_date | string | 维修日期（YYYY-MM-DD） |
| tools | string | 使用工具 |
| duration_minutes | int | 耗时（分钟） |
| recurred | bool | 是否复发 |
