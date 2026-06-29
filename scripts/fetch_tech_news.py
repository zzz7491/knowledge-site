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

# 配置 - 阿里云百炼平台
AI_API_URL = "https://ws-n29fiz9196oqjon0.cn-beijing.maas.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
AI_MODEL = "qwen-turbo"
DASHSCOPE_API_KEY = os.environ.get('DASHSCOPE_API_KEY', '')

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

def ai_translate_and_summarize(articles):
    """调用阿里云百炼平台翻译并生成中文摘要"""
    if not articles:
        return articles
    
    if not DASHSCOPE_API_KEY:
        print("❌ 错误: 未设置 DASHSCOPE_API_KEY 环境变量")
        return articles
    
    prompt = """你是一个资深科技编辑，精通中英文。请将以下科技资讯翻译成通顺流畅的中文，并生成专业的中文摘要。

要求：
1. 标题翻译要准确、简洁、吸引人
2. 摘要控制在50-80字，要包含核心观点
3. 必须用专业、流畅的中文表达
4. 不要直译，要意译成符合中文阅读习惯的表达

以下是待处理的文章：

"""
    for i, article in enumerate(articles):
        prompt += f"\n文章 {i+1}:\n"
        prompt += f"标题: {article['title']}\n"
        prompt += f"来源: {article['source']}\n"
        if article.get('content'):
            prompt += f"内容: {article['content'][:1000]}\n"
        elif article.get('summary'):
            prompt += f"摘要: {article['summary']}\n"
        elif article.get('text'):
            prompt += f"描述: {article['text']}\n"
        prompt += "\n"
    
    prompt += """
请按以下格式返回（每篇文章用空行分隔，全部用中文）：

文章1:
标题: [准确的中文标题]
摘要: [50-80字的中文摘要]
核心观点: [一句话概括核心价值]
关键信息: [3-5个关键词]

文章2:
标题: [准确的中文标题]
摘要: [50-80字的中文摘要]
核心观点: [一句话概括核心价值]
关键信息: [3-5个关键词]

...以此类推

注意：所有输出必须使用中文，标题要翻得准确，摘要要翻得流畅专业。"""
    
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {DASHSCOPE_API_KEY}'
        }
        
        payload = {
            "model": AI_MODEL,
            "input": {
                "messages": [
                    {"role": "system", "content": "你是一个专业的科技编辑，擅长中英互译和科技内容摘要。只输出中文，确保翻译准确、表达流畅。"},
                    {"role": "user", "content": prompt}
                ]
            },
            "parameters": {
                "temperature": 0.3,
                "max_tokens": 4000
            }
        }
        
        response = requests.post(
            AI_API_URL,
            json=payload,
            headers=headers,
            timeout=180
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'output' in result and 'text' in result['output']:
                ai_output = result['output']['text']
            elif 'choices' in result and len(result['choices']) > 0:
                ai_output = result['choices'][0]['message']['content']
            else:
                print(f"未知的API响应格式: {result}")
                return articles
            
            print(f"AI 响应长度: {len(ai_output)} 字符")
            
            lines = ai_output.strip().split('\n')
            current_idx = -1
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                match = re.match(r'^文章\s*(\d+)[:：]', line)
                if match:
                    current_idx = int(match.group(1)) - 1
                    title_part = line.replace(match.group(0), '').strip()
                    if title_part and 0 <= current_idx < len(articles):
                        if '标题' in title_part:
                            articles[current_idx]['ai_title'] = title_part.replace('标题:', '').replace('标题：', '').strip()
                    continue
                
                if 0 <= current_idx < len(articles):
                    if line.startswith('标题') or line.startswith('标题:'):
                        articles[current_idx]['ai_title'] = line.replace('标题:', '').replace('标题：', '').strip()
                    elif line.startswith('摘要') or line.startswith('摘要:'):
                        articles[current_idx]['ai_summary'] = line.replace('摘要:', '').replace('摘要：', '').strip()
                    elif line.startswith('核心观点') or line.startswith('核心观点:'):
                        articles[current_idx]['ai_value'] = line.replace('核心观点:', '').replace('核心观点：', '').strip()
                    elif line.startswith('关键信息') or line.startswith('关键信息:'):
                        articles[current_idx]['ai_keypoints'] = line.replace('关键信息:', '').replace('关键信息：', '').strip()
        else:
            print(f"阿里云API调用失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"AI 调用错误: {e}")
    
    return articles

def generate_markdown(articles, date_str):
    """生成 Markdown 内容 - 优化排版"""
    content = f"""---
title: 科技前沿快报 {date_str}
sidebar_position: 1
tags: [科技, AI, 前沿, 每日更新]
---

# 🚀 科技前沿快报 - {date_str}

> 🤖 自动精选全球科技资讯，中文摘要由通义千问生成
> 📅 每日更新 | 每6小时刷新

---
"""
    sources = {}
    for article in articles:
        source = article.get('source', '其他')
        if source not in sources:
            sources[source] = []
        sources[source].append(article)
    
    for source, items in sources.items():
        icons = {
            'Hacker News': '💬',
            'arXiv AI': '📄',
            'TechCrunch': '📰'
        }
        icon = icons.get(source, '📌')
        content += f"\n## {icon} {source}\n\n"
        content += f"共 {len(items)} 条\n\n"
        
        for idx, item in enumerate(items, 1):
            title = item.get('ai_title') or item.get('title', '').strip()
            url = item.get('url', '#')
            
            score_tag = ''
            if item.get('score'):
                score = item.get('score')
                if score > 500:
                    score_tag = ' 🔥🔥🔥'
                elif score > 200:
                    score_tag = ' 🔥🔥'
                elif score > 50:
                    score_tag = ' 🔥'
                score_tag += f' 热度: {score}'
            
            content += f"### {idx}. {title}{score_tag}\n\n"
            
            if item.get('ai_summary'):
                content += f"> {item.get('ai_summary')}\n\n"
            elif item.get('summary'):
                content += f"> {item.get('summary')}\n\n"
            
            if item.get('ai_value') or item.get('ai_keypoints'):
                content += "**💡 核心观点**\n\n"
                if item.get('ai_value'):
                    content += f"- {item.get('ai_value')}\n"
                if item.get('ai_keypoints'):
                    content += f"- **关键信息**：{item.get('ai_keypoints')}\n"
                content += "\n"
            
            content += f"📎 [阅读原文]({url})\n\n"
            content += "---\n\n"
    
    content += f"\n📊 **本次更新统计**\n"
    content += f"- 共抓取 {len(articles)} 篇科技资讯\n"
    content += f"- AI 生成中文摘要\n"
    content += f"- 更新时间: {datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M')}\n"
    
    return content

def main():
    print("🚀 开始抓取科技资讯...")
    print(f"🤖 AI: 阿里云通义千问 ({AI_MODEL})")
    
    if not DASHSCOPE_API_KEY:
        print("❌ 错误: 请设置 DASHSCOPE_API_KEY 环境变量")
        return
    
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
    
    print(f"🧠 正在调用阿里云通义千问翻译并生成摘要 ({len(all_articles)} 篇)...")
    all_articles = ai_translate_and_summarize(all_articles)
    ai_count = sum(1 for a in all_articles if a.get('ai_summary'))
    print(f"✅ AI 生成摘要: {ai_count}/{len(all_articles)} 篇")
    
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    md_content = generate_markdown(all_articles, date_str)
    
    docs_dir = Path('docs/每日更新')
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成当天文件
    today_file = docs_dir / f'{date_str}-快报.md'
    with open(today_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    # 滚动更新：只保留最近7个快报文件
    all_files = sorted(docs_dir.glob('*-快报.md'), reverse=True)
    for old_file in all_files[7:]:
        old_file.unlink()
        print(f"🗑️ 已删除旧文件: {old_file.name}")
    
    print(f"✅ 已生成: {today_file}")
    print(f"📊 共 {len(all_articles)} 篇文章")
    
    # 获取保留文件数量
    remaining_files = list(docs_dir.glob('*-快报.md'))
    print(f"📁 当前保留 {len(remaining_files)} 个快报文件")

if __name__ == '__main__':
    main()