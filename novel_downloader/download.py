#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
番茄小说下载器
基于番茄小说网页版API，用于下载指定小说的全部章节内容

⚠️ 使用前提：您已获得该小说的合法授权（如IP改编授权）
"""

import requests
import json
import time
import re
import os
import sys
from urllib.parse import urlparse, parse_qs
from pathlib import Path


class FanqieDownloader:
    """番茄小说下载器"""
    
    # 番茄小说相关API（基于网页版分析）
    BASE_URL = "https://fanqienovel.com"
    API_BASE = "https://fanqienovel.com/api"
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Referer": "https://fanqienovel.com/",
    }
    
    def __init__(self, output_dir: str = "downloads"):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def extract_book_id(self, url_or_id: str) -> str:
        """
        从URL或输入中提取书籍ID
        支持格式：
        - 纯数字ID: 7494874354086333464
        - 完整URL: https://fanqienovel.com/page/7494874354086333464
        - 分享URL: https://fanqienovel.com/reader/7494874354086333464
        """
        # 如果是纯数字
        if url_or_id.isdigit():
            return url_or_id
        
        # 从URL中提取
        parsed = urlparse(url_or_id)
        path_parts = parsed.path.strip('/').split('/')
        
        for part in path_parts:
            if part.isdigit():
                return part
        
        # 尝试从查询参数提取
        query = parse_qs(parsed.query)
        if 'book_id' in query:
            return query['book_id'][0]
        
        raise ValueError(f"无法从输入中提取书籍ID: {url_or_id}")
    
    def get_book_info(self, book_id: str) -> dict:
        """获取书籍基本信息"""
        url = f"{self.API_BASE}/book/info"
        params = {"book_id": book_id}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get("code") == 0:
                return data.get("data", {})
            else:
                print(f"获取书籍信息失败: {data.get('msg', '未知错误')}")
                return {}
        except Exception as e:
            print(f"请求失败: {e}")
            return {}
    
    def get_chapter_list(self, book_id: str) -> list:
        """获取书籍章节列表"""
        url = f"{self.API_BASE}/book/directory"
        params = {"book_id": book_id}
        
        chapters = []
        try:
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get("code") == 0:
                directory = data.get("data", {})
                # 解析目录结构
                for item in directory.get("item_list", []):
                    chapter = {
                        "chapter_id": item.get("item_id"),
                        "title": item.get("title", ""),
                        "is_locked": item.get("is_locked", False),
                    }
                    chapters.append(chapter)
            else:
                print(f"获取目录失败: {data.get('msg', '未知错误')}")
        except Exception as e:
            print(f"请求失败: {e}")
        
        return chapters
    
    def get_chapter_content(self, chapter_id: str) -> str:
        """获取单个章节内容"""
        url = f"{self.API_BASE}/reader/full"
        params = {"item_id": chapter_id}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get("code") == 0:
                content_data = data.get("data", {})
                content = content_data.get("content", "")
                # 清洗内容
                content = self._clean_content(content)
                return content
            else:
                return ""
        except Exception as e:
            print(f"获取章节内容失败: {e}")
            return ""
    
    def _clean_content(self, content: str) -> str:
        """清洗章节内容"""
        # 去除HTML标签
        content = re.sub(r'<[^>]+>', '', content)
        # 去除多余空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        # 去除特殊标记
        content = re.sub(r'【.*?】', '', content)
        return content.strip()
    
    def download_book(self, url_or_id: str, save_format: str = "txt") -> str:
        """
        下载完整书籍
        :param url_or_id: 书籍URL或ID
        :param save_format: 保存格式 (txt/json)
        :return: 保存的文件路径
        """
        book_id = self.extract_book_id(url_or_id)
        print(f"书籍ID: {book_id}")
        
        # 获取书籍信息
        print("正在获取书籍信息...")
        book_info = self.get_book_info(book_id)
        if not book_info:
            print("无法获取书籍信息，请检查书籍ID是否正确")
            return ""
        
        book_name = book_info.get("book_name", "未知书名")
        author = book_info.get("author", "未知作者")
        
        print(f"书名: {book_name}")
        print(f"作者: {author}")
        
        # 获取章节列表
        print("正在获取章节列表...")
        chapters = self.get_chapter_list(book_id)
        if not chapters:
            print("无法获取章节列表")
            return ""
        
        total = len(chapters)
        print(f"共 {total} 章")
        
        # 下载各章节
        print("开始下载章节内容...")
        downloaded_chapters = []
        
        for i, chapter in enumerate(chapters, 1):
            chapter_id = chapter["chapter_id"]
            chapter_title = chapter["title"]
            
            if chapter.get("is_locked"):
                print(f"  [{i}/{total}] {chapter_title} - 跳过（付费章节）")
                continue
            
            content = self.get_chapter_content(chapter_id)
            if content:
                downloaded_chapters.append({
                    "index": i,
                    "title": chapter_title,
                    "content": content
                })
                print(f"  [{i}/{total}] {chapter_title} - 成功")
            else:
                print(f"  [{i}/{total}] {chapter_title} - 失败")
            
            # 添加延迟，避免请求过快
            time.sleep(0.5)
        
        # 保存文件
        safe_name = re.sub(r'[\\/*?:"<>|]', "_", book_name)
        
        if save_format == "txt":
            output_path = self.output_dir / f"{safe_name}.txt"
            self._save_as_txt(output_path, book_name, author, downloaded_chapters)
        elif save_format == "json":
            output_path = self.output_dir / f"{safe_name}.json"
            self._save_as_json(output_path, book_name, author, downloaded_chapters)
        else:
            print(f"不支持的格式: {save_format}")
            return ""
        
        print(f"\n下载完成！")
        print(f"成功: {len(downloaded_chapters)}/{total} 章")
        print(f"保存路径: {output_path}")
        
        return str(output_path)
    
    def _save_as_txt(self, path: Path, book_name: str, author: str, chapters: list):
        """保存为TXT格式"""
        with open(path, 'w', encoding='utf-8') as f:
            # 写入书名和作者
            f.write(f"《{book_name}》\n")
            f.write(f"作者: {author}\n")
            f.write("=" * 50 + "\n\n")
            
            # 写入各章节
            for ch in chapters:
                f.write(f"\n{ch['title']}\n")
                f.write("-" * 30 + "\n")
                f.write(ch['content'])
                f.write("\n\n")
    
    def _save_as_json(self, path: Path, book_name: str, author: str, chapters: list):
        """保存为JSON格式"""
        data = {
            "book_name": book_name,
            "author": author,
            "total_chapters": len(chapters),
            "chapters": chapters
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    """主函数"""
    print("=" * 50)
    print("     番茄小说下载器")
    print("=" * 50)
    print()
    
    # 获取输入
    if len(sys.argv) > 1:
        url_or_id = sys.argv[1]
    else:
        url_or_id = input("请输入番茄小说链接或书籍ID: ").strip()
    
    if not url_or_id:
        print("错误：未提供书籍链接或ID")
        return
    
    # 选择格式
    format_choice = "txt"
    if len(sys.argv) > 2:
        format_choice = sys.argv[2]
    else:
        choice = input("选择保存格式 (1-TXT, 2-JSON) [默认1]: ").strip()
        if choice == "2":
            format_choice = "json"
    
    # 开始下载
    downloader = FanqieDownloader()
    downloader.download_book(url_or_id, save_format=format_choice)


if __name__ == "__main__":
    main()
