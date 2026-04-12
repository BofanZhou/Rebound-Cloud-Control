# PaaS 部署指南（临时演示）

使用 Vercel（前端）+ Render（后端）免费部署，5 分钟上线。

---

## 前置准备

1. 代码推送到 GitHub
2. 注册 [Vercel](https://vercel.com) 账号（用 GitHub 登录）
3. 注册 [Render](https://render.com) 账号

---

## 第一步：部署后端（Render）

1. 登录 [Render Dashboard](https://dashboard.render.com)
2. 点击 **New +** → **Web Service**
3. 选择你的 GitHub 仓库
4. 填写配置：
   - **Name**: `rebound-api`（或你喜欢的名字）
   - **Environment**: `Python`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. 点击 **Create Web Service**

等待 2-3 分钟部署完成，会获得一个地址：`https://rebound-api-xxxx.onrender.com`

**复制这个地址，下一步要用。**

---

## 第二步：配置前端 API 地址

修改 `frontend/.env.production`：

```env
VITE_API_BASE=https://rebound-api-xxxx.onrender.com/api
```

**把地址换成你实际的后端地址**

提交并推送到 GitHub：
```bash
git add .
git commit -m "配置生产环境 API 地址"
git push
```

---

## 第三步：部署前端（Vercel）

1. 登录 [Vercel Dashboard](https://vercel.com/dashboard)
2. 点击 **Add New...** → **Project**
3. 选择你的 GitHub 仓库
4. **Framework Preset**: 选择 `Vite`
5. **Root Directory**: 设置为 `frontend`
6. 点击 **Deploy**

等待 1-2 分钟，会获得一个地址：`https://rebound-cloud-xxxx.vercel.app`

---

## 完成！

现在你可以把 `https://rebound-cloud-xxxx.vercel.app` 发给任何人访问了！

**默认账号：**
- 管理员：admin / admin123
- 维修人员：maintenance / maint123
- 操作员：operator / oper123

---

## 注意事项

⚠️ **数据不会持久保存** - Render 免费版服务休眠后重启，数据会重置（符合原型演示需求）

⚠️ **首次访问较慢** - Render 免费版服务休眠后，首次访问需要 30 秒左右唤醒

---

## 自定义域名（可选）

### Vercel 自定义域名
1. 进入 Vercel 项目 → Settings → Domains
2. 添加你的域名，按提示配置 DNS

### Render 自定义域名
1. 进入 Render 服务 → Settings → Custom Domains
2. 添加域名并验证

---

## 故障排查

### 前端无法连接后端
- 检查 `.env.production` 中的 API 地址是否正确
- 检查后端 CORS 配置是否允许前端域名

### 部署失败
- 检查 Build Logs 查看具体错误
- 确保 `requirements.txt` 包含所有依赖

### 数据丢失
- 这是预期行为，免费 PaaS 服务重启后数据重置
- 如需持久化，需要接入 MongoDB Atlas 等云数据库
