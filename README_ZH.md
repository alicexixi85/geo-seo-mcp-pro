# GEO & SEO AI 搜索就绪度检测 MCP（开源免费核心版 · Lite）

[![alicexixi85/geo-seo-mcp-pro MCP server](https://glama.ai/mcp/servers/alicexixi85/geo-seo-mcp-pro/badges/score.svg)](https://glama.ai/mcp/servers/alicexixi85/geo-seo-mcp-pro)

🌐 **[English README](README.md)** | **简体中文**

**为什么你的出海独立站、Webflow/Shopify 商城或文档站 Google 收录正常，但在 ChatGPT Search、Perplexity 和 Claude 里却完全搜不到、零引用？**

大多数排查只测了 Googlebot。实际线上排查中，站点常常因为 `robots.txt` 把 AI 搜索爬虫和训练爬虫一起误杀、CDN/WAF 对 AI User-Agent 静默返回 `403`、首屏 HTML 缺少 `JSON-LD` 结构化数据，或 `/llms.txt` 与 `/sitemap.xml` 返回假 200（HTML 软 404），直接丢掉高意图 AI 搜索询盘与客户续费。

---

## 立即免费试用（3 步从 10 秒网页体检到企业级白标交付）

### ① 10 秒免安装 · 免费在线 GEO 体检（0 注册、打开即测）
👉 **立即在线实测你的域名**：[**https://usethelever.com/tools/ai-crawler-checker**](https://usethelever.com/tools/ai-crawler-checker)
- 拆分检测 **AI 搜索爬虫**（`OAI-SearchBot`、`PerplexityBot`、`Claude-SearchBot`）与 **AI 训练爬虫**（`GPTBot`、`ClaudeBot`、`Google-Extended`、`CCBot`）的 `robots.txt` 放行规则与真实 HTTP 状态码；
- 一键核验 `/llms.txt`、`canonical` / `og:url` 跨域名漂移、首屏 `JSON-LD` 结构化数据及 XML Sitemap（含自动兼容 Webflow 反向属性与 HTML5 无引号压缩写法），支持复制实时可分享诊断链接。

### ② 1 行命令 · 本地 MIT 开源免费核心版（零依赖 Python 3.10+）
无需 API Key、无需账号，直接命令行实测或接入 **Claude Desktop / Cursor / Windsurf**（官方 MCP Registry 标识：`io.github.alicexixi85/geo-seo-mcp-pro`）：

```bash
git clone https://github.com/alicexixi85/geo-seo-mcp-pro.git && cd geo-seo-mcp-pro
python3 server.py --check https://你的出海域名.com
```

**直接接入 Claude Desktop / Cursor MCP 配置（`mcp.json`）：**

```json
{
  "mcpServers": {
    "geo-seo-readiness": {
      "command": "python3",
      "args": ["/你的绝对路径/geo-seo-mcp-pro/server.py"]
    }
  }
}
```

也可以免安装直连只读远程 MCP 端点：`https://mcp.usethelever.com/geo-audit/mcp`

### ③ 4 页白标客户报告样例 PDF 预览 ＋ 开源版 vs 出海/企业 Pro v2.2 对比

👉 **直接预览 4 页客户 vs 竞品白标 A4 诊断报告样例 PDF**：
- 仓库内置样板：[`GEO_SEO_MCP_2_1_Sample_4Page_Audit_Report.pdf`](GEO_SEO_MCP_2_1_Sample_4Page_Audit_Report.pdf)
- 在线直开样板：[**https://usethelever.com/tools/sample-audit-report.pdf**](https://usethelever.com/tools/sample-audit-report.pdf)

| 核心能力对比 | MIT 开源免费核心版（本仓库） | 商业白标版 GEO & SEO Suite Pro v2.2 |
| :--- | :--- | :--- |
| 5 项基础检查（AI 搜索/训练爬虫、`llms.txt`、首屏 JSON-LD、`canonical`/meta、Sitemap） | ✅ 完全免费（支持 CLI & MCP） | ✅ 全量内置 |
| 明确标注 `PASS / WARN / FAIL / UNMEASURED`（遇 403/超时绝不瞎猜） | ✅ 支持 | ✅ 支持 |
| **无头 Chromium 动态渲染**（完整扫描 React / Next.js / Vue / Shopify SPA 站点） | ❌ 仅静态首屏 HTML | ✅ 跨平台支持（macOS / Windows / Linux） |
| **隐形反 AI 引用阻断深度侦测**（`X-Robots-Tag`、`noai`/`noimageai`、Canonical 错配） | ❌ 基础检查 | ✅ 全量检出 |
| **双站同口径竞品对比评分**（你的站点 vs 行业第一竞品逐项分差） | ❌ 单站 | ✅ 自动出双站加权对比 |
| **自动生成 5 文件即装商业修复补丁包**（`robots.txt`、`llms.txt`、`llms-full.txt`、`schema.jsonld`、`head-meta.html`） | ❌ 仅诊断清单 | ✅ 一键生成可交付补丁包 |
| **4 页中英双语（`zh-CN` / `en`）A4 白标客户 PDF 报告**（可直接交给客户做 SEO/AEO 提案） | ❌ 无 | ✅ 支持自定义机构 Logo 与交付 |

👉 **需要完整工程版（42 个文件、1,374 行实测源码 + 70 项自动测试、无头浏览器抓动态站、一键出 5 份上线补丁与 4 页中文 A4 白牌报告）？**

### 🇨🇳 国内用户直购入口（支付宝 AI 付 SkillPay · 人民币一次买断，无需外币卡）
直接访问公开货架：**[君博AI实战技能工坊（支付宝 AI 付 SkillPay）](https://skillpay.alipay.com/public/junbo-skills)**
- **国内官网版**：`问豆包总推同行？查清AI为啥不搜你官网`（适配 **豆包、DeepSeek、Kimi、通义千问、百度 AI 搜索**，适合国内企业官网、工厂站、软件站、个人独立站）
- **跨境外贸独立站纯中文版**：`做外贸独立站没客流？纯中文查清原因`（**全中文操作说明**，专测 Shopify、外贸 B2B 独立站与 8 大海外托管单品页，英文不熟也能 3 分钟上手）
- 支持零安装直接导入豆包 / DeepSeek / Kimi 对话体检，也内置跨平台完整本地 Python 引擎源码可本地部署出 PDF 报告。

### 🌍 海外美元支付用户（Gumroad）
- [前往 Gumroad 商店（Solo / Agency 美元版）](https://dejunchen770231.gumroad.com/l/geo-seo-mcp-pro)
- **定制诊断咨询**：如果你正卡在某个官网或独立站的隐形反收录阻断 / SPA 渲染抓取问题，欢迎发目标域名至 `support@usethelever.com` 或在本仓库提 Issue 交流。

---

## 本仓库开源版 5 个内置 MCP 工具

| 工具名 | 检测内容 |
| :--- | :--- |
| `quick_readiness_report` | 一键跑完以下全部检测，按 `FAIL` 优先于 `WARN` 输出 `fix_first` 优先修复清单 |
| `check_ai_crawler_access` | 拆解 `robots.txt` 针对 AI 搜索爬虫（`OAI-SearchBot`/`PerplexityBot`/`Claude-SearchBot`）、训练爬虫与经典搜索引擎的放行状态 |
| `check_llms_txt` | 检查 `/llms.txt` 是否真实为 Markdown（防 HTML 软 404）及标题/分区/链接完整性 |
| `extract_structured_data` | 提取首屏 JSON-LD 类型（含 `@graph`）、校验语法、`canonical`/`og:url` 同域性与空壳 JS 页面预警 |
| `check_sitemap` | 自动从 `robots.txt` 或 `/sitemap.xml` 解析 `urlset`/`sitemapindex` 与 URL 总数（支持 gzip，最大读 4 MiB） |

## 开源版使用边界说明（使用前请知晓）
- 本开源版仅抓取**初始 HTML 响应**，不执行客户端 JavaScript（遇到纯前端渲染空壳页会显式提醒）；
- `robots.txt` 只是第一层规则，CDN/WAF（如 Cloudflare Bot Fight Mode）仍可能在网关层返回 `403`，请结合在线探针实测结果排查；
- 仅允许检测公网 `http`/`https` 地址，拒绝访问 `localhost` 与内网 IP。

## 开源协议
MIT License · 由 [@alicexixi85](https://github.com/alicexixi85) 维护，欢迎提交 Issue 与 PR。
