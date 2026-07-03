#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下载《攀龙》- 咔叽黄桃
书籍ID: 7546956076533419070
共483章，105.2万字
"""
import requests
from lxml import etree
import json
import time
import random
import os
import re
import sys

# 配置
BOOK_ID = "7546956076533419070"
BOOK_NAME = "攀龙"
AUTHOR = "咔叽黄桃"
SAVE_DIR = "/workspace/downloads"
OUTPUT_FILE = os.path.join(SAVE_DIR, f"{BOOK_NAME}_{AUTHOR}.txt")
os.makedirs(SAVE_DIR, exist_ok=True)

# 加载charset解码表
charset_path = "/workspace/fanqienovel-downloader/src/charset.json"
with open(charset_path, 'r', encoding='UTF-8') as f:
    CHARSET = json.load(f)

CODE = [[58344, 58715], [58345, 58716]]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

def decode_content(content):
    if not content:
        return ""
    result = []
    for char in content:
        code = ord(char)
        decoded = None
        for i, (start, end) in enumerate(CODE):
            if start <= code <= end:
                decoded = CHARSET[str(i)].get(str(code - start), char)
                break
        result.append(decoded if decoded else char)
    return ''.join(result)

def get_chapter_list():
    """从网页获取完整章节列表"""
    print(f"获取章节列表...")
    url = f"https://fanqienovel.com/page/{BOOK_ID}"
    
    resp = requests.get(url, headers=HEADERS, timeout=15)
    tree = etree.HTML(resp.text)
    
    # 获取所有章节链接
    chapters = []
    a_elements = tree.xpath('//div[@class="chapter"]//a')
    
    for a in a_elements:
        href = a.get('href', '')
        title = a.text
        if href and title and '/reader/' in href:
            chapter_id = href.split('/reader/')[-1]
            chapters.append((title.strip(), chapter_id))
    
    print(f"  找到 {len(chapters)} 章")
    return chapters

def get_cookie():
    """获取有效的novel_web_id cookie"""
    print("获取阅读cookie...")
    
    # 用本书的第一章作为测试
    test_chapter_id = "7546956235237507646"  # 第1章
    
    base = 1000000000000000000
    start = random.randint(base * 6, base * 7)
    end = start + 100  # 先测试100个
    
    for i in range(start, end):
        time.sleep(random.randint(30, 80) / 1000)
        cookie = f'novel_web_id={i}'
        
        try:
            headers = HEADERS.copy()
            headers['cookie'] = cookie
            
            resp = requests.get(
                f"https://fanqienovel.com/reader/{test_chapter_id}",
                headers=headers,
                timeout=10
            )
            
            tree = etree.HTML(resp.text)
            content = '\n'.join(
                tree.xpath('//div[@class="muye-reader-content noselect"]//p/text()')
            )
            
            if len(content) > 200:
                print(f"  Cookie获取成功: novel_web_id={i}")
                return cookie
        except:
            pass
    
    print("  Cookie获取失败，尝试不带cookie下载...")
    return ""

def download_chapter(session, chapter_id, cookie, title):
    """下载单个章节"""
    headers = HEADERS.copy()
    if cookie:
        headers['cookie'] = cookie
    
    for attempt in range(3):
        try:
            resp = session.get(
                f"https://fanqienovel.com/reader/{chapter_id}",
                headers=headers,
                timeout=10
            )
            
            tree = etree.HTML(resp.text)
            
            # 尝试多种xpath
            content = '\n'.join(
                tree.xpath('//div[@class="muye-reader-content noselect"]//p/text()')
            )
            
            if not content or len(content) < 50:
                content = '\n'.join(
                    tree.xpath('//div[@id="chapterContent"]//p/text()')
                )
            
            if content and len(content) > 50:
                return decode_content(content)
                
        except Exception as e:
            if attempt == 2:
                return ""
            time.sleep(1)
    
    return ""

def main():
    print("=" * 60)
    print(f"  下载《{BOOK_NAME}》 - {AUTHOR}")
    print(f"  书籍ID: {BOOK_ID}")
    print("=" * 60)
    
    # 获取章节列表
    chapters = get_chapter_list()
    
    if not chapters:
        print("获取章节列表失败！")
        return
    
    # 获取cookie
    session = requests.Session()
    session.headers.update(HEADERS)
    cookie = get_cookie()
    
    # 开始下载
    print(f"\n开始下载 {len(chapters)} 章...")
    print("-" * 60)
    
    all_text = [f"《{BOOK_NAME}》\n作者: {AUTHOR}\n{'=' * 50}\n\n"]
    
    success = 0
    fail = 0
    fail_chapters = []
    
    for idx, (title, chapter_id) in enumerate(chapters, 1):
        content = download_chapter(session, chapter_id, cookie, title)
        
        if content and len(content) > 50:
            all_text.append(f"\n{title}\n{'-' * 30}\n{content}\n")
            success += 1
            if idx % 10 == 0 or idx <= 5:
                print(f"  [{idx}/{len(chapters)}] {title} ✓")
        else:
            fail += 1
            fail_chapters.append((idx, title, chapter_id))
            print(f"  [{idx}/{len(chapters)}] {title} ✗")
        
        time.sleep(random.randint(50, 150) / 1000)
    
    # 保存文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_text))
    
    # 输出统计
    print(f"\n{'=' * 60}")
    print(f"  下载完成!")
    print(f"  成功: {success} 章")
    print(f"  失败: {fail} 章")
    print(f"  保存: {OUTPUT_FILE}")
    
    if fail_chapters:
        print(f"\n  失败章节列表:")
        for idx, title, ch_id in fail_chapters:
            print(f"    第{idx}章 {title} (ID: {ch_id})")
        
        # 保存失败列表供重试
        retry_file = os.path.join(SAVE_DIR, "fail_chapters.json")
        with open(retry_file, 'w', encoding='utf-8') as f:
            json.dump([{"idx": i, "title": t, "id": c} for i, t, c in fail_chapters], f, ensure_ascii=False, indent=2)
        print(f"  失败列表已保存: {retry_file}")
    
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
