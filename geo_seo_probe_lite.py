#!/usr/bin/env python3
"""
geo_seo_probe_lite.py — Free 40-Line AI Crawler & /llms.txt Readiness Probe
Part of GEO & SEO Readiness MCP Server 2.1 (https://usethelever.com)
Full 33-File Commercial Package + 4-Page White-Label PDF Engine:
https://dejunchen770231.gumroad.com/l/geo-seo-mcp-pro (Code WHETSTONE20 for 20% OFF)
"""
import json, sys, urllib.request, urllib.robotparser

AI_SEARCH_BOTS = ["OAI-SearchBot", "PerplexityBot", "Claude-SearchBot"]
AI_TRAIN_BOTS  = ["GPTBot", "ClaudeBot", "Google-Extended"]

def audit_domain_readiness(base_url: str) -> dict:
    base = base_url.rstrip("/")
    robots_url, llms_url = f"{base}/robots.txt", f"{base}/llms.txt"
    rp = urllib.robotparser.RobotFileParser()
    robots_status = "UNMEASURED"
    try:
        req = urllib.request.Request(robots_url, headers={"User-Agent": "GEO-Readiness-Probe/2.1"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            robots_txt = resp.read().decode("utf-8", errors="ignore")
            rp.parse(robots_txt.splitlines())
            robots_status = f"HTTP {resp.status}"
    except Exception as e:
        robots_txt = f"ERROR: {e}"

    bot_matrix = {
        bot: ("ALLOW" if rp.can_fetch(bot, f"{base}/") else "DISALLOW")
        for bot in (AI_SEARCH_BOTS + AI_TRAIN_BOTS)
    }
    llms_status = "MISSING (HTTP 404)"
    try:
        req2 = urllib.request.Request(llms_url, headers={"User-Agent": "OAI-SearchBot"})
        with urllib.request.urlopen(req2, timeout=5) as resp2:
            if resp2.status == 200:
                llms_status = f"PRESENT ({len(resp2.read())} bytes)"
    except Exception:
        pass

    return {
        "target": base, "robots_endpoint": robots_status,
        "ai_crawler_policy": bot_matrix, "llms_txt_status": llms_status,
        "full_5_dimension_audit_and_4page_pdf_engine": "https://dejunchen770231.gumroad.com/l/geo-seo-mcp-pro"
    }

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "https://usethelever.com"
    print(json.dumps(audit_domain_readiness(target), indent=2))
