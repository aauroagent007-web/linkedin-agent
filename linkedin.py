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

def ai_generate_hacker_data(post_content):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content":
                f"Based on this LinkedIn post, create a hacker-style infographic structure.\n"
                f"Post: {post_content}\n\n"
                f"Reply with JSON only, no extra text:\n"
                f"{{\n"
                f"  \"count\": \"10\",\n"
                f"  \"title_line1\": \"KEY CONCEPTS IN\",\n"
                f"  \"title_line2\": \"TOPIC NAME\",\n"
                f"  \"subtitle\": \"Real insights. Real impact. Real knowledge.\",\n"
                f"  \"tagline\": \"BUILT ON RESEARCH. USED BY PROFESSIONALS.\",\n"
                f"  \"categories\": [\n"
                f"    {{\n"
                f"      \"name\": \"CATEGORY NAME\",\n"
                f"      \"icon\": \"one of: shield, brain, lock, network, warning, gear, eye, code\",\n"
                f"      \"items\": [\n"
                f"        {{\n"
                f"          \"name\": \"ITEM NAME\",\n"
                f"          \"description\": \"Short description max 8 words\"\n"
                f"        }}\n"
                f"      ]\n"
                f"    }}\n"
                f"  ],\n"
                f"  \"mindset_title\": \"STAY SHARP.\",\n"
                f"  \"mindset_points\": [\"Point 1 max 4 words\", \"Point 2 max 4 words\", \"Point 3 max 4 words\", \"Point 4 max 4 words\"],\n"
                f"  \"footer_text\": \"Short powerful closing statement.\"\n"
                f"}}\n\n"
                f"Create exactly 6 categories.\n"
                f"Each category has exactly 2-3 items.\n"
                f"Make everything specific to the post topic.\n"
                f"count should reflect total number of items across all categories."}
        ],
        max_tokens=1000,
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

def get_content_seed(post_content):
    return int(hashlib.md5(post_content.encode()).hexdigest(), 16)

def draw_hex_icon(draw, cx, cy, size, color, icon_type):
    points = []
    for i in range(6):
        angle = math.pi / 3 * i - math.pi / 6
        px = cx + size * math.cos(angle)
        py = cy + size * math.sin(angle)
        points.append((px, py))
    draw.polygon(points, outline=color, fill=(color[0]//4, color[1]//4, color[2]//4))
    if icon_type == "shield":
        draw.polygon([(cx, cy-8), (cx+7, cy-4), (cx+7, cy+4), (cx, cy+9), (cx-7, cy+4), (cx-7, cy-4)], outline=color)
    elif icon_type == "brain":
        draw.ellipse([(cx-7, cy-7), (cx+7, cy+7)], outline=color)
        draw.line([(cx, cy-7), (cx, cy+7)], fill=color, width=1)
    elif icon_type == "lock":
        draw.rectangle([(cx-5, cy-2), (cx+5, cy+7)], outline=color)
        draw.arc([(cx-5, cy-8), (cx+5, cy+2)], 180, 0, fill=color)
    elif icon_type == "network":
        draw.ellipse([(cx-2, cy-2), (cx+2, cy+2)], fill=color)
        for angle in [0, 72, 144, 216, 288]:
            rad = math.radians(angle)
            ex = cx + 8*math.cos(rad)
            ey = cy + 8*math.sin(rad)
            draw.line([(cx, cy), (int(ex), int(ey))], fill=color, width=1)
            draw.ellipse([(int(ex)-2, int(ey)-2), (int(ex)+2, int(ey)+2)], fill=color)
    elif icon_type == "warning":
        draw.polygon([(cx, cy-9), (cx+8, cy+6), (cx-8, cy+6)], outline=color)
    elif icon_type == "gear":
        draw.ellipse([(cx-6, cy-6), (cx+6, cy+6)], outline=color)
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            draw.line([(int(cx+6*math.cos(rad)), int(cy+6*math.sin(rad))),
                       (int(cx+9*math.cos(rad)), int(cy+9*math.sin(rad)))], fill=color, width=2)
    elif icon_type == "eye":
        draw.arc([(cx-8, cy-4), (cx+8, cy+4)], 0, 180, fill=color)
        draw.arc([(cx-8, cy-4), (cx+8, cy+4)], 180, 360, fill=color)
        draw.ellipse([(cx-3, cy-3), (cx+3, cy+3)], fill=color)
    elif icon_type == "code":
        draw.text((cx-8, cy-6), "</>", fill=color)

def draw_grid_pattern(draw, width, height, color):
    for x in range(0, width, 50):
        draw.line([(x, 0), (x, height)], fill=color, width=1)
    for y in range(0, height, 50):
        draw.line([(0, y), (width, y)], fill=color, width=1)

def draw_circuit_lines(draw, width, height, color, seed):
    rng = random.Random(seed)
    for _ in range(30):
        x = rng.randint(0, width)
        y = rng.randint(0, height)
        length = rng.randint(30, 150)
        direction = rng.choice(['h', 'v'])
        if direction == 'h':
            draw.line([(x, y), (x+length, y)], fill=color, width=1)
            draw.ellipse([(x+length-2, y-2), (x+length+2, y+2)], fill=color)
        else:
            draw.line([(x, y), (x, y+length)], fill=color, width=1)
            draw.ellipse([(x-2, y+length-2), (x+2, y+length+2)], fill=color)

def create_hacker_image(post_content, data):
    print(f"[{datetime.now()}] Creating hacker-style image...")

    width, height = 1080, 1440
    seed = get_content_seed(post_content)

    image = Image.new("RGB", (width, height), (8, 8, 12))
    draw = ImageDraw.Draw(image)

    draw_grid_pattern(draw, width, height, (18, 18, 25))
    draw_circuit_lines(draw, width, height, (20, 40, 20), seed)

    try:
        font_count = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 120)
        font_title1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        font_title2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
        font_subtitle = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        font_tagline = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        font_cat = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        font_item = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        font_desc = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
        font_mindset = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        font_footer = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
    except:
        font_count = ImageFont.load_default()
        font_title1 = ImageFont.load_default()
        font_title2 = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
        font_tagline = ImageFont.load_default()
        font_cat = ImageFont.load_default()
        font_item = ImageFont.load_default()
        font_desc = ImageFont.load_default()
        font_mindset = ImageFont.load_default()
        font_footer = ImageFont.load_default()
        font_small = ImageFont.load_default()

    RED = (200, 30, 30)
    RED_BRIGHT = (240, 60, 60)
    WHITE = (240, 240, 240)
    GRAY = (150, 150, 160)
    DARK_GRAY = (40, 40, 50)
    GREEN = (0, 200, 100)
    CYAN = (0, 200, 220)
    ORANGE = (220, 140, 0)
    YELLOW = (220, 200, 0)
    CAT_COLORS = [CYAN, GREEN, ORANGE, YELLOW, RED_BRIGHT, (180, 100, 220)]

    # ── Header ────────────────────────────────────────────────────────────────
    draw.ellipse([(-50, -50), (350, 350)], fill=(25, 5, 5))
    draw.ellipse([(20, 20), (280, 280)], fill=(35, 8, 8))
    draw.text((60, 80), "◈", font=font_count, fill=(60, 15, 15))

    count = data.get("count", "10")
    draw.text((width//2 - 20, 20), count, font=font_count, fill=RED)

    title1 = data.get("title_line1", "KEY CONCEPTS IN")
    title2 = data.get("title_line2", "CYBERSECURITY")

    bbox = draw.textbbox((0,0), title1, font=font_title1)
    t1w = bbox[2]-bbox[0]
    draw.text((width - t1w - 30, 20), title1, font=font_title1, fill=WHITE)

    bbox = draw.textbbox((0,0), title2, font=font_title2)
    t2w = bbox[2]-bbox[0]
    draw.text((width - t2w - 20, 60), title2, font=font_title2, fill=RED)

    # Subtitle
    subtitle = data.get("subtitle", "")
    parts = [p.strip() for p in subtitle.split(".") if p.strip()]
    sub_y = 150
    for i, part in enumerate(parts[:3]):
        color = RED_BRIGHT if i == len(parts[:3]) - 1 else WHITE
        draw.text((width//2 + 20, sub_y), part + ".", font=font_subtitle, fill=color)
        sub_y += 30

    # Tagline box
    tagline = data.get("tagline", "")
    tag_y = 195
    draw.rectangle([(width//2 + 10, tag_y), (width-20, tag_y+35)],
                   fill=(20, 20, 28), outline=GRAY, width=1)
    draw.text((width//2 + 20, tag_y + 8), tagline, font=font_tagline, fill=WHITE)

    draw.line([(20, 245), (width-20, 245)], fill=DARK_GRAY, width=1)

    # ── Categories grid ───────────────────────────────────────────────────────
    categories = data.get("categories", [])[:6]
    mindset_w = 240
    cat_area_w = width - mindset_w - 30
    cat_w = (cat_area_w - 40) // 3 - 5
    cat_h = 280
    cat_start_y = 255
    cat_start_x = 15

    for idx, cat in enumerate(categories):
        col = idx % 3
        row = idx // 2
        cx_pos = cat_start_x + col * (cat_w + 8)
        cy_pos = cat_start_y + row * (cat_h + 8)

        cat_color = CAT_COLORS[idx % len(CAT_COLORS)]
        icon_type = cat.get("icon", "shield")

        draw.rectangle([(cx_pos, cy_pos), (cx_pos+cat_w, cy_pos+cat_h)],
                       fill=(12, 12, 18), outline=(40, 40, 55), width=1)
        draw.rectangle([(cx_pos, cy_pos), (cx_pos+cat_w, cy_pos+28)],
                       fill=(18, 18, 28))

        draw_hex_icon(draw, cx_pos+18, cy_pos+14, 10, cat_color, icon_type)

        cat_name = cat.get("name", "")
        cat_wrapped = textwrap.fill(cat_name, width=16)
        draw.text((cx_pos+35, cy_pos+5), cat_wrapped, font=font_cat, fill=cat_color)

        draw.line([(cx_pos+5, cy_pos+30), (cx_pos+cat_w-5, cy_pos+30)],
                  fill=(40, 40, 55), width=1)

        items = cat.get("items", [])[:3]
        item_y = cy_pos + 38
        for item in items:
            name = item.get("name", "")
            desc = item.get("description", "")
            draw.ellipse([(cx_pos+8, item_y+6), (cx_pos+14, item_y+12)], fill=cat_color)
            draw.text((cx_pos+20, item_y), name, font=font_item, fill=WHITE)
            desc_wrapped = textwrap.fill(desc, width=20)
            draw.text((cx_pos+20, item_y+20), desc_wrapped, font=font_desc, fill=GRAY)
            item_y += 20 + len(desc_wrapped.split('\n')) * 16 + 15

    # ── Mindset panel ─────────────────────────────────────────────────────────
    mx = cat_area_w + 25
    my = cat_start_y
    mw = mindset_w - 10
    mh = cat_h * 2 + 8

    draw.rectangle([(mx, my), (mx+mw, my+mh)],
                   fill=(12, 12, 18), outline=(40, 40, 55), width=1)
    draw.rectangle([(mx, my), (mx+mw, my+60)], fill=(18, 18, 28))

    mindset_title = data.get("mindset_title", "STAY SHARP.")
    draw.text((mx+10, my+8), mindset_title, font=font_mindset, fill=RED_BRIGHT)
    draw.text((mx+10, my+32), "THINK LIKE THEM.", font=font_mindset, fill=WHITE)

    mindset_points = data.get("mindset_points", [])[:4]
    mp_y = my + 80
    mp_icons = ["▶", "◈", "◉", "◆"]
    for i, point in enumerate(mindset_points):
        draw.text((mx+10, mp_y), mp_icons[i], font=font_item, fill=CYAN)
        draw.text((mx+30, mp_y), point, font=font_desc, fill=WHITE)
        mp_y += 35

    draw.line([(mx+10, mp_y+10), (mx+mw-10, mp_y+10)], fill=RED, width=2)
    draw.text((mx+10, mp_y+18), "THAT'S THE", font=font_cat, fill=WHITE)
    draw.text((mx+10, mp_y+38), "MINDSET.", font=font_mindset, fill=RED_BRIGHT)

    # ── Footer ────────────────────────────────────────────────────────────────
    footer_y = cat_start_y + 2 * (cat_h + 8) + 15
    draw.rectangle([(0, footer_y), (width, height)], fill=(10, 5, 5))
    draw.line([(0, footer_y), (width, footer_y)], fill=RED, width=3)

    draw.text((25, footer_y+15), "AURO", font=font_title1, fill=WHITE)
    draw.text((25, footer_y+50), "007", font=font_title2, fill=RED)

    footer_text = data.get("footer_text", "KNOWLEDGE IS THE BEST WEAPON.")
    footer_parts = [p.strip() for p in footer_text.split(".") if p.strip()]
    ft_x = 180
    for i, part in enumerate(footer_parts):
        color = RED_BRIGHT if i == len(footer_parts)-1 else WHITE
        text_with_dot = part + "."
        draw.text((ft_x, footer_y+35), text_with_dot, font=font_footer, fill=color)
        ft_x += draw.textbbox((0,0), text_with_dot, font=font_footer)[2] + 5

    date_str = datetime.now().strftime("%B %d, %Y")
    draw.text((25, footer_y+100),
              f"aurobindaojha  |  Cybersecurity & Agentic AI  |  {date_str}",
              font=font_small, fill=GRAY)
    draw.text((25, footer_y+122),
              "#AgenticAI  #Cybersecurity  #AIResearch",
              font=font_small, fill=(80, 80, 90))

    img_bytes = io.BytesIO()
    image.save(img_bytes, format="JPEG", quality=95)
    img_bytes.seek(0)
    print(f"Hacker image created!")
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
    print(f"[{datetime.now()}] Generating LinkedIn hacker post about: {TOPIC}")

    content = ai_generate_post(TOPIC)
    print(f"Generated content: {content[:100]}...")

    data = ai_generate_hacker_data(content)
    print(f"Title: {data.get('title_line2')}")

    image_bytes = create_hacker_image(content, data)
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
                            "text": data.get("title_line2", TOPIC)
                        },
                        "media": asset,
                        "title": {
                            "text": data.get("title_line2", TOPIC)[:100]
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
    print(f"[{datetime.now()}] LinkedIn hacker post published! ID: {post_id}")

if __name__ == "__main__":
    if RUN_MODE == "post":
        job_post()
