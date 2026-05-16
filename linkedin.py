import openai
import requests
import os
import textwrap
import random
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

COLOR_THEMES = [
    {"bg_top": (10, 25, 47), "bg_bottom": (0, 10, 30), "accent": (100, 255, 218), "highlight": (0, 180, 255)},
    {"bg_top": (20, 0, 40), "bg_bottom": (5, 0, 20), "accent": (200, 100, 255), "highlight": (255, 50, 150)},
    {"bg_top": (0, 30, 20), "bg_bottom": (0, 10, 5), "accent": (50, 255, 150), "highlight": (0, 200, 100)},
    {"bg_top": (40, 10, 0), "bg_bottom": (20, 5, 0), "accent": (255, 150, 50), "highlight": (255, 80, 0)},
    {"bg_top": (0, 20, 40), "bg_bottom": (0, 5, 20), "accent": (50, 200, 255), "highlight": (0, 150, 255)},
    {"bg_top": (30, 0, 30), "bg_bottom": (10, 0, 10), "accent": (255, 100, 200), "highlight": (200, 0, 200)},
    {"bg_top": (10, 10, 10), "bg_bottom": (0, 0, 0), "accent": (255, 215, 0), "highlight": (255, 165, 0)},
]

def ai_generate_post(topic):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": AGENT_PERSONA},
            {"role": "user", "content":
                f"Write a professional LinkedIn post about a fresh angle on: {topic}\n\n"
                f"IMPORTANT FORMAT RULES:\n"
                f"- Write in SHORT lines with line breaks between each thought\n"
                f"- Max 2-3 sentences per paragraph\n"
                f"- Add relevant emojis at the start of key lines\n"
                f"- Use simple conversational language\n"
                f"- Start with a hook line that grabs attention\n"
                f"- End with a question to spark discussion\n"
                f"- Total max 150 words\n\n"
                f"Example style:\n"
                f"Most people think AI agents are just chatbots.\n\n"
                f"They're wrong.\n\n"
                f"🤖 Agentic AI can now autonomously detect and respond to threats.\n\n"
                f"🔐 Without human intervention.\n\n"
                f"This changes everything about how we think about cybersecurity.\n\n"
                f"Are your defenses ready for machine-speed attacks?"}
        ],
        max_tokens=400,
    )
    return response.choices[0].message.content.strip()

def ai_generate_headline(post_content):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content":
                f"Based on this LinkedIn post, write ONE powerful headline (max 8 words).\n"
                f"Post: {post_content[:300]}\n"
                f"Reply with ONLY the headline, nothing else."}
        ],
        max_tokens=20,
    )
    return response.choices[0].message.content.strip()

def ai_generate_image_data(post_content):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content":
                f"Based on this LinkedIn post, generate structured data for an infographic image.\n"
                f"Post: {post_content}\n\n"
                f"Reply with JSON only, no extra text:\n"
                f"{{\n"
                f"  \"stat1_number\": \"85%\",\n"
                f"  \"stat1_label\": \"of attacks use AI\",\n"
                f"  \"stat2_number\": \"3x\",\n"
                f"  \"stat2_label\": \"faster threat detection\",\n"
                f"  \"stat3_number\": \"$4.5M\",\n"
                f"  \"stat3_label\": \"average breach cost\",\n"
                f"  \"key_insight\": \"One short powerful insight from the post (max 10 words)\",\n"
                f"  \"visual_type\": \"one of: network, shield, brain, lock, warning, graph\"\n"
                f"}}"}
        ],
        max_tokens=200,
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    import json
    return json.loads(raw)

def get_content_seed(post_content):
    hash_val = int(hashlib.md5(post_content.encode()).hexdigest(), 16)
    return hash_val

def create_gradient_background(width, height, color_top, color_bottom):
    image = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(image)
    for y in range(height):
        ratio = y / height
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * ratio)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * ratio)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return image

def draw_network_visual(draw, cx, cy, size, accent, highlight, rng):
    nodes = []
    for i in range(6):
        angle = math.pi / 3 * i
        nx = cx + size * math.cos(angle)
        ny = cy + size * math.sin(angle)
        nodes.append((nx, ny))
        draw.ellipse([(nx-8, ny-8), (nx+8, ny+8)], fill=accent)
    draw.ellipse([(cx-12, cy-12), (cx+12, cy+12)], fill=highlight)
    for node in nodes:
        draw.line([(cx, cy), node], fill=accent, width=1)
    for i in range(len(nodes)):
        if rng.random() > 0.5:
            draw.line([nodes[i], nodes[(i+1) % len(nodes)]], fill=accent, width=1)

def draw_shield_visual(draw, cx, cy, size, accent, highlight):
    shield_points = [
        (cx, cy - size),
        (cx + size * 0.8, cy - size * 0.5),
        (cx + size * 0.8, cy + size * 0.2),
        (cx, cy + size),
        (cx - size * 0.8, cy + size * 0.2),
        (cx - size * 0.8, cy - size * 0.5),
    ]
    draw.polygon(shield_points, outline=accent, fill=None)
    inner = [(cx + (p[0]-cx)*0.7, cy + (p[1]-cy)*0.7) for p in shield_points]
    draw.polygon(inner, outline=highlight, fill=None)
    draw.text((cx - 10, cy - 15), "✓", fill=accent)

def draw_brain_visual(draw, cx, cy, size, accent, highlight, rng):
    draw.ellipse([(cx-size, cy-size*0.8), (cx+size, cy+size*0.8)], outline=accent)
    draw.line([(cx, cy-size*0.8), (cx, cy+size*0.8)], fill=highlight, width=2)
    for i in range(4):
        y = cy - size*0.5 + i * (size*0.3)
        draw.arc([(cx-size*0.8, y-15), (cx, y+15)], 180, 0, fill=accent)

def draw_lock_visual(draw, cx, cy, size, accent, highlight):
    draw.rectangle([(cx-size*0.6, cy), (cx+size*0.6, cy+size)], outline=accent)
    draw.arc([(cx-size*0.5, cy-size*0.8), (cx+size*0.5, cy+size*0.2)], 180, 0, fill=highlight)
    draw.ellipse([(cx-8, cy+size*0.4), (cx+8, cy+size*0.6)], fill=accent)

def draw_warning_visual(draw, cx, cy, size, accent, highlight):
    triangle = [(cx, cy-size), (cx+size, cy+size*0.8), (cx-size, cy+size*0.8)]
    draw.polygon(triangle, outline=accent)
    inner = [(cx + (p[0]-cx)*0.7, cy + (p[1]-cy)*0.7) for p in triangle]
    draw.polygon(inner, outline=highlight)
    draw.text((cx-8, cy-5), "!", fill=accent)

def draw_graph_visual(draw, cx, cy, size, accent, highlight, rng):
    draw.line([(cx-size, cy+size*0.5), (cx+size, cy+size*0.5)], fill=accent, width=2)
    draw.line([(cx-size, cy-size), (cx-size, cy+size*0.5)], fill=accent, width=2)
    points = []
    for i in range(6):
        x = cx - size + i * (size*0.4)
        y = cy + size*0.5 - rng.randint(10, int(size*1.3))
        points.append((x, y))
    for i in range(len(points)-1):
        draw.line([points[i], points[i+1]], fill=highlight, width=2)
    for p in points:
        draw.ellipse([(p[0]-4, p[1]-4), (p[0]+4, p[1]+4)], fill=accent)

def draw_visual_element(draw, visual_type, cx, cy, size, accent, highlight, seed):
    rng = random.Random(seed)
    if visual_type == "network":
        draw_network_visual(draw, cx, cy, size, accent, highlight, rng)
    elif visual_type == "shield":
        draw_shield_visual(draw, cx, cy, size, accent, highlight)
    elif visual_type == "brain":
        draw_brain_visual(draw, cx, cy, size, accent, highlight, rng)
    elif visual_type == "lock":
        draw_lock_visual(draw, cx, cy, size, accent, highlight)
    elif visual_type == "warning":
        draw_warning_visual(draw, cx, cy, size, accent, highlight)
    elif visual_type == "graph":
        draw_graph_visual(draw, cx, cy, size, accent, highlight, rng)
    else:
        draw_network_visual(draw, cx, cy, size, accent, highlight, rng)

def draw_unique_pattern(draw, width, height, accent, highlight, seed):
    rng = random.Random(seed)
    for _ in range(15):
        x = rng.randint(0, width)
        y = rng.randint(0, height)
        length = rng.randint(30, 150)
        direction = rng.choice(['h', 'v'])
        color = accent if rng.random() > 0.5 else highlight
        if direction == 'h':
            draw.line([(x, y), (x + length, y)], fill=color, width=1)
        else:
            draw.line([(x, y), (x, y + length)], fill=color, width=1)
    for _ in range(20):
        x = rng.randint(0, width)
        y = rng.randint(0, height)
        r = rng.randint(1, 3)
        draw.ellipse([(x-r, y-r), (x+r, y+r)], fill=accent)

def create_post_image(post_content, headline, image_data):
    print(f"[{datetime.now()}] Creating unique infographic image...")

    width, height = 1200, 627
    seed = get_content_seed(post_content)
    theme = COLOR_THEMES[seed % len(COLOR_THEMES)]

    bg_top = theme["bg_top"]
    bg_bottom = theme["bg_bottom"]
    accent = theme["accent"]
    highlight = theme["highlight"]

    bg_image = create_gradient_background(width, height, bg_top, bg_bottom)
    draw = ImageDraw.Draw(bg_image)

    draw_unique_pattern(draw, width, height, accent, highlight, seed)

    # Split layout: left = text, right = visual
    split_x = 720

    # Left panel separator
    draw.rectangle([(40, 40), (46, height - 40)], fill=accent)
    draw.line([(split_x, 40), (split_x, height - 40)], fill=accent, width=1)

    # Draw visual element on right panel
    visual_cx = split_x + (width - split_x) // 2
    visual_cy = height // 2 - 30
    visual_size = 80
    draw_visual_element(
        draw,
        image_data.get("visual_type", "network"),
        visual_cx, visual_cy, visual_size,
        accent, highlight, seed
    )

    # Draw 3 stats below visual
    stats = [
        (image_data.get("stat1_number", ""), image_data.get("stat1_label", "")),
        (image_data.get("stat2_number", ""), image_data.get("stat2_label", "")),
        (image_data.get("stat3_number", ""), image_data.get("stat3_label", "")),
    ]

    # Load fonts
    try:
        font_headline = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42)
        font_body = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 23)
        font_insight = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_stat_num = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
        font_stat_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        font_author = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        font_tag = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except:
        font_headline = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_insight = ImageFont.load_default()
        font_stat_num = ImageFont.load_default()
        font_stat_label = ImageFont.load_default()
        font_author = ImageFont.load_default()
        font_tag = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Draw stats on right panel
    stat_y = visual_cy + visual_size + 40
    stat_spacing = (width - split_x) // 3
    for i, (num, label) in enumerate(stats):
        sx = split_x + i * stat_spacing + stat_spacing // 2 - 20
        draw.text((sx, stat_y), num, font=font_stat_num, fill=accent)
        draw.text((sx - 10, stat_y + 36), label, font=font_stat_label, fill=(180, 180, 180))

    # Draw key insight box on right
    insight = image_data.get("key_insight", "")
    if insight:
        insight_wrapped = textwrap.fill(insight, width=22)
        draw.rectangle([(split_x + 10, 40), (width - 10, 120)], fill=(0, 0, 0))
        draw.rectangle([(split_x + 10, 40), (width - 10, 120)], outline=accent)
        draw.text((split_x + 20, 50), insight_wrapped, font=font_insight, fill=accent)

    # Left panel content
    draw.rectangle([(0, 0), (width, 5)], fill=accent)
    draw.rectangle([(0, height - 5), (width, height)], fill=accent)

    # Headline on left
    headline_clean = headline.replace('"', '').replace("'", '')
    headline_wrapped = textwrap.fill(headline_clean, width=30)
    draw.text((65, 60), headline_wrapped, font=font_headline, fill=accent)

    # Separator
    draw.rectangle([(65, 185), (500, 189)], fill=highlight)

    # Post excerpt lines on left
    lines = [l for l in post_content.split('\n') if l.strip()][:5]
    y_pos = 205
    for line in lines:
        if y_pos > height - 130:
            break
        line_wrapped = textwrap.fill(line.strip(), width=48)
        draw.text((65, y_pos), line_wrapped, font=font_body, fill=(210, 210, 210))
        y_pos += len(line_wrapped.split('\n')) * 28 + 8

    # Bottom bar
    draw.rectangle([(0, height - 90), (width, height)], fill=(5, 10, 20))
    draw.text((65, height - 72), "Aurobinda Ojha", font=font_author, fill=accent)
    draw.text((65, height - 46), "Independent Researcher | Cybersecurity & Agentic AI", font=font_tag, fill=(180, 180, 180))
    draw.text((65, height - 24), "linkedin.com/in/aurobindaojha", font=font_small, fill=(100, 100, 100))

    draw.text((width - 330, 15), "#AgenticAI  #Cybersecurity", font=font_tag, fill=accent)
    date_str = datetime.now().strftime("%B %d, %Y")
    draw.text((width - 200, height - 26), date_str, font=font_small, fill=(100, 100, 100))

    img_bytes = io.BytesIO()
    bg_image.save(img_bytes, format="JPEG", quality=95)
    img_bytes.seek(0)
    print(f"Infographic image created! Visual type: {image_data.get('visual_type')}")
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
    print(f"[{datetime.now()}] Generating LinkedIn post with infographic about: {TOPIC}")

    content = ai_generate_post(TOPIC)
    print(f"Generated content: {content[:100]}...")

    headline = ai_generate_headline(content)
    print(f"Headline: {headline}")

    image_data = ai_generate_image_data(content)
    print(f"Image data: {image_data}")

    image_bytes = create_post_image(content, headline, image_data)
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
                            "text": headline
                        },
                        "media": asset,
                        "title": {
                            "text": headline[:100]
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
    print(f"[{datetime.now()}] LinkedIn infographic post published! ID: {post_id}")

if __name__ == "__main__":
    if RUN_MODE == "post":
        job_post()
