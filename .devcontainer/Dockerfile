# 使用微软官方提供的、预装了常用工具的基础镜像
# 更多信息: https://github.com/devcontainers/images/tree/main/src/base-ubuntu
FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

# [可选] 安装 Oh My Zsh 和配置 Zsh 为默认 Shell，提供更好的终端体验
# 如果不需要可以注释掉此段
ARG INSTALL_ZSH="true"
COPY library-scripts/zsh-debian.sh /tmp/
RUN if [ "${INSTALL_ZSH}" = "true" ]; then \
    apt-get update && export DEBIAN_FRONTEND=noninteractive && apt-get -y install curl git && \
    /bin/bash /tmp/zsh-debian.sh --skip-oh-my-zsh-from-root --zsh-path /bin/zsh --install-in-user-group vscode; \
    fi

# 安装 Go 语言环境
ARG GO_VERSION="1.21"
RUN curl -fsSL "https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz" | tar -C /usr/local -xz
ENV PATH=$PATH:/usr/local/go/bin

# 安装 Node.js, pnpm (用于 Vue/前端)
ARG NODE_VERSION="18"
RUN su vscode -c "source /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} && nvm alias default ${NODE_VERSION}"
# 安装 pnpm
RUN su vscode -c "source /usr/local/share/nvm/nvm.sh && npm install -g pnpm"

# [可选] 安装其他系统依赖，例如编译可能需要的 build-essential
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends build-essential

# 清理 apt 缓存
RUN apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# 设置 Go 环境变量
ENV GOPATH=/go
ENV PATH=$GOPATH/bin:$PATH
# 在 vscode 用户下创建 Go 工作目录
RUN mkdir -p "$GOPATH/src" "$GOPATH/bin" && chown -R vscode:vscode "$GOPATH"

