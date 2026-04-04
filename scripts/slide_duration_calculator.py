#!/usr/bin/env python3
"""
Slide Duration Calculator - Calculate reading time based on content.

根据内容量和页面类型计算合理的阅读时间。
核心原则：内容为王，转场是装饰，静态展示时间应该足够用户阅读。
"""

import re
from typing import Dict, Optional


def calculate_reading_time(content: str, page_type: str = "content") -> int:
    """
    根据内容量计算合理的阅读时间（秒）

    Args:
        content: 页面内容文本
        page_type: 页面类型
            - "cover": 封面页
            - "content": 内容页
            - "data": 数据页
            - "summary": 总结页

    Returns:
        建议的阅读时间（秒）

    原则：
        - 封面页：3-5秒（展示标题，吸引注意力）
        - 内容页：根据字数计算，200-300字/分钟
        - 数据页：基础时间+2秒（图表理解时间）
        - 总结页：根据内容量，5-10秒
    """
    # 清理内容，移除多余空白
    clean_content = content.strip()

    # 计算有效字符数（移除标点和空格后的字符）
    char_count = len(re.sub(r"[^\w\u4e00-\u9fff]", "", clean_content))

    # 中文阅读速度：约 4 字/秒（200-300 字/分钟）
    # 英文阅读速度：约 15 字/秒
    # 这里使用保守估计
    reading_chars_per_second = 4

    if page_type == "cover":
        # 封面页：展示标题，3-5秒
        return min(5, max(3, char_count // 20 + 3))

    elif page_type == "data":
        # 数据页：基础时间 + 图表理解时间
        base_time = char_count / reading_chars_per_second
        # 图表理解需要额外时间
        chart_time = 2
        return min(12, max(5, int(base_time) + chart_time))

    elif page_type == "summary":
        # 总结页：根据内容量
        base_time = char_count / reading_chars_per_second
        return min(10, max(5, int(base_time)))

    else:  # content
        # 内容页：根据字数计算
        base_time = char_count / reading_chars_per_second

        # 最小时间：3秒（内容太少）
        # 最大时间：15秒（内容太多建议拆分）
        # 理想时间：5-8秒
        ideal_time = min(15, max(3, int(base_time)))

        # 如果是理想范围内，直接返回
        if ideal_time <= 8:
            return ideal_time

        # 如果超过理想时间，建议拆分但仍然给出合理时间
        return ideal_time


def calculate_all_durations(slides: list) -> Dict[int, int]:
    """
    计算所有页面的阅读时间

    Args:
        slides: 幻灯片列表，每个元素包含 slide_number, page_type, content

    Returns:
        字典 {slide_number: duration_in_seconds}
    """
    durations = {}

    for slide in slides:
        slide_number = slide.get("slide_number", 1)
        page_type = slide.get("page_type", "content")
        content = slide.get("content", "")

        duration = calculate_reading_time(content, page_type)
        durations[slide_number] = duration

    return durations


def get_duration_report(slides: list) -> str:
    """
    生成时长报告

    Args:
        slides: 幻灯片列表

    Returns:
        可读的时长报告字符串
    """
    durations = calculate_all_durations(slides)

    lines = ["📊 阅读时间分配", ""]
    total_time = 0

    for slide in slides:
        slide_number = slide.get("slide_number", 1)
        page_type = slide.get("page_type", "content")
        content = slide.get("content", "")

        # 提取标题（第一行）
        title = (
            content.split("\n")[0][:30] + "..."
            if len(content.split("\n")[0]) > 30
            else content.split("\n")[0]
        )

        duration = durations[slide_number]
        total_time += duration

        type_emoji = {
            "cover": "📑",
            "content": "📄",
            "data": "📊",
            "summary": "✨",
        }.get(page_type, "📄")

        lines.append(f"  {type_emoji} 第{slide_number}页 [{duration}秒]: {title}")

    lines.append("")
    lines.append(
        f"⏱️ 总阅读时间: {total_time}秒 (约{total_time // 60}分{total_time % 60}秒)"
    )

    return "\n".join(lines)


# 预设的时长建议
RECOMMENDED_DURATIONS = {
    "cover": {
        "min": 3,
        "max": 5,
        "recommended": 4,
        "description": "封面页：展示标题，吸引注意力",
    },
    "content": {
        "min": 3,
        "max": 15,
        "recommended": "根据内容量计算",
        "description": "内容页：200-300字/分钟，建议每页5-8秒",
    },
    "data": {
        "min": 5,
        "max": 12,
        "recommended": 7,
        "description": "数据页：基础时间+图表理解时间",
    },
    "summary": {
        "min": 5,
        "max": 10,
        "recommended": 7,
        "description": "总结页：总结要点，行动建议",
    },
}


if __name__ == "__main__":
    # 测试用例
    test_slides = [
        {
            "slide_number": 1,
            "page_type": "cover",
            "content": "AI产品设计指南\n副标题：构建以用户为中心的智能体验",
        },
        {
            "slide_number": 2,
            "page_type": "content",
            "content": "核心原则\n- 简单直观\n- 快速响应\n- 透明可控",
        },
        {
            "slide_number": 3,
            "page_type": "content",
            "content": "设计流程\n1. 用户研究\n2. 原型设计\n3. 测试迭代",
        },
        {
            "slide_number": 4,
            "page_type": "data",
            "content": "用户满意度\n使用前：65%\n使用后：92%\n提升：+27%",
        },
        {
            "slide_number": 5,
            "page_type": "summary",
            "content": "总结\n- 以用户为中心\n- 持续优化迭代\n- 数据驱动决策",
        },
    ]

    print(get_duration_report(test_slides))
