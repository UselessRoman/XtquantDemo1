# 上传项目到 GitHub 指南

## 📋 前提条件

1. 已安装 Git（如果未安装，从 https://git-scm.com/downloads 下载）
2. 已注册 GitHub 账号（https://github.com）
3. 已配置 Git 用户信息（首次使用需要）

## 🔧 首次配置 Git（如果未配置过）

```bash
# 配置用户名和邮箱
git config --global user.name "你的用户名"
git config --global user.email "你的邮箱@example.com"
```

## 📤 上传步骤

### 步骤1：初始化 Git 仓库

在项目根目录（`e:\XTquantdemo1`）打开终端，执行：

```bash
cd e:\XTquantdemo1
git init
```

### 步骤2：检查 .gitignore 文件

确保 `.gitignore` 文件包含以下内容（已自动创建）：
- Python 缓存文件（`__pycache__/`, `*.pyc`）
- 虚拟环境（`.venv/`, `venv/`）
- IDE 配置（`.idea/`, `.vscode/`）
- 测试覆盖率报告（`htmlcov/`, `.pytest_cache/`）
- 日志文件（`*.log`）
- 系统文件（`.DS_Store`, `Thumbs.db`）

### 步骤3：添加文件到 Git

```bash
# 查看要添加的文件（可选）
git status

# 添加所有文件到暂存区
git add .

# 查看已添加的文件（可选）
git status
```

### 步骤4：创建首次提交

```bash
git commit -m "Initial commit: XTquant量化交易框架"
```

### 步骤5：在 GitHub 上创建新仓库

1. 登录 GitHub (https://github.com)
2. 点击右上角的 "+" 号，选择 "New repository"
3. 填写仓库信息：
   - **Repository name**: `XTquant-demo`（或其他你喜欢的名字）
   - **Description**: `基于迅投量化(XTquant)的完整量化交易框架`
   - **Visibility**: 选择 Public（公开）或 Private（私有）
   - **不要**勾选 "Initialize this repository with a README"（因为本地已有文件）
4. 点击 "Create repository"

### 步骤6：连接本地仓库到 GitHub

GitHub 创建仓库后，会显示仓库地址，格式类似：
- HTTPS: `https://github.com/你的用户名/仓库名.git`
- SSH: `git@github.com:你的用户名/仓库名.git`

**使用 HTTPS（推荐，简单）**：

```bash
# 添加远程仓库（替换为你的实际仓库地址）
git remote add origin https://github.com/你的用户名/XTquant-demo.git

# 验证远程仓库
git remote -v
```

**使用 SSH（需要配置 SSH 密钥）**：

如果你已经配置了 SSH 密钥，可以使用：
```bash
git remote add origin git@github.com:你的用户名/XTquant-demo.git
```

### 步骤7：推送代码到 GitHub

```bash
# 推送代码（首次推送）
git branch -M main
git push -u origin main
```

如果使用 HTTPS，首次推送会要求输入 GitHub 用户名和密码（或 Personal Access Token）

## 🔐 GitHub 认证说明

如果使用 HTTPS，GitHub 不再支持密码认证，需要使用 **Personal Access Token (PAT)**：

1. 进入 GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. 点击 "Generate new token (classic)"
3. 勾选 `repo` 权限
4. 生成后复制 token（只会显示一次）
5. 推送时，用户名输入 GitHub 用户名，密码输入 token

## 📝 后续更新代码

当代码有更新时，使用以下命令：

```bash
# 查看更改
git status

# 添加更改的文件
git add .

# 提交更改
git commit -m "描述你的更改"

# 推送到 GitHub
git push
```

## 🛠️ 常用 Git 命令

```bash
# 查看当前状态
git status

# 查看提交历史
git log

# 查看远程仓库
git remote -v

# 查看分支
git branch

# 拉取远程更新
git pull

# 创建新分支
git checkout -b feature/新功能

# 切换分支
git checkout main
```

## ⚠️ 注意事项

1. **不要提交敏感信息**：
   - API 密钥
   - 密码
   - 真实账户信息
   - 本地配置文件中的敏感数据

2. **.gitignore 已配置**：会自动排除：
   - `__pycache__/` - Python 缓存
   - `.venv/` - 虚拟环境
   - `.pytest_cache/` - 测试缓存
   - `htmlcov/` - 覆盖率报告
   - `*.log` - 日志文件
   - `.cursor/` - Cursor IDE 配置

3. **建议提交前检查**：
   ```bash
   git status
   git diff  # 查看具体更改内容
   ```

## 🎯 快速命令总结

```bash
# 完整流程（首次上传）
cd e:\XTquantdemo1
git init
git add .
git commit -m "Initial commit: XTquant量化交易框架"
git branch -M main
git remote add origin https://github.com/你的用户名/仓库名.git
git push -u origin main
```

## 📚 参考资源

- Git 官方文档：https://git-scm.com/doc
- GitHub 官方指南：https://guides.github.com
- Git 中文教程：https://git-scm.com/book/zh/v2
