#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import requests
import datetime
from pathlib import Path

# 配置
AI_API_URL = os.environ.get('AI_API_URL', 'http://585351.xyz:34567')
AI_MODEL = 'glm-4-9b'

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
                            'source': 'Hacker News',
                            'summary': item.get('text', '')[:300] if item.get('text') else ''
                        })
            return articles
    except Exception as e:
        print(f"获取 Hacker News 失败: {e}")
    return []

def fetch_arxiv():
    """获取 arXiv AI 论文"""
    url = "http://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=submittedDate&max_results=8"
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            import xml.etree.ElementTree as ET
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            root = ET.fromstring(resp.text)
            entries = root.findall('atom:entry', ns)
            articles = []
            for entry in entries[:8]:
                title = entry.find('atom:title', ns)
                link = entry.find('atom:link', ns)
                summary = entry.find('atom:summary', ns)
                articles.append({
                    'title': title.text.strip() if title is not None else '',
                    'url': link.get('href', '') if link is not None else '',
                    'summary': summary.text.strip()[:500] if summary is not None else '',
                    'source': 'arXiv AI',
                    'score': 0
                })
            return articles
    except Exception as e:
        print(f"获取 arXiv 失败: {e}")
    return []

def fetch_techcrunch():
    """获取 TechCrunch AI 新闻"""
    url = "https://techcrunch.com/wp-json/wp/v2/posts?categories=147&per_page=8"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            articles = []
            for post in data:
                articles.append({
                    'title': post.get('title', {}).get('rendered', ''),
                    'url': post.get('link', ''),
                    'source': 'TechCrunch',
                    'score': 0,
                    'summary': post.get('excerpt', {}).get('rendered', '')[:300]
                })
            return articles
    except Exception as e:
        print(f"获取 TechCrunch 失败: {e}")
    return []

def ai_summarize(articles):
    """调用本地 AI 生成中文摘要"""
    if not articles:
        return articles
    
    # 构建提示词
    prompt = "请用中文为以下每篇文章生成简洁的摘要（每篇30-50字），并提炼出核心价值：\n\n"
    for i, article in enumerate(articles):
        prompt += f"{i+1}. 标题: {article['title']}\n"
        if article.get('summary'):
            prompt += f"   原文摘要: {article['summary'][:200]}\n"
        prompt += f"   来源: {article['source']}\n\n"
    prompt += "请按以下格式返回：\n"
    prompt += "1. [文章标题] 摘要: xxx\n"
    prompt += "2. [文章标题] 摘要: xxx\n"
    prompt += "..."
    
    try:
        # 调用 Ollama API
        payload = {
            "model": AI_MODEL,
            "prompt": prompt,
            "stream": False,
            "temperature": 0.7,
            "max_tokens": 2000
        }
        response = requests.post(
            f"{AI_API_URL}/api/generate",
            json=payload,
            timeout=120
        )
        if response.status_code == 200:
            result = response.json()
            ai_output = result.get('response', '')
            print(f"AI 响应: {ai_output[:200]}...")
            
            # 解析 AI 输出并更新文章摘要
            lines = ai_output.strip().split('\n')
            for line in lines:
                if line.strip():
                    for i, article in enumerate(articles):
                        if article['title'] in line:
                            # 提取摘要部分
                            if '摘要:' in line or '摘要：' in line:
                                summary_part = line.split('摘要:')[-1].split('摘要：')[-1].strip()
                                article['ai_summary'] = summary_part
                            break
        else:
            print(f"AI API 调用失败: {response.status_code}")
    except Exception as e:
        print(f"AI 调用错误: {e}")
    
    return articles

def generate_markdown(articles, date_str):
    """生成 Markdown 内容"""
    content = f"""---
title: 科技前沿快报 {date_str}
sidebar_position: 1
tags: [科技, AI, 前沿, 每日更新]
---

# 🚀 科技前沿快报 - {date_str}

> 由 AI 自动抓取全网科技资讯，每6小时更新一次
> 🤖 本文包含 AI 生成摘要

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
                content += f"### **[{title}]({url})** 🔥 热度: {score}\n"
            else:
                content += f"### **[{title}]({url})**\n"
            
            # AI 摘要或原文摘要
            if item.get('ai_summary'):
                content += f"> 💡 {item.get('ai_summary')}\n\n"
            elif item.get('summary'):
                content += f"> 📝 {item.get('summary')}\n\n"
            else:
                content += "\n"
    
    content += f"\n---\n\n*最后更新: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
    content += f"*共抓取 {len(articles)} 篇科技资讯*"
    return content

def main():
    print("🚀 开始抓取科技资讯...")
    print(f"🤖 AI API: {AI_API_URL}")
    
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
    
    # AI 摘要
    print("🧠 正在调用 AI 生成摘要...")
    all_articles = ai_summarize(all_articles)
    ai_count = sum(1 for a in all_articles if a.get('ai_summary'))
    print(f"✅ AI 摘要生成: {ai_count}/{len(all_articles)} 篇")
    
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