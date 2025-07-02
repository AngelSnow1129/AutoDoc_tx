# 使用官方的 Go 语言镜像作为基础
# 选择一个较新的版本以获得最新的语言特性和安全更新
FROM golang:1.22-bookworm

# 定义一些参数，方便后续修改
ARG NODE_VERSION="20"
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# 安装必要的系统依赖、常用工具和 Git
# - git: 版本控制
# - curl, wget: 下载工具
# - zsh: 更强大的 shell
# - sudo: 权限管理
# - procps, lsof: 进程查看工具
# - apt-transport-https, ca-certificates, gnupg: 用于添加外部软件源
# - build-essential: C/C++ 编译工具链，很多 Node 模块编译时需要
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends git curl wget zsh sudo procps lsof apt-transport-https ca-certificates gnupg build-essential

# 创建一个非 root 用户，并赋予 sudo 权限，这是一种安全最佳实践
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd -s /bin/zsh --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# 安装 GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update \
    && apt-get install -y gh

# 切换到新创建的用户
USER $USERNAME

# 安装 nvm (Node Version Manager) 和 Node.js
# 这允许我们轻松管理 Node.js 版本，对于前端开发非常重要
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
ENV NVM_DIR=/home/$USERNAME/.nvm
RUN . "$NVM_DIR/nvm.sh" && nvm install ${NODE_VERSION} \
    && nvm alias default ${NODE_VERSION} \
    && nvm use default

# 将 nvm 的路径添加到 shell 配置文件中，确保每次登录都能使用
ENV PATH="/home/${USERNAME}/.nvm/versions/node/v${NODE_VERSION}/bin:${PATH}"

# 安装 Vue CLI 和 pnpm，pnpm 是一个更高效的包管理器
RUN npm install -g @vue/cli pnpm

# 安装 Oh My Zsh，提升终端使用体验
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

# 清理 apt 缓存，减小镜像体积
USER root
RUN apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# 切换回非 root 用户
USER $USERNAME

# 设置工作目录
WORKDIR /workspace

# 设置默认的 shell
CMD [ "zsh" ]
