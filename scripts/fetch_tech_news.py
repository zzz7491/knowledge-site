#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import requests
import datetime
import time
import re
from pathlib import Path
from urllib.parse import urlparse

# 配置
AI_API_URL = os.environ.get('AI_API_URL', 'http://585351.xyz:34567')
AI_MODEL = 'glm-4-9b'

HACKER_NEWS_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"
ARXIV_QUERY_URL = "http://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=submittedDate&max_results=5"
TECHCRUNCH_URL = "https://techcrunch.com/wp-json/wp/v2/posts?categories=147&per_page=5"

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
                        # 获取文章内容
                        url = item.get('url', f"https://news.ycombinator.com/item?id={sid}")
                        content = fetch_article_content(url) if url else ''
                        articles.append({
                            'title': item.get('title', ''),
                            'url': url,
                            'score': item.get('score', 0),
                            'source': 'Hacker News',
                            'content': content[:3000] if content else '',
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
                    'content': content[:3000] if content else '',
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
        # 使用 requests 获取 HTML
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        resp = requests.get(url, timeout=15, headers=headers)
        if resp.status_code == 200:
            # 简单提取文本（去除 HTML 标签）
            import re
            text = re.sub(r'<[^>]+>', ' ', resp.text)
            text = re.sub(r'\s+', ' ', text).strip()
            return text[:3000]
    except Exception as e:
        print(f"抓取内容失败 {url}: {e}")
    return ''

def ai_translate_and_summarize(articles):
    """调用 AI 翻译并生成中文摘要"""
    if not articles:
        return articles
    
    # 构建提示词
    prompt = "你是一个科技新闻编辑。请将以下科技资讯翻译成中文，并为每篇文章生成精炼的摘要（50-80字），突出核心价值：\n\n"
    for i, article in enumerate(articles):
        prompt += f"{i+1}. 标题: {article['title']}\n"
        prompt += f"   来源: {article['source']}\n"
        if article.get('content'):
            prompt += f"   内容: {article['content'][:800]}\n"
        elif article.get('summary'):
            prompt += f"   摘要: {article['summary']}\n"
        elif article.get('text'):
            prompt += f"   描述: {article['text']}\n"
        prompt += "\n"
    
    prompt += """请按以下格式返回（每篇文章用空行分隔）：
    
[文章编号]. 中文标题: xxx
中文摘要: xxx
核心价值: xxx
关键要点: xxx

注意：直接用中文输出，不要用英文。"""
    
    try:
        payload = {
            "model": AI_MODEL,
            "prompt": prompt,
            "stream": False,
            "temperature": 0.5,
            "max_tokens": 4000
        }
        response = requests.post(
            f"{AI_API_URL}/api/generate",
            json=payload,
            timeout=180
        )
        if response.status_code == 200:
            result = response.json()
            ai_output = result.get('response', '')
            print(f"AI 响应长度: {len(ai_output)} 字符")
            
            # 解析 AI 输出
            lines = ai_output.strip().split('\n')
            current_idx = 0
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # 匹配 [编号] 或 编号.
                match = re.match(r'^(\d+)\.?\s*', line)
                if match:
                    idx = int(match.group(1)) - 1
                    if 0 <= idx < len(articles):
                        articles[idx]['ai_title'] = line.replace(match.group(0), '').strip()
                elif line.startswith('中文摘要:') or line.startswith('中文摘要：'):
                    if current_idx < len(articles):
                        articles[current_idx]['ai_summary'] = line.replace('中文摘要:', '').replace('中文摘要：', '').strip()
                elif line.startswith('核心价值:') or line.startswith('核心价值：'):
                    if current_idx < len(articles):
                        articles[current_idx]['ai_value'] = line.replace('核心价值:', '').replace('核心价值：', '').strip()
                elif line.startswith('关键要点:') or line.startswith('关键要点：'):
                    if current_idx < len(articles):
                        articles[current_idx]['ai_keypoints'] = line.replace('关键要点:', '').replace('关键要点：', '').strip()
                elif re.match(r'^\d+', line):
                    # 新文章开始
                    match2 = re.match(r'^(\d+)', line)
                    if match2:
                        current_idx = int(match2.group(1)) - 1
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

> 🤖 由 AI 自动抓取并生成中文摘要，每6小时更新一次

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
        for idx, item in enumerate(items, 1):
            title = item.get('ai_title') or item.get('title', '').strip()
            url = item.get('url', '#')
            
            content += f"### {idx}. {title}\n\n"
            content += f"🔗 [原文链接]({url})\n\n"
            
            if item.get('ai_summary'):
                content += f"📝 **摘要**：{item.get('ai_summary')}\n\n"
            elif item.get('summary'):
                content += f"📝 **摘要**：{item.get('summary')}\n\n"
            
            if item.get('ai_value'):
                content += f"💡 **核心价值**：{item.get('ai_value')}\n\n"
            
            if item.get('ai_keypoints'):
                content += f"📌 **关键要点**：{item.get('ai_keypoints')}\n\n"
            
            if item.get('score'):
                content += f"🔥 **热度**：{item.get('score')}\n\n"
            
            content += "---\n\n"
    
    content += f"\n*最后更新: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
    content += f"*共抓取 {len(articles)} 篇科技资讯，AI 生成中文摘要*"
    return content

def main():
    print("🚀 开始抓取科技资讯...")
    print(f"🤖 AI API: {AI_API_URL}")
    
    # 获取所有来源
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
        print("⚠️ 没有抓取到任何文章")
        return
    
    # AI 翻译和摘要
    print(f"🧠 正在调用 AI 翻译并生成摘要 ({len(all_articles)} 篇)...")
    all_articles = ai_translate_and_summarize(all_articles)
    ai_count = sum(1 for a in all_articles if a.get('ai_summary'))
    print(f"✅ AI 生成摘要: {ai_count}/{len(all_articles)} 篇")
    
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