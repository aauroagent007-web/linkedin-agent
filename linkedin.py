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
import random

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

def ai_generate_chalkboard_data(post_content):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content":
                f"Based on this LinkedIn post, create a chalkboard-style infographic structure.\n"
                f"Post: {post_content}\n\n"
                f"Reply with JSON only, no extra text:\n"
                f"{{\n"
                f"  \"title\": \"Topic: A Simple Analogy\",\n"
                f"  \"subtitle\": \"Confused? Here is a simple breakdown\",\n"
                f"  \"items\": [\n"
                f"    {{\n"
                f"      \"term\": \"TERM\",\n"
                f"      \"analogy\": \"Simple Analogy\",\n"
                f"      \"points\": [\"point 1 max 6 words\", \"point 2 max 6 words\", \"point 3 max 6 words\"],\n"
                f"      \"note\": \"Key insight max 6 words\",\n"
                f"      \"note_type\": \"warning or success or info\"\n"
                f"    }}\n"
                f"  ],\n"
                f"  \"flow\": [\"Term1 does X\", \"Term2 does Y\", \"Term3 does Z\", \"Term4 does W\"]\n"
                f"}}\n\n"
                f"Create exactly 4 items explaining the post topic like analogies.\n"
                f"Make analogies simple and relatable.\n"
                f"flow has exactly 4 steps matching the 4 items."}
        ],
        max_tokens=800,
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

def get_content_seed(post_content):
    return int(hashlib.md5(post_content.encode()).hexdigest(), 16)

def draw_chalk_text(draw, x, y, text, font, color, roughness=1):
    # Simulate chalk effect with slight offset
    draw.text((x+roughness, y+roughness), text, font=font, fill=(*color[:3], 80))
    draw.text((x, y), text, font=font, fill=color)

def draw_chalk_line(draw, x0, y0, x1, y1, color, width=2):
    # Dashed chalk line
    length = math.sqrt((x1-x0)**2 + (y1-y0)**2)
    segments = int(length / 12)
    if segments == 0:
        segments = 1
    for i in range(segments):
        t0 = i / segments
        t1 = min((i + 0.6) / segments, 1.0)
        sx0 = int(x0 + t0 * (x1-x0))
        sy0 = int(y0 + t0 * (y1-y0))
        sx1 = int(x0 + t1 * (x1-x0))
        sy1 = int(y0 + t1 * (y1-y0))
        draw.line([(sx0, sy0), (sx1, sy1)], fill=color, width=width)

def draw_chalk_rect(draw, x0, y0, x1, y1, color, width=2):
    draw_chalk_line(draw, x0, y0, x1, y0, color, width)
    draw_chalk_line(draw, x1, y0, x1, y1, color, width)
    draw_chalk_line(draw, x1, y1, x0, y1, color, width)
    draw_chalk_line(draw, x0, y1, x0, y0, color, width)

def draw_arrow_down_chalk(draw, x, y, size, color):
    draw_chalk_line(draw, x, y, x, y+size, color, 3)
    draw.polygon([(x-10, y+size-8), (x+10, y+size-8), (x, y+size+10)], fill=color)

def draw_stars(draw, width, height, color):
    rng = random.Random(42)
    for _ in range(8):
        sx = rng.randint(20, width-20)
        sy = rng.randint(20, 150)
        draw.text((sx, sy), "★", fill=color)

def draw_banner(draw, x, y, width, height, color, font, text):
    # Draw banner ribbon shape
    draw.polygon([
        (x, y+15), (x+15, y), (x+width-15, y),
        (x+width, y+15), (x+width, y+height-15),
        (x+width-15, y+height), (x+15, y+height),
        (x, y+height-15)
    ], fill=color)
    bbox = draw.textbbox((0,0), text, font=font)
    tw = bbox[2]-bbox[0]
    draw.text((x+(width-tw)//2, y+8), text, font=font, fill=(255,255,255))

def create_chalkboard_image(post_content, data):
    print(f"[{datetime.now()}] Creating chalkboard image...")

    width, height = 1080, 1440

    # Chalkboard green background
    image = Image.new("RGB", (width, height), (45, 90, 60))
    draw = ImageDraw.Draw(image)

    # Add texture overlay — vertical subtle lines
    for x in range(0, width, 3):
        alpha = random.randint(0, 15)
        draw.line([(x, 0), (x, height)], fill=(40+alpha, 85+alpha, 55+alpha), width=1)

    # Wooden frame border
    frame = 20
    draw.rectangle([(0, 0), (width, height)], outline=(101, 67, 33), width=frame)
    draw.rectangle([(frame, frame), (width-frame, height-frame)],
                   outline=(120, 80, 40), width=4)

    # Load fonts
    try:
        font_banner = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42)
        font_subtitle = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        font_term = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
        font_analogy = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        font_point = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        font_note = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        font_flow = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
        font_author = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except:
        font_banner = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
        font_term = ImageFont.load_default()
        font_analogy = ImageFont.load_default()
        font_point = ImageFont.load_default()
        font_note = ImageFont.load_default()
        font_flow = ImageFont.load_default()
        font_author = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Colors
    WHITE = (240, 240, 240)
    YELLOW = (255, 220, 50)
    RED = (220, 80, 80)
    CYAN = (80, 220, 200)
    GREEN_LIGHT = (100, 220, 130)
    ORANGE = (255, 160, 50)
    PINK = (220, 100, 180)

    ITEM_COLORS = [CYAN, YELLOW, GREEN_LIGHT, ORANGE]
    NOTE_COLORS = {
        "warning": (220, 80, 80),
        "success": (100, 200, 100),
        "info": (80, 160, 220)
    }
    NOTE_ICONS = {
        "warning": "⚠",
        "success": "✓",
        "info": "ℹ"
    }

    # Draw stars
    draw_stars(draw, width, height, YELLOW)

    # ── Banner title ──────────────────────────────────────────────────────────
    title = data.get("title", "AI Concepts: A Simple Analogy")
    parts = title.split(":")
    banner_y = 40
    banner_w = width - 80

    draw_banner(draw, 40, banner_y, banner_w, 65, (150, 30, 30), font_banner,
                parts[0] if len(parts) > 1 else title)

    if len(parts) > 1:
        rest = parts[1].strip()
        bbox = draw.textbbox((0,0), rest, font=font_banner)
        rw = bbox[2]-bbox[0]
        draw.text(((width-rw)//2, banner_y+20), rest, font=font_banner, fill=WHITE)

    # Subtitle
    subtitle = data.get("subtitle", "")
    bbox = draw.textbbox((0,0), subtitle, font=font_subtitle)
    sw = bbox[2]-bbox[0]
    draw_chalk_text(draw, (width-sw)//2, 120, subtitle, font_subtitle, (180, 200, 180))

    # Divider
    draw_chalk_line(draw, 40, 155, width-40, 155, WHITE, 2)

    # ── Left dashed vertical line ─────────────────────────────────────────────
    draw_chalk_line(draw, 230, 165, 230, 1200, (100, 160, 120), 2)

    # ── Items ─────────────────────────────────────────────────────────────────
    items = data.get("items", [])[:4]
    item_start_y = 170
    item_gap = 240

    for idx, item in enumerate(items):
        color = ITEM_COLORS[idx % len(ITEM_COLORS)]
        iy = item_start_y + idx * item_gap

        # Term on left side (large)
        term = item.get("term", "")
        draw_chalk_text(draw, 45, iy + 20, term, font_term, WHITE)

        # Equals sign
        draw_chalk_text(draw, 45, iy + 80, "=", font_analogy, RED)

        # Analogy
        analogy = item.get("analogy", "")
        analogy_bbox = draw.textbbox((0,0), "= ", font=font_analogy)
        draw_chalk_text(draw, 80, iy + 80, analogy, font_analogy, color)

        # Underline analogy
        analogy_w = draw.textbbox((0,0), analogy, font=font_analogy)[2]
        draw_chalk_line(draw, 80, iy + 115, 80+analogy_w, iy + 115, color, 2)

        # Bullet points
        points = item.get("points", [])
        py = iy + 130
        for point in points[:3]:
            draw.ellipse([(248, py+8), (258, py+18)], fill=WHITE)
            draw_chalk_text(draw, 268, py, point, font_point, WHITE)
            py += 30

        # Note box
        note = item.get("note", "")
        note_type = item.get("note_type", "info")
        note_color = NOTE_COLORS.get(note_type, RED)
        note_icon = NOTE_ICONS.get(note_type, "•")

        if note:
            note_x = 248
            note_y = py + 5
            note_w = width - note_x - 50
            draw_chalk_rect(draw, note_x, note_y, note_x+note_w, note_y+32, note_color, 2)
            draw_chalk_text(draw, note_x+8, note_y+6,
                          f"{note_icon} {note}", font_note, note_color)

        # Arrow down between items
        if idx < len(items) - 1:
            arrow_y = iy + item_gap - 25
            draw_arrow_down_chalk(draw, width//2, arrow_y, 20, RED)

    # ── Flow bar at bottom ────────────────────────────────────────────────────
    flow_y = item_start_y + len(items) * item_gap + 10
    flow_steps = data.get("flow", [])[:4]

    # Flow background oval
    draw.rounded_rectangle(
        [(35, flow_y), (width-35, flow_y+65)],
        radius=32,
        fill=(30, 70, 45),
        outline=YELLOW,
        width=3
    )

    step_w = (width - 80) // len(flow_steps)
    for i, step in enumerate(flow_steps):
        sx = 40 + i * step_w + step_w//2
        color = ITEM_COLORS[i % len(ITEM_COLORS)]

        # Step text
        bbox = draw.textbbox((0,0), step, font=font_flow)
        sw = bbox[2]-bbox[0]
        draw.text((sx - sw//2, flow_y+18), step, font=font_flow, fill=color)

        # Arrow between steps
        if i < len(flow_steps) - 1:
            ax = 40 + (i+1) * step_w - 15
            draw.text((ax, flow_y+18), "→", font=font_flow, fill=WHITE)

    # ── Chalk tray decoration ─────────────────────────────────────────────────
    tray_y = height - 90
    draw.rectangle([(frame, tray_y), (width-frame, tray_y+8)], fill=(80, 50, 20))

    # Chalk pieces
    chalk_colors = [(240,240,240), (220,100,100), (100,180,220), (220,200,100)]
    for ci, cc in enumerate(chalk_colors):
        cx = 60 + ci * 80
        draw.rectangle([(cx, tray_y+15), (cx+55, tray_y+32)], fill=cc)

    # ── Footer ────────────────────────────────────────────────────────────────
    footer_y = tray_y + 40
    footer_text = f"Follow Aurobinda Ojha  |  Cybersecurity & Agentic AI Research"
    bbox = draw.textbbox((0,0), footer_text, font=font_author)
    fw = bbox[2]-bbox[0]
    draw.text(((width-fw)//2, footer_y), footer_text, font=font_author, fill=(180, 180, 180))

    date_str = datetime.now().strftime("%B %d, %Y")
    bbox = draw.textbbox((0,0), f"#AgenticAI  #Cybersecurity  |  {date_str}", font=font_small)
    dw = bbox[2]-bbox[0]
    draw.text(((width-dw)//2, footer_y+24), f"#AgenticAI  #Cybersecurity  |  {date_str}",
              font=font_small, fill=(140, 140, 140))

    img_bytes = io.BytesIO()
    image.save(img_bytes, format="JPEG", quality=95)
    img_bytes.seek(0)
    print(f"Chalkboard image created!")
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
    print(f"[{datetime.now()}] Generating LinkedIn chalkboard post about: {TOPIC}")

    content = ai_generate_post(TOPIC)
    print(f"Generated content: {content[:100]}...")

    data = ai_generate_chalkboard_data(content)
    print(f"Chalkboard title: {data.get('title')}")

    image_bytes = create_chalkboard_image(content, data)
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
    print(f"[{datetime.now()}] LinkedIn chalkboard post published! ID: {post_id}")

if __name__ == "__main__":
    if RUN_MODE == "post":
        job_post()
