import openai
import requests
import os
import textwrap
import json
import hashlib
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io
import math

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
LINKEDIN_ACCESS_TOKEN = os.environ["LINKEDIN_ACCESS_TOKEN"]
LINKEDIN_PERSON_ID = os.environ["LINKEDIN_PERSON_ID"]
TOPIC = os.environ.get("TOPIC", "Agentic AI cybersecurity and autonomous threat detection")
RUN_MODE = os.environ.get("RUN_MODE", "post")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

LINKEDIN_HEADERS = {
    "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
    "Content-Type": "application/json",
    "X-Restli-Protocol-Version": "2.0.0"
}

AGENT_PERSONA = """You are Aurobinda Ojha, an Independent Researcher on Cybersecurity
and Agentic AI. You write sharp, punchy LinkedIn posts with short lines and emojis.
Your style is direct, conversational and thought provoking.
You use line breaks between thoughts. You add emojis to key points.
Plain text only. No markdown. Short sentences. Max 150 words."""

STEP_COLORS = [
    (41, 98, 181),   # blue
    (211, 84, 0),    # orange
    (39, 174, 96),   # green
    (192, 57, 43),   # red
    (142, 68, 173),  # purple
    (41, 98, 181),   # blue
    (192, 57, 43),   # red
    (211, 84, 0),    # orange
    (39, 174, 96),   # green
    (41, 98, 181),   # blue
]

SIDE_COLORS = [
    (39, 174, 96),   # green
    (211, 84, 0),    # orange
    (41, 98, 181),   # blue
]

def ai_generate_post(topic):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": AGENT_PERSONA},
            {"role": "user", "content":
                f"Write a professional LinkedIn post about a fresh angle on: {topic}\n\n"
                f"FORMAT RULES:\n"
                f"- SHORT lines with line breaks between thoughts\n"
                f"- Add relevant emojis at key lines\n"
                f"- Start with attention grabbing hook\n"
                f"- End with a question\n"
                f"- Max 150 words"}
        ],
        max_tokens=400,
    )
    return response.choices[0].message.content.strip()

def ai_generate_flowchart_data(post_content):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content":
                f"Based on this LinkedIn post, create a flowchart architecture diagram structure.\n"
                f"Post: {post_content}\n\n"
                f"Reply with JSON only, no extra text:\n"
                f"{{\n"
                f"  \"title\": \"Main Topic Architecture\",\n"
                f"  \"subtitle\": \"by Aurobinda Ojha\",\n"
                f"  \"start_label\": \"START\",\n"
                f"  \"end_label\": \"END\",\n"
                f"  \"end_subtitle\": \"Continuous Loop\",\n"
                f"  \"steps\": [\n"
                f"    {{\n"
                f"      \"number\": 1,\n"
                f"      \"title\": \"Step Title\",\n"
                f"      \"points\": [\"point 1 max 4 words\", \"point 2 max 4 words\"]\n"
                f"    }}\n"
                f"  ],\n"
                f"  \"left_panel\": {{\n"
                f"    \"title\": \"LEFT PANEL\",\n"
                f"    \"items\": [\"Item 1\", \"Item 2\", \"Item 3\", \"Item 4\"]\n"
                f"  }},\n"
                f"  \"right_panels\": [\n"
                f"    {{\n"
                f"      \"title\": \"PANEL TITLE\",\n"
                f"      \"items\": [\"point 1 max 5 words\", \"point 2 max 5 words\", \"point 3 max 5 words\"]\n"
                f"    }}\n"
                f"  ],\n"
                f"  \"footer\": \"© Aurobinda Ojha | Follow for more\"\n"
                f"}}\n\n"
                f"Create exactly 8 steps in the flow.\n"
                f"Each step has exactly 2 bullet points.\n"
                f"Create exactly 3 right panels.\n"
                f"Left panel has exactly 4 items.\n"
                f"Make everything specific to the post topic."}
        ],
        max_tokens=1200,
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

def get_content_seed(post_content):
    return int(hashlib.md5(post_content.encode()).hexdigest(), 16)

def draw_rounded_rect(draw, x0, y0, x1, y1, radius, fill=None, outline=None, width=2):
    draw.rounded_rectangle([(x0, y0), (x1, y1)],
                            radius=radius, fill=fill, outline=outline, width=width)

def draw_arrow_down(draw, x, y, length, color):
    draw.line([(x, y), (x, y+length)], fill=color, width=2)
    draw.polygon([
        (x-8, y+length-8),
        (x+8, y+length-8),
        (x, y+length+6)
    ], fill=color)

def draw_number_circle(draw, cx, cy, number, color, font):
    r = 16
    draw.ellipse([(cx-r, cy-r), (cx+r, cy+r)], fill=color)
    bbox = draw.textbbox((0,0), str(number), font=font)
    tw = bbox[2]-bbox[0]
    th = bbox[3]-bbox[1]
    draw.text((cx-tw//2, cy-th//2-1), str(number), font=font, fill=(255,255,255))

def draw_step_box(draw, x, y, w, h, number, title, points, color, fonts):
    font_num, font_title, font_point = fonts

    # Box
    draw_rounded_rect(draw, x, y, x+w, y+h, 10,
                      fill=(255,255,255), outline=color, width=2)

    # Number circle
    draw_number_circle(draw, x+22, y+h//2, number, color, font_num)

    # Title
    draw.text((x+46, y+8), title, font=font_title, fill=color)

    # Divider
    draw.line([(x+46, y+32), (x+w-10, y+32)], fill=(220,220,220), width=1)

    # Points
    py = y+38
    for point in points[:2]:
        draw.ellipse([(x+46, py+5), (x+53, py+12)], fill=color)
        draw.text((x+60, py), point, font=font_point, fill=(60,60,60))
        py += 22

def draw_side_panel(draw, x, y, w, h, title, items, color, fonts):
    font_title, font_item = fonts

    draw_rounded_rect(draw, x, y, x+w, y+h, 10,
                      fill=(255,255,255), outline=color, width=2)

    # Title background
    draw_rounded_rect(draw, x, y, x+w, y+40, 10,
                      fill=color, outline=color, width=0)

    # Title text
    bbox = draw.textbbox((0,0), title, font=font_title)
    tw = bbox[2]-bbox[0]
    draw.text((x+(w-tw)//2, y+10), title, font=font_title, fill=(255,255,255))

    # Items with checkmarks
    iy = y+50
    for item in items[:3]:
        draw.text((x+10, iy), "✓", font=font_item, fill=color)
        item_wrapped = textwrap.fill(item, width=18)
        draw.text((x+30, iy), item_wrapped, font=font_item, fill=(60,60,60))
        iy += len(item_wrapped.split('\n')) * 20 + 8

def draw_left_panel(draw, x, y, w, h, title, items, fonts):
    font_title, font_item = fonts
    color = (100, 130, 180)

    draw_rounded_rect(draw, x, y, x+w, y+h, 10,
                      fill=(240, 245, 255), outline=color, width=2)

    # Title
    draw.text((x+10, y+15), title, font=font_title, fill=color)
    draw.line([(x+10, y+38), (x+w-10, y+38)], fill=color, width=1)

    # Items with icons
    icons = ["📊", "🔔", "⚠", "🔄"]
    iy = y+48
    for i, item in enumerate(items[:4]):
        icon = icons[i] if i < len(icons) else "•"
        draw.text((x+8, iy), icon, font=font_item, fill=color)
        draw.text((x+35, iy), item, font=font_item, fill=(60,60,60))
        iy += 28

def create_flowchart_image(post_content, data):
    print(f"[{datetime.now()}] Creating flowchart image...")

    width, height = 1080, 1920
    seed = get_content_seed(post_content)

    # White background
    image = Image.new("RGB", (width, height), (250, 250, 252))
    draw = ImageDraw.Draw(image)

    # Subtle background
    for y in range(0, height, 40):
        draw.line([(0, y), (width, y)], fill=(240, 240, 245), width=1)

    # Load fonts
    try:
        font_main_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 44)
        font_subtitle = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        font_author = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        font_step_num = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        font_step_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
        font_step_point = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        font_panel_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        font_panel_item = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        font_start = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_footer = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except:
        font_main_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
        font_author = ImageFont.load_default()
        font_step_num = ImageFont.load_default()
        font_step_title = ImageFont.load_default()
        font_step_point = ImageFont.load_default()
        font_panel_title = ImageFont.load_default()
        font_panel_item = ImageFont.load_default()
        font_start = ImageFont.load_default()
        font_footer = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # ── Header ────────────────────────────────────────────────────────────────
    title = data.get("title", "Cybersecurity Architecture")
    title_wrapped = textwrap.fill(title, width=30)
    title_lines = title_wrapped.split('\n')
    ty = 25
    for line in title_lines:
        bbox = draw.textbbox((0,0), line, font=font_main_title)
        tw = bbox[2]-bbox[0]
        draw.text(((width-tw)//2, ty), line, font=font_main_title, fill=(30,30,30))
        ty += 52

    subtitle = data.get("subtitle", "by Aurobinda Ojha")
    bbox = draw.textbbox((0,0), subtitle, font=font_subtitle)
    sw = bbox[2]-bbox[0]
    draw.text(((width-sw)//2, ty), subtitle, font=font_subtitle, fill=(41,98,181))
    ty += 40

    # ── START oval ────────────────────────────────────────────────────────────
    start_label = data.get("start_label", "START")
    start_w, start_h = 140, 40
    start_x = (width - start_w) // 2
    start_y = ty
    draw_rounded_rect(draw, start_x, start_y, start_x+start_w, start_y+start_h,
                      20, fill=(255,255,255), outline=(220,50,50), width=2)
    bbox = draw.textbbox((0,0), start_label, font=font_start)
    slw = bbox[2]-bbox[0]
    draw.text(((width-slw)//2, start_y+8), start_label, font=font_start, fill=(220,50,50))
    ty += start_h + 5

    # Layout dimensions
    left_panel_w = 140
    right_panel_w = 200
    flow_x = left_panel_w + 20
    flow_w = width - left_panel_w - right_panel_w - 50
    flow_cx = flow_x + flow_w // 2
    step_h = 90
    arrow_h = 25
    step_gap = step_h + arrow_h

    steps = data.get("steps", [])[:8]

    # ── Left panel ────────────────────────────────────────────────────────────
    left_panel = data.get("left_panel", {})
    left_h = len(steps) * step_gap + 60
    draw_left_panel(
        draw, 5, ty+10, left_panel_w-10, left_h,
        left_panel.get("title", "MONITORING"),
        left_panel.get("items", []),
        (font_panel_title, font_panel_item)
    )

    # Parallel inputs text
    draw.text((8, ty+left_h+15), "Parallel inputs", font=font_small, fill=(150,150,150))

    # ── Right panels ──────────────────────────────────────────────────────────
    right_panels = data.get("right_panels", [])[:3]
    rp_h = 160
    rp_x = width - right_panel_w - 10
    rp_y = ty + 10

    for idx, panel in enumerate(right_panels):
        color = SIDE_COLORS[idx % len(SIDE_COLORS)]
        draw_side_panel(
            draw, rp_x, rp_y, right_panel_w, rp_h,
            panel.get("title", "PANEL"),
            panel.get("items", []),
            color,
            (font_panel_title, font_panel_item)
        )

        # Arrow from panel to flow
        arrow_x = rp_x - 2
        arrow_y = rp_y + rp_h // 2
        draw.line([(arrow_x-30, arrow_y), (arrow_x, arrow_y)],
                  fill=color, width=2)
        draw.polygon([
            (arrow_x-12, arrow_y-6),
            (arrow_x-12, arrow_y+6),
            (arrow_x-2, arrow_y)
        ], fill=color)

        rp_y += rp_h + 30

    # ── Flow steps ────────────────────────────────────────────────────────────
    step_fonts = (font_step_num, font_step_title, font_step_point)
    current_y = ty

    for idx, step in enumerate(steps):
        color = STEP_COLORS[idx % len(STEP_COLORS)]

        # Arrow down from previous
        if idx > 0:
            draw_arrow_down(draw, flow_cx, current_y, arrow_h, (100,100,100))
            current_y += arrow_h + 5

        # Step box
        draw_step_box(
            draw,
            flow_x, current_y,
            flow_w, step_h,
            step.get("number", idx+1),
            step.get("title", f"Step {idx+1}"),
            step.get("points", []),
            color,
            step_fonts
        )

        # Left arrow connector
        draw.line([
            (flow_x-20, current_y+step_h//2),
            (flow_x, current_y+step_h//2)
        ], fill=color, width=2)
        draw.polygon([
            (flow_x-10, current_y+step_h//2-5),
            (flow_x-10, current_y+step_h//2+5),
            (flow_x, current_y+step_h//2)
        ], fill=color)

        current_y += step_h

    # ── END oval ──────────────────────────────────────────────────────────────
    draw_arrow_down(draw, flow_cx, current_y, arrow_h, (100,100,100))
    current_y += arrow_h + 10

    end_label = data.get("end_label", "END")
    end_subtitle = data.get("end_subtitle", "Continuous Loop")
    end_w, end_h = 160, 50
    end_x = flow_cx - end_w//2
    draw_rounded_rect(draw, end_x, current_y, end_x+end_w, current_y+end_h,
                      25, fill=(255,255,255), outline=(220,50,50), width=2)
    bbox = draw.textbbox((0,0), end_label, font=font_start)
    elw = bbox[2]-bbox[0]
    draw.text((flow_cx-elw//2, current_y+4), end_label, font=font_start, fill=(220,50,50))
    bbox = draw.textbbox((0,0), end_subtitle, font=font_small)
    esw = bbox[2]-bbox[0]
    draw.text((flow_cx-esw//2, current_y+28), end_subtitle, font=font_small, fill=(150,150,150))
    current_y += end_h + 20

    # ── Footer ────────────────────────────────────────────────────────────────
    draw.line([(20, current_y), (width-20, current_y)], fill=(200,200,200), width=1)
    footer = data.get("footer", "© Aurobinda Ojha | Follow for more")
    bbox = draw.textbbox((0,0), footer, font=font_footer)
    fw = bbox[2]-bbox[0]
    draw.text(((width-fw)//2, current_y+10), footer, font=font_footer, fill=(100,100,100))

    date_str = datetime.now().strftime("%B %d, %Y")
    bbox = draw.textbbox((0,0), f"#AgenticAI  #Cybersecurity  |  {date_str}", font=font_small)
    dw = bbox[2]-bbox[0]
    draw.text(((width-dw)//2, current_y+35),
              f"#AgenticAI  #Cybersecurity  |  {date_str}",
              font=font_small, fill=(150,150,150))

    current_y += 65

    # Crop to content
    image = image.crop((0, 0, width, min(current_y + 20, height)))

    img_bytes = io.BytesIO()
    image.save(img_bytes, format="JPEG", quality=95)
    img_bytes.seek(0)
    print(f"Flowchart image created!")
    return img_bytes.read()

def upload_image_to_linkedin(image_data):
    print(f"[{datetime.now()}] Uploading image to LinkedIn...")

    register_payload = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": f"urn:li:person:{LINKEDIN_PERSON_ID}",
            "serviceRelationships": [
                {
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent"
                }
            ]
        }
    }

    r = requests.post(
        "https://api.linkedin.com/v2/assets?action=registerUpload",
        headers=LINKEDIN_HEADERS,
        json=register_payload
    )
    r.raise_for_status()
    response_json = r.json()

    upload_url = response_json["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
    asset = response_json["value"]["asset"]
    print(f"Asset ID: {asset}")

    upload_headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/octet-stream"
    }
    upload_response = requests.put(
        upload_url,
        headers=upload_headers,
        data=image_data
    )
    upload_response.raise_for_status()
    print(f"Image uploaded successfully!")
    return asset

def job_post():
    print(f"[{datetime.now()}] Generating LinkedIn flowchart post about: {TOPIC}")

    content = ai_generate_post(TOPIC)
    print(f"Generated content: {content[:100]}...")

    data = ai_generate_flowchart_data(content)
    print(f"Title: {data.get('title')}")

    image_bytes = create_flowchart_image(content, data)
    asset = upload_image_to_linkedin(image_bytes)

    payload = {
        "author": f"urn:li:person:{LINKEDIN_PERSON_ID}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": content
                },
                "shareMediaCategory": "IMAGE",
                "media": [
                    {
                        "status": "READY",
                        "description": {
                            "text": data.get("title", TOPIC)
                        },
                        "media": asset,
                        "title": {
                            "text": data.get("title", TOPIC)[:100]
                        }
                    }
                ]
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    r = requests.post(
        "https://api.linkedin.com/v2/ugcPosts",
        headers=LINKEDIN_HEADERS,
        json=payload
    )
    r.raise_for_status()
    post_id = r.json().get("id")
    print(f"[{datetime.now()}] LinkedIn flowchart post published! ID: {post_id}")

if __name__ == "__main__":
    if RUN_MODE == "post":
        job_post()
