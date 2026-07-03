#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
番茄小说下载脚本 - 基于fanqienovel-downloader开源项目
用于搜索并下载指定小说全文
"""
import requests as req
import json
import time
import random
import os
import re
from lxml import html as lxml_html

# 配置
SAVE_DIR = "/workspace/downloads"
os.makedirs(SAVE_DIR, exist_ok=True)

HEADERS_LIB = [
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'},
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'},
]

# 加载charset
charset_path = "/workspace/fanqienovel-downloader/src/charset.json"
with open(charset_path, 'r', encoding='UTF-8') as f:
    CHARSET = json.load(f)

CODE = [[58344, 58715], [58345, 58716]]

def decode_content(content):
    """解码小说内容"""
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

def get_session():
    """创建HTTP session"""
    session = req.Session()
    session.headers.update({
        'User-Agent': random.choice(HEADERS_LIB)['User-Agent'],
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    })
    return session

def search_novel(keyword):
    """搜索小说"""
    print(f"\n搜索: {keyword}")
    url = "https://api5-normal-lf.fqnovel.com/reading/bookapi/search/page/v/"
    params = {
        "query": keyword,
        "aid": "1967",
        "channel": "0",
        "os_version": "0",
        "device_type": "0",
        "device_platform": "0",
        "iid": "466614321180296",
        "passback": "0",
        "version_code": "999"
    }
    
    session = get_session()
    try:
        resp = session.get(url, params=params, timeout=10)
        data = resp.json()
        
        if data.get('code') == 0 and data.get('data'):
            books = data['data']
            print(f"找到 {len(books)} 个结果:\n")
            for i, book in enumerate(books):
                book_id = book.get('book_id', '')
                title = book.get('book_name', '')
                author = book.get('author', '')
                word_count = book.get('word_count', 0)
                status = book.get('creation_status', 0)
                status_text = "已完结" if status == 1 else "连载中"
                desc = book.get('abstract', '')[:80]
                print(f"  [{i+1}] 《{title}》 - {author}")
                print(f"      ID: {book_id} | {word_count}字 | {status_text}")
                print(f"      简介: {desc}...")
                print()
            return books
        else:
            print(f"搜索失败: {data.get('msg', '未知错误')}")
            return []
    except Exception as e:
        print(f"搜索出错: {e}")
        return []

def get_chapter_list(session, book_id):
    """获取章节列表"""
    url = f"https://fanqienovel.com/page/{book_id}"
    
    try:
        resp = session.get(url, timeout=15)
        resp.raise_for_status()
        
        tree = lxml_html.fromstring(resp.content)
        
        # 获取书名
        name_elem = tree.xpath('//h1/text()')
        name = name_elem[0].strip() if name_elem else "未知书名"
        
        # 获取章节列表
        chapters = {}
        chapter_elements = tree.xpath('//div[@class="chapter-item"]//a')
        
        if not chapter_elements:
            # 尝试其他选择器
            chapter_elements = tree.xpath('//a[contains(@href, "/reader/")]')
        
        for elem in chapter_elements:
            href = elem.get('href', '')
            title = elem.text_content().strip()
            if title and '/reader/' in href:
                chapter_id = href.split('/reader/')[-1].split('?')[0]
                chapters[title] = chapter_id
        
        # 获取状态
        status_elem = tree.xpath('//span[contains(text(), "完结") or contains(text(), "连载")]')
        status = [s.text_content().strip() for s in status_elem]
        
        return name, chapters, status
    except Exception as e:
        print(f"获取章节列表失败: {e}")
        return "err", {}, []

def get_cookie(session):
    """获取有效的cookie"""
    print("正在获取cookie...")
    
    # 先尝试获取一个测试章节ID
    test_url = "https://fanqienovel.com/page/7143038691944959011"
    try:
        resp = session.get(test_url, timeout=15)
        tree = lxml_html.fromstring(resp.content)
        chapter_links = tree.xpath('//a[contains(@href, "/reader/")]')
        
        if not chapter_links:
            print("无法获取测试章节")
            return None
        
        test_chapter_id = chapter_links[0].get('href', '').split('/reader/')[-1].split('?')[0]
    except Exception as e:
        print(f"获取测试章节失败: {e}")
        return None
    
    # 尝试不同的cookie值
    base = 1000000000000000000
    for i in range(random.randint(base * 6, base * 7), base * 9):
        time.sleep(random.randint(50, 150) / 1000)
        cookie = f'novel_web_id={i}'
        
        try:
            content_url = f"https://fanqienovel.com/reader/{test_chapter_id}"
            resp = session.get(content_url, headers={'Cookie': cookie}, timeout=10)
            tree = lxml_html.fromstring(resp.content)
            
            # 检查是否有内容
            content_elem = tree.xpath('//div[@id="chapterContent"]//p')
            if content_elem and len(content_elem) > 3:
                print(f"Cookie获取成功: {cookie}")
                return cookie
        except:
            continue
    
    print("Cookie获取失败")
    return None

def download_chapter(session, chapter_id, cookie):
    """下载单个章节"""
    url = f"https://fanqienovel.com/reader/{chapter_id}"
    
    try:
        resp = session.get(url, headers={'Cookie': cookie}, timeout=10)
        tree = lxml_html.fromstring(resp.content)
        
        # 提取章节内容
        content_elems = tree.xpath('//div[@id="chapterContent"]//p/text()')
        if not content_elems:
            content_elems = tree.xpath('//div[contains(@class, "muye-reader-content")]//p/text()')
        if not content_elems:
            content_elems = tree.xpath('//p/text()')
        
        content = '\n'.join(content_elems)
        content = decode_content(content)
        
        return content
    except Exception as e:
        return ""

def download_novel(book_id, cookie):
    """下载完整小说"""
    session = get_session()
    
    print(f"\n获取章节列表...")
    name, chapters, status = get_chapter_list(session, book_id)
    
    if name == 'err' or not chapters:
        print("获取章节列表失败！")
        print("可能原因：该书是短故事(非长篇小说)，需要通过APP阅读")
        return False
    
    print(f"书名: {name}")
    print(f"状态: {', '.join(status) if status else '未知'}")
    print(f"章节数: {len(chapters)}")
    
    # 下载所有章节
    print(f"\n开始下载...")
    all_content = [f"《{name}》\n{'='*50}\n\n"]
    
    success_count = 0
    fail_count = 0
    
    for idx, (title, chapter_id) in enumerate(chapters.items(), 1):
        content = download_chapter(session, chapter_id, cookie)
        
        if content and len(content) > 50:
            all_content.append(f"\n{title}\n{'-'*30}\n{content}\n")
            success_count += 1
            print(f"  [{idx}/{len(chapters)}] {title} - 成功")
        else:
            fail_count += 1
            print(f"  [{idx}/{len(chapters)}] {title} - 失败(可能需要登录)")
        
        time.sleep(random.randint(50, 150) / 1000)
    
    # 保存文件
    safe_name = re.sub(r'[\\/*?:"<>|]', '_', name)
    output_path = os.path.join(SAVE_DIR, f"{safe_name}.txt")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_content))
    
    print(f"\n下载完成!")
    print(f"成功: {success_count} 章, 失败: {fail_count} 章")
    print(f"保存路径: {output_path}")
    
    return True

def main():
    print("=" * 50)
    print("     番茄小说下载器")
    print("=" * 50)
    
    # 第一步：搜索
    books = search_novel("九九无归路")
    
    if not books:
        print("\n未找到《九九无归路》，尝试其他搜索...")
        books = search_novel("九九无归")
    
    if not books:
        print("\n仍然未找到。该书可能是番茄小说的【短故事】(非长篇小说)")
        print("短故事只能通过番茄小说APP阅读，网页版无法下载。")
        print("\n建议：")
        print("  1. 在番茄小说APP中打开该书")
        print("  2. 长按文字 → 全选 → 复制")
        print("  3. 粘贴到文件中保存")
        return
    
    # 第二步：选择
    print("\n请选择要下载的编号 (输入序号):")
    choice = input("> ").strip()
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(books):
            book = books[idx]
            book_id = book.get('book_id', '')
            print(f"\n选择了: 《{book.get('book_name', '')}》 (ID: {book_id})")
        else:
            print("无效选择")
            return
    except (ValueError, IndexError):
        print("无效输入")
        return
    
    # 第三步：获取cookie
    session = get_session()
    cookie = get_cookie(session)
    
    if not cookie:
        print("\n无法获取cookie，部分章节可能无法下载")
        cookie = ""
    
    # 第四步：下载
    download_novel(book_id, cookie)

if __name__ == "__main__":
    main()
