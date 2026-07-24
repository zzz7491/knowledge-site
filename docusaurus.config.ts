import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: '我的知识库',
  tagline: '面向未来的科技知识库',
  favicon: 'img/favicon.ico',

  url: 'https://aidongcheng.com',
  baseUrl: '/',

  organizationName: 'zzz7491',
  projectName: 'knowledge-site',

  onBrokenLinks: 'warn',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'zh-Hans',
    locales: ['zh-Hans'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          editUrl: 'https://github.com/zzz7491/knowledge-site/tree/main/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/docusaurus-social-card.jpg',
    navbar: {
      title: '我的知识库',
      logo: {
        alt: '我的知识库',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'mainSidebar',
          position: 'left',
          label: '知识库',
        },
        {
          to: '/admin',
          label: '管理后台',
          position: 'right',
        },
        {
          to: '/login',
          label: '登录',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: '知识库',
          items: [
            {
              label: '网站介绍',
              to: '/docs/intro',
            },
            {
              label: '每日更新',
              to: '/docs/每日更新/2026-07-24-快报',
            },
          ],
        },
        {
          title: '关于',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/zzz7491',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} 我的知识库. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
