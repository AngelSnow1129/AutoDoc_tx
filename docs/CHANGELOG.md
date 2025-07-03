# 更新日志

## 版本 0.1.0 - (2025-07-02)

### ✨ 新功能

- **引入自动化开发容器 (`.devcontainer`)**
  - 使用 Docker Compose 集成了 Go, Vue, MySQL, 和 Redis 的全栈开发环境。
  - 创建了 `Dockerfile`，基于官方 Go 镜像，并增加了 Node.js (v20), pnpm, Vue CLI, Zsh, Oh My Zsh, 和 GitHub CLI 等开发工具。
  - 编写了 `devcontainer.json`，预装了 Go, Vue, Docker, Git, 数据库客户端等一系列提高生产力的 VS Code 插件。

- **实现数据库自动化初始化**
  - 添加了 `init.sql` 脚本，在 MySQL 容器首次启动时自动创建数据库 (`myapp_dev`)。
  - 在初始化脚本中自动创建了一个拥有完整权限的管理员用户 (`app_admin`)，并创建了初始的 `users` 表。

- **增强了环境配置和安全性**
  - 引入了 `.env` 文件来管理所有环境变量（如数据库密码），将敏感配置与代码分离。
  - 提供了 `.env.example` 作为配置模板。

- **提升了“开箱即用”体验**
- 在 `devcontainer.json` 中配置了 `postCreateCommand`，容器首次创建后会自动安装 Go 和 Node.js 的依赖项，无需手动操作。

## 版本 0.1.1 - (2025-07-03)

### 📝 文档

- **分析并校验 `.devcontainer/devcontainer.json` 配置**
  - 文件结构和内容无误，字段配置合理，插件 ID 正确。
  - 唯一注意点是文件包含注释，标准 JSON 语法不支持注释，但 VS Code Remote Containers 支持带注释的 JSON（JSONC）。
  - 如需兼容严格 JSON 工具，建议移除注释或将文件后缀改为 `.jsonc`。
  - 无需其他修改。
