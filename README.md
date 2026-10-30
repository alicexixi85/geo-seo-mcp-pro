# GEO & SEO Readiness MCP Server 2.1 (`geo-seo-mcp-pro`)

**Stop paying $129/month for bloated legacy SEO subscriptions that don't even check if ChatGPT, Perplexity, or Claude can read your site.**

`GEO & SEO Readiness MCP Server 2.1` is a local-first Python Model Context Protocol (`stdio`) server and automated white-label PDF report engine. It audits any target URL or competitor domain using verifiable HTTP and headless Chromium DOM evidence—never hallucinated scores or fake revenue-loss numbers.

## Why We Built This
1. **AI Search Blind Spots**: Traditional SEO tools ignore `/llms.txt` and fail to distinguish between AI search crawlers (`OAI-SearchBot`, `PerplexityBot`, `Claude-SearchBot`) and training scrapers (`GPTBot`, `ClaudeBot`, `Google-Extended`).
2. **SPA Empty Shells**: Modern React/Next.js/Vue sites often return 0 readable characters and 0 JSON-LD schemas to static crawlers. Our engine includes a 2-second Playwright Chromium DOM observer to verify what actually renders.
3. **Honest Engineering (Zero Hallucinated Metrics)**: If a target blocks probes or lacks a metric, the engine marks it `UNMEASURED`, re-normalizes measured weights, and trips a comparability circuit breaker rather than inventing fake scores.

## What's in This Repository (Open-Source Probe & Sample Audit)
- **`geo_seo_probe_lite.py`**: 45-line zero-dependency Python MCP probe that checks any domain's `/robots.txt` permissions across 6 major AI crawlers (`OAI-SearchBot`, `PerplexityBot`, `Claude-SearchBot`, `GPTBot`, `ClaudeBot`, `Google-Extended`) and verifies `/llms.txt` availability.
- **`GEO_SEO_MCP_2_1_Sample_4Page_Audit_Report.pdf`**: Real 4-page A4 white-label technical audit report comparing Midea (`midea.com/global`) vs. Haier (`haier.com/global`).
- **`llms.txt`**: Standardized machine-readable discovery index.

## 5-Dimension Readiness Matrix
- **Search & AI Crawler Policy (30%)**: RFC 9309 `robots.txt` evaluation across 6 major AI search & training bots.
- **LLM-Readable Index (15%)**: Validates `/llms.txt` structure and HTTP status.
- **Structured Data / Schema.org (25%)**: Extracts static and dynamically injected JSON-LD (`SoftwareApplication`, `FAQPage`, `Product`, `Organization`).
- **XML Sitemaps (15%)**: Streaming parser supporting multi-megabyte child sitemaps without memory crashes.
- **TTFB & Response Performance (15%)**: Real navigation timing measurement with optional HTTP/SOCKS5 proxy routing.

## Get the Full Commercial Source Package + 4-Page White-Label PDF Engine
This repository hosts the open-source 1-tool probe, sample audit report, and specification. The complete, production-ready **33-file commercial source package** (including all 4 MCP tools, bilingual EN/ZH 4-page A4 white-label PDF generator, Playwright SPA renderer, automated patch generator, and regression test suite) is available as a **one-time purchase (no recurring subscription)**:

👉 **[Download GEO & SEO Readiness MCP Server 2.1 on Gumroad ($49 Solo / $129 Agency White-Label)](https://dejunchen770231.gumroad.com/l/geo-seo-mcp-pro)**
*(Launch special: Use code `WHETSTONE20` at checkout for 20% off)*

- Live Ecosystem & `llms.txt`: https://usethelever.com/llms.txt
- Support: `merciai@agent.qq.com`
