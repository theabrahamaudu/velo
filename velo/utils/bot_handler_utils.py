import os
import html
from typing import List, Optional, DefaultDict
from collections import defaultdict
from telegram import InputMediaPhoto
from velo.config import CREATIVES_PATH
from velo.utils.service_logs import service as logger
from velo.agents.tools import TASK_SERVICE
from velo.types.agent import (
    ContentGenOut,
    Schedule,
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


def load_results(campaign_id: int) -> str:
    tasks = TASK_SERVICE.readAll_by_campaign_id(campaign_id)
    if not tasks:
        return "No tasks found for this campaign."

    audience_out: Optional[AudienceResearchOut] = None
    content_out: Optional[ContentGenOut] = None
    schedule_out: Optional[ScheduleGenOut] = None

    for task in tasks:
        try:
            if task.tool_name == "audience_agent":
                audience_out = AudienceResearchOut.model_validate(
                    task.output_json
                )
        except Exception as e:
            logger.warning(
                "failed to parse %s: %s",
                task.tool_name,
                e,
                exc_info=True
            )
        try:
            if task.tool_name == "content_agent":
                content_out = ContentGenOut.model_validate(task.output_json)
        except Exception as e:
            logger.warning(
                "failed to parse %s: %s",
                task.tool_name,
                e,
                exc_info=True
            )
        try:
            if task.tool_name == "scheduler_agent":
                schedule_out = ScheduleGenOut.model_validate(task.output_json)
        except Exception as e:
            logger.warning(
                "failed to parse %s: %s",
                task.tool_name,
                e,
                exc_info=True
            )

    parts = []

    if audience_out:
        parts.append(format_audience(audience_out))
    else:
        parts.append(
            "🎯 <b>Audience Research Summary</b>\n<i>Not available.</i>"
        )

    # Content + Schedule handling
    if content_out and schedule_out:
        merged_outputs = merge_outputs(content_out, schedule_out)
        parts.append(format_output(merged_outputs))

    elif content_out and not schedule_out:
        parts.append(format_content(content_out))

    elif schedule_out and not content_out:
        parts.append(format_schedule(schedule_out))

    else:
        parts.append("<i>No content or schedule created.</i>")

    parts.append("🖼️ <b>Campaign Creatives:</b>")

    combined_output = "\n\n".join(parts).strip()

    safe_output = html.escape(combined_output, quote=False)

    safe_output = (
        safe_output
        .replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
        .replace("&lt;i&gt;", "<i>").replace("&lt;/i&gt;", "</i>")
    )

    return safe_output


def format_audience(audience: AudienceResearchOut) -> str:
    lines = [
        "🎯 <b>Audience Research Summary</b>\n",
        "<b>🔑 Keywords:</b>",
        ", ".join(audience.keywords)
        if audience.keywords
        else "<i>No keywords found.</i>",
        "",
        "<b>💡 Interests:</b>",
        ", ".join(audience.interests)
        if audience.interests
        else "<i>No interests identified.</i>",
        "",
        "<b>😟 Pain Points:</b>",
        ", ".join(audience.pain_points)
        if audience.pain_points
        else "<i>No pain points listed.</i>",
    ]

    return "\n".join(lines).strip()


def format_content(content_out: ContentGenOut) -> str:
    """Format output if only content is available (no schedule)."""
    lines = ["🧱 <b>Generated Content (No Schedule)</b>\n"]

    if content_out.ad_copies:
        lines.append("<b>📢 Ad Copies</b>")
        for ad in content_out.ad_copies:
            lines.append(f"<i>{ad.channel}</i>: {ad.content}")
        lines.append("")

    if content_out.emails:
        lines.append("<b>✉️ Emails</b>")
        for email in content_out.emails:
            lines.append(f"<b>{email.title}</b>\n{email.body}")
        lines.append("")

    if content_out.social_posts:
        lines.append("<b>💬 Social Posts</b>")
        for post in content_out.social_posts:
            lines.append(f"<i>{post.platform}</i>: {post.post}")
        lines.append("")

    return "\n".join(lines).strip()


def format_schedule(schedule_out: ScheduleGenOut) -> str:
    """Format output if only schedule is available (no content)."""
    lines = ["📅 <b>Schedule (No Content)</b>\n"]

    grouped: dict[str, list[Schedule]] = defaultdict(list)
    for s in sorted(schedule_out.schedule, key=lambda x: x.datetime):
        grouped[s.platform].append(s)

    for platform, items in grouped.items():
        lines.append(f"<b>🌐 {platform}</b>")
        for s in items:
            dt_str = s.datetime.strftime("%a, %b %d at %H:%M UTC")
            emoji = {
                "ad_copy": "📢",
                "email": "✉️",
                "social_post": "💬"
            }.get(s.content_type, "📝")
            lines.append(
                f"{emoji} <i>{s.content_type.replace('_', ' ').title()}</i>"
            )
            lines.append(f"🕒 {dt_str}")
        lines.append("─" * 30)

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
    grouped: DefaultDict[str, DefaultDict[str, List[ScheduledContent]]] =\
        defaultdict(lambda: defaultdict(list))

    for item in sorted(merged_items, key=lambda x: x.datetime):
        grouped[item.platform][item.content_type].append(item)

    lines = ["📅 Here's your content schedule, grouped by platform:\n"]

    for platform, type_groups in grouped.items():
        lines.append(f"<b>🌐 {platform}</b>")

        for content_type, items in type_groups.items():
            emoji = {
                "ad_copy": "📢",
                "email": "✉️",
                "social_post": "💬"
            }.get(content_type, "📝")
            lines.append(
                f"{emoji} <b>{content_type.replace('_', ' ').title()}</b>"
            )

            for item in items:
                dt_str = item.datetime.strftime("%a, %b %d at %H:%M UTC")
                lines.append(f"🕒 {dt_str}")
                lines.append(f"<i>{item.content_title}</i>")
                lines.append(f"{item.content_body}\n")

        lines.append("─" * 30)

    return "\n".join(lines).strip()
