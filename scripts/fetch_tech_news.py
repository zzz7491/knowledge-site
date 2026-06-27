#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import requests
import datetime
from pathlib import Path

# 配置
RSS_SOURCES = [
    "https://feeds.feedburner.com/QuantumGravityResearch?format=xml",
    "https://www.technologyreview.com/feed",
    "https://feeds.arxiv.org/archive/cs.AI",
]

HACKER_NEWS_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"

def fetch_hacker_news():
    """获取 Hacker News 热门文章"""
    try:
        resp = requests.get(HACKER_NEWS_URL, timeout=10)
        if resp.status_code == 200:
            ids = resp.json()[:10]
            articles = []
            for sid in ids:
                item_resp = requests.get(HN_ITEM_URL.format(sid), timeout=10)
                if item_resp.status_code == 200:
                    item = item_resp.json()
                    if item and 'title' in item:
                        articles.append({
                            'title': item.get('title', ''),
                            'url': item.get('url', f"https://news.ycombinator.com/item?id={sid}"),
                            'score': item.get('score', 0),
                            'source': 'Hacker News'
                        })
            return articles
    except Exception as e:
        print(f"获取 Hacker News 失败: {e}")
    return []

def fetch_arxiv():
    """获取 arXiv AI 论文"""
    url = "http://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=submittedDate&max_results=10"
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            import xml.etree.ElementTree as ET
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            root = ET.fromstring(resp.text)
            entries = root.findall('atom:entry', ns)
            articles = []
            for entry in entries[:10]:
                title = entry.find('atom:title', ns)
                link = entry.find('atom:link', ns)
                summary = entry.find('atom:summary', ns)
                articles.append({
                    'title': title.text.strip() if title is not None else '',
                    'url': link.get('href', '') if link is not None else '',
                    'summary': summary.text.strip()[:200] + '...' if summary is not None else '',
                    'source': 'arXiv AI'
                })
            return articles
    except Exception as e:
        print(f"获取 arXiv 失败: {e}")
    return []

def fetch_techcrunch():
    """获取 TechCrunch AI 新闻"""
    url = "https://techcrunch.com/wp-json/wp/v2/posts?categories=147&per_page=10"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            articles = []
            for post in data:
                articles.append({
                    'title': post.get('title', {}).get('rendered', ''),
                    'url': post.get('link', ''),
                    'source': 'TechCrunch'
                })
            return articles
    except Exception as e:
        print(f"获取 TechCrunch 失败: {e}")
    return []

def generate_markdown(articles, date_str):
    """生成 Markdown 内容"""
    content = f"""---
title: 科技前沿快报 {date_str}
sidebar_position: 1
tags: [科技, AI, 前沿]
---

# 🚀 科技前沿快报 - {date_str}

> 由 AI 自动抓取全网科技资讯，每6小时更新一次

"""
    # 按来源分组
    sources = {}
    for article in articles:
        source = article.get('source', '其他')
        if source not in sources:
            sources[source] = []
        sources[source].append(article)
    
    for source, items in sources.items():
        content += f"\n## 📡 {source}\n\n"
        for item in items:
            title = item.get('title', '').strip()
            url = item.get('url', '#')
            score = item.get('score')
            if score:
                content += f"- **[{title}]({url})** (热度: {score})\n"
            elif item.get('summary'):
                content += f"- **[{title}]({url})**\n"
                content += f"  > {item.get('summary', '')}\n"
            else:
                content += f"- [{title}]({url})\n"
    
    content += f"\n---\n\n*最后更新: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
    return content

def main():
    print("🚀 开始抓取科技资讯...")
    
    # 获取所有来源
    all_articles = []
    all_articles.extend(fetch_hacker_news())
    print(f"✅ Hacker News: {len(all_articles)} 条")
    all_articles.extend(fetch_arxiv())
    print(f"✅ arXiv: {len(all_articles)} 条")
    all_articles.extend(fetch_techcrunch())
    print(f"✅ TechCrunch: {len(all_articles)} 条")
    
    if not all_articles:
        print("⚠️ 没有抓取到任何文章")
        return
    
    # 生成 Markdown
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    md_content = generate_markdown(all_articles, date_str)
    
    # 保存文件
    docs_dir = Path('docs/每日更新')
    docs_dir.mkdir(parents=True, exist_ok=True)
    file_path = docs_dir / f'{date_str}-快报.md'
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"✅ 已生成: {file_path}")
    print(f"📊 共 {len(all_articles)} 篇文章")

if __name__ == '__main__':
    main()