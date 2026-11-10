#!/usr/bin/env python3
"""GEO & SEO Readiness MCP — Lite (open source).

A zero-dependency MCP server (stdio) that checks whether a public website is
readable by AI search engines: robots.txt rules for AI search and training
crawlers, /llms.txt, JSON-LD structured data, canonical tags and XML sitemaps.

Run:  python server.py            (MCP stdio server)
      python server.py --check URL (one-off report in the terminal)
"""
from __future__ import annotations

import gzip
import html
import ipaddress
import json
import re
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser

from mcp_stdio import StdioServer

VERSION = "1.0.0"
USER_AGENT = "GEO-SEO-Readiness-MCP-Lite/1.0 (+https://github.com/alicexixi85/geo-seo-mcp-pro)"
TIMEOUT = 10
MAX_BYTES = 4 * 1024 * 1024

AI_SEARCH_BOTS = ["OAI-SearchBot", "PerplexityBot", "Claude-SearchBot"]
AI_TRAINING_BOTS = ["GPTBot", "ClaudeBot", "Google-Extended", "CCBot"]
CLASSIC_SEARCH_BOTS = ["Googlebot", "Bingbot"]


# ---------------------------------------------------------------- networking
def _normalize(url: str) -> str:
    url = (url or "").strip()
    if not url:
        raise ValueError("url is required")
    if not re.match(r"^https?://", url, re.I):
        url = "https://" + url
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError(f"Not a valid http(s) URL: {url}")
    if not parsed.path:
        url = urllib.parse.urlunparse(parsed._replace(path="/"))
    return url


def _assert_public(host: str) -> None:
    """Refuse localhost and private/intranet addresses (SSRF guard)."""
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as exc:
        raise ValueError(f"Cannot resolve host {host}: {exc}") from exc
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            raise ValueError(f"Refusing to fetch non-public address {ip} for host {host}")


def _fetch(url: str, accept: str = "*/*") -> dict:
    url = _normalize(url)
    _assert_public(urllib.parse.urlparse(url).hostname)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": accept,
                                                "Accept-Encoding": "identity"})
    started = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            ttfb_ms = round((time.monotonic() - started) * 1000)
            body = resp.read(MAX_BYTES + 1)
            return {"url": url, "final_url": resp.geturl(), "status": resp.status,
                    "content_type": resp.headers.get("Content-Type", ""),
                    "truncated": len(body) > MAX_BYTES, "body": body[:MAX_BYTES],
                    "ttfb_ms": ttfb_ms, "error": None}
    except urllib.error.HTTPError as exc:
        return {"url": url, "final_url": url, "status": exc.code,
                "content_type": exc.headers.get("Content-Type", "") if exc.headers else "",
                "truncated": False, "body": b"", "ttfb_ms": None, "error": f"HTTP {exc.code}"}
    except Exception as exc:  # timeouts, TLS errors, DNS
        return {"url": url, "final_url": url, "status": None, "content_type": "",
                "truncated": False, "body": b"", "ttfb_ms": None, "error": str(exc)}


def _origin(url: str) -> str:
    p = urllib.parse.urlparse(_normalize(url))
    return f"{p.scheme}://{p.netloc}"


def _text(body: bytes) -> str:
    if body[:2] == b"\x1f\x8b":
        body = gzip.decompress(body)[:MAX_BYTES]
    return body.decode("utf-8", errors="replace")


# ---------------------------------------------------------------- checks
def check_ai_crawler_access(url: str) -> dict:
    page = _normalize(url)
    robots_url = _origin(page) + "/robots.txt"
    res = _fetch(robots_url, "text/plain")
    findings = []
    if res["status"] == 200:
        rp = urllib.robotparser.RobotFileParser()
        robots = _text(res["body"])
        rp.parse(robots.splitlines())
        policy = {}
        for group, bots in (("ai_search", AI_SEARCH_BOTS), ("ai_training", AI_TRAINING_BOTS),
                            ("classic_search", CLASSIC_SEARCH_BOTS)):
            policy[group] = {b: ("allowed" if rp.can_fetch(b, page) else "blocked") for b in bots}
        blocked_search = [b for b, v in policy["ai_search"].items() if v == "blocked"]
        if blocked_search:
            findings.append(f"FAIL: robots.txt blocks AI search crawlers {blocked_search}; these engines cannot cite this page.")
        else:
            findings.append("PASS: AI search crawlers (OAI-SearchBot, PerplexityBot, Claude-SearchBot) are allowed by robots.txt.")
        blocked_classic = [b for b, v in policy["classic_search"].items() if v == "blocked"]
        if blocked_classic:
            findings.append(f"FAIL: robots.txt blocks {blocked_classic}.")
        blocked_train = [b for b, v in policy["ai_training"].items() if v == "blocked"]
        if blocked_train:
            findings.append(f"INFO: training crawlers blocked {blocked_train}. This is a policy choice and does not affect AI search citations.")
        sitemaps = re.findall(r"(?im)^\s*sitemap:\s*(\S+)", robots)
    elif res["status"] in (404, 410):
        policy, sitemaps = "no robots.txt (all crawlers allowed by default)", []
        findings.append("WARN: /robots.txt not found. Crawlers are allowed by default, but you cannot declare a sitemap.")
    else:
        policy, sitemaps = "unmeasured", []
        findings.append(f"UNMEASURED: robots.txt returned {res['status'] or res['error']}. A WAF or CDN may be blocking automated requests; "
                        "check that it does not also block AI search crawlers.")
    return {"page": page, "robots_url": robots_url, "robots_status": res["status"] or res["error"],
            "policy": policy, "declared_sitemaps": sitemaps, "findings": findings,
            "note": "robots.txt rules only. A CDN/WAF can still block bots by user-agent; verify with your CDN's bot settings."}


def check_llms_txt(url: str) -> dict:
    llms_url = _origin(url) + "/llms.txt"
    res = _fetch(llms_url, "text/plain, text/markdown")
    findings = []
    out = {"llms_url": llms_url, "status": res["status"] or res["error"], "content_type": res["content_type"]}
    if res["status"] != 200:
        findings.append("FAIL: /llms.txt not available. Add a short Markdown index of your key pages for AI agents.")
        out["findings"] = findings
        return out
    text = _text(res["body"])
    if re.search(r"(?i)<!doctype html|<html", text[:500]):
        findings.append("FAIL: /llms.txt returns an HTML page (likely a soft 404 or SPA fallback), not Markdown.")
    h1 = re.findall(r"(?m)^# (.+)$", text)
    h2 = re.findall(r"(?m)^## (.+)$", text)
    links = re.findall(r"\[[^\]]+\]\((https?://[^)\s]+)\)", text)
    bare = re.findall(r"(?<!\()https?://[^\s)>\]]+", text)
    hosts = sorted({urllib.parse.urlparse(u).netloc for u in links + bare})
    if not h1:
        findings.append("WARN: no H1 title ('# Name') at the top of llms.txt.")
    if not h2:
        findings.append("WARN: no H2 sections ('## Section') grouping your links.")
    if not links:
        findings.append("WARN: no Markdown links ([title](url)); agents use these to find pages.")
    if h1 and h2 and links:
        findings.append("PASS: llms.txt has a title, sections and links.")
    out.update({"bytes": len(res["body"]), "h1": h1[:3], "h2_sections": h2[:20],
                "markdown_links": len(links), "linked_hosts": hosts, "findings": findings})
    return out


class _HeadParser:
    """Regex-based extraction is enough for the head tags we need."""

    @staticmethod
    def attr(tag: str, name: str) -> str | None:
        m = re.search(rf'{name}\s*=\s*("([^"]*)"|\'([^\']*)\'|([^\s>]+))', tag, re.I)
        if not m:
            return None
        return html.unescape(m.group(2) or m.group(3) or m.group(4) or "")

    @classmethod
    def link_rel(cls, doc: str, rel: str) -> list[str]:
        out = []
        for tag in re.findall(r"<link\b[^>]*>", doc, re.I):
            if (cls.attr(tag, "rel") or "").lower() == rel:
                out.append(cls.attr(tag, "href") or "")
        return out

    @classmethod
    def meta(cls, doc: str, key: str) -> str | None:
        for tag in re.findall(r"<meta\b[^>]*>", doc, re.I):
            if (cls.attr(tag, "property") or cls.attr(tag, "name") or "").lower() == key:
                return cls.attr(tag, "content")
        return None


def _jsonld_types(node, acc: list) -> None:
    if isinstance(node, list):
        for n in node:
            _jsonld_types(n, acc)
    elif isinstance(node, dict):
        t = node.get("@type")
        if t:
            acc.extend(t if isinstance(t, list) else [t])
        for key in ("@graph", "mainEntity", "offers", "itemListElement"):
            if key in node:
                _jsonld_types(node[key], acc)


def extract_structured_data(url: str) -> dict:
    res = _fetch(url, "text/html")
    page = _normalize(url)
    if res["status"] != 200:
        return {"page": page, "status": res["status"] or res["error"],
                "findings": [f"UNMEASURED: page returned {res['status'] or res['error']}."]}
    doc = _text(res["body"])
    findings = []
    blocks = re.findall(r'<script[^>]+type\s*=\s*["\']application/ld\+json["\'][^>]*>(.*?)</script>', doc, re.I | re.S)
    types, errors = [], 0
    for b in blocks:
        try:
            _jsonld_types(json.loads(b.strip()), types)
        except json.JSONDecodeError:
            errors += 1
    title = re.search(r"<title[^>]*>(.*?)</title>", doc, re.I | re.S)
    canonical = _HeadParser.link_rel(doc, "canonical")
    og_url = _HeadParser.meta(doc, "og:url")
    description = _HeadParser.meta(doc, "description")
    lang = re.search(r"<html[^>]*\blang\s*=\s*[\"']?([\w-]+)", doc, re.I)
    visible = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", doc)
    visible = re.sub(r"<[^>]+>", " ", visible)
    visible_chars = len(re.sub(r"\s+", " ", visible).strip())

    page_host = urllib.parse.urlparse(res["final_url"]).netloc
    if not blocks:
        findings.append("WARN: no JSON-LD found in the initial HTML. If the site injects it with JavaScript, "
                        "non-rendering crawlers will not see it.")
    else:
        findings.append(f"PASS: {len(blocks)} JSON-LD block(s), types: {sorted(set(types))}.")
    if errors:
        findings.append(f"FAIL: {errors} JSON-LD block(s) are not valid JSON.")
    for label, value in (("canonical", canonical[0] if canonical else None), ("og:url", og_url)):
        if not value:
            findings.append(f"WARN: no {label} tag.")
            continue
        host = urllib.parse.urlparse(urllib.parse.urljoin(res["final_url"], value)).netloc
        if host and host != page_host:
            findings.append(f"FAIL: {label} points to another host ({host}); answer engines may attribute this page elsewhere.")
    if len(canonical) > 1:
        findings.append(f"FAIL: {len(canonical)} canonical tags on one page.")
    if visible_chars < 500:
        findings.append(f"WARN: only {visible_chars} characters of text in the initial HTML; the page may be a JavaScript shell.")
    if not description:
        findings.append("WARN: no meta description.")
    return {"page": page, "final_url": res["final_url"], "status": res["status"], "ttfb_ms": res["ttfb_ms"],
            "title": html.unescape(title.group(1).strip()) if title else None, "lang": lang.group(1) if lang else None,
            "meta_description": description, "canonical": canonical, "og_url": og_url,
            "jsonld_blocks": len(blocks), "jsonld_types": sorted(set(types)), "initial_html_text_chars": visible_chars,
            "findings": findings}


def check_sitemap(url: str, sitemap_url: str | None = None) -> dict:
    candidates = [sitemap_url] if sitemap_url else []
    if not candidates:
        robots = _fetch(_origin(url) + "/robots.txt", "text/plain")
        if robots["status"] == 200:
            candidates = re.findall(r"(?im)^\s*sitemap:\s*(\S+)", _text(robots["body"]))
        if not candidates:
            candidates = [_origin(url) + "/sitemap.xml"]
    target = candidates[0]
    res = _fetch(target, "application/xml, text/xml")
    out = {"sitemap_url": target, "declared": candidates, "status": res["status"] or res["error"]}
    if res["status"] != 200:
        out["findings"] = [f"FAIL: sitemap not reachable ({res['status'] or res['error']})."]
        return out
    text = _text(res["body"])
    kind = "sitemapindex" if "<sitemapindex" in text else ("urlset" if "<urlset" in text else "unknown")
    locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", text)
    hosts = sorted({urllib.parse.urlparse(u).netloc for u in locs})
    findings = []
    if kind == "unknown":
        findings.append("FAIL: response is not an XML sitemap (no <urlset> or <sitemapindex>).")
    elif not locs:
        findings.append("WARN: sitemap has no <loc> entries.")
    else:
        findings.append(f"PASS: {kind} with {len(locs)} <loc> entries.")
    if res["truncated"]:
        findings.append("INFO: sitemap larger than 4 MiB; only the first 4 MiB were read.")
    foreign = [h for h in hosts if h != urllib.parse.urlparse(target).netloc]
    if foreign:
        findings.append(f"WARN: sitemap lists URLs on other hosts {foreign[:5]}.")
    out.update({"type": kind, "loc_count": len(locs), "sample": locs[:10], "hosts": hosts, "findings": findings})
    return out


def quick_readiness_report(url: str) -> dict:
    sections = {
        "ai_crawler_access": check_ai_crawler_access(url),
        "llms_txt": check_llms_txt(url),
        "structured_data_and_canonical": extract_structured_data(url),
        "sitemap": check_sitemap(url),
    }
    summary = {"PASS": 0, "WARN": 0, "FAIL": 0, "UNMEASURED": 0, "INFO": 0}
    all_findings = []
    for name, sec in sections.items():
        for f in sec.get("findings", []):
            level = f.split(":", 1)[0]
            summary[level] = summary.get(level, 0) + 1
            all_findings.append(f"[{name}] {f}")
    priority = [f for f in all_findings if "] FAIL" in f] + [f for f in all_findings if "] WARN" in f]
    return {"target": _normalize(url), "summary": summary, "fix_first": priority[:10],
            "sections": sections,
            "method": "Rule-based checks on the initial HTTP responses. No score is invented; dimensions that could not be fetched are reported as UNMEASURED."}


# ---------------------------------------------------------------- MCP wiring
URL_SCHEMA = {"type": "object", "properties": {"url": {"type": "string", "description": "Public page or site URL, e.g. https://example.com/pricing"}},
              "required": ["url"]}

server = StdioServer(
    "geo-seo-readiness-lite", VERSION,
    instructions="Checks whether a public website can be read and cited by AI search engines. "
                 "Start with quick_readiness_report, then drill into a single check.")

server.tool("quick_readiness_report",
            "Run all checks (AI crawler access, llms.txt, JSON-LD/canonical, sitemap) for a URL and return a prioritized fix list.",
            URL_SCHEMA)(quick_readiness_report)
server.tool("check_ai_crawler_access",
            "Evaluate robots.txt for AI search crawlers (OAI-SearchBot, PerplexityBot, Claude-SearchBot), AI training crawlers "
            "(GPTBot, ClaudeBot, Google-Extended, CCBot) and Googlebot/Bingbot, for the given page path.",
            URL_SCHEMA)(check_ai_crawler_access)
server.tool("check_llms_txt",
            "Fetch /llms.txt for the site and check that it is Markdown with a title, sections and links (detects HTML soft-404s).",
            URL_SCHEMA)(check_llms_txt)
server.tool("extract_structured_data",
            "Extract JSON-LD types, canonical, og:url, title, meta description and initial-HTML text size for a page; flags canonicals pointing to another host.",
            URL_SCHEMA)(extract_structured_data)
server.tool("check_sitemap",
            "Find the XML sitemap (robots.txt Sitemap: lines or /sitemap.xml) and count its URLs. Reads up to 4 MiB; supports gzip.",
            {"type": "object", "properties": {
                "url": {"type": "string", "description": "Site URL"},
                "sitemap_url": {"type": "string", "description": "Optional explicit sitemap URL"}},
             "required": ["url"]})(check_sitemap)


def main() -> None:
    if len(sys.argv) >= 3 and sys.argv[1] == "--check":
        print(json.dumps(quick_readiness_report(sys.argv[2]), indent=2, ensure_ascii=False))
        return
    server.serve()


if __name__ == "__main__":
    main()
