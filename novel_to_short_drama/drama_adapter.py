#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
短剧改编辅助工具
功能：剧情提取、角色分析、场景识别、分镜生成、节奏分析
"""

import re
import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from collections import Counter
import jieba
import jieba.posseg as pseg


@dataclass
class Character:
    """角色信息"""
    name: str
    aliases: List[str]
    appearance_count: int
    first_appearance_chapter: int
    key_traits: List[str]
    description: str = ""


@dataclass
class Scene:
    """场景信息"""
    location: str
    chapter_index: int
    characters: List[str]
    mood: str
    key_events: List[str]
    word_count: int


@dataclass
class PlotPoint:
    """剧情节点"""
    chapter_index: int
    title: str
    description: str
    importance: int  # 1-10
    type: str  # 'hook', 'conflict', 'twist', 'climax', 'resolution'
    characters_involved: List[str]


@dataclass
class Shot:
    """分镜信息"""
    shot_number: int
    scene_location: str
    shot_type: str  # 'close-up', 'medium', 'wide', 'extreme-close-up'
    description: str
    characters: List[str]
    dialogue: str
    action: str
    duration_estimate: int  # 秒


class DramaAdapter:
    """短剧改编器"""
    
    # 短剧节奏配置
    DRAMA_CONFIG = {
        "total_duration_minutes": 15,  # 总时长（分钟）
        "episodes": 30,  # 集数
        "episode_duration_seconds": 30,  # 每集时长
        "hooks_per_episode": 2,  # 每集钩子数
        "cliffhanger_interval": 3,  # 悬念间隔（集）
    }
    
    # 场景关键词
    LOCATION_KEYWORDS = [
        "房间", "办公室", "公司", "家里", "酒店", "餐厅", "医院", "学校",
        "别墅", "公寓", "大厦", "商场", "街头", "公园", "机场", "车站",
        "客厅", "卧室", "厨房", "浴室", "阳台", "院子", "门口", "走廊",
        "会议室", "实验室", "工厂", "仓库", "码头", "山顶", "河边", "海边"
    ]
    
    # 情绪关键词
    MOOD_KEYWORDS = {
        "紧张": ["紧张", "焦虑", "不安", "恐惧", "危险", "紧迫"],
        "浪漫": ["温柔", "甜蜜", "心动", "爱意", "浪漫", "温馨"],
        "悲伤": ["悲伤", "痛苦", "绝望", "哭泣", "失落", "难过"],
        "愤怒": ["愤怒", "暴怒", "仇恨", "报复", "气愤", "怒火"],
        "喜悦": ["开心", "高兴", "兴奋", "欢喜", "快乐", "欣慰"],
        "悬疑": ["疑惑", "谜团", "秘密", "未知", "诡异", "神秘"]
    }
    
    def __init__(self, novel_data: Dict):
        """
        初始化改编器
        :param novel_data: 小说数据结构，来自NovelProcessor的输出
        """
        self.novel = novel_data
        self.characters: List[Character] = []
        self.scenes: List[Scene] = []
        self.plot_points: List[PlotPoint] = []
        self.shots: List[List[Shot]] = []  # 每集的分镜列表
        
    def analyze_characters(self) -> List[Character]:
        """
        分析小说中的角色
        使用jieba进行人名识别
        """
        all_text = ""
        for ch in self.novel.get("chapters", []):
            all_text += ch.get("content", "")
        
        # 使用jieba词性标注识别人名
        words = pseg.cut(all_text)
        name_counts = Counter()
        name_first_appearance = {}
        
        for word, flag in words:
            if flag == 'nr':  # nr = 人名
                name_counts[word] += 1
                if word not in name_first_appearance:
                    # 找到第一次出现的章节
                    for ch in self.novel.get("chapters", []):
                        if word in ch.get("content", ""):
                            name_first_appearance[word] = ch.get("index", 0)
                            break
        
        # 过滤出现次数少的人名（可能是误识别）
        min_appearances = max(3, len(self.novel.get("chapters", [])) // 20)
        
        characters = []
        for name, count in name_counts.most_common(20):
            if count >= min_appearances:
                char = Character(
                    name=name,
                    aliases=[],
                    appearance_count=count,
                    first_appearance_chapter=name_first_appearance.get(name, 0),
                    key_traits=[],
                    description=""
                )
                characters.append(char)
        
        self.characters = characters
        return characters
    
    def extract_scenes(self) -> List[Scene]:
        """
        提取小说中的场景信息
        """
        scenes = []
        
        for ch in self.novel.get("chapters", []):
            content = ch.get("content", "")
            chapter_index = ch.get("index", 0)
            
            # 识别场景位置
            found_locations = []
            for loc in self.LOCATION_KEYWORDS:
                if loc in content:
                    found_locations.append(loc)
            
            # 识别情绪
            mood_scores = {mood: 0 for mood in self.MOOD_KEYWORDS}
            for mood, keywords in self.MOOD_KEYWORDS.items():
                for kw in keywords:
                    mood_scores[mood] += content.count(kw)
            
            dominant_mood = max(mood_scores, key=mood_scores.get) if max(mood_scores.values()) > 0 else "中性"
            
            # 提取关键事件（简单实现：找包含动作词的句子）
            action_patterns = r'[^。！？]*(?:发现|得知|决定|拒绝|接受|逃离|追赶|相遇|冲突|揭露)[^。！？]*[。！？]'
            key_events = re.findall(action_patterns, content[:1000])
            
            if found_locations:
                scene = Scene(
                    location=found_locations[0],
                    chapter_index=chapter_index,
                    characters=[],  # 后续可关联角色分析结果
                    mood=dominant_mood,
                    key_events=key_events[:3],
                    word_count=ch.get("word_count", 0)
                )
                scenes.append(scene)
        
        self.scenes = scenes
        return scenes
    
    def identify_plot_points(self) -> List[PlotPoint]:
        """
        识别关键剧情节点
        """
        plot_points = []
        chapters = self.novel.get("chapters", [])
        total = len(chapters)
        
        if total == 0:
            return plot_points
        
        # 自动识别关键节点位置
        key_positions = [
            (1, "hook", "开篇钩子"),
            (max(1, total // 10), "conflict", "初期冲突"),
            (max(1, total // 4), "twist", "第一次转折"),
            (max(1, total // 2), "climax", "中期高潮"),
            (max(1, total * 3 // 4), "twist", "重大转折"),
            (max(1, total - 5), "climax", "终极高潮"),
        ]
        
        for pos, ptype, label in key_positions:
            if pos <= total:
                ch = chapters[pos - 1]
                content = ch.get("content", "")[:300]
                
                pp = PlotPoint(
                    chapter_index=pos,
                    title=ch.get("title", f"第{pos}章"),
                    description=content,
                    importance=8 if ptype == "climax" else 6,
                    type=ptype,
                    characters_involved=[]
                )
                plot_points.append(pp)
        
        self.plot_points = plot_points
        return plot_points
    
    def generate_episode_outline(self) -> List[Dict]:
        """
        生成短剧分集大纲
        """
        episodes = []
        chapters = self.novel.get("chapters", [])
        total_chapters = len(chapters)
        
        if total_chapters == 0:
            return episodes
        
        episodes_count = self.DRAMA_CONFIG["episodes"]
        chapters_per_episode = max(1, total_chapters // episodes_count)
        
        for ep in range(1, episodes_count + 1):
            start_ch = (ep - 1) * chapters_per_episode + 1
            end_ch = min(ep * chapters_per_episode, total_chapters)
            
            # 获取该集覆盖的章节
            episode_chapters = chapters[start_ch - 1:end_ch]
            
            # 生成该集内容摘要
            episode_content = ""
            for ch in episode_chapters:
                episode_content += ch.get("content", "")[:200] + "... "
            
            # 判断是否有悬念点
            has_cliffhanger = ep % self.DRAMA_CONFIG["cliffhanger_interval"] == 0
            
            episode = {
                "episode_number": ep,
                "title": f"第{ep}集",
                "chapters_covered": f"第{start_ch}章 - 第{end_ch}章",
                "summary": episode_content[:300],
                "key_scenes": [],
                "has_cliffhanger": has_cliffhanger,
                "estimated_duration": self.DRAMA_CONFIG["episode_duration_seconds"]
            }
            episodes.append(episode)
        
        return episodes
    
    def generate_shots_for_episode(self, episode_index: int, 
                                   episode_data: Dict) -> List[Shot]:
        """
        为单集生成分镜脚本
        """
        shots = []
        shot_number = 1
        
        # 简单的分镜生成逻辑
        scenes_in_episode = episode_data.get("key_scenes", [])
        
        # 开场镜头
        shots.append(Shot(
            shot_number=shot_number,
            scene_location="开场",
            shot_type="wide",
            description="建立场景，展示环境",
            characters=[],
            dialogue="",
            action="画面渐入",
            duration_estimate=3
        ))
        shot_number += 1
        
        # 根据场景生成分镜
        for scene in scenes_in_episode[:5]:  # 每集最多5个场景
            # 中景展示角色
            shots.append(Shot(
                shot_number=shot_number,
                scene_location=scene.get("location", "未知地点"),
                shot_type="medium",
                description="角色进入场景",
                characters=scene.get("characters", []),
                dialogue=scene.get("dialogue", "")[:50],
                action="角色动作",
                duration_estimate=5
            ))
            shot_number += 1
            
            # 特写展示情绪
            shots.append(Shot(
                shot_number=shot_number,
                scene_location=scene.get("location", "未知地点"),
                shot_type="close-up",
                description="角色表情特写",
                characters=scene.get("characters", [])[:1],
                dialogue="",
                action="表情变化",
                duration_estimate=3
            ))
            shot_number += 1
        
        # 结尾钩子镜头
        shots.append(Shot(
            shot_number=shot_number,
            scene_location="转场",
            shot_type="extreme-close-up",
            description="悬念特写",
            characters=[],
            dialogue="",
            action="画面定格/悬念音效",
            duration_estimate=2
        ))
        
        return shots
    
    def export_adaptation_report(self, output_path: str) -> str:
        """
        导出改编分析报告
        """
        report = {
            "novel_title": self.novel.get("title", "未知"),
            "novel_author": self.novel.get("author", "未知"),
            "analysis_summary": {
                "total_chapters": len(self.novel.get("chapters", [])),
                "total_word_count": self.novel.get("total_word_count", 0),
                "character_count": len(self.characters),
                "scene_count": len(self.scenes),
                "key_plot_points": len(self.plot_points)
            },
            "characters": [
                {
                    "name": c.name,
                    "appearance_count": c.appearance_count,
                    "first_appearance": f"第{c.first_appearance_chapter}章"
                }
                for c in self.characters[:10]
            ],
            "plot_points": [
                {
                    "chapter": pp.chapter_index,
                    "type": pp.type,
                    "title": pp.title,
                    "importance": pp.importance
                }
                for pp in self.plot_points
            ],
            "episode_outline": self.generate_episode_outline()[:10]  # 前10集
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return output_path


if __name__ == "__main__":
    print("短剧改编辅助工具")
    print("用法: 导入DramaAdapter类，传入小说数据")
    print("")
    print("示例代码:")
    print("  adapter = DramaAdapter(novel_data)")
    print("  adapter.analyze_characters()")
    print("  adapter.extract_scenes()")
    print("  adapter.identify_plot_points()")
    print("  adapter.export_adaptation_report('report.json')")
