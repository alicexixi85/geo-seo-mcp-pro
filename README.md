# GEO & SEO Readiness MCP — Lite

An open-source [Model Context Protocol](https://modelcontextprotocol.io) server that checks whether a public website can be **read and cited by AI search engines** (ChatGPT Search, Perplexity, Claude) as well as classic search.

Ask your assistant *"Is example.com ready for AI search?"* and it runs five rule-based checks and returns a prioritized fix list. No API keys, no account, no dependencies beyond Python 3.10+.

## Tools

| Tool | What it checks |
|---|---|
| `quick_readiness_report` | Runs every check below and returns a `fix_first` list (FAIL before WARN). |
| `check_ai_crawler_access` | `robots.txt` rules for the page path, split into **AI search crawlers** (`OAI-SearchBot`, `PerplexityBot`, `Claude-SearchBot`), **AI training crawlers** (`GPTBot`, `ClaudeBot`, `Google-Extended`, `CCBot`) and `Googlebot`/`Bingbot`. Blocking training crawlers is reported as a policy choice, not an error. |
| `check_llms_txt` | Whether `/llms.txt` exists, is Markdown rather than an HTML soft-404, and has a title, sections and links. |
| `extract_structured_data` | JSON-LD types (including `@graph`), invalid JSON-LD, `canonical` and `og:url` pointing to another host, missing meta description, and pages whose initial HTML is an almost-empty JavaScript shell. |
| `check_sitemap` | Finds the sitemap from `robots.txt` or `/sitemap.xml`, detects `urlset` vs `sitemapindex`, counts URLs (reads up to 4 MiB, gzip supported). |

Every finding is labelled `PASS`, `WARN`, `FAIL`, `INFO` or `UNMEASURED`. When a site blocks the request (403/429, timeouts), the check says `UNMEASURED` instead of guessing.

## Install

```bash
git clone https://github.com/alicexixi85/geo-seo-mcp-pro.git
```

**Claude Desktop** (`claude_desktop_config.json`) / **Cursor** (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "geo-seo-readiness": {
      "command": "python3",
      "args": ["/absolute/path/to/geo-seo-mcp-pro/server.py"]
    }
  }
}
```

**Docker**

```bash
docker build -t geo-seo-readiness-lite .
docker run -i --rm geo-seo-readiness-lite
```

**One-off check in a terminal**

```bash
python3 server.py --check https://example.com
```

## Example prompts

- "Run a quick readiness report for https://example.com and tell me the three fixes that matter most."
- "Does my robots.txt block OAI-SearchBot or PerplexityBot on /pricing?"
- "Is my canonical tag pointing somewhere it shouldn't?"

## Limits (read before relying on results)

- Checks the **initial HTML response** only. It does not execute JavaScript, so JSON-LD injected client-side is not seen (the tool tells you when the page looks like a JavaScript shell).
- `robots.txt` is only one layer. A CDN or WAF (for example Cloudflare bot settings) can still block crawlers by user agent; verify those settings separately.
- Refuses localhost and private network addresses. Public `http`/`https` URLs only.
- Does not produce a single "score". Rankings and citations depend on much more than technical readiness.

## Commercial edition

This repository is the free, MIT-licensed Lite server. A separate paid edition (GEO & SEO Readiness MCP Server 2.1) adds headless-Chromium rendering for SPAs, weighted scoring, two-site competitor comparison, candidate `robots.txt` / `llms.txt` / JSON-LD patches and a white-label PDF report for agencies. A sample report from that edition is in [`GEO_SEO_MCP_2_1_Sample_4Page_Audit_Report.pdf`](GEO_SEO_MCP_2_1_Sample_4Page_Audit_Report.pdf); details and pricing are on [Gumroad](https://dejunchen770231.gumroad.com/l/geo-seo-mcp-pro). The Lite server is complete on its own and does not require the paid edition.

## License

MIT. Built by [@alicexixi85](https://github.com/alicexixi85). Issues and pull requests welcome.

<!-- mcp-name: io.github.alicexixi85/geo-seo-mcp-pro -->
