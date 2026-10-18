# Knowledge System · 科技知识库

一个持续更新的科技知识库站点，使用 [Docusaurus](https://docusaurus.io/) 构建，托管于 Cloudflare Pages。内容以技术指南与教程为骨架，并由自动化流水线每日生成「科技快报」增量更新。

## 内容栏目

- **技术指南**（`docs/技术指南`、`docs/dev-guides`）：开发与基础设施相关的指南文章；
- **教程**（`docs/tutorial-basics`、`docs/tutorial-extras`）：基础与进阶教程；
- **付费知识**（`docs/付费知识`、`docs/paid-knowledge`）：付费内容专区；
- **每日更新**（`docs/每日更新`）：每日科技快报，由自动化工作流定时生成并提交。

## 自动化链路

仓库包含两条 GitHub Actions 链路：

- **科技前沿自动更新**：定时生成每日科技快报，提交到 `docs/每日更新/`；
- **发布知识库到 Cloudflare Pages**：`main` 分支变化后自动构建站点，配置 Cloudflare 凭据后自动发布。

## 本地开发

```bash
npm ci
npm run start     # 本地开发服务器
npm run build     # 构建检查，产物输出到 build/
```

## 发布设置

Cloudflare Pages 项目设置应保持以下值：

- Production branch：`main`
- Build command：`npm run build`
- Build output directory：`build`
- Root directory：仓库根目录

发布工作流需要两个 GitHub Actions Secrets：

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`

## 目录

```
├── docs/            # 知识库内容（技术指南 / 教程 / 付费知识 / 每日更新）
├── src/             # 站点自定义页面与组件
├── static/          # 静态资源
├── functions/       # Cloudflare Pages Functions
├── scripts/         # 内容生成与维护脚本
├── docusaurus.config.ts  # 站点配置
└── sidebars.ts      # 侧边栏结构
```
