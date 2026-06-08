# 部署指南 · Deployment Guide

## 在线工具部署（Vercel + GitHub Pages）

### 🚀 快速开始

#### 步骤 1：提交代码到 GitHub

```bash
cd E:\BaiduSyncdisk\Shsmu\doctor_discovery

# 添加所有新文件
git add app.py templates/index.html vercel.json requirements.txt DEPLOYMENT.md

# 创建提交
git commit -m "feat: Add online tool with Flask web app and Vercel deployment"

# 推送到 fork
git push -u origin fix/emoji-encoding
```

#### 步骤 2：合并到 master（可选）

如果想在 master 分支上部署，合并 PR 后再推送 master。

#### 步骤 3：部署到 Vercel

1. **访问 Vercel：** https://vercel.com
2. **登录** GitHub 账号（tienanweiq-ui）
3. **导入项目：**
   - 点击 "New Project"
   - 选择 "Import Git Repository"
   - 选择 `Shsmu_tienanTools` 仓库
4. **配置：**
   - Framework: Python
   - 其他配置保持默认（Vercel 会自动读取 vercel.json）
5. **部署：** 点击 "Deploy"

等待几分钟，Vercel 会自动构建并部署应用。

#### 步骤 4：获取部署链接

部署完成后，Vercel 会提供一个公开的 URL，例如：
```
https://your-project.vercel.app
```

### 📋 文件说明

- **app.py** - Flask 后端应用
- **templates/index.html** - 前端网页
- **vercel.json** - Vercel 部署配置
- **requirements.txt** - Python 依赖

### 🔧 本地运行测试

```bash
# 安装依赖
pip install Flask Flask-CORS requests

# 运行应用
python app.py

# 访问 http://localhost:5000
```

### 📊 功能说明

#### API 端点

- **GET /** - 主页
- **POST /api/search** - 搜索医生研究画像
  - 请求参数：name, affiliation, offline, max
  - 返回：论文列表，包含摘要和期刊信息
- **GET /api/health** - 健康检查

#### 前端功能

1. **搜索医生** - 输入姓名和单位
2. **查询 PubMed** - 实时从 PubMed 采集论文
3. **显示摘要** - 点击论文查看摘要
4. **质量评分** - 显示每篇论文的质量分
5. **期刊信息** - 显示期刊名称和 IF
6. **离线演示** - 使用内置样例数据

### 🌐 部署后的 URL

你的在线工具部署后的访问地址：
```
https://<your-vercel-project>.vercel.app
```

### 📱 分享

部署完成后，可以直接分享 URL 给其他人使用：

```
👩‍⚕️ 医生临床研究画像在线工具
🔗 https://<your-vercel-project>.vercel.app

直接搜索任何医生的论文和研究成果！
```

### ⚙️ 环境变量（如需）

Vercel 自动支持以下环境变量（如需配置，在 Vercel 项目设置中添加）：

```
NCBI_EMAIL=your-email@example.com
```

### 🐛 故障排查

**问题：部署失败**
- 检查 vercel.json 配置
- 确保 requirements.txt 包含所有依赖
- 查看 Vercel 构建日志

**问题：搜索失败**
- 确保网络可以访问 PubMed
- 检查 NCBI_EMAIL 配置
- 查看浏览器开发者工具的网络标签

**问题：前端样式不显示**
- 清除浏览器缓存
- 检查 templates 文件夹路径
- 确保 Flask 正确提供静态文件

### 📚 相关链接

- [Vercel 文档](https://vercel.com/docs)
- [Flask 文档](https://flask.palletsprojects.com/)
- [PubMed API](https://www.ncbi.nlm.nih.gov/home/develop/api/)
