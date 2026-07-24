# Knowledge System

一个面向未来的科技知识库，使用 [Docusaurus](https://docusaurus.io/) 构建。

## 本地开发

```bash
npm ci
npm run start
```

## 构建检查

```bash
npm run build
```

构建产物输出到 `build/`，Cloudflare Pages 的输出目录也设置为 `build`。

## 发布

仓库包含两条自动化链路：

- `科技前沿自动更新`：定时生成每日科技快报并提交到 `docs/每日更新/`。
- `发布知识库到 Cloudflare Pages`：`main` 变化后构建站点；配置 Cloudflare 凭据后自动发布。

Cloudflare Pages 项目设置应保持以下值：

- Production branch：`main`
- Build command：`npm run build`
- Build output directory：`build`
- Root directory：仓库根目录

发布工作流需要两个 GitHub Actions Secrets：

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`
