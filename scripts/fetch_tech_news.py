#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import requests
import datetime
import time
import re
from pathlib import Path
from urllib.parse import urlparse

# 配置 - OpenRouter（与 dlt-assistant 项目共用同一 AI 通道，密钥经仓库 Secrets 注入）
AI_API_URL = "https://openrouter.ai/api/v1/chat/completions"
AI_MODEL = os.environ.get('OPENROUTER_MODEL', 'deepseek/deepseek-chat')
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '')

HACKER_NEWS_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"
ARXIV_QUERY_URL = "https://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=submittedDate&max_results=5"
TECHCRUNCH_URL = "https://techcrunch.com/wp-json/wp/v2/posts?categories=577047203&per_page=5"

def fetch_hacker_news():
    """获取 Hacker News 热门文章"""
    try:
        resp = requests.get(HACKER_NEWS_URL, timeout=10)
        if resp.status_code == 200:
            ids = resp.json()[:8]
            articles = []
            for sid in ids:
                item_resp = requests.get(HN_ITEM_URL.format(sid), timeout=10)
                if item_resp.status_code == 200:
                    item = item_resp.json()
                    if item and 'title' in item:
                        url = item.get('url', f"https://news.ycombinator.com/item?id={sid}")
                        content = fetch_article_content(url) if url else ''
                        articles.append({
                            'title': item.get('title', ''),
                            'url': url,
                            'score': item.get('score', 0),
                            'source': 'Hacker News',
                            'content': content[:2000] if content else '',
                            'text': item.get('text', '')[:500]
                        })
            return articles
    except Exception as e:
        print(f"获取 Hacker News 失败: {e}")
    return []

def fetch_arxiv():
    """获取 arXiv AI 论文"""
    try:
        resp = requests.get(ARXIV_QUERY_URL, timeout=15)
        if resp.status_code == 200:
            import xml.etree.ElementTree as ET
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            root = ET.fromstring(resp.text)
            entries = root.findall('atom:entry', ns)
            articles = []
            for entry in entries[:5]:
                title = entry.find('atom:title', ns)
                link = entry.find('atom:link', ns)
                summary = entry.find('atom:summary', ns)
                articles.append({
                    'title': title.text.strip() if title is not None else '',
                    'url': link.get('href', '') if link is not None else '',
                    'summary': summary.text.strip()[:500] if summary is not None else '',
                    'source': 'arXiv AI',
                    'score': 0,
                    'content': summary.text.strip()[:2000] if summary is not None else '',
                    'text': ''
                })
            return articles
    except Exception as e:
        print(f"获取 arXiv 失败: {e}")
    return []

def fetch_techcrunch():
    """获取 TechCrunch AI 新闻"""
    try:
        resp = requests.get(TECHCRUNCH_URL, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            articles = []
            for post in data[:5]:
                url = post.get('link', '')
                content = fetch_article_content(url) if url else ''
                articles.append({
                    'title': post.get('title', {}).get('rendered', ''),
                    'url': url,
                    'source': 'TechCrunch',
                    'score': 0,
                    'content': content[:2000] if content else '',
                    'text': post.get('excerpt', {}).get('rendered', '')[:300]
                })
            return articles
    except Exception as e:
        print(f"获取 TechCrunch 失败: {e}")
    return []

def fetch_article_content(url):
    """抓取文章内容"""
    if not url:
        return ''
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        resp = requests.get(url, timeout=15, headers=headers)
        if resp.status_code == 200:
            import re
            text = re.sub(r'<[^>]+>', ' ', resp.text)
            text = re.sub(r'\s+', ' ', text).strip()
            return text[:2000]
    except Exception as e:
        print(f"抓取内容失败 {url}: {e}")
    return ''

# ---------- AI 加工：逐篇调用 + 中文校验 + 重试，不合格不上架 ----------

def _has_cjk(text):
    return bool(re.search(r'[\u4e00-\u9fff]', text or ''))

def _parse_ai_block(text):
    """解析单篇 AI 输出的四行格式，缺关键字段返回 None"""
    fields = {}
    for raw in (text or '').split('\n'):
        line = raw.strip().strip('*').strip()
        for key in ('标题', '摘要', '核心观点', '关键信息'):
            if line.startswith(key + ':') or line.startswith(key + '：'):
                fields[key] = line[len(key) + 1:].strip().strip('*').strip()
                break
    title = fields.get('标题', '')
    summary = fields.get('摘要', '')
    value = fields.get('核心观点', '')
    keypoints = fields.get('关键信息', '')
    # 硬校验：标题与摘要必须是中文、长度合理，核心观点不能为空
    if not (_has_cjk(title) and len(title) >= 4):
        return None
    if not (_has_cjk(summary) and 25 <= len(summary) <= 200):
        return None
    if not (_has_cjk(value) and len(value) >= 4):
        return None
    return {
        'ai_title': title,
        'ai_summary': summary,
        'ai_value': value,
        'ai_keypoints': keypoints,
    }

def _ai_process_one(article, strict=False):
    """对单篇文章调用一次 AI，成功返回四字段 dict，失败返回 None"""
    material = article.get('content') or article.get('summary') or article.get('text') or ''
    material = material[:1200]
    prompt = f"""请把下面这篇科技资讯加工成中文，只输出四行，格式严格如下，不要输出任何其他内容：
标题: [准确简洁的中文标题]
摘要: [50-80字的中文摘要，包含核心信息]
核心观点: [一句话概括核心价值]
关键信息: [3-5个关键词，用顿号分隔]

原文标题: {article.get('title', '')}
来源: {article.get('source', '')}
原文内容: {material}"""
    if strict:
        prompt += "\n\n注意：上一次输出不合格（缺字段或混有英文）。这次必须四行齐全、全部用中文。"
    payload = {
        "model": AI_MODEL,
        "messages": [
            {"role": "system", "content": "你是一个专业的科技编辑，擅长中英互译和科技内容摘要。只输出中文，确保翻译准确、表达流畅。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 800,
    }
    try:
        resp = requests.post(
            AI_API_URL,
            json=payload,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {OPENROUTER_API_KEY}',
            },
            timeout=90,
        )
        if resp.status_code != 200:
            print(f"  AI 调用失败 HTTP {resp.status_code}: {resp.text[:200]}")
            return None
        result = resp.json()
        text = result['choices'][0]['message']['content']
    except Exception as e:
        print(f"  AI 调用异常: {e}")
        return None
    return _parse_ai_block(text)

def ai_translate_and_summarize(articles):
    """逐篇加工：每篇独立调用、校验、最多重试一次；不合格的条目剔除并告警"""
    if not OPENROUTER_API_KEY:
        print("❌ 错误: 未设置 OPENROUTER_API_KEY 环境变量")
        return [], articles
    ok, dropped = [], []
    for i, article in enumerate(articles, 1):
        print(f"  [{i}/{len(articles)}] {article.get('source', '')} | {article.get('title', '')[:60]}")
        parsed = None
        for attempt in (1, 2):
            parsed = _ai_process_one(article, strict=(attempt == 2))
            if parsed:
                break
            print(f"    第 {attempt} 次加工不合格，重试" if attempt == 1 else "    第二次仍不合格")
            time.sleep(2)
        if parsed:
            article.update(parsed)
            ok.append(article)
        else:
            dropped.append(article)
            print(f"::warning:: 条目加工失败已剔除（不上架）: {article.get('title', '')[:80]}")
        time.sleep(0.5)
    return ok, dropped

def generate_markdown(articles, date_str, fetched_total=None):
    """生成快报 Markdown：紧凑排版，手机优先。
    articles 必须全部是已通过中文校验的条目，这里不再做任何英文兜底。"""
    content = f"""---
title: 科技前沿快报 {date_str}
sidebar_position: 1
tags: [科技, AI, 前沿, 每日更新]
---

# 🚀 科技前沿快报 · {date_str}

> 🤖 自动精选全球科技资讯，中文摘要由 AI 生成（OpenRouter）· 每日更新

"""
    sources = {}
    for article in articles:
        sources.setdefault(article.get('source', '其他'), []).append(article)

    icons = {'Hacker News': '💬', 'arXiv AI': '📄', 'TechCrunch': '📰'}
    for source, items in sources.items():
        icon = icons.get(source, '📌')
        content += f"\n## {icon} {source}（{len(items)} 条）\n"
        for idx, item in enumerate(items, 1):
            content += f"\n### {idx}. {item['ai_title']}\n\n"
            content += f"{item['ai_summary']}\n\n"
            extra = []
            if item.get('ai_value'):
                extra.append(f"💡 {item['ai_value']}")
            if item.get('ai_keypoints'):
                extra.append(f"🏷️ {item['ai_keypoints']}")
            if extra:
                content += '　'.join(extra) + "\n\n"
            meta = []
            score = item.get('score') or 0
            if score:
                flames = '🔥🔥🔥' if score > 500 else ('🔥🔥' if score > 200 else ('🔥' if score > 50 else ''))
                meta.append(f"{flames} 热度 {score}".strip())
            meta.append(f"[阅读原文 →]({item.get('url', '#')})")
            content += ' · '.join(meta) + "\n"

    total = fetched_total if fetched_total is not None else len(articles)
    content += f"\n---\n\n📊 本次共发布 {len(articles)} 篇（抓取 {total} 篇，未通过中文校验的不上架）· 更新时间 {datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M')}\n"
    return content

def main():
    print("🚀 开始抓取科技资讯...")
    print(f"🤖 AI: OpenRouter ({AI_MODEL})")

    if not OPENROUTER_API_KEY:
        print("❌ 错误: 请设置 OPENROUTER_API_KEY 环境变量")
        sys.exit(1)

    all_articles = []
    hn_articles = fetch_hacker_news()
    print(f"✅ Hacker News: {len(hn_articles)} 条")
    all_articles.extend(hn_articles)

    arxiv_articles = fetch_arxiv()
    print(f"✅ arXiv: {len(arxiv_articles)} 条")
    all_articles.extend(arxiv_articles)

    tc_articles = fetch_techcrunch()
    print(f"✅ TechCrunch: {len(tc_articles)} 条")
    all_articles.extend(tc_articles)

    if not all_articles:
        print("❌ 没有抓取到任何文章，任务失败")
        sys.exit(1)

    fetched_total = len(all_articles)
    print(f"🧠 逐篇调用 OpenRouter AI 翻译并生成摘要 ({fetched_total} 篇)...")
    ok_articles, dropped = ai_translate_and_summarize(all_articles)
    print(f"✅ AI 加工合格: {len(ok_articles)}/{fetched_total} 篇，剔除 {len(dropped)} 篇")

    # 成品率过低说明 AI 通道整体异常：宁可任务失败报警，也不发半成品
    if len(ok_articles) == 0 or len(ok_articles) < fetched_total * 0.5:
        print("❌ 合格率低于 50%，判定 AI 通道异常，本次不发布")
        sys.exit(1)

    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    md_content = generate_markdown(ok_articles, date_str, fetched_total=fetched_total)

    docs_dir = Path('docs/每日更新')
    docs_dir.mkdir(parents=True, exist_ok=True)

    today_file = docs_dir / f'{date_str}-快报.md'
    with open(today_file, 'w', encoding='utf-8') as f:
        f.write(md_content)

    all_files = sorted(docs_dir.glob('*-快报.md'), reverse=True)
    for old_file in all_files[7:]:
        old_file.unlink()
        print(f"🗑️ 已删除旧文件: {old_file.name}")

    print(f"✅ 已生成: {today_file}")
    remaining_files = list(docs_dir.glob('*-快报.md'))
    print(f"📁 当前保留 {len(remaining_files)} 个快报文件")

if __name__ == '__main__':
    main()
