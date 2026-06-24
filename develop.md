# 开发日志

## 2026-06-24: 当前进度汇总

### Phase 1 基础设施 — 全部完成 ✅

| 模块 | 状态 | 备注 |
|------|------|------|
| Astro 5.x 项目骨架 | ✅ | Content Collections + Tailwind CSS 4.x + Pagefind |
| GitHub Pages 部署 | ✅ | peaceiris/actions-gh-pages，base=/cyanalyst/ |
| 网站页面 | ✅ | 首页 / 关于 / 研报列表 / 研报详情（3 类动态路由） |
| Cloudflare R2 Bucket | ✅ | `cyanalyst-files`，公共访问已开启 |
| R2 上传脚本 | ✅ | `scripts/upload_to_r2.py`（boto3 S3 兼容 API） |
| 示例 HTML 研报 | ✅ | 4 篇（日报×2 / 周报×1 / 专题×1），已上传 R2 |
| `src/config.ts` | ✅ | R2 URL 集中管理（`r2Url()` 函数） |
| 研报格式定稿 | ✅ | HTML 格式，Agent 原生生成，浏览器原生渲染 |
| 架构分离 | ✅ | 仓库纯元数据（~1KB/篇），HTML 研报完全在 R2 |

### Phase 2 数据管道 — 待启动

- [ ] HTML 研报生成 Agent / Prompt 模板
- [ ] 盘后数据采集脚本
- [ ] 「采集 → 分析 → 生成 HTML → 上传 R2 → 更新元数据」全链路

### Phase 3 自动化 — 待启动

- [ ] WorkBuddy Automations 定时调度
- [ ] Resend 邮件推送

### 研报内容清单

| # | 分类 | 文件名 | R2 状态 |
|---|------|--------|---------|
| 1 | 日报 | 2026-06-24-morning | ✅ 已上传 |
| 2 | 日报 | 2026-06-23-evening | ✅ 已上传 |
| 3 | 周报 | 2026-06-21-week-25 | ✅ 已上传 |
| 4 | 专题 | 2026-06-15-ai-chips | ✅ 已上传 |

### 下一步

1. 编写 HTML 研报生成的 Prompt 模板（含排版规范、涨红跌绿、表格/图表等）
2. 实现自动化研报生成 + 上传链路
3. Resend 邮件配置

---

## 2026-06-24: 架构升级 — 研报格式从 .docx/.pdf 切换为 .html

### 决策背景
原方案研报用 .docx + .pdf 双格式，用户访问时有两个按钮（在线阅读 PDF / 下载 DOCX）。经过讨论，决定全面切换为 **HTML 格式**。

### 核心理由
1. **Agent 友好**：Agent 天生擅长编写 HTML，比生成 .docx（需 python-docx 拼装）更可靠
2. **浏览器原生渲染**：HTML 无需阅读器，不支持格式转换，点开即看
3. **丰富表现力**：支持富文本、表格、SVG 图表、涨红跌绿样式，完全不输 PDF
4. **体积极小**：纯文本 HTML 每篇 ~20-50 KB（vs .docx 约 100-200 KB）
5. **自动化友好**：Agent 一步到位生成 HTML → 上传 R2 → 更新元数据，无需 LibreOffice 转换

### 对项目的影响
- **仓库更轻**：Markdown 元数据从 ~30KB/篇 缩小到 ~1KB/篇（仅 frontmatter + 简介）
- **R2 更省**：HTML 比 .docx 小约 3-5 倍，10GB 免费额度几乎永久用不完
- **详情页简化**：无需中间详情页，卡片直接链到 R2 HTML，用户点开即看
- **无需 PDF 转换**：不再需要 LibreOffice headless 或 docx2pdf

### 文档同步
- PROJECT_PLAN.md 已全面更新：架构图、存储策略、R2 路径、实施路线图、风险表
- 所有 .docx/.pdf 引用已替换为 .html
- 删除了 PDF 转换相关的所有 TODO

---

## 2026-06-24: 架构落地 — 仓库仅存元数据，R2 存文件（旧版 .docx 方案，已废弃）

### 架构确认
彻底贯彻「仓库纯文本、R2 存文件」的分离原则：
- **GitHub 仓库**：Markdown 文件仅含 frontmatter（title, date, tags, summary）+ 一句占位描述，不再包含完整研报正文
- **Cloudflare R2**：存储完整的 .docx / .pdf 研报文件
- **详情页**：不再渲染 Markdown 正文（移除 `<Content />`），改为元数据展示 + 突出的 R2 行动按钮（在线阅读 PDF / 下载 DOCX）
- **用户访问路径**：列表卡片 → 详情页（元数据 + 按钮） → 点击 → R2 直接打开文件

### 完成的变更
1. **生成 3 篇示例 .docx 研报**（`scripts/generate_sample_docs.py`）
   - 从原始 Markdown 正文转换为格式化的 Word 文档（含表格、标题层级、涨红跌绿配色）
   - 输出到 `scripts/output/research/{daily,weekly,special}/`
2. **上传 R2 验证通过**
   - 4 个文件全部成功上传到 `cyanalyst-files` bucket
   - 公共 URL 直接访问可下载（HTTP 200 + 正确 Content-Type）
3. **前后端分离成果验证**
   - `https://pub-e042cb137f3f4d9d91009d7a9233dd5b.r2.dev/research/daily/2026-06-24-morning.docx` ✅
   - `https://pub-e042cb137f3f4d9d91009d7a9233dd5b.r2.dev/research/weekly/2026-06-21-week-25.docx` ✅
   - `https://pub-e042cb137f3f4d9d91009d7a9233dd5b.r2.dev/research/special/2026-06-15-ai-chips.docx` ✅
4. **所有 Markdown 内容文件瘦身**
   - `daily/`, `weekly/`, `special/` 下共 4 个 .md 文件全部精简为仅含 frontmatter + 一句占位
5. **PROJECT_PLAN.md 更新**
   - 核心分离原则补充了「仓库只存元数据不含正文」的明确描述
   - 新增用户访问链路说明

### 构建结果
- `npx astro build` 通过，10 个页面全部生成，无错误
- 详情页 HTML 中 R2 链接正确嵌入

### 当前状态
| 模块 | 状态 | 备注 |
|------|------|------|
| 网站骨架 | ✅ 完成 | Astro 5.x + Tailwind CSS 4.x + Pagefind |
| GitHub Pages 部署 | ✅ 完成 | `.github/workflows/deploy.yml` |
| Cloudflare R2 Bucket | ✅ 完成 | `cyanalyst-files`，公共访问已开启 |
| R2 上传脚本 | ✅ 完成 | `scripts/upload_to_r2.py` |
| 架构设计（前后端分离） | ✅ 完成 | 仓库纯元数据，R2 存 HTML 研报 |
| HTML 研报生成 Agent | ⏳ 待建 | Prompt 模板 + 自动化生成 + 上传 |
| 数据采集 Pipeline | ⏳ 待建 | 盘后数据采集 + AI 分析 + HTML 生成 |
| 定时调度 | ⏳ 待建 | WorkBuddy Automations |
| 邮件推送 | ⏳ 待建 | Resend API |

---

## 2026-06-24: 前端从 VitePress 迁移到 Astro

### 背景
原 VitePress 方案存在数据与展示混杂、Vue 组件硬编码数据、下载链接指向不存在路径等问题。决定推倒重来。

### 技术选型
- **框架**: Astro 5.x（Content Collections 自动管理研报索引）
- **样式**: Tailwind CSS 4.x（@tailwindcss/vite 插件）
- **搜索**: Pagefind（构建时索引，零后端）
- **部署**: GitHub Pages（base: /cyanalyst/）
- **研报文件存储**: Cloudflare R2（.docx/.pdf 不进 Git）

### 项目结构
```
cyanalyst/
├── astro.config.mjs        # Astro 配置，base=/cyanalyst/
├── package.json            # Astro + Tailwind + Pagefind
├── tsconfig.json
├── src/
│   ├── content.config.ts   # 三个内容集合: daily, weekly, special
│   ├── styles/global.css   # Tailwind + 自定义 prose 样式 + Pagefind 主题
│   ├── layouts/BaseLayout.astro
│   ├── components/
│   │   ├── Header.astro    # 导航栏（深色主题）
│   │   ├── Footer.astro
│   │   ├── ResearchCard.astro  # 研报卡片（涨红跌绿配色）
│   │   └── Search.astro    # Pagefind 搜索组件
│   ├── pages/
│   │   ├── index.astro     # 首页（Hero + 分类入口 + 最新研报）
│   │   ├── about.astro     # 关于页面
│   │   └── research/
│   │       ├── index.astro         # 全部研报（含搜索）
│   │       ├── daily/index.astro   # 日报列表
│   │       ├── daily/[...slug].astro   # 日报详情
│   │       ├── weekly/index.astro
│   │       ├── weekly/[...slug].astro
│   │       ├── special/index.astro
│   │       └── special/[...slug].astro
│   └── content/
│       ├── daily/          # 日报 Markdown
│       ├── weekly/         # 周报 Markdown
│       └── special/        # 专题 Markdown
├── public/favicon.svg
└── .github/workflows/deploy.yml  # GitHub Actions 部署
```

### Content Collection Schema
```typescript
{
  title: string,
  date: date,
  tags: string[],     // default: []
  summary: string,    // default: ''
}
```

### 示例内容
- daily: 2026-06-24-morning.md（早盘速览）
- weekly: 2026-06-21-week-25.md（第25周市场回顾）
- special: 2026-06-15-ai-chips.md（AI芯片国产替代专题）

### 设计特点
- 深色导航栏 + 浅色内容区，专业金融风格
- 涨红跌绿配色（--color-up: #dc2626, --color-down: #16a34a）
- 研报卡片：分类徽章颜色区分（日报蓝/周报紫/专题橙）
- R2 下载链接占位: https://r2.cyanalyst.com/{category}/{id}.docx
- Pagefind 搜索：构建时生成索引，中文翻译已配置

### 启动方式
```bash
npm install
npm run dev      # 开发服务器 http://localhost:5173/cyanalyst/
npm run build    # 构建 + Pagefind 索引
npm run preview  # 预览构建结果
```

---

## 2026-06-24: 当前开发进展同步

### 已完成

- **Astro 5.x 项目初始化**（`astro.config.mjs`，base: `/cyanalyst/`）
- **Tailwind CSS 4.x** 样式集成（`@tailwindcss/vite` 插件）
- **Pagefind** 搜索集成（构建时索引，中文翻译已配置）
- **Content Collections** 配置（`src/content.config.ts`，daily / weekly / special 三集合，schema: title, date, tags, summary）
- **网站骨架**：首页（Hero + 分类入口 + 最新研报）、关于页、研报列表页、研报详情页（动态路由 `[...slug]`）
- **组件**：Header（深色导航栏）、Footer、ResearchCard（涨红跌绿配色 + 分类徽章）、Search（Pagefind）
- **3 篇示例内容**：日报（2026-06-24-morning）、周报（2026-06-21-week-25）、专题（2026-06-15-ai-chips）
- **GitHub Actions 部署工作流**（`.github/workflows/deploy.yml`，构建 `dist` → GitHub Pages）
- **PROJECT_PLAN.md 同步更新**：技术栈从 VitePress 更新为 Astro，目录结构和路线图已对齐实际项目

### 待完成

- **Cloudflare R2 bucket 创建**与公共域名配置（`cyanalyst-reports`）
- **`upload_to_r2.py`** 上传脚本编写
- **`generate_docs.py` 输出路径更新**：当前仍指向废弃的 `site/docs/public/research/daily/` 旧路径，需改为 `scripts/output/` 临时目录 + R2 上传
- **数据采集 + AI 分析 Pipeline**：盘后数据采集脚本、AI 分析 Prompt 模板、Markdown 简报生成器
- **WorkBuddy Automations 定时调度**：盘前 8:30 / 盘后 15:30 / 周末深度研报
- **Resend 邮件推送**配置

---

## 2026-06-24: Cloudflare R2 存储开发

### 背景
项目需要将研报二进制文件（.docx/.pdf）存储在 Cloudflare R2 对象存储，与 GitHub Pages 的 Markdown 纯文本内容分离。用户已注册 Cloudflare 免费账户。

### 已完成的自动化开发

1. **`scripts/upload_to_r2.py`** — R2 上传脚本
   - 使用 boto3 S3 兼容 API，endpoint 指向 `{account_id}.r2.cloudflarestorage.com`
   - 支持：单文件上传、目录批量上传、列出 bucket 内容、测试连接
   - 自动根据文件扩展名设置 Content-Type
   - 从 `.env` 文件读取凭据（python-dotenv）
   - CLI 用法：
     ```bash
     python upload_to_r2.py --test                              # 测试连接
     python upload_to_r2.py file.docx research/daily/file.docx  # 上传单文件
     python upload_to_r2.py --dir scripts/output research/      # 批量上传
     python upload_to_r2.py --list research/                    # 列出文件
     ```

2. **`.env.example`** — 环境变量模板
   - 列出 R2_ACCOUNT_ID、R2_ACCESS_KEY_ID、R2_SECRET_ACCESS_KEY、R2_BUCKET_NAME、R2_PUBLIC_URL
   - 包含注释说明每个变量从何处获取

3. **`generate_docs.py` 输出路径更新**
   - 从废弃的 `site/docs/public/research/daily/` 改为 `scripts/output/research/daily/`
   - 临时输出目录由 `.gitignore` 排除

4. **`.gitignore` 更新**
   - 新增 `scripts/output/`（临时输出目录）
   - 新增 `.venv/`（Python 虚拟环境）
   - 新增 `__pycache__/`、`*.pyc`（Python 缓存）

### 需要用户手动操作的步骤

在 Cloudflare Dashboard 中完成以下 3 步：

1. **创建 R2 Bucket**：R2 > Create bucket > 名称 `cyanalyst-reports`
2. **开启公共访问**：bucket 设置 > Settings > Public access > 允许 r2.dev 访问
3. **创建 API Token**：R2 > Manage R2 API Tokens > Create API Token
   - 权限选择：Object Read & Write
   - 创建后会获得 Access Key ID 和 Secret Access Key
   - 同时记下页面上的 Account ID

完成后将凭据填入 `.env` 文件即可使用。

### 依赖
- `boto3` — S3 兼容 API 客户端
- `python-dotenv` — .env 文件加载（可选但推荐）

---

## 2026-06-24: R2 全链路打通 + 前端接入（旧版 .docx 方案，已被 HTML 方案替代）

### R2 连接验证
- 用户完成 Cloudflare Dashboard 配置，填好 `.env`
- Bucket 名称：`cyanalyst-files`（用户自选）
- R2 公共 URL：`https://pub-e042cb137f3f4d9d91009d7a9233dd5b.r2.dev`
- `--test` 连接通过，`--list` 正常列出对象

### 端到端测试
- `generate_docs.py` 生成 2 份 .docx 研报到 `scripts/output/research/daily/`
- `upload_to_r2.py --dir scripts/output ""` 成功上传至 R2
- 公共 URL `curl -sI` 验证返回 HTTP 200 + 正确 Content-Type
- 上传后修复了 `upload_directory()` 路径拼接 bug（空前缀导致双斜杠）

### 前端接入实际 R2 URL
- 新建 `src/config.ts`：集中管理 R2_BASE_URL + `r2Url()` 辅助函数
- 三个详情页（daily/weekly/special）统一改为从 config.ts 导入
- 每篇研报底部现在有两个按钮：
  - **在线阅读 (.pdf)** — 新标签页打开，浏览器原生 PDF 预览
  - **下载 (.docx)** — 直接下载 Word 文档
- PDF 在线预览方案：浏览器原生渲染 `application/pdf`，无需额外组件
- 后续 `generate_docs.py` 需增加 PDF 转换步骤（LibreOffice headless 或 docx2pdf）
