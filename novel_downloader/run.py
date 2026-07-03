#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
番茄小说下载器 - 精简独立版
基于 fanqienovel-downloader 开源项目核心逻辑
"""
import requests as req
from lxml import etree
from bs4 import BeautifulSoup
import json
import time
import random
import os
import re
import sys

SAVE_DIR = "/workspace/downloads"
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

def decode_content(content, mode=0):
    """解码番茄小说内容"""
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

def search_novel(keyword):
    """搜索小说"""
    print(f"\n{'='*50}")
    print(f"搜索: {keyword}")
    print(f"{'='*50}")
    
    url = "https://fanqienovel.com"
    # 通过网页搜索
    search_url = f"{url}/library"
    
    session = req.Session()
    session.headers.update(HEADERS)
    
    # 方法1: 使用网页版搜索页面
    try:
        resp = session.get(f"{url}/library", params={"query": keyword}, timeout=15)
        tree = etree.HTML(resp.text)
        
        # 尝试从搜索结果中提取
        book_links = tree.xpath('//a[contains(@href, "/page/")]')
        results = []
        seen_ids = set()
        
        for link in book_links:
            href = link.get('href', '')
            book_id = href.split('/page/')[-1].split('?')[0].split('/')[0] if '/page/' in href else ''
            
            if book_id and book_id.isdigit() and book_id not in seen_ids:
                seen_ids.add(book_id)
                title = link.text_content().strip()
                if title and len(title) > 1:
                    results.append({'book_id': book_id, 'title': title})
        
        if results:
            print(f"找到 {len(results)} 个结果:\n")
            for i, r in enumerate(results):
                print(f"  [{i+1}] 《{r['title']}》 (ID: {r['book_id']})")
            return results
    except Exception as e:
        print(f"网页搜索出错: {e}")
    
    # 方法2: 直接通过页面访问验证
    print("\n尝试直接验证...")
    return []

def get_cookie(session):
    """获取有效的novel_web_id cookie"""
    print("\n正在获取cookie（这可能需要1-2分钟）...")
    
    # 先获取一个测试章节
    test_novel_id = "7143038691944959011"
    try:
        resp = session.get(f"https://fanqienovel.com/page/{test_novel_id}", headers=HEADERS, timeout=15)
        tree = etree.HTML(resp.text)
        a_elements = tree.xpath('//div[@class="chapter"]/div/a')
        
        if not a_elements:
            print("无法获取测试章节，跳过cookie获取")
            return ""
        
        # 取一个后面的章节ID
        test_chapter_id = a_elements[-1].get('href', '').split('/')[-1]
    except Exception as e:
        print(f"获取测试章节失败: {e}")
        return ""
    
    base = 1000000000000000000
    start = random.randint(base * 6, base * 7)
    end = base * 9
    
    for i in range(start, end):
        time.sleep(random.randint(50, 150) / 1000)
        cookie = f'novel_web_id={i}'
        
        try:
            headers = HEADERS.copy()
            headers['cookie'] = cookie
            
            resp = session.get(
                f"https://fanqienovel.com/reader/{test_chapter_id}",
                headers=headers,
                timeout=10
            )
            
            content = '\n'.join(
                etree.HTML(resp.text).xpath(
                    '//div[@class="muye-reader-content noselect"]//p/text()'
                )
            )
            
            if len(content) > 200:
                print(f"Cookie获取成功!")
                return cookie
        except:
            continue
    
    print("Cookie获取失败，将尝试不带cookie下载")
    return ""

def get_chapter_list(session, novel_id):
    """获取小说章节列表"""
    url = f"https://fanqienovel.com/page/{novel_id}"
    
    try:
        resp = session.get(url, headers=HEADERS, timeout=15)
        tree = etree.HTML(resp.text)
        
        # 获取书名
        title_elem = tree.xpath('//h1/text()')
        name = title_elem[0].strip() if title_elem else "未知"
        
        # 获取状态
        status_elem = tree.xpath('//span[@class="info-label-yellow"]/text()')
        status = status_elem if status_elem else ["未知"]
        
        # 获取章节
        chapters = {}
        a_elements = tree.xpath('//div[@class="chapter"]/div/a')
        
        for a in a_elements:
            href = a.get('href', '')
            title = a.text
            if href and title:
                chapter_id = href.split('/')[-1]
                chapters[title] = chapter_id
        
        return name, chapters, status
    except Exception as e:
        print(f"获取章节列表失败: {e}")
        return "err", {}, []

def download_chapter(session, chapter_id, cookie):
    """下载单个章节内容"""
    headers = HEADERS.copy()
    if cookie:
        headers['cookie'] = cookie
    
    for attempt in range(3):
        try:
            # 方法1: 网页解析
            resp = session.get(
                f"https://fanqienovel.com/reader/{chapter_id}",
                headers=headers,
                timeout=10
            )
            
            content = '\n'.join(
                etree.HTML(resp.text).xpath(
                    '//div[@class="muye-reader-content noselect"]//p/text()'
                )
            )
            
            if content and len(content) > 50:
                return decode_content(content)
            
            # 方法2: API
            resp2 = session.get(
                f"https://fanqienovel.com/api/reader/full?itemId={chapter_id}",
                headers=headers,
                timeout=10
            )
            data = resp2.json()
            api_content = data.get('data', {}).get('chapterData', {}).get('content', '')
            if api_content:
                return decode_content(api_content)
            
        except Exception as e:
            if attempt == 2:
                return ""
            time.sleep(1)
    
    return ""

def download_novel(book_id, cookie=""):
    """下载完整小说"""
    session = req.Session()
    session.headers.update(HEADERS)
    
    print(f"\n获取章节列表 (ID: {book_id})...")
    name, chapters, status = get_chapter_list(session, book_id)
    
    if name == 'err' or not chapters:
        print("获取章节列表失败！")
        print("可能原因:")
        print("  1. 该ID不是有效的长篇小说")
        print("  2. 网络连接问题")
        print("  3. 该书是短故事，只能通过APP阅读")
        return False
    
    print(f"\n书名: {name}")
    print(f"状态: {status[0] if status else '未知'}")
    print(f"章节数: {len(chapters)}")
    print(f"\n开始下载...")
    
    all_text = [f"《{name}》\n{'='*50}\n\n"]
    success = 0
    fail = 0
    
    for idx, (title, chapter_id) in enumerate(chapters.items(), 1):
        content = download_chapter(session, chapter_id, cookie)
        
        if content and len(content) > 50:
            all_text.append(f"\n{title}\n{'-'*30}\n{content}\n")
            success += 1
            print(f"  [{idx}/{len(chapters)}] {title} ✓")
        else:
            fail += 1
            print(f"  [{idx}/{len(chapters)}] {title} ✗ (空内容/需登录)")
        
        time.sleep(random.randint(50, 150) / 1000)
    
    # 保存
    safe_name = re.sub(r'[\\/*?:"<>|]', '_', name)
    output_path = os.path.join(SAVE_DIR, f"{safe_name}.txt")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_text))
    
    print(f"\n{'='*50}")
    print(f"下载完成!")
    print(f"成功: {success} 章 | 失败: {fail} 章")
    print(f"保存: {output_path}")
    print(f"{'='*50}")
    
    return True

def main():
    print("=" * 50)
    print("  番茄小说下载器")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        # 命令行模式：直接用ID下载
        book_id = sys.argv[1]
        print(f"\n直接下载 ID: {book_id}")
        session = req.Session()
        cookie = get_cookie(session)
        download_novel(book_id, cookie)
    else:
        # 交互模式
        print("\n选择操作:")
        print("  1. 搜索小说")
        print("  2. 输入ID直接下载")
        print("  3. 输入URL直接下载")
        
        choice = input("\n请选择 (1/2/3): ").strip()
        
        if choice == '1':
            keyword = input("输入搜索关键词: ").strip()
            results = search_novel(keyword)
            
            if results:
                idx = input(f"\n选择编号 (1-{len(results)}): ").strip()
                try:
                    book = results[int(idx) - 1]
                    session = req.Session()
                    cookie = get_cookie(session)
                    download_novel(book['book_id'], cookie)
                except (ValueError, IndexError):
                    print("无效选择")
        
        elif choice == '2':
            book_id = input("输入书籍ID: ").strip()
            session = req.Session()
            cookie = get_cookie(session)
            download_novel(book_id, cookie)
        
        elif choice == '3':
            url = input("输入书籍URL: ").strip()
            book_id = url.split('/page/')[-1].split('?')[0].split('/')[0]
            session = req.Session()
            cookie = get_cookie(session)
            download_novel(book_id, cookie)

if __name__ == "__main__":
    main()
