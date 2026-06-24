# 📊 智能投研资料库 — 项目总体规划

> 最后更新：2026-06-24

---

## 一、项目概述

构建一个**自动化投研工作流**，核心链路：

```
数据采集 → AI 分析 → 内容生成 → 网站发布 → 邮件推送
```

**目标用户**：你自己（A股交易辅助，全球市场作为宏观参考）

---

## 二、架构设计

### 2.1 总体架构

```
┌─────────────────────────────────────────────────────┐
│                    定时调度层                          │
│           WorkBuddy Automations (内置)                │
│   盘前 8:30 触发 / 盘后 15:30 触发 / 周末研报          │
└────────┬──────────┬──────────┬──────────┬───────────┘
         │          │          │          │
    ┌────▼───┐ ┌───▼────┐ ┌───▼────┐ ┌───▼──────┐
    │数据采集 │ │AI 分析 │ │内容生成 │ │邮件推送   │
    │Skills  │ │Agent   │ │Markdown│ │Resend API│
    └────┬───┘ └───┬────┘ └───┬────┘ └───┬──────┘
         │         │          │          │
         └─────────┼──────────┼──────────┘
                   │          │
              ┌────▼──────────▼────┐
              │   资料库网站        │
              │  Astro 静态站点     │
              │  托管: GitHub Pages │
              └────────┬───────────┘
                       │
              ┌────────▼───────────┐
              │  Cloudflare R2     │
              │  研报文件存储        │
              │  (.html)           │
              └────────────────────┘
```

**核心分离原则**：
- **GitHub 仓库**：只存储研报元数据（标题、日期、标签、摘要）—— Markdown 仅含 frontmatter + 一句描述，不含正文。纯文本，Git 友好，版本可控
- **GitHub Pages**：渲染元数据为 HTML 页面（首页、导航、索引、研报卡片）—— 体积小，加载快
- **Cloudflare R2**：存储完整的研报 HTML 文件 —— 浏览器原生渲染，无需阅读器，支持富文本和图表

**研报格式**：选择 **HTML**（而非 .docx / .pdf），理由：
- Agent 天生擅长编写 HTML（比 .docx 更可靠、更可控）
- 浏览器原生渲染，无需任何插件或阅读器
- 支持富文本、表格、图表（SVG）、涨红跌绿样式，表现力不输 PDF
- 用户如需离线，可浏览器另存为或打印为 PDF
- 文件体积小（纯文本 HTML），R2 存储更省

**用户访问链路**：
```
首页/列表页 → 研报卡片（标题 + 摘要）→ 点击 → R2 直接在浏览器打开 HTML 研报
```
- 研报卡片直接链接到 R2 上的 HTML 文件，无需中间详情页
- 用户体验：点一下，研报就在眼前（原生浏览器渲染）

### 2.2 模块划分

| 模块 | 职责 | 技术方案 |
|------|------|----------|
| **资料库网站** | 文档挂载、简报展示、搜索 | Astro 5.x + Tailwind CSS 4.x + Pagefind / GitHub Pages 部署 |
| **研报文件存储** | HTML 研报托管与分发 | Cloudflare R2 对象存储 |
| **数据采集** | A股行情、全球指数、新闻 | 已有 Skills 全家桶 |
| **AI 分析** | 多智能体研报、标的筛选 | ai-stock-researcher + 定制 Agent |
| **内容生成** | 盘前/盘后简报、周度研报 | HTML 生成 → R2 上传 → 网站发布 |
| **邮件分发** | 精选标的 + 策略推送 | Resend API (免费) |
| **定时调度** | 全流程自动化 | WorkBuddy Automations |

---

## 三、技术选型详解

### 3.1 资料库网站

**方案：Astro**

| 维度 | Astro | VitePress | Next.js | Docusaurus |
|------|-------|-----------|---------|------------|
| 构建速度 | ⚡ 极快 | ⚡ 极快 | 中等 | 较慢 |
| Markdown 原生支持 | ⭐ Content Collections | ⭐ 最佳 | 需配置 | ⭐ 优秀 |
| 零 JS by default | ✅ 默认零 JS | ✅ 极少 | ❌ 需要 | ❌ React 全载 |
| 搜索 | Pagefind（构建时索引） | 内置全文搜索 | 需 Algolia | 内置/ Algolia |
| 组件灵活性 | ⭐ 任意框架组件（React/Vue/Svelte） | 仅 Vue | React 生态 | React 生态 |
| 学习成本 | 低 | 低 | 中高 | 中 |
| 部署体积 | 极小 | 极小 | 中等 | 较大 |
| 适合场景 | **内容站点 + 灵活组件** | 纯文档站点 | 复杂 Web 应用 | 文档站点 |

**结论**：Astro 最适合「资料库 + 灵活展示」定位。Content Collections 提供 schema 校验的 Markdown 内容管理，零 JS by default 保证极致性能，Pagefind 提供构建时全文搜索（中文友好），同时支持按需引入任意框架组件用于交互增强。

**网站托管方案：GitHub Pages**

| 平台 | 用途 | 免费额度 | 国内访问 | 构建限制 | 自定义域名 |
|------|------|----------|---------|----------|------------|
| **GitHub Pages** | 网站托管 | 100GB带宽/月 | ⭐ 较差 | 10min/次 | ✅ |
| Cloudflare Pages | （备选）网站托管 | 无限带宽 | ⭐⭐⭐ 较好 | 20min/次 | ✅ |
| Vercel | （备选）网站托管 | 100GB带宽/月 | ⭐⭐ 一般 | 45min/天 | ✅ |

> 选择 GitHub Pages 是因为与 GitHub 仓库原生集成，push 即部署，零配置（`.github/workflows/deploy.yml` 已就绪）。Markdown 页面体积极小，100GB/月带宽完全够用。国内访问速度不理想时，可后续接入自定义域名 + CDN 优化。

### 3.2 Cloudflare R2 对象存储 — 研报 HTML 文件

**用途**：存储由 AI Agent 生成的 `.html` 研报文件，网站页面通过 URL 直接链接。

**存储路径规划**：
```
R2 Bucket: cyanalyst-files
├── research/daily/          # 每日简报
│   ├── 2026-06-23-morning.html
│   └── 2026-06-22-evening.html
├── research/weekly/         # 周度研报
│   └── 2026-W26.html
└── research/special/        # 专题分析
    └── 2026-06-20-semiconductor.html
```

**访问方式**：通过 R2 公共开发 URL（`<bucket>.r2.dev`）或自定义域名直接访问，浏览器原生渲染 HTML。

**免费额度**：
| 项目 | 免费额度 |
|------|---------|
| 存储 | 10 GB |
| Class A 操作（写/列表） | 100 万次/月 |
| Class B 操作（读） | 1000 万次/月 |
| 出口流量 | **免费**（零出口流量费） |

> R2 零出口流量费是其核心优势。HTML 纯文本体积极小（每篇约 20-50 KB），10GB 可存约 20-50 万篇，基本无限。且出口流量免费，用户访问不产生任何费用。

**与 GitHub 仓库的关系**：仓库中只保留 Markdown 元数据 + 网站代码。完整的 HTML 研报文件在 R2。生成流程：`AI Agent 生成 HTML` → 临时目录 → `upload_to_r2.py` 上传 R2 → Markdown 元数据中引用 R2 URL。

### 3.3 数据采集层 — 已有资源盘点

目前你已经安装了非常全面的数据 Skills，基本覆盖所有需求：

| Skill | 覆盖范围 | 用途 |
|-------|---------|------|
| **a-stock-data** | A股全栈（行情/研报/资金/新闻/龙虎榜） | 核心数据源 |
| **ai-stock-researcher** | 多智能体分析（7位AI分析师） | 核心分析引擎 |
| **eastmoney-intraday** | A股日内分时数据 | 盘中监控 |
| **westockdata** | A股/港股/美股 财务+技术指标 | 跨市场对比 |
| **tencent-finance** | A股/港股/美股/期货 实时行情 | 实时报价 |
| **baidu-search** | 百度搜索 | 资讯搜索 |
| **web-access** | 浏览器自动化 | 网页抓取 |
| **neodata-financial-search** | 自然语言金融搜索 | 快速查询 |

**你不需要额外购买任何数据服务。**

### 3.4 邮件发送

**推荐：Resend（免费层完全够用）**

| 方案 | 月免费量 | 日限额 | 你的用量预估 |
|------|---------|--------|------------|
| Resend Free | 3,000 封 | 100 封/天 | ~30封/天（你自己一个人收） |

- 每天 2 封（盘前+盘后简报）+ 周末研报 = 约 60 封/月
- 免费层的 3,000 封/月绰绰有余
- API 极简，`resend.emails.send()` 一行搞定
- 如果未来要群发给朋友，Pro 方案 $20/月 给 50,000 封

### 3.5 定时调度

**WorkBuddy 内置 Automations**：无需额外工具，直接在项目内设置定时任务。

---

## 四、存储策略分析 ⭐

### 4.1 Markdown 元数据 — 存在 GitHub 仓库

**完全不用担心超限。**

| 项目 | 数值 |
|------|------|
| 一个 Markdown 元数据文件大小 | ~500 B - 1 KB（仅 frontmatter + 摘要） |
| 每天生成 5 篇研报元数据 | 约 5 KB/天 |
| 一年元数据总大小 | 约 **1.8 MB** |
| GitHub Pages 站点限制 | **1 GB**（够存 ~550 年） |
| GitHub 仓库 .git 限制 | **10 GB**（推荐上限） |
| 单个文件大小限制 | **100 MB** |

> 研报 HTML 正文全部在 R2，仓库只存元数据，体积极其微小。即使每天写 100 篇元数据，连写 10 年也远达不到限制。Markdown 纯文本在 Git 中还会被进一步压缩。

### 4.2 HTML 研报文件 — 存在 Cloudflare R2

研报 HTML 文件**不应进入 Git 仓库**，原因：
- 体积持续增长，但属于纯内容数据
- 应由 Agent 自动生成，不应手动编辑
- 版本管理无意义（内容不可 diff）

**方案**：
1. AI Agent 生成完整的 HTML 研报到临时目录
2. `upload_to_r2.py` 上传到 R2 bucket（自动设置 `Content-Type: text/html`）
3. Markdown 元数据文件中引用 R2 公共 URL
4. `.gitignore` 排除 `scripts/output/` 等临时目录

### 4.3 注意事项

- ⚠️ **图表**：建议在 HTML 研报中使用 SVG（矢量，极小程序化），也可内嵌 Canvas/Chart.js
- ⚠️ **图片**：若需截图，可上传至 R2 同一 bucket 的 `assets/` 目录，HTML 中相对路径引用
- ✅ **.gitignore**：把 `node_modules/`、`.cache/`、构建产物、研报临时文件加入忽略

---

## 五、成本分析

| 项目 | 方案 | 月费 |
|------|------|------|
| 网站托管 | GitHub Pages | ¥0 |
| 研报文件存储 | Cloudflare R2 (免费层) | ¥0 |
| 域名（可选） | Cloudflare Registrar | ~¥50/年 |
| 数据源 | 已有 Skills | ¥0 |
| AI 分析 | WorkBuddy 订阅 | ¥0（已含） |
| 邮件发送 | Resend Free | ¥0 |
| 代码托管 | GitHub Free | ¥0 |
| **合计** | | **¥0/月** |

> **结论：一毛钱都不用花。** 你现有的 WorkBuddy 订阅 + 已安装的 Skills 已经覆盖了所有需求。

---

## 六、目录结构设计

```
cyanalyst/
├── astro.config.mjs                # Astro 配置（site, base=/cyanalyst/）
├── package.json                    # Astro + Tailwind + Pagefind 依赖
├── tsconfig.json
├── PROJECT_PLAN.md
├── AGENTS.md
├── develop.md                      # 开发日志
├── README.md
├── .gitignore
├── .github/
│   └── workflows/
│       ├── deploy.yml              # GitHub Pages 部署（已就绪）
│       └── generate-reports.yml    # 研报生成 + HTML 上传 R2（待建）
├── scripts/
│   ├── generate_research.py       # 研报 HTML 生成（Agent 主入口，待建）
│   ├── upload_to_r2.py            # R2 上传脚本（已就绪）
│   └── output/                    # 临时输出（gitignored）
├── public/
│   └── favicon.svg
├── src/
│   ├── content.config.ts           # Content Collections schema（daily/weekly/special）
│   ├── styles/
│   │   └── global.css              # Tailwind + 自定义 prose 样式 + Pagefind 主题
│   ├── layouts/
│   │   └── BaseLayout.astro
│   ├── components/
│   │   ├── Header.astro            # 导航栏（深色主题）
│   │   ├── Footer.astro
│   │   ├── ResearchCard.astro      # 研报卡片（涨红跌绿配色）
│   │   └── Search.astro            # Pagefind 搜索组件
│   ├── pages/
│   │   ├── index.astro             # 首页
│   │   ├── about.astro             # 关于
│   │   └── research/
│   │       ├── index.astro         # 全部研报（含搜索）
│   │       ├── daily/
│   │       │   ├── index.astro     # 日报列表
│   │       │   └── [...slug].astro # 日报详情（下载链接指向 R2）
│   │       ├── weekly/
│   │       │   ├── index.astro
│   │       │   └── [...slug].astro
│   │       └── special/
│   │           ├── index.astro
│   │           └── [...slug].astro
│   └── content/
│       ├── daily/                  # 日报 Markdown
│       ├── weekly/                 # 周报 Markdown
│       └── special/                # 专题 Markdown
└── .env                            # R2 密钥等（gitignored）
```

**R2 存储结构**：
```
R2 Bucket: cyanalyst-files
├── research/daily/
│   ├── 2026-06-23-morning.html
│   └── 2026-06-22-evening.html
├── research/weekly/
│   └── 2026-W26.html
└── research/special/
    └── 2026-06-20-semiconductor.html
```

---

## 七、实施路线图

### Phase 1：基础设施（第 1-2 天）✅
- [x] 初始化 Astro 项目（Astro 5.x + Tailwind CSS 4.x + Pagefind）
- [x] 配置 GitHub Pages 自动部署（`.github/workflows/deploy.yml` 已就绪）
- [x] 搭建基本网站结构（首页、导航、搜索、研报列表/详情页）
- [x] 创建 Cloudflare R2 bucket（`cyanalyst-files`）
- [x] 配置 R2 公共访问域名（`pub-e042cb137f3f4d9d91009d7a9233dd5b.r2.dev`）
- [x] 编写 `upload_to_r2.py` 上传脚本
- [x] 仓库仅存元数据，HTML 研报完全在 R2（架构落地）
- [x] 生成 4 篇示例 HTML 研报并上传至 R2 验证（日报×2 / 周报×1 / 专题×1）
- [x] 网页端研报卡片直接链接 R2 HTML，浏览器原生渲染，无需中间详情页
- [ ] 编写 HTML 研报生成 Agent / Prompt 模板
- [ ] 配置 Resend API Key

### Phase 2：数据管道（第 3-4 天）
- [ ] 编写盘后数据采集脚本（调用已有 Skills）
- [ ] 编写 AI 分析 Prompt 模板（含 HTML 排版要求）
- [ ] 实现「采集 → 分析 → 生成 HTML → 上传 R2 → 更新 Web 元数据」完整链路
- [ ] 端到端测试：生成一篇完整 HTML 研报并在浏览器中验证

### Phase 3：自动化（第 5-6 天）
- [ ] 配置 WorkBuddy Automation：工作日盘前 8:30 触发
- [ ] 配置 WorkBuddy Automation：工作日盘后 15:30 触发
- [ ] 配置 WorkBuddy Automation：周末深度研报
- [ ] 配置邮件自动发送

### Phase 4：优化迭代（持续）
- [ ] 标的池管理与信号跟踪
- [ ] 回测数据整合
- [ ] 自定义分析指标
- [ ] 移动端适配
- [ ] 国内访问 CDN 优化（如需要）

---

## 八、风险与注意事项

| 风险 | 应对 |
|------|------|
| 数据源接口变动 | 多个 Skill 互为备份（东财/腾讯/同花顺） |
| AI 分析质量不稳定 | 人工复核机制，迭代 Prompt |
| 自动发布出错 | 先推送到 staging，确认后再发布 |
| 合规风险 | 邮件仅发自己，研报标注「仅供参考，不构成投资建议」 |
| GitHub Pages 国内访问较慢 | 可考虑后续接入自定义域名 + CDN |
| R2 免费额度用尽 | HTML 体积极小，10GB 存储几乎不可能用尽 |

---

## 九、下一步行动

Phase 1 基础设施已全部完成（含 Cloudflare R2 + 前后端分离架构落地）。接下来需要：

1. **编写 HTML 研报生成 Prompt 模板**（含排版、涨红跌绿、表格、图表等要求）
2. **开发「数据采集 → AI 分析 → 生成 HTML → 上传 R2 → 更新 Web」完整自动化链路**
3. **Resend 邮件推送配置**
4. **WorkBuddy Automations 定时调度设置**
