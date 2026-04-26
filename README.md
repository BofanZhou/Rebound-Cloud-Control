# 回弹云控管理系统

> 钢管折弯回弹补偿智能控制平台 —— 支持多机管理与 AI 模型训练的原型系统。

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + TypeScript + Vue Router + Pinia |
| 后端 | Python + FastAPI + Pydantic + SQLAlchemy |
| 数据库 | SQLite（默认）/ PostgreSQL（生产环境可配置） |
| AI 模型 | PyTorch + scikit-learn |
| 部署 | Vercel（前端）/ Fly.io（后端） |

---

## 功能特性

- **双模式登录**：支持机器直连登录与用户名密码登录（管理员/维修员/操作员）
- **设备状态监控**：实时查看设备运行状态、温度、压力等参数
- **回弹参数推荐**：基于规则引擎的补偿参数推荐
- **历史记录管理**：查看、筛选、导出折弯作业历史
- **AI 模型训练**：上传数据集、在线训练 PyTorch 分类模型、迭代预测
- **多机管理**：添加、编辑、删除多台生产设备，支持机器切换
- **用户管理**：管理员可创建/删除用户、重置密码
- **操作日志**：记录关键操作，支持审计追踪
- **WebSocket 实时推送**：设备状态实时更新

---

## 环境要求

- **Python** >= 3.10（推荐 3.12/3.13）
- **Node.js** >= 18
- **Git**

---

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/BofanZhou/Rebound-Cloud-Control.git
cd Rebound-Cloud-Control
```

### 2. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
cd ..
```

> 建议创建虚拟环境：`python -m venv venv && .\venv\Scripts\activate`

### 3. 安装前端依赖

```bash
cd frontend
npm install
cd ..
```

### 4. 启动项目

#### 方式一：一键启动（推荐）

```bash
# Windows
python start.py

# 或 PowerShell
.\start.ps1
```

#### 方式二：手动分步启动

**终端 1 —— 启动后端：**
```bash
cd backend
python main.py
```
后端服务将运行在 `http://localhost:8000`

**终端 2 —— 启动前端：**
```bash
cd frontend
npm run dev
```
前端开发服务器将运行在 `http://localhost:5173`

### 5. 访问系统

打开浏览器访问：`http://localhost:5173`

---

## 项目结构

```
Rebound-Cloud-Control/
├── api/                    # Vercel Serverless 入口
├── backend/                # FastAPI 后端
│   ├── app/
│   │   ├── db/             # 数据库模型与连接
│   │   ├── models/         # Pydantic 数据模型
│   │   ├── routers/        # API 路由
│   │   ├── services/       # 业务逻辑
│   │   └── utils/          # 工具函数
│   ├── data/               # SQLite 数据与机器配置
│   ├── requirements.txt    # Python 依赖
│   └── main.py             # 后端入口
├── frontend/               # Vue 3 前端
│   ├── src/
│   │   ├── api/            # API 封装
│   │   ├── components/     # 公共组件
│   │   ├── stores/         # Pinia 状态管理
│   │   ├── views/          # 页面视图
│   │   └── types/          # TypeScript 类型定义
│   ├── package.json
│   └── vite.config.ts
├── tools/                  # 软著文档生成工具
├── start.py                # 一键启动脚本
├── start.ps1               # PowerShell 启动脚本
├── start.bat               # Windows 批处理入口
└── README.md
```

---

## 默认账号

| 角色 | 用户名 | 密码 | 权限 |
|------|--------|------|------|
| 管理员 | `admin` | `admin123` | 全部功能 |
| 维修员 | `maintenance` | `maint123` | 设备管理、参数推荐 |
| 操作员 | `operator` | `oper123` | 设备监控、历史查看 |

> 也支持**机器登录**：直接输入机器编号（如 `MCH-001`）即可进入单设备控制界面。

---

## API 文档

启动后端后，自动生成的交互式文档地址：

- Swagger UI：`http://localhost:8000/docs`
- ReDoc：`http://localhost:8000/redoc`

---

## 部署说明

### 前端部署（Vercel）

```bash
cd frontend
npm run build
```

将 `frontend/dist/` 目录部署到 Vercel。

### 后端部署（Fly.io）

```bash
cd backend
fly deploy
```

---

## 许可证

本项目为原型验证系统，仅供学习与演示使用。
