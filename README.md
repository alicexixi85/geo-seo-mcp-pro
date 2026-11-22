# GEO & SEO Readiness MCP — Lite

An open-source [Model Context Protocol](https://modelcontextprotocol.io) server that checks whether a public website can be **read and cited by AI search engines** (ChatGPT Search, Perplexity, Claude) as well as classic search.

Ask your assistant *"Is example.com ready for AI search?"* and it runs five deterministic checks and returns a prioritized fix list (`FAIL` before `WARN`). No API keys, no account, no external dependencies.

---

## Option 1: Zero-Install Remote MCP (1-Click Paste — No Python or Docker Needed)

Connect directly to the hosted Streamable HTTP MCP endpoint with zero local setup:

```text
https://mcp.usethelever.com/geo-audit/mcp
```

- **Claude Web (`claude.ai`) & Claude Desktop**: Go to `Settings → Connectors → Add Custom Connector` and paste `https://mcp.usethelever.com/geo-audit/mcp`.
- **ChatGPT Developer Mode (MCP)**: Go to `Settings → Connectors → Create` and paste `https://mcp.usethelever.com/geo-audit/mcp`.
- **Cursor (`~/.cursor/mcp.json`) / Windsurf (`~/.codeium/windsurf/mcp_config.json`)**:

```json
{
  "mcpServers": {
    "geo-seo-readiness": {
      "url": "https://mcp.usethelever.com/geo-audit/mcp"
    }
  }
}
```

**No MCP client? Run the free check in your browser:** [AI Crawler Checker](https://usethelever.com/tools/ai-crawler-checker)

---

## Option 2: Local Python `stdio` / CLI / Docker (Zero Dependencies, Python 3.10+)

**Run a 10-second check in your terminal:**

```bash
git clone https://github.com/alicexixi85/geo-seo-mcp-pro.git && cd geo-seo-mcp-pro
python3 server.py --check https://your-site.com
```

**Local `stdio` config (`claude_desktop_config.json` / `.cursor/mcp.json`):**

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

**Docker:**

```bash
docker build -t geo-seo-readiness-lite .
docker run -i --rm geo-seo-readiness-lite
```

Listed in the [official MCP Registry](https://registry.modelcontextprotocol.io/v0/servers?search=geo-seo-mcp-pro) as `io.github.alicexixi85/geo-seo-mcp-pro` and on [Glama](https://glama.ai/mcp/servers/alicexixi85/geo-seo-mcp-pro).

---

## Tools

| Tool | What it checks |
|---|---|
| `quick_readiness_report` | Runs every check below and returns a `fix_first` list (`FAIL` before `WARN`). |
| `check_ai_crawler_access` | `robots.txt` rules for the page path, split into **AI search crawlers** (`OAI-SearchBot`, `PerplexityBot`, `Claude-SearchBot`), **AI training crawlers** (`GPTBot`, `ClaudeBot`, `Google-Extended`, `CCBot`), and `Googlebot`/`Bingbot`. Blocking training crawlers is reported as a policy choice, not an error. |
| `check_llms_txt` | Whether `/llms.txt` exists, is Markdown rather than an HTML soft-404, and has a title, sections, and links. |
| `extract_structured_data` | JSON-LD types (including `@graph`), invalid JSON-LD, `canonical` and `og:url` pointing to another host, missing meta description, and pages whose initial HTML is an empty client-side JavaScript shell. |
| `check_sitemap` | Finds the sitemap from `robots.txt` or `/sitemap.xml`, detects `urlset` vs `sitemapindex`, and counts URLs (reads up to 4 MiB, gzip supported). |

Every finding is labelled `PASS`, `WARN`, `FAIL`, `INFO`, or `UNMEASURED`. When a site blocks the request (403/429, timeouts), the check reports `UNMEASURED` instead of guessing.

## Example prompts

- "Run a quick readiness report for https://example.com and tell me the three fixes that matter most."
- "Does my robots.txt block OAI-SearchBot or PerplexityBot on /pricing?"
- "Is my canonical tag pointing somewhere it shouldn't?"

## Real example: it caught a deployment bug on our own site

We ran it against our own product pages. The landing page passed, but the free-trial URL failed two checks: its `canonical` and `og:url` pointed to a different host, because a deployment had replaced the page with the site's fallback homepage while still returning HTTP `200 OK`. Answer engines would have attributed that URL to the wrong page. Rolling back the deployment resolved both failures.

```text
$ python3 server.py --check https://replay.usethelever.com/mds/en/trial
  "summary": {"PASS": 3, "WARN": 1, "FAIL": 2, "UNMEASURED": 0, "INFO": 0},
  "fix_first": [
    "[structured_data_and_canonical] FAIL: canonical points to another host (usethelever.com); answer engines may attribute this page elsewhere.",
    "[structured_data_and_canonical] FAIL: og:url points to another host (usethelever.com); answer engines may attribute this page elsewhere.",
    "[structured_data_and_canonical] WARN: no JSON-LD found in the initial HTML. ..."
  ],
```

Background on the five checks: [Is your site invisible to ChatGPT Search? Five checks you can run in a minute](https://dev.to/alicexixi85/is-your-site-invisible-to-chatgpt-search-five-checks-you-can-run-in-a-minute-1a18).

## Limits (read before relying on results)

- Checks the **initial HTML response** only. It does not execute JavaScript, so JSON-LD injected client-side is not seen (the tool reports when the page looks like a JavaScript shell).
- `robots.txt` is only one layer. A CDN or WAF (for example Cloudflare bot settings) can still block crawlers by user agent; verify those settings separately.
- Refuses localhost and private network addresses. Public `http`/`https` URLs only.
- Does not produce a synthetic single score in Lite mode. Rankings and citations depend on content quality and authority as well as technical readiness.

---

## Free Checker, Quick-Start Kit & Pro White-Label Edition

- **Free Web Checker (Browser)**: [usethelever.com/tools/ai-crawler-checker](https://usethelever.com/tools/ai-crawler-checker) — instant browser check, zero install.
- **GEO Audit Quick-Start Kit ($9)**: [gumroad.com/l/geo-audit-starter](https://gumroad.com/l/geo-audit-starter) — ready-to-deploy `robots.txt` rules (separating search vs. training crawlers), `/llms.txt` templates, SSR JSON-LD snippets, and pre-launch checklist.
- **GEO & SEO Readiness MCP 2.1 Pro — White-Label PDF ($49 Solo / $129 Agency)**: [gumroad.com/l/geo-seo-mcp-pro](https://gumroad.com/l/geo-seo-mcp-pro) — adds headless-Chromium rendering for JavaScript SPAs, weighted readiness scoring, two-site competitor comparison, candidate `robots.txt` / `llms.txt` / JSON-LD patches, and a 4-page white-label client PDF report ([`GEO_SEO_MCP_2_1_Sample_4Page_Audit_Report.pdf`](GEO_SEO_MCP_2_1_Sample_4Page_Audit_Report.pdf)).
- **Support**: `support@usethelever.com`

The open-source Lite server in this repository is complete on its own under the MIT license and does not require any paid edition.

## License

MIT. Built by [@alicexixi85](https://github.com/alicexixi85). Issues and pull requests welcome.

<!-- mcp-name: io.github.alicexixi85/geo-seo-mcp-pro -->
