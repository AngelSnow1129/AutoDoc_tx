# 更新日志

## 版本 0.1.3 - (2025-07-07)

### ♻️ 重构

- **重构：迁移 `tencent_docs_scraper` 到 `docs_scraper` 并更新依赖**
  - 将抓取逻辑从 `tencent_docs_scraper` 迁移到 `docs_scraper`。
  - 更新了二进制文件并添加了 `auth_state.json`。
  - 添加了 `docs/page_source.html`。
  - 修改了 `prompts.log`。

## 版本 0.1.2 - (2025-07-07)

### ✨ 新功能

- **新增文档抓取模块与开发工具环境配置**
  - 此提交引入了新的文档抓取工具 (`tencent_docs_scraper2`)，并在 `tools/` 目录下建立了结构化的开发环境。
  - 主要变更包括：
    - **抓取模块更新**：移除了旧的 `Pro2` 模块，替换为 `tencent_docs_scraper2`，并包含了其 Python 依赖和单元测试。集成了 `chrome-headless-shell` 和 `chromedriver` 二进制文件，用于无头浏览器操作。
    - **开发工具集成**：新增 `tools/` 目录，包含 Go 后端项目、前端项目以及相关的配置文件（`.editorconfig`, `.env`, `.vscode/settings.json`）。
    - **环境配置更新**：更新了 `.devcontainer/devcontainer.json` 和 `.env` 以支持新的工具和抓取模块。
    - **其他**：新增 `.kilocode/mcp.json`，并对 `init_gemini.sh` 和 `docs/population_data.csv` 进行了小幅更新。

## 版本 0.1.1 - (2025-07-03)

### 📝 文档

- **分析并校验 `.devcontainer/devcontainer.json` 配置**
  - 文件结构和内容无误，字段配置合理，插件 ID 正确。
  - 唯一注意点是文件包含注释，标准 JSON 语法不支持注释，但 VS Code Remote Containers 支持带注释的 JSON（JSONC）。
  - 如需兼容严格 JSON 工具，建议移除注释或将文件后缀改为 `.jsonc`。
  - 无需其他修改。

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