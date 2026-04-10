# 钢管回弹智能补偿 Web 原型系统

第一阶段原型系统 - 多机管理版本

## 项目概述

本项目是一个钢管回弹智能补偿系统的 Web 原型，用于验证"参数输入 -> 推荐参数返回 -> 设备状态展示 -> 任务提交 -> 单机演示"的最小闭环。

**新增功能：多机管理和用户认证系统**

## 技术栈

### 前端
- Vue 3 + Vite + TypeScript
- Vue Router（路由管理）
- Pinia（状态管理）
- ECharts（数据可视化）

### 后端
- Python + FastAPI
- Pydantic（数据验证）
- Uvicorn（ASGI 服务器）

## 项目结构

```
project-root/
├── frontend/                 # 前端项目
│   ├── src/
│   │   ├── api/             # API 接口封装
│   │   ├── router/          # 路由配置
│   │   ├── stores/          # Pinia Store
│   │   ├── types/           # TypeScript 类型定义
│   │   ├── views/           # 页面视图
│   │   │   ├── LoginView.vue       # 登录页面
│   │   │   ├── MachineSelectView.vue  # 机器选择页面
│   │   │   ├── DashboardView.vue   # 参数推荐页面
│   │   │   ├── DeviceView.vue      # 设备状态页面
│   │   │   └── HistoryView.vue     # 历史记录页面
│   │   ├── App.vue          # 根组件
│   │   └── main.ts          # 入口文件
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
│
├── backend/                  # 后端项目
│   ├── app/
│   │   ├── models/          # Pydantic 数据模型
│   │   ├── routers/         # API 路由
│   │   │   ├── auth.py      # 认证路由
│   │   │   ├── machines.py  # 机器管理路由
│   │   │   ├── device.py    # 设备状态路由
│   │   │   ├── recommend.py # 推荐参数路由
│   │   │   └── history.py   # 历史记录路由
│   │   ├── services/        # 业务逻辑服务
│   │   │   ├── auth.py      # 用户认证服务
│   │   │   ├── machine_manager.py  # 机器管理服务
│   │   │   ├── device_simulator.py # 设备模拟器
│   │   │   └── rule_engine.py      # 规则引擎
│   │   └── __init__.py
│   ├── data/                # 数据存储目录
│   │   ├── machines/        # 机器数据（每台机器独立存储）
│   │   └── users.json       # 用户数据
│   ├── main.py              # FastAPI 入口
│   └── requirements.txt
│
└── README.md
```

## 快速启动

### 环境要求
- Node.js >= 18
- Python >= 3.8
- npm 或 pnpm

### 1. 克隆/进入项目

```bash
cd Rebound-Cloud-Control  # 进入项目目录
```

### 2. 启动后端服务

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（推荐）
python -m venv venv313

# 激活虚拟环境
# Windows:
venv313\Scripts\activate
# macOS/Linux:
source venv313/bin/activate

# 安装依赖
pip install fastapi uvicorn pydantic

# 启动服务
python main.py
```

后端服务将在 `http://localhost:8000` 启动，API 文档访问 `http://localhost:8000/docs`

### 3. 启动前端服务

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 `http://localhost:5173` 启动

## 使用说明

### 登录系统

系统支持两种登录方式：

#### 1. 机器登录
- 直接输入机器ID（如默认机器的 ID 或新创建的机器 ID）
- 直接进入该机器的操作界面

#### 2. 用户登录
- 使用用户名和密码登录
- 登录后需要选择要管理的机器
- 支持三种角色：
  - **管理员(admin)**: 管理所有机器和用户，可创建新机器
  - **维修人员(maintenance)**: 查看机器状态和历史记录
  - **操作员(operator)**: 操作指定机器

**默认账号：**
| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 维修人员 | maintenance | maint123 |
| 操作员 | operator | oper123 |

### 参数推荐页面（首页）

1. 输入钢管参数：
   - 管径（10-500 mm）
   - 壁厚（1-50 mm）
   - 材质（普通钢/高强钢/不锈钢/铝合金）
   - 目标角度（0-180°）

2. 点击"获取推荐参数"按钮

3. 系统根据规则引擎返回：
   - 推荐角度
   - 补偿值
   - 说明文字

4. 确认参数后点击"提交任务"

### 设备状态页面

- 实时显示设备状态（在线/离线/空闲/运行中/已完成）
- 显示当前角度、实际角度和偏差
- 提供控制面板（模拟用）
- 支持自动刷新

### 历史记录页面

- 显示最近提交的任务列表
- 包含输入参数、推荐参数、执行结果
- 支持查看详情
- 支持刷新和清空

## API 接口

### 认证相关

#### 登录
```http
POST /api/auth/login
Content-Type: application/json

{
    "username": "admin",
    "password": "admin123",
    "login_type": "user"  // 或 "machine"
}
```

### 机器管理

#### 获取机器列表
```http
GET /api/machines
Authorization: Bearer {token}
```

#### 创建机器（仅管理员）
```http
POST /api/machines
Authorization: Bearer {token}
Content-Type: application/json

{
    "name": "新机器",
    "location": "车间B"
}
```

#### 选择机器
```http
POST /api/machines/{machine_id}/select
Authorization: Bearer {token}
```

### 参数推荐
```http
POST /api/recommend
Content-Type: application/json

{
    "diameter": 50,
    "thickness": 5,
    "material": "普通钢",
    "target_angle": 90
}
```

### 获取设备状态
```http
GET /api/device/status
Authorization: Bearer {token}
```

### 提交任务
```http
POST /api/device/submit
Authorization: Bearer {token}
Content-Type: application/json

{
    "diameter": 50,
    "thickness": 5,
    "material": "普通钢",
    "target_angle": 90,
    "recommended_angle": 92,
    "recommended_offset": 2
}
```

### 获取历史记录
```http
GET /api/history?limit=10
Authorization: Bearer {token}
```

## 数据存储

### 机器数据隔离
每个机器有独立的存储目录：
```
data/
├── machines/
│   ├── {machine_id}/
│   │   ├── machine.json    # 机器基本信息
│   │   └── history.json    # 历史记录
│   └── ...
└── users.json              # 用户数据
```

## 推荐规则说明

### 材质基础补偿
- 普通钢：+2.0°
- 高强钢：+3.0°
- 不锈钢：+2.5°
- 铝合金：+1.5°

### 壁厚修正
- 壁厚 > 10mm：-0.5°（厚壁回弹小）
- 壁厚 < 3mm：+0.5°（薄壁回弹大）

### 管径修正
- 管径 > 200mm：-0.3°（大管径回弹小）

## 设备模拟说明

本阶段使用模拟设备，不接真实 PLC：

- 状态流转：idle -> running -> completed
- 任务执行时间：3-8 秒（随机）
- 实际角度误差：±0.5°（随机）
- 支持轮询方式获取状态更新
- 每台机器有独立的模拟器实例

## 已实现功能

✅ Web 页面基本框架  
✅ 参数输入页面（管径、壁厚、材质、目标角度）  
✅ 推荐参数展示（推荐角度、补偿值、说明）  
✅ 设备状态展示（在线状态、当前角度、实际角度、偏差）  
✅ 前后端接口打通  
✅ 单机演示用的模拟设备状态流  
✅ 规则引擎推荐器  
✅ 历史记录功能  
✅ **多机管理**  
✅ **用户认证系统**  
✅ **机器登录/用户登录**  
✅ **数据隔离存储**  

## 未实现内容（后续阶段）

❌ 真实 PLC 通信  
❌ 真实 AI 模型（目前是规则引擎）  
❌ WebSocket 实时推送（目前是轮询）  
❌ Docker 部署  

## 开发说明

### 前端开发

```bash
cd frontend
npm run dev      # 启动开发服务器
npm run build    # 构建生产包
npm run preview  # 预览生产包
```

### 后端开发

```bash
cd backend
python main.py                    # 启动服务
uvicorn main:app --reload         # 使用 uvicorn 启动（带热重载）
```

## 常见问题

### Q: 前端无法连接后端？
A: 检查：
1. 后端服务是否已启动（端口 8000）
2. 前端代理配置是否正确（vite.config.ts）
3. CORS 配置是否允许前端域名

### Q: 如何修改推荐规则？
A: 编辑 `backend/app/services/rule_engine.py` 中的 `RuleEngine` 类

### Q: 如何调整设备模拟参数？
A: 编辑 `backend/app/services/device_simulator.py` 中的相关参数

### Q: 如何添加新用户？
A: 编辑 `backend/app/services/auth.py` 中的 `_create_default_users` 方法

## 许可证

MIT License

## 更新日志

### v0.2.0 (2026-04)
- 新增多机管理功能
- 新增用户认证系统
- 支持机器登录和用户登录两种模式
- 支持管理员、维修人员、操作员三种角色
- 数据存储按机器隔离

### v0.1.0 (2024-01)
- 第一阶段原型完成
- 实现核心功能闭环
