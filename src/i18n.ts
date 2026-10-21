// 栏目定义：照搬现有站点结构，中英双语
export const CATEGORIES = {
  seo: { zh: 'SEO', en: 'SEO' },
  geo: { zh: 'GEO', en: 'GEO' },
  'independent-site': { zh: '独立站', en: 'Independent Site' },
  ads: { zh: '广告投放', en: 'Paid Ads' },
  social: { zh: '社媒运营', en: 'Social Media' },
  cases: { zh: '案例复盘', en: 'Case Studies' },
} as const;

export type CategorySlug = keyof typeof CATEGORIES;

export const UI = {
  zh: {
    home: '首页',
    articles: '全部文章',
    about: '关于',
    featured: '精选文章',
    latest: '最新文章',
    minRead: '分钟',
    viewAll: '查看全部文章',
    language: 'EN',
    allCategories: '全部栏目',
    archiveTitle: '全部文章',
    updated: '更新于',
    related: '相关阅读',
    backToList: '返回文章列表',
  },
  en: {
    home: 'Home',
    articles: 'All Articles',
    about: 'About',
    featured: 'Featured',
    latest: 'Latest',
    minRead: 'min read',
    viewAll: 'View all articles',
    language: '中文',
    allCategories: 'All Topics',
    archiveTitle: 'All Articles',
    updated: 'Updated',
    related: 'Related reading',
    backToList: 'Back to articles',
  },
} as const;

export type Lang = keyof typeof UI;
