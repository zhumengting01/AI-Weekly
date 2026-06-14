#!/usr/bin/env python3
"""
AI Weekly 周刊自动生成脚本

功能：
1. 从多个 RSS 源采集上周（周一至周日）AI 相关新闻
2. 调用 MiMo API（Anthropic 兼容）对新闻进行分类、摘要
3. 生成 Markdown 周刊文件，放入 Astro 内容目录
4. 支持自动重试机制
5. 支持 PDF/HTML 导出（通过 Astro 构建）

使用方式：
    python scripts/generate_weekly.py [--issue N] [--dry-run] [--retry N]

环境变量：
    ANTHROPIC_AUTH_TOKEN  - API 密钥（必需）
    ANTHROPIC_BASE_URL    - API 地址（默认 https://api.xiaomimimo.com/anthropic）
    ANTHROPIC_MODEL       - 模型名称（默认 mimo-v2.5-pro）
"""

import os
import sys
import json
import time
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
from xml.etree import ElementTree

try:
    import requests
except ImportError:
    print("请先安装依赖: pip install requests")
    sys.exit(1)

try:
    import anthropic
except ImportError:
    print("请先安装依赖: pip install anthropic")
    sys.exit(1)

# ============================================================
# 日志配置
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("ai-weekly")

# ============================================================
# 配置
# ============================================================

# RSS 源列表
RSS_SOURCES = [
    # 中文源
    {
        "name": "量子位",
        "url": "https://www.qbitai.com/feed",
        "category": "行业动态",
    },
    {
        "name": "36氪",
        "url": "https://36kr.com/feed",
        "category": "行业动态",
    },
    {
        "name": "机器之心",
        "url": "https://www.jiqizhixin.com/rss",
        "category": "技术突破",
    },
    # 英文源
    {
        "name": "OpenAI Blog",
        "url": "https://openai.com/blog/rss.xml",
        "category": "大模型",
    },
    {
        "name": "Hugging Face Blog",
        "url": "https://huggingface.co/blog/feed.xml",
        "category": "开源AI",
    },
    {
        "name": "Google AI Blog",
        "url": "https://blog.google/technology/ai/rss/",
        "category": "大模型",
    },
    {
        "name": "MIT Technology Review",
        "url": "https://www.technologyreview.com/feed/",
        "category": "行业动态",
    },
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "category": "行业动态",
    },
    {
        "name": "The Verge AI",
        "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        "category": "行业动态",
    },
    {
        "name": "AI News",
        "url": "https://artificialintelligence-news.com/feed/",
        "category": "行业动态",
    },
    {
        "name": "arXiv AI",
        "url": "https://rss.arxiv.org/rss/cs.AI",
        "category": "研究论文",
    },
]

# Astro 内容目录
CONTENT_DIR = Path(__file__).parent.parent / "src" / "content" / "weekly"
IMAGES_DIR = Path(__file__).parent.parent / "public" / "images"
EXPORT_DIR = Path(__file__).parent.parent / "exports"

# 自动加载 scripts/.env 文件
_env_file = Path(__file__).parent / ".env"
if _env_file.exists():
    with open(_env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()
                if key and key not in os.environ:
                    os.environ[key] = value

# MiMo API 配置（Anthropic 兼容）
ANTHROPIC_BASE_URL = os.environ.get("ANTHROPIC_BASE_URL", "https://api.xiaomimimo.com/anthropic")
ANTHROPIC_AUTH_TOKEN = os.environ.get("ANTHROPIC_AUTH_TOKEN", "")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "mimo-v2.5-pro")

# 重试配置
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 10

# 每期最大新闻条目
MAX_ITEMS_PER_CATEGORY = 5


# ============================================================
# 日期工具
# ============================================================

def get_last_week_range() -> tuple[datetime, datetime]:
    """获取上周的日期范围（周一至周日）"""
    today = datetime.now()
    # 本周一
    this_monday = today - timedelta(days=today.weekday())
    # 上周一
    last_monday = this_monday - timedelta(weeks=1)
    # 上周日
    last_sunday = this_monday - timedelta(days=1)
    return last_monday, last_sunday


def format_date_range(monday: datetime, sunday: datetime) -> str:
    """格式化日期范围为可读字符串"""
    return f"{monday.strftime('%Y年%m月%d日')} - {sunday.strftime('%m月%d日')}"


# ============================================================
# 重试装饰器
# ============================================================

def retry_with_backoff(func, max_retries=MAX_RETRIES, delay=RETRY_DELAY_SECONDS):
    """带指数退避的重试包装器"""
    for attempt in range(1, max_retries + 1):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries:
                logger.error(f"第 {attempt} 次尝试失败，已达最大重试次数: {e}")
                raise
            wait_time = delay * (2 ** (attempt - 1))
            logger.warning(f"第 {attempt} 次尝试失败: {e}，{wait_time}秒后重试...")
            time.sleep(wait_time)


# ============================================================
# RSS 采集
# ============================================================

def fetch_rss(url: str, timeout: int = 10) -> list[dict]:
    """从 RSS 源获取最近 7 天的文章"""
    try:
        resp = requests.get(url, timeout=timeout, headers={
            "User-Agent": "AI-Weekly-Bot/1.0"
        })
        resp.raise_for_status()
    except Exception as e:
        logger.warning(f"无法获取 {url}: {e}")
        return []

    items = []
    try:
        root = ElementTree.fromstring(resp.content)
        # 兼容 RSS 2.0 和 Atom
        entries = root.findall(".//item") or root.findall(".//{http://www.w3.org/2005/Atom}entry")

        cutoff = datetime.now() - timedelta(days=7)

        for entry in entries:
            title_el = entry.find("title")
            link_el = entry.find("link")
            desc_el = entry.find("description")
            if desc_el is None:
                desc_el = entry.find("summary")
            if desc_el is None:
                desc_el = entry.find("{http://www.w3.org/2005/Atom}summary")
            date_el = entry.find("pubDate")
            if date_el is None:
                date_el = entry.find("published")
            if date_el is None:
                date_el = entry.find("{http://www.w3.org/2005/Atom}published")

            title = title_el.text if title_el is not None else ""
            link = ""
            if link_el is not None:
                link = link_el.text or link_el.get("href", "")
            desc = desc_el.text if desc_el is not None else ""
            pub_date = date_el.text if date_el is not None else ""

            if not title:
                continue

            items.append({
                "title": title.strip(),
                "link": link.strip(),
                "description": (desc or "")[:500].strip(),
                "date": pub_date.strip(),
            })
    except ElementTree.ParseError as e:
        logger.warning(f"RSS 解析失败 {url}: {e}")

    return items


def collect_all_news() -> list[dict]:
    """从所有 RSS 源采集新闻"""
    all_news = []
    for source in RSS_SOURCES:
        logger.info(f"采集: {source['name']} ({source['url']})")
        items = fetch_rss(source["url"])
        for item in items:
            item["source_name"] = source["name"]
            item["category_hint"] = source["category"]
        all_news.extend(items)
        logger.info(f"  获取 {len(items)} 条")
    return all_news


# ============================================================
# MiMo API 整理（Anthropic 兼容）
# ============================================================

def call_mimo_api(news_text: str, issue_number: int, date_range: str) -> dict:
    """调用 MiMo API 对新闻进行分类和摘要"""
    if not ANTHROPIC_AUTH_TOKEN:
        raise ValueError("请设置 ANTHROPIC_AUTH_TOKEN 环境变量")

    client = anthropic.Anthropic(
        api_key=ANTHROPIC_AUTH_TOKEN,
        base_url=ANTHROPIC_BASE_URL,
    )

    prompt = f"""你是一位专业的 AI 周刊编辑。请根据以下本周（{date_range}）AI 新闻，生成第 {issue_number} 期 AI Weekly 周刊内容。

要求：
1. 将新闻分为以下几个板块：
   - 本周焦点（最重要的 3-5 条新闻，具有重大行业影响）
   - 前沿速递（本周重要的 AI 技术进展、模型发布、算法创新）
   - 落地前线（AI 在各行业的落地应用案例、商业化进展）
   - 研究论文精选（本周重要的 AI 研究论文、学术成果）
   - 洞察之声（行业领袖、学者的观点与评论）
2. 每条新闻用中文撰写简明摘要（2-3 句话），保留原始链接
3. 如果某个板块没有相关新闻，可以省略该板块
4. 【重要】内容来源必须多样化！不要只聚焦某一家公司（如 OpenAI），要涵盖不同公司、不同领域的动态
5. 内容需准确客观，引用权威来源
6. 输出 JSON 格式

本周新闻列表：
{news_text}

请输出以下 JSON 格式（不要包含 markdown 代码块标记）：
{{
  "title": "用一句话概括本周最核心的主题，例如「GPT-5发布与开源模型崛起」，不要包含期号和AI Weekly前缀",
  "excerpt": "一句话概述本周AI领域最重要的事件",
  "headline_news": [
    {{"title": "新闻标题", "summary": "中文摘要", "link": "原始链接"}}
  ],
  "tech_breakthroughs": [
    {{"title": "技术标题", "summary": "中文摘要", "link": "原始链接"}}
  ],
  "industry_applications": [
    {{"title": "应用标题", "summary": "中文摘要", "link": "原始链接"}}
  ],
  "research_papers": [
    {{"title": "论文标题", "summary": "中文摘要", "link": "原始链接"}}
  ],
  "expert_opinions": [
    {{"title": "观点标题", "summary": "中文摘要", "link": "原始链接"}}
  ],
  "editor_note": "一周观察：对本周AI行业趋势的简短评论"
}}"""

    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=4000,
        system="你是一位专业的 AI 周刊编辑，擅长将技术新闻整理为结构清晰的中文周刊。内容必须准确客观，引用权威来源。",
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )

    content = response.content[0].text.strip()

    # 清理可能的 markdown 代码块标记
    if content.startswith("```"):
        content = content.split("\n", 1)[1]
    if content.endswith("```"):
        content = content.rsplit("```", 1)[0]
    content = content.strip()
    if content.startswith("json"):
        content = content[4:].strip()

    # 尝试直接解析
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # 尝试提取 JSON 对象（从第一个 { 到最后一个 }）
    import re
    json_match = re.search(r'\{[\s\S]*\}', content)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    # 最后尝试修复常见问题：单引号、尾随逗号
    fixed = content
    fixed = re.sub(r',\s*([}\]])', r'\1', fixed)  # 移除尾随逗号
    json_match = re.search(r'\{[\s\S]*\}', fixed)
    if json_match:
        return json.loads(json_match.group())

    raise ValueError(f"无法解析 API 返回的 JSON: {content[:500]}")


def generate_weekly_content(news_items: list[dict], issue_number: int, date_range: str) -> dict:
    """调用 MiMo API 整理内容，带自动重试"""
    # 构建新闻列表文本
    # 限制发送给 API 的新闻数量，避免输入过长
    max_items = 80
    selected_items = news_items[:max_items]
    if len(news_items) > max_items:
        logger.info(f"  截取前 {max_items} 条新闻发送给 API（共 {len(news_items)} 条）")

    news_text = ""
    for i, item in enumerate(selected_items, 1):
        news_text += f"{i}. [{item['source_name']}] {item['title']}\n"
        if item["description"]:
            news_text += f"   摘要: {item['description'][:150]}\n"
        if item["link"]:
            news_text += f"   链接: {item['link']}\n"
        news_text += "\n"

    def _call():
        return call_mimo_api(news_text, issue_number, date_range)

    try:
        return retry_with_backoff(_call)
    except Exception as e:
        logger.error(f"API 调用最终失败: {e}")
        return {
            "title": f"AI Weekly #{issue_number:03d}",
            "excerpt": "本周AI热点汇总",
            "headline_news": [],
            "tech_breakthroughs": [],
            "industry_applications": [],
            "research_papers": [],
            "expert_opinions": [],
            "editor_note": "本周内容生成失败，请手动编辑。",
        }


# ============================================================
# Markdown 生成
# ============================================================

def generate_section(title: str, items: list[dict]) -> str:
    """生成一个板块的 Markdown 内容"""
    if not items:
        return ""
    md = f"# {title}\n\n"
    for i, item in enumerate(items):
        md += f"## {item['title']}\n\n"
        md += f"{item['summary']}\n\n"
        if item.get("link"):
            md += f"[阅读原文]({item['link']})\n\n"
        if i < len(items) - 1:
            md += "---\n\n"
    return md


def generate_markdown(data: dict, issue_number: int, date_range: str) -> str:
    """将周刊数据转换为 Markdown 文件"""
    today = datetime.now().strftime("%Y-%m-%d")
    title = data.get("title", f"AI Weekly #{issue_number:03d}")
    excerpt = data.get("excerpt", "本周AI热点汇总")

    md = f"""---
title: "{title}"
date: {today}
excerpt: "{excerpt}"
tags: [AI, 周刊]
---

"""

    sections = [
        ("本周焦点", data.get("headline_news", [])),
        ("前沿速递", data.get("tech_breakthroughs", [])),
        ("落地前线", data.get("industry_applications", [])),
        ("研究论文精选", data.get("research_papers", [])),
        ("洞察之声", data.get("expert_opinions", [])),
    ]

    first_section = True
    for section_title, items in sections:
        section_md = generate_section(section_title, items)
        if section_md:
            if not first_section:
                md += "---\n\n"
            md += section_md
            first_section = False

    editor_note = data.get("editor_note", "")
    if editor_note:
        md += "---\n\n"
        md += f"# 一周观察\n\n{editor_note}\n"

    return md


def get_next_issue_number() -> int:
    """根据已有文件自动推断下一期期号"""
    if not CONTENT_DIR.exists():
        return 1
    existing = list(CONTENT_DIR.glob("ai-weekly-*.md"))
    if not existing:
        return 1
    numbers = []
    for f in existing:
        try:
            num = int(f.stem.split("-")[-1])
            numbers.append(num)
        except ValueError:
            pass
    return max(numbers) + 1 if numbers else 1


# ============================================================
# 主流程
# ============================================================

def main():
    global MAX_RETRIES

    parser = argparse.ArgumentParser(description="AI Weekly 周刊生成器")
    parser.add_argument("--issue", type=int, help="期号（默认自动推断）")
    parser.add_argument("--dry-run", action="store_true", help="只输出内容，不写入文件")
    parser.add_argument("--retry", type=int, default=MAX_RETRIES, help=f"最大重试次数（默认 {MAX_RETRIES}）")
    args = parser.parse_args()

    MAX_RETRIES = args.retry

    issue_number = args.issue or get_next_issue_number()
    last_monday, last_sunday = get_last_week_range()
    date_range = format_date_range(last_monday, last_sunday)

    logger.info(f"=== 生成 AI Weekly #{issue_number:03d} ({date_range}) ===\n")

    # 1. 采集 RSS
    logger.info("[1/3] 采集 RSS 新闻...")
    news_items = collect_all_news()
    logger.info(f"共采集 {len(news_items)} 条新闻\n")

    if not news_items:
        logger.warning("未采集到任何新闻，跳过生成。")
        sys.exit(0)

    # 2. 调用 MiMo 整理
    logger.info("[2/3] 调用 MiMo API 整理内容...")
    weekly_data = generate_weekly_content(news_items, issue_number, date_range)
    logger.info("内容整理完成\n")

    # 3. 生成 Markdown
    logger.info("[3/3] 生成 Markdown 文件...")
    markdown = generate_markdown(weekly_data, issue_number, date_range)

    if args.dry_run:
        print("\n--- 预览 ---\n")
        print(markdown)
        return

    # 确保目录存在
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    filename = f"ai-weekly-{issue_number:03d}.md"
    filepath = CONTENT_DIR / filename
    filepath.write_text(markdown, encoding="utf-8")
    logger.info(f"已生成: {filepath}")

    logger.info(f"\n=== AI Weekly #{issue_number:03d} 生成完成 ===")
    logger.info("下一步: cd astro-brook && npm run build")


if __name__ == "__main__":
    main()
