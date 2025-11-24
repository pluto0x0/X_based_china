#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
from pathlib import Path
from datetime import datetime

def load_users(jsonl_path: Path):
    users = []
    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                users.append(obj)
            except json.JSONDecodeError:
                # 可以根据需要打印错误信息
                continue
    return users

def format_created_at(raw):
    """将 Twitter 的 created_at 转成 YYYY-MM-DD，失败就原样返回。"""
    if not raw:
        return ""
    try:
        dt = datetime.strptime(raw, "%a %b %d %H:%M:%S %z %Y")
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return raw

def build_html(users, css_filename="styles.css", title="Twitter Accounts Based in China"):
    cards_html = []

    for u in users:
        username = u.get("username") or ""
        info = u.get("info", {}) or {}
        core = info.get("core", {}) or {}
        avatar = info.get("avatar", {}) or {}

        screen_name = core.get("screen_name") or username
        display_name = core.get("name") or screen_name
        created_at = format_created_at(core.get("created_at"))
        is_blue_verified = bool(info.get("is_blue_verified") or info.get("verification", {}).get("verified"))
        rest_id = info.get("rest_id", "")
        about = info.get("about_profile", {}) or {}

        country = about.get("account_based_in") or ""
        source  = about.get("source") or ""
        location_accurate = about.get("location_accurate")
        username_changes = (about.get("username_changes") or {}).get("count")

        avatar_url = avatar.get("image_url") or ""

        verified_badge = ""
        if is_blue_verified:
            verified_badge = '<span class="badge badge-verified" title="Verified">✔</span>'

        # 额外信息行：只展示有值的字段，节省空间
        meta_items = []
        if created_at:
            meta_items.append(f"<span>注册：{created_at}</span>")
        if country:
            meta_items.append(f"<span>地区：{country}</span>")
        if source:
            meta_items.append(f"<span>来源：{source}</span>")
        if username_changes not in (None, ""):
            meta_items.append(f"<span>改名次数：{username_changes}</span>")

        meta_html = ""
        if meta_items:
            meta_html = '<div class="user-meta">' + " · ".join(meta_items) + "</div>"

        id_html = ""
        if rest_id:
            id_html = f'<div class="user-id">ID: {rest_id}</div>'

        # 卡片 HTML
        card = f"""
        <article class="user-card">
            <div class="user-avatar-wrap">
                <a href="https://twitter.com/{screen_name}" target="_blank">
                    <img src="{avatar_url}" alt="{display_name} avatar" loading="lazy" class="user-avatar" />
                </a>
            </div>
            <div class="user-content">
                <div class="user-title-row">
                    <h2 class="user-name" title="{display_name}">{display_name}</h2>
                    {verified_badge}
                </div>
                <div class="user-handle">@{screen_name}</div>
                {meta_html}
                {id_html}
            </div>
        </article>
        """
        cards_html.append(card)

    cards_str = "\n".join(cards_html)

    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <link rel="stylesheet" href="{css_filename}">
</head>
<body>
    <div class="page">
        <header class="page-header">
            <h1>
            {title}
            <a href="https://github.com/pluto0x0/X_based_china" target="_blank"><img src="https://img.shields.io/badge/GitHub-Repository-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub Repository"></a>
            </h1>
            <p class="page-subtitle">共 {len(users)} 个用户</p>
        </header>
        <main class="page-main">
            <section class="user-grid">
                {cards_str}
            </section>
        </main>
    </div>
</body>
</html>
"""
    return html

def write_css(css_path: Path):
    css = r"""
*,
*::before,
*::after {
    box-sizing: border-box;
}

html, body {
    margin: 0;
    padding: 0;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
    background: #020617;
    color: #e5e7eb;
    -webkit-font-smoothing: antialiased;
}

.page {
    max-width: 1280px;
    margin: 0 auto;
    padding: 16px 12px 40px;
}

.page-header {
    display: flex;
    flex-direction: column;
    gap: 4px;
    margin-bottom: 12px;
}

.page-header h1 {
    margin: 0;
    font-size: 20px;
    font-weight: 600;
    color: #f9fafb;
}

.page-subtitle {
    margin: 0;
    font-size: 12px;
    color: #9ca3af;
}

.user-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 8px;
}

/* 卡片本身尽量紧凑 */
.user-card {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    padding: 8px;
    border-radius: 10px;
    background: radial-gradient(circle at top left, rgba(56,189,248,0.10), transparent 55%) #020617;
    border: 1px solid rgba(148,163,184,0.2);
    box-shadow: 0 6px 18px rgba(15,23,42,0.70);
    transition: transform 0.12s ease-out, box-shadow 0.12s ease-out, border-color 0.12s ease-out, background 0.12s ease-out;
}

.user-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 28px rgba(15,23,42,0.85);
    border-color: rgba(94,234,212,0.7);
    background: radial-gradient(circle at top left, rgba(94,234,212,0.16), transparent 55%) #020617;
}

.user-avatar-wrap {
    flex: 0 0 auto;
}

.user-avatar {
    width: 44px;
    height: 44px;
    border-radius: 999px;
    object-fit: cover;
    border: 1px solid rgba(148,163,184,0.6);
    background: #020617;
}

.user-content {
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.user-title-row {
    display: flex;
    align-items: center;
    gap: 4px;
}

.user-name {
    margin: 0;
    font-size: 13px;
    font-weight: 600;
    color: #e5e7eb;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.user-handle {
    font-size: 12px;
    color: #9ca3af;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* 元信息一行展示，紧凑 */
.user-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-top: 2px;
    font-size: 11px;
    color: #9ca3af;
}

.user-meta span {
    white-space: nowrap;
}

.user-id {
    margin-top: 2px;
    font-size: 11px;
    color: #64748b;
    word-break: break-all;
}

.badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0 4px;
    border-radius: 999px;
    font-size: 10px;
    line-height: 1.4;
}

.badge-verified {
    background: linear-gradient(135deg, #38bdf8, #22c55e);
    color: #0f172a;
    font-weight: 700;
    min-width: 16px;
    min-height: 16px;
}

/* 小屏适配 */
@media (max-width: 640px) {
    .page {
        padding-inline: 10px;
    }
    .user-card {
        padding: 8px;
    }
    .user-avatar {
        width: 40px;
        height: 40px;
    }
}
"""
    css_path.write_text(css.strip() + "\n", encoding="utf-8")

def main():
    if len(sys.argv) < 2:
        print("用法: python generate_users_page.py users.jsonl [output_dir]")
        sys.exit(1)

    jsonl_path = Path(sys.argv[1])
    if not jsonl_path.is_file():
        print(f"找不到文件: {jsonl_path}")
        sys.exit(1)

    if len(sys.argv) >= 3:
        out_dir = Path(sys.argv[2])
    else:
        out_dir = Path("output")

    out_dir.mkdir(parents=True, exist_ok=True)

    users = load_users(jsonl_path)
    print(f"读取到 {len(users)} 行用户数据")

    css_filename = "styles.css"
    html_path = out_dir / "index.html"
    css_path = out_dir / css_filename

    write_css(css_path)
    html = build_html(users, css_filename=css_filename, title="Twitter Accounts Based in China")
    html_path.write_text(html, encoding="utf-8")

    print(f"已生成: {html_path}")
    print(f"CSS 文件: {css_path}")

if __name__ == "__main__":
    main()
