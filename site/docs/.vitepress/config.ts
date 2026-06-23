import { defineConfig } from 'vitepress'

const isDev = process.env.NODE_ENV === 'development'

export default defineConfig({
  title: 'CyAnalyst',
  description: 'A股智能投研 · 数据驱动的市场分析与交易策略',
  lang: 'zh-CN',
  base: isDev ? '/' : '/cyanalyst/',
  lastUpdated: true,
  cleanUrls: true,
  ignoreDeadLinks: [
    /\.docx$/,
    /\.pdf$/,
    /\.xlsx$/,
  ],

  head: [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/logo.svg' }],
    ['meta', { name: 'theme-color', content: '#dc2626' }],
    ['meta', { name: 'viewport', content: 'width=device-width, initial-scale=1.0' }],
  ],

  themeConfig: {
    logo: '/logo.svg',
    search: {
      provider: 'local',
      options: {
        translations: {
          button: { buttonText: '搜索研报', buttonAriaLabel: '搜索研报' },
          modal: {
            noResultsText: '未找到相关结果',
            resetButtonTitle: '清除查询',
            footer: { selectText: '选择', navigateText: '切换', closeText: '关闭' }
          }
        }
      }
    },

    nav: [
      { text: '首页', link: '/' },
      { text: '每日简报', link: '/research/daily/' },
      { text: '周度研报', link: '/research/weekly/' },
      { text: '专题分析', link: '/research/special/' },
      { text: '关于', link: '/about' },
    ],

    sidebar: {
      '/research/daily/': [
        {
          text: '每日简报',
          items: [
            { text: '最新简报', link: '/research/daily/' },
            { text: '历史归档', link: '/research/daily/archive' },
          ]
        }
      ],
      '/research/weekly/': [
        {
          text: '周度研报',
          items: [
            { text: '本周研报', link: '/research/weekly/' },
            { text: '历史研报', link: '/research/weekly/archive' },
          ]
        }
      ],
      '/research/special/': [
        {
          text: '专题分析',
          items: [
            { text: '全部专题', link: '/research/special/' },
          ]
        }
      ],
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/YLchen22/cyanalyst' }
    ],

    footer: {
      message: '数据来源：东方财富 · 腾讯财经 · 公开市场数据',
      copyright: 'Copyright © 2026 CyAnalyst. 仅供参考，不构成投资建议。'
    },

    docFooter: {
      prev: '上一篇',
      next: '下一篇'
    },

    lastUpdated: {
      text: '最后更新于',
      formatOptions: { dateStyle: 'full', timeStyle: 'medium' }
    },

    outline: {
      level: [2, 3],
      label: '页面导航'
    }
  }
})
