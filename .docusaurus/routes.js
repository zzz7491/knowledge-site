import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/admin',
    component: ComponentCreator('/admin', '96c'),
    exact: true
  },
  {
    path: '/login',
    component: ComponentCreator('/login', 'f20'),
    exact: true
  },
  {
    path: '/markdown-page',
    component: ComponentCreator('/markdown-page', '53a'),
    exact: true
  },
  {
    path: '/docs',
    component: ComponentCreator('/docs', '430'),
    routes: [
      {
        path: '/docs',
        component: ComponentCreator('/docs', 'fb1'),
        routes: [
          {
            path: '/docs',
            component: ComponentCreator('/docs', '7d2'),
            routes: [
              {
                path: '/docs/测试下载',
                component: ComponentCreator('/docs/测试下载', 'c57'),
                exact: true
              },
              {
                path: '/docs/付费知识/示例文章',
                component: ComponentCreator('/docs/付费知识/示例文章', '4e8'),
                exact: true,
                sidebar: "mainSidebar"
              },
              {
                path: '/docs/技术指南/入门教程',
                component: ComponentCreator('/docs/技术指南/入门教程', '213'),
                exact: true,
                sidebar: "mainSidebar"
              },
              {
                path: '/docs/每日更新/2026-06-27',
                component: ComponentCreator('/docs/每日更新/2026-06-27', '74f'),
                exact: true,
                sidebar: "mainSidebar"
              },
              {
                path: '/docs/dev-guides/ai-dev-paradigm',
                component: ComponentCreator('/docs/dev-guides/ai-dev-paradigm', '416'),
                exact: true
              },
              {
                path: '/docs/dev-guides/cloudflare-setup',
                component: ComponentCreator('/docs/dev-guides/cloudflare-setup', '95d'),
                exact: true
              },
              {
                path: '/docs/dev-guides/setup-guide',
                component: ComponentCreator('/docs/dev-guides/setup-guide', '253'),
                exact: true
              },
              {
                path: '/docs/intro',
                component: ComponentCreator('/docs/intro', '38d'),
                exact: true,
                sidebar: "mainSidebar"
              },
              {
                path: '/docs/paid-knowledge/ai-agent-2026',
                component: ComponentCreator('/docs/paid-knowledge/ai-agent-2026', '2f0'),
                exact: true
              },
              {
                path: '/docs/paid-knowledge/first-article',
                component: ComponentCreator('/docs/paid-knowledge/first-article', '6a3'),
                exact: true
              },
              {
                path: '/docs/paid-knowledge/future-tech',
                component: ComponentCreator('/docs/paid-knowledge/future-tech', '566'),
                exact: true
              },
              {
                path: '/docs/tutorial-basics/congratulations',
                component: ComponentCreator('/docs/tutorial-basics/congratulations', 'fe2'),
                exact: true
              },
              {
                path: '/docs/tutorial-basics/create-a-blog-post',
                component: ComponentCreator('/docs/tutorial-basics/create-a-blog-post', 'eef'),
                exact: true
              },
              {
                path: '/docs/tutorial-basics/create-a-document',
                component: ComponentCreator('/docs/tutorial-basics/create-a-document', 'e00'),
                exact: true
              },
              {
                path: '/docs/tutorial-basics/create-a-page',
                component: ComponentCreator('/docs/tutorial-basics/create-a-page', '660'),
                exact: true
              },
              {
                path: '/docs/tutorial-basics/deploy-your-site',
                component: ComponentCreator('/docs/tutorial-basics/deploy-your-site', '19f'),
                exact: true
              },
              {
                path: '/docs/tutorial-basics/markdown-features',
                component: ComponentCreator('/docs/tutorial-basics/markdown-features', '272'),
                exact: true
              },
              {
                path: '/docs/tutorial-extras/manage-docs-versions',
                component: ComponentCreator('/docs/tutorial-extras/manage-docs-versions', '764'),
                exact: true
              },
              {
                path: '/docs/tutorial-extras/translate-your-site',
                component: ComponentCreator('/docs/tutorial-extras/translate-your-site', '898'),
                exact: true
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '/',
    component: ComponentCreator('/', '2e1'),
    exact: true
  },
  {
    path: '/',
    component: ComponentCreator('/', 'e5f'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
