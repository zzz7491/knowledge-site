import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: '我的知识库',
  tagline: '知识付费分享平台',
  favicon: 'img/favicon.ico',

  url: 'https://aidongcheng.com',
  baseUrl: '/',

  organizationName: 'lsv3255',
  projectName: 'knowledge-site',

  onBrokenLinks: 'throw',
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
          editUrl: 'https://github.com/lsv3255/knowledge-site/tree/main/',
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
              label: '付费知识',
              to: '/docs/付费知识',
            },
            {
              label: '技术指南',
              to: '/docs/技术指南',
            },
          ],
        },
        {
          title: '关于',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/lsv3255',
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