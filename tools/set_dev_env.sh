#!/bin/bash

# ==============================================================================
# Go & Vue.js Full-Stack Development Environment Setup Script
# ==============================================================================
#
# 这个脚本会自动执行以下操作:
#   1. 检查并安装 Go (最新版).
#   2. 检查并安装 Node.js (LTS 版本) 和 pnpm.
#   3. 创建一个包含后端和前端目录的基本项目结构.
#   4. 生成 VS Code 的推荐设置和 EditorConfig 文件.
#
# 用法:
#   - 在一个空目录中直接运行: ./setup_dev_env.sh
#   - 指定项目名称运行: ./setup_dev_env.sh <project-name>
#
# ==============================================================================

# --- 配置 & 变量 ---

# 设置颜色，让输出更易读
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 如果传入了参数，则将其作为项目目录名
PROJECT_DIR=${1:-"."}

# --- 函数定义 ---

# 打印信息
info() {
  echo -e "${BLUE}INFO: $1${NC}"
}

# 打印成功信息
success() {
  echo -e "${GREEN}SUCCESS: $1${NC}"
}

# 打印警告信息
warn() {
  echo -e "${YELLOW}WARNING: $1${NC}"
}

# 检查命令是否存在
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# --- 脚本主逻辑 ---

# 如果指定了项目目录，则创建并进入该目录
if [ "$PROJECT_DIR" != "." ]; then
  mkdir -p "$PROJECT_DIR"
  cd "$PROJECT_DIR" || exit
  info "项目目录 '${PROJECT_DIR}' 已创建并进入。"
fi

# 1. 安装 Go
# ------------------------------------------------------------------------------
info "正在检查 Go 环境..."
if command_exists go; then
  success "Go 已安装: $(go version)"
else
  info "未检测到 Go，正在开始安装..."
  GO_LATEST_VERSION=$(curl -s "https://go.dev/VERSION?m=text")
  GO_TARBALL="${GO_LATEST_VERSION}.linux-amd64.tar.gz"
  
  info "正在下载 ${GO_TARBALL}..."
  curl -fsSL "https://go.dev/dl/${GO_TARBALL}" -o "/tmp/${GO_TARBALL}"
  
  info "正在安装 Go..."
  sudo rm -rf /usr/local/go
  sudo tar -C /usr/local -xzf "/tmp/${GO_TARBALL}"
  rm "/tmp/${GO_TARBALL}"
  
  # 将 Go 添加到 PATH
  echo 'export PATH=$PATH:/usr/local/go/bin' | sudo tee /etc/profile.d/go.sh > /dev/null
  export PATH=$PATH:/usr/local/go/bin

  success "Go 安装完成: $(go version)"
  warn "请重启终端或运行 'source /etc/profile' 来让 Go 命令生效。"
fi

# 2. 安装 Node.js (使用 nvm) 和 pnpm
# ------------------------------------------------------------------------------
info "正在检查 Node.js 环境..."
if command_exists node && command_exists pnpm; then
  success "Node.js 已安装: $(node -v)"
  success "pnpm 已安装: $(pnpm -v)"
else
  info "未检测到 Node.js 或 pnpm，正在开始安装..."
  # 安装 nvm (Node Version Manager)
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
  
  # 加载 nvm
  export NVM_DIR="$HOME/.nvm"
  [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
  
  info "正在使用 nvm 安装 Node.js LTS 版本..."
  nvm install --lts
  nvm use --lts
  nvm alias default 'lts/*'
  
  info "正在安装 pnpm..."
  npm install -g pnpm
  
  success "Node.js 安装完成: $(node -v)"
  success "pnpm 安装完成: $(pnpm -v)"
  warn "请重启终端或运行 'source ~/.bashrc' (或 ~/.zshrc) 来让 Node.js 命令生效。"
fi

# 3. 创建项目骨架和配置文件
# ------------------------------------------------------------------------------
info "正在创建项目文件和目录结构..."

# 创建目录
mkdir -p backend frontend .vscode

# --- 创建后端文件 ---
info "创建 Go 后端文件..."
cat << EOF > backend/go.mod
module my-go-vue-project/backend

go 1.21
EOF

cat << EOF > backend/main.go
package main

import (
	"fmt"
	"log"
	"net/http"
)

func main() {
	// 创建一个简单的 HTTP 处理器
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintln(w, "<h1>Hello from Go Backend!</h1>")
		fmt.Fprintln(w, "<p>Your full-stack application is running.</p>")
	})

	port := "8080"
	fmt.Printf("Go server starting on http://localhost:%s\n", port)
	
	// 启动 HTTP 服务器
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatalf("Failed to start server: %s\n", err)
	}
}
EOF

# --- 创建前端文件 ---
info "创建 Vue 前端文件..."
cat << EOF > frontend/package.json
{
  "name": "frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.3.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^4.5.0",
    "vite": "^5.0.0"
  }
}
EOF

# --- 创建 VS Code 设置 ---
info "创建 VS Code 配置文件..."
cat << EOF > .vscode/settings.json
{
  "terminal.integrated.defaultProfile.linux": "bash",
  "go.toolsManagement.autoUpdate": true,
  "go.useLanguageServer": true,
  "editor.formatOnSave": true,
  "[go]": {
    "editor.defaultFormatter": "golang.go"
  },
  "[vue]": {
    "editor.defaultFormatter": "Vue.volar"
  },
  "[json]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[jsonc]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[markdown]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
EOF

# --- 创建 EditorConfig ---
info "创建 EditorConfig 文件..."
cat << EOF > .editorconfig
root = true

[*]
indent_style = space
indent_size = 2
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

[*.md]
trim_trailing_whitespace = false
EOF

# 4. 完成
# ------------------------------------------------------------------------------
echo ""
success "开发环境设置完成!"
echo ""
info "--- 后续步骤 ---"
echo "1. ${YELLOW}重启你的终端${NC}或运行 ${YELLOW}'source ~/.bashrc'${NC} (或 ~/.zshrc) 来加载新的环境变量。"
echo "2. 进入后端目录安装依赖: ${YELLOW}cd backend && go mod tidy${NC}"
echo "3. 进入前端目录安装依赖: ${YELLOW}cd ../frontend && pnpm install${NC}"
echo "4. 启动后端服务: 在 'backend' 目录运行 ${YELLOW}go run main.go${NC}"
echo "5. 启动前端服务: 在 'frontend' 目录运行 ${YELLOW}pnpm dev${NC}"
echo "--------------------"
echo ""