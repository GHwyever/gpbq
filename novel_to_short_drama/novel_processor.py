#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说内容处理器 - 用于处理合法获取的小说内容
功能：章节解析、内容清洗、结构化存储
"""

import re
import json
import os
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from pathlib import Path


@dataclass
class Chapter:
    """章节数据结构"""
    index: int
    title: str
    content: str
    word_count: int
    volume: str = ""
    volume_index: int = 0


@dataclass
class Novel:
    """小说数据结构"""
    title: str
    author: str
    description: str
    chapters: List[Chapter]
    total_word_count: int
    total_chapters: int
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class NovelProcessor:
    """小说处理器"""
    
    def __init__(self, content: str = "", file_path: str = ""):
        """
        初始化处理器
        :param content: 直接传入小说文本内容
        :param file_path: 从文件路径读取
        """
        self.raw_content = content
        self.file_path = file_path
        self.novel: Optional[Novel] = None
        
        if file_path and os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                self.raw_content = f.read()
    
    def parse_from_txt(self, title: str = "", author: str = "", 
                       chapter_pattern: str = None) -> Novel:
        """
        从TXT格式解析小说
        :param title: 小说标题
        :param author: 作者
        :param chapter_pattern: 章节匹配正则，默认匹配常见格式
        :return: Novel对象
        """
        if chapter_pattern is None:
            # 匹配常见章节格式：第X章、Chapter X、第X回等
            chapter_pattern = r'(?:^|\n)\s*(?:第[\d一二三四五六七八九十百千零]+[章回节卷]|Chapter\s+\d+|\d+\s*[、.．])\s*([^\n]*)'
        
        # 查找所有章节位置
        matches = list(re.finditer(chapter_pattern, self.raw_content, re.MULTILINE))
        
        chapters = []
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(self.raw_content)
            
            chapter_text = self.raw_content[start:end].strip()
            chapter_title = match.group(0).strip()
            chapter_content = chapter_text[len(chapter_title):].strip()
            
            # 清洗内容
            chapter_content = self._clean_content(chapter_content)
            
            chapter = Chapter(
                index=i + 1,
                title=chapter_title,
                content=chapter_content,
                word_count=len(chapter_content)
            )
            chapters.append(chapter)
        
        total_words = sum(c.word_count for c in chapters)
        
        self.novel = Novel(
            title=title,
            author=author,
            description="",
            chapters=chapters,
            total_word_count=total_words,
            total_chapters=len(chapters)
        )
        
        return self.novel
    
    def _clean_content(self, content: str) -> str:
        """清洗章节内容"""
        # 去除多余空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        # 去除特殊广告标记
        content = re.sub(r'【.*?】', '', content)
        # 去除网址
        content = re.sub(r'https?://\S+', '', content)
        return content.strip()
    
    def extract_description(self, max_length: int = 500) -> str:
        """从开头提取简介"""
        if not self.novel:
            return ""
        
        # 取前3章的前500字作为简介参考
        desc_parts = []
        for ch in self.novel.chapters[:3]:
            desc_parts.append(ch.content[:200])
        
        description = " ".join(desc_parts)[:max_length]
        self.novel.description = description
        return description
    
    def export_to_json(self, output_path: str) -> str:
        """导出为JSON格式"""
        if not self.novel:
            raise ValueError("请先解析小说内容")
        
        data = {
            "title": self.novel.title,
            "author": self.novel.author,
            "description": self.novel.description,
            "total_word_count": self.novel.total_word_count,
            "total_chapters": self.novel.total_chapters,
            "tags": self.novel.tags,
            "chapters": [
                {
                    "index": c.index,
                    "title": c.title,
                    "word_count": c.word_count,
                    "content_preview": c.content[:200] + "..." if len(c.content) > 200 else c.content
                }
                for c in self.novel.chapters
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return output_path
    
    def get_chapter_range(self, start: int, end: int) -> List[Chapter]:
        """获取指定范围的章节"""
        if not self.novel:
            return []
        return self.novel.chapters[start-1:end]
    
    def search_content(self, keyword: str) -> List[Tuple[int, str, int]]:
        """
        搜索包含关键词的章节
        :return: [(章节序号, 章节标题, 出现次数), ...]
        """
        if not self.novel:
            return []
        
        results = []
        for ch in self.novel.chapters:
            count = ch.content.count(keyword)
            if count > 0:
                results.append((ch.index, ch.title, count))
        
        return sorted(results, key=lambda x: x[2], reverse=True)


if __name__ == "__main__":
    # 示例用法
    print("小说内容处理器")
    print("用法: 导入NovelProcessor类，传入小说文本或文件路径")
    print("")
    print("示例代码:")
    print("  processor = NovelProcessor(file_path='novel.txt')")
    print("  novel = processor.parse_from_txt(title='小说名', author='作者')")
    print("  processor.export_to_json('output.json')")
