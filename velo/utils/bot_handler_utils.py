import os
from typing import List
from collections import defaultdict
from telegram import InputMediaPhoto
from velo.config import CREATIVES_PATH
from velo.utils.service_logs import service as logger
from velo.agents.tools import TASK_SERVICE, validate_schema
from velo.types.agent import (
    ContentGenOut,
    ScheduleGenOut,
    ScheduledContent,
    AudienceResearchOut
)


def load_images(
        chat_id: str,
        campaign_id: str
        ) -> list[InputMediaPhoto] | None:
    base_path = CREATIVES_PATH+"/"+chat_id+"/campaign_"+campaign_id
    try:
        image_paths = []
        for filename in os.listdir(base_path):
            if filename.endswith(".png"):
                image_paths.append(filename)

        images = []
        for idx, image_path in enumerate(image_paths):
            images.append(
                InputMediaPhoto(
                    open(base_path+"/"+image_path, "rb"),
                    filename=f"creative_{idx+1}"
                )
            )
        return images
    except Exception as e:
        logger.error(
            "error loading generated images from file >> %s",
            e,
            exc_info=True
        )


def load_results(campaign_id: int):
    tasks = TASK_SERVICE.readAll_by_campaign_id(campaign_id)

    if tasks:
        for task in tasks:
            if task.tool_name == "audience_agent":
                audience_out = validate_schema(
                    task.tool_name,
                    task.output_json,
                    logger
                )
            elif task.tool_name == "content_agent":
                content_out = validate_schema(
                    task.tool_name,
                    task.output_json,
                    logger
                )
            elif task.tool_name == "scheduler_agent":
                schedule_out = validate_schema(
                    task.tool_name,
                    task.output_json,
                    logger
                )
        formatted_audience = format_audience(
            audience_out  # type: ignore
        )
        merged_outputs = merge_outputs(
            content_out,  # type: ignore
            schedule_out  # type: ignore
        )

        formatted_output = format_output(
            merged_outputs
        )

        return formatted_audience + "\n\n" + formatted_output


def format_audience(audience: AudienceResearchOut) -> str:
    lines = [
        "🎯 **Audience Research Summary**\n",
        "**🔑 Keywords:**",
        ", ".join(
            audience.keywords
        ) if audience.keywords else "_No keywords found._",
        "",
        "**💡 Interests:**",
        ", ".join(
            audience.interests
        ) if audience.interests else "_No interests identified._",
        "",
        "**😟 Pain Points:**",
        ", ".join(
            audience.pain_points
        ) if audience.pain_points else "_No pain points listed._",
    ]

    return "\n".join(lines).strip()


def merge_outputs(
        content_out: ContentGenOut,
        schedule_out: ScheduleGenOut
        ) -> List[ScheduledContent]:
    merged = []

    for s in sorted(schedule_out.schedule, key=lambda x: x.datetime):
        if s.content_type == "ad_copy":
            content_item = content_out.ad_copies[s.content_idx]
            title = f"Ad Copy ({content_item.channel})"
            body = content_item.content

        elif s.content_type == "email":
            content_item = content_out.emails[s.content_idx]
            title = content_item.title
            body = content_item.body

        elif s.content_type == "social_post":
            content_item = content_out.social_posts[s.content_idx]
            title = f"Social Post ({content_item.platform})"
            body = content_item.post

        else:
            continue

        merged.append(
            ScheduledContent(
                platform=s.platform,
                content_type=s.content_type,
                datetime=s.datetime,
                content_title=title,
                content_body=body,
            )
        )

    return merged


def format_output(merged_items: List[ScheduledContent]) -> str:

    grouped = defaultdict(list[ScheduledContent])
    for item in sorted(merged_items, key=lambda x: x.datetime):
        grouped[item.platform].append(item)

    lines = ["📅 Here's your content schedule, grouped by platform:\n"]

    for platform, items in grouped.items():
        lines.append(f"**🌐 {platform}**")
        for item in items:
            dt_str = item.datetime.strftime("%a, %b %d at %H:%M UTC")
            type_emoji = {
                "ad_copy": "📢",
                "email": "✉️",
                "social_post": "💬"
            }.get(item.content_type, "📝")

            lines.append(f"{type_emoji} *{item.content_title}*")
            lines.append(f"🕒 {dt_str}")
            lines.append(f"{item.content_body}\n")

        lines.append("─" * 30)

    return "\n".join(lines).strip()
