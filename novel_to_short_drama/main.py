#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
短剧改编工作流主程序
整合小说处理与短剧改编全流程
"""

import os
import sys
import json
import argparse
from pathlib import Path

from novel_processor import NovelProcessor
from drama_adapter import DramaAdapter


def print_banner():
    """打印程序横幅"""
    print("=" * 60)
    print("     番茄小说 → 短剧改编 工作流工具")
    print("=" * 60)
    print()


def step1_process_novel(file_path: str, title: str = "", author: str = "") -> dict:
    """
    步骤1：处理小说文件
    """
    print("【步骤1】解析小说内容...")
    
    if not os.path.exists(file_path):
        print(f"错误：文件不存在 {file_path}")
        return {}
    
    processor = NovelProcessor(file_path=file_path)
    novel = processor.parse_from_txt(title=title, author=author)
    
    print(f"  ✓ 标题: {novel.title}")
    print(f"  ✓ 作者: {novel.author}")
    print(f"  ✓ 章节数: {novel.total_chapters}")
    print(f"  ✓ 总字数: {novel.total_word_count:,}")
    
    # 导出JSON
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    json_path = output_dir / "novel_structure.json"
    processor.export_to_json(str(json_path))
    print(f"  ✓ 结构已导出: {json_path}")
    
    # 转换为字典格式供后续使用
    novel_data = {
        "title": novel.title,
        "author": novel.author,
        "description": novel.description,
        "total_word_count": novel.total_word_count,
        "total_chapters": novel.total_chapters,
        "tags": novel.tags,
        "chapters": [
            {
                "index": c.index,
                "title": c.title,
                "content": c.content,
                "word_count": c.word_count
            }
            for c in novel.chapters
        ]
    }
    
    return novel_data


def step2_analyze_novel(novel_data: dict) -> DramaAdapter:
    """
    步骤2：分析小说内容
    """
    print("\n【步骤2】分析小说内容...")
    
    adapter = DramaAdapter(novel_data)
    
    # 角色分析
    characters = adapter.analyze_characters()
    print(f"  ✓ 识别角色: {len(characters)}个")
    for char in characters[:5]:
        print(f"    - {char.name} (出现{char.appearance_count}次)")
    
    # 场景提取
    scenes = adapter.extract_scenes()
    print(f"  ✓ 提取场景: {len(scenes)}个")
    
    # 剧情节点
    plot_points = adapter.identify_plot_points()
    print(f"  ✓ 关键剧情节点: {len(plot_points)}个")
    for pp in plot_points:
        icon = {"hook": "🎣", "conflict": "⚔️", "twist": "🔄", "climax": "🔥"}.get(pp.type, "•")
        print(f"    {icon} 第{pp.chapter_index}章 - {pp.type}: {pp.title[:30]}")
    
    return adapter


def step3_generate_drama_plan(adapter: DramaAdapter):
    """
    步骤3：生成短剧改编方案
    """
    print("\n【步骤3】生成短剧改编方案...")
    
    # 生成分集大纲
    episodes = adapter.generate_episode_outline()
    print(f"  ✓ 分集大纲: {len(episodes)}集")
    
    # 显示前3集概要
    for ep in episodes[:3]:
        cliffhanger = " [悬念]" if ep["has_cliffhanger"] else ""
        print(f"    第{ep['episode_number']}集: {ep['chapters_covered']}{cliffhanger}")
    
    # 导出改编报告
    output_dir = Path("output")
    report_path = output_dir / "adaptation_report.json"
    adapter.export_adaptation_report(str(report_path))
    print(f"  ✓ 改编报告已导出: {report_path}")
    
    return episodes


def step4_generate_shots(adapter: DramaAdapter, episodes: list):
    """
    步骤4：生成详细分镜脚本（前3集示例）
    """
    print("\n【步骤4】生成示例分镜脚本...")
    
    output_dir = Path("output")
    shots_dir = output_dir / "shots"
    shots_dir.mkdir(exist_ok=True)
    
    for i, ep in enumerate(episodes[:3]):
        shots = adapter.generate_shots_for_episode(i, ep)
        
        # 导出分镜
        shot_data = []
        for shot in shots:
            shot_data.append({
                "镜号": shot.shot_number,
                "景别": shot.shot_type,
                "场景": shot.scene_location,
                "画面描述": shot.description,
                "角色": shot.characters,
                "台词": shot.dialogue,
                "动作": shot.action,
                "时长(秒)": shot.duration_estimate
            })
        
        shot_path = shots_dir / f"episode_{i+1:02d}_shots.json"
        with open(shot_path, 'w', encoding='utf-8') as f:
            json.dump(shot_data, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ 第{i+1}集分镜: {len(shots)}个镜头 → {shot_path}")


def generate_summary(novel_data: dict, adapter: DramaAdapter):
    """
    生成改编总结文档
    """
    output_dir = Path("output")
    summary_path = output_dir / "改编总结.md"
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(f"# 《{novel_data.get('title', '未知')}》短剧改编方案\n\n")
        f.write(f"> 作者: {novel_data.get('author', '未知')}\n")
        f.write(f"> 生成时间: 自动生成\n\n")
        
        f.write("## 一、原作分析\n\n")
        f.write(f"- **总章节数**: {novel_data.get('total_chapters', 0)}\n")
        f.write(f"- **总字数**: {novel_data.get('total_word_count', 0):,}\n")
        f.write(f"- **主要角色数**: {len(adapter.characters)}\n")
        f.write(f"- **关键场景数**: {len(adapter.scenes)}\n\n")
        
        f.write("### 主要角色\n\n")
        f.write("| 角色名 | 首次出场 | 出现次数 |\n")
        f.write("|--------|----------|----------|\n")
        for char in adapter.characters[:10]:
            f.write(f"| {char.name} | 第{char.first_appearance_chapter}章 | {char.appearance_count} |\n")
        
        f.write("\n## 二、关键剧情节点\n\n")
        for pp in adapter.plot_points:
            f.write(f"### {pp.type.upper()}: 第{pp.chapter_index}章\n")
            f.write(f"- **标题**: {pp.title}\n")
            f.write(f"- **重要度**: {'⭐' * pp.importance}\n")
            f.write(f"- **内容**: {pp.description[:100]}...\n\n")
        
        f.write("## 三、短剧改编建议\n\n")
        f.write("### 节奏设计\n")
        f.write("- 每集30秒，共30集\n")
        f.write("- 每3集设置一个悬念钩子\n")
        f.write("- 前3集快速建立人物关系和核心冲突\n\n")
        
        f.write("### 改编要点\n")
        f.write("1. **开篇**: 快速切入核心冲突，前10秒抓住观众\n")
        f.write("2. **节奏**: 每集至少2个情绪转折点\n")
        f.write("3. **视觉**: 优先选择有冲击力的场景进行改编\n")
        f.write("4. **对白**: 精简原著对白，增加口语化和情绪张力\n\n")
        
        f.write("## 四、输出文件清单\n\n")
        f.write("- `novel_structure.json` - 小说结构化数据\n")
        f.write("- `adaptation_report.json` - 完整改编分析报告\n")
        f.write("- `shots/episode_XX_shots.json` - 分镜脚本\n")
        f.write("- `改编总结.md` - 本文档\n")
    
    return summary_path


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='番茄小说短剧改编工具')
    parser.add_argument('file', help='小说TXT文件路径')
    parser.add_argument('--title', '-t', default='', help='小说标题')
    parser.add_argument('--author', '-a', default='', help='作者名')
    parser.add_argument('--output', '-o', default='output', help='输出目录')
    
    args = parser.parse_args()
    
    print_banner()
    
    # 检查依赖
    try:
        import jieba
    except ImportError:
        print("正在安装依赖...")
        os.system(f"{sys.executable} -m pip install jieba -q")
        print("依赖安装完成\n")
    
    # 执行工作流
    novel_data = step1_process_novel(args.file, args.title, args.author)
    
    if not novel_data:
        print("处理失败，请检查文件路径")
        return
    
    adapter = step2_analyze_novel(novel_data)
    episodes = step3_generate_drama_plan(adapter)
    step4_generate_shots(adapter, episodes)
    
    # 生成总结
    summary_path = generate_summary(novel_data, adapter)
    print(f"\n  ✓ 改编总结: {summary_path}")
    
    print("\n" + "=" * 60)
    print("  改编分析完成！所有文件已保存到 output/ 目录")
    print("=" * 60)


if __name__ == "__main__":
    main()
