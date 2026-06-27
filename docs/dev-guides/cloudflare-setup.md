---
id: cloudflare-setup
title: Cloudflare Pages 部署流程
---

# 部署实战

:::tip 提示
使用 Wrangler CLI 部署是最快的方式，不需要手动点击上传。
:::

按照以下步骤操作即可将本地代码推送到云端：

1. 运行 `npm run build` 生成构建文件。
2. 运行 `npx wrangler pages deploy build --project-name knowledge-site`。

:::danger 注意
部署前请务必确认你的 `npm run build` 命令没有报错。
:::