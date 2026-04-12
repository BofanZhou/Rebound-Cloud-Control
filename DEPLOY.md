# Vercel 部署指南（推荐）

使用 Vercel 统一部署前后端，**完全免费，无需信用卡**。

---

## ⚠️ 重要限制

Vercel Serverless 有 **10 秒超时限制**，刚好满足当前模拟设备需求（3-8 秒）。

数据存储在内存中，**每次重新部署或函数冷启动后数据会重置**，适合临时演示。

---

## 部署步骤

### 1. 推送代码到 GitHub

```bash
git add .
git commit -m "配置 Vercel 部署"
git push
```

### 2. 注册并登录 Vercel

1. 打开 [vercel.com](https://vercel.com)
2. 用 GitHub 账号登录
3. 点击 **Add New...** → **Project**

### 3. 导入项目

1. 选择你的 GitHub 仓库 `Rebound-Cloud-Control`
2. **Framework Preset**: 选择 `Other`
3. 配置如下：

| 配置项 | 值 |
|--------|-----|
| Build Command | `cd frontend && npm install && npm run build` |
| Output Directory | `frontend/dist` |
| Install Command | `npm install` |

4. 展开 **Environment Variables**，添加：

| Name | Value |
|------|-------|
| `PYTHONPATH` | `backend` |

5. 点击 **Deploy**

### 4. 配置 API 路由（重要）

部署完成后，进入项目设置：

1. 点击 **Settings** → **Functions**
2. 确保 **Function Region** 选择靠近你的地区（如 `sin1` 新加坡）
3. 点击保存

### 5. 重新部署

如果第一次部署后 API 访问有问题，点击 **Redeploy** 重新部署。

---

## 访问地址

部署完成后，Vercel 会给你一个域名：

```
https://rebound-cloud-control-xxxx.vercel.app
```

**前后端统一在这个域名下：**
- 前端：`https://xxx.vercel.app/`
- API：`https://xxx.vercel.app/api/`

---

## 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 维修人员 | maintenance | maint123 |
| 操作员 | operator | oper123 |

---

## 故障排查

### API 返回 404
- 检查 `vercel.json` 配置是否正确
- 确保 `api/index.py` 存在
- 尝试重新部署

### API 返回 500
- 检查 Vercel Functions 日志
- 可能是 Python 依赖问题，检查 `requirements.txt`

### 前端无法连接 API
- 确保使用的是相对路径 `/api/xxx`
- 检查 CORS 配置

---

## 切换到独立后端（可选）

如果 Vercel 的 10 秒超时不够用，可以：

1. 后端部署到 Render/Railway
2. 前端部署到 Vercel
3. 修改 `frontend/.env.production` 中的 API 地址

详见其他部署方案。

---

## 2026-04 Stability Notes

- `vercel.json` now includes a dedicated rewrite for `/api` (without trailing path) and keeps API function `maxDuration` at `10` seconds to match Vercel serverless limits.
- API error responses are normalized to `{ code, message, data }` for both HTTP and validation errors.
- Data directories are split on Vercel:
  - `USER_DATA_DIR=/tmp/data`
  - `MACHINE_DATA_DIR=/tmp/data/machines`
- Frontend supports optional environment variables:
  - `VITE_API_BASE` (default: `/api`)
  - `VITE_API_TIMEOUT_MS` (default: `12000`)
