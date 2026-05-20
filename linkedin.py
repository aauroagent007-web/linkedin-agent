import openai
import requests
import os
import textwrap
import json
import hashlib
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io

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
    {"bg": (5, 5, 15), "accent": (0, 255, 200), "highlight": (0, 180, 255), "card": (10, 20, 40)},
    {"bg": (10, 0, 20), "accent": (180, 80, 255), "highlight": (255, 50, 150), "card": (20, 5, 35)},
    {"bg": (0, 15, 10), "accent": (50, 255, 150), "highlight": (0, 200, 100), "card": (5, 25, 15)},
    {"bg": (20, 5, 0), "accent": (255, 150, 50), "highlight": (255, 80, 0), "card": (30, 10, 0)},
    {"bg": (0, 10, 25), "accent": (50, 200, 255), "highlight": (0, 150, 255), "card": (0, 15, 35)},
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

def ai_generate_infographic_data(post_content):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content":
                f"Based on this LinkedIn post, create structured infographic data.\n"
                f"Post: {post_content}\n\n"
                f"Reply with JSON only:\n"
                f"{{\n"
                f"  \"title\": \"SHORT TITLE CAPS (max 4 words)\",\n"
                f"  \"sections\": [\n"
                f"    {{\n"
                f"      \"heading\": \"Section Title\",\n"
                f"      \"color\": \"one of: cyan, yellow, green, orange, pink\",\n"
                f"      \"points\": [\"point 1 max 5 words\", \"point 2 max 5 words\", \"point 3 max 5 words\"]\n"
                f"    }}\n"
                f"  ]\n"
                f"}}\n\n"
                f"Create exactly 6 sections relevant to the post.\n"
                f"Each section has exactly 3 bullet points."}
        ],
        max_tokens=600,
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

def get_content_seed(post_content):
    return int(hashlib.md5(post_content.encode()).hexdigest(), 16)

def get_color(name):
    colors = {
        "cyan": (0, 255, 200),
        "yellow": (255, 220, 0),
        "green": (50, 255, 150),
        "orange": (255, 150, 50),
        "pink": (255, 100, 200),
        "blue": (50, 200, 255),
    }
    return colors.get(name, (0, 255, 200))

def draw_dashed_rect(draw, x0, y0, x1, y1, color, dash=8, width=2):
    x = x0
    while x < x1:
        draw.line([(x, y0), (min(x+dash, x1), y0)], fill=color, width=width)
        x += dash * 2
    x = x0
    while x < x1:
        draw.line([(x, y1), (min(x+dash, x1), y1)], fill=color, width=width)
        x += dash * 2
    y = y0
    while y < y1:
        draw.line([(x0, y), (x0, min(y+dash, y1))], fill=color, width=width)
        y += dash * 2
    y = y0
    while y < y1:
        draw.line([(x1, y), (x1, min(y+dash, y1))], fill=color, width=width)
        y += dash * 2

def draw_base_frame(width, height, bg, accent, infographic_data, fonts):
    image = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(image)

    # Grid pattern
    for x in range(0, width, 40):
        draw.line([(x, 0), (x, height)], fill=(20, 20, 35), width=1)
    for y in range(0, height, 40):
        draw.line([(0, y), (width, y)], fill=(20, 20, 35), width=1)

    font_title, font_author, font_section, font_label, font_point, font_small = fonts

    # Author header
    draw.ellipse([(width//2 - 35, 20), (width//2 + 35, 90)], outline=accent, width=2)
    draw.text((width//2 - 20, 42), "AO", font=font_author, fill=accent)
    draw.text((width//2 - 70, 98), "Aurobinda Ojha", font=font_author, fill=(200, 200, 200))
    draw.text((width//2 - 55, 122), "Follow For More", font=font_small, fill=(120, 120, 120))

    # Title
    title = infographic_data.get("title", "AI SECURITY").upper()
    title_wrapped = textwrap.fill(title, width=18)
    title_lines = title_wrapped.split('\n')
    title_y = 160
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=font_title)
        title_w = bbox[2] - bbox[0]
        draw.text(((width - title_w) // 2, title_y), line, font=font_title, fill=(255, 255, 255))
        title_y += 80

    draw.rectangle([(60, title_y + 10), (width - 60, title_y + 13)], fill=accent)

    return image, draw, title_y

def create_frame(width, height, bg, accent, card_bg, infographic_data, fonts, visible_cards):
    image, draw, title_y = draw_base_frame(width, height, bg, accent, infographic_data, fonts)

    font_title, font_author, font_section, font_label, font_point, font_small = fonts

    sections = infographic_data.get("sections", [])[:6]
    card_w = (width - 80) // 2 - 10
    card_h = 270
    card_start_y = title_y + 35

    for idx, section in enumerate(sections):
        if idx >= visible_cards:
            break

        col = idx % 2
        row = idx // 2
        cx = 40 + col * (card_w + 20)
        cy = card_start_y + row * (card_h + 20)

        section_color = get_color(section.get("color", "cyan"))

        # Card background
        draw.rectangle([(cx, cy), (cx + card_w, cy + card_h)], fill=card_bg)
        draw_dashed_rect(draw, cx, cy, cx + card_w, cy + card_h, section_color)

        # Heading
        draw.rectangle([(cx, cy), (cx + card_w, cy + 40)], fill=section_color)
        heading = section.get("heading", "")
        heading_wrapped = textwrap.fill(heading, width=22)
        draw.text((cx + 10, cy + 8), heading_wrapped, font=font_section, fill=(0, 0, 0))

        # Points
        points = section.get("points", [])
        point_y = cy + 55
        for point in points[:3]:
            draw.ellipse([(cx + 12, point_y + 6), (cx + 20, point_y + 14)], fill=section_color)
            point_wrapped = textwrap.fill(str(point), width=28)
            draw.text((cx + 28, point_y), point_wrapped, font=font_point, fill=(210, 210, 210))
            point_y += len(point_wrapped.split('\n')) * 22 + 8

        labels = {
            0: "Purpose:", 1: "What it covers:", 2: "Key Controls:",
            3: "Risks Addressed:", 4: "Framework:", 5: "Tools & Methods:"
        }
        draw.text((cx + 10, cy + card_h - 28), labels.get(idx, "Details:"), font=font_label, fill=section_color)

    # Footer
    card_start_y_footer = card_start_y + 3 * (card_h + 20) + 15
    draw.rectangle([(0, card_start_y_footer), (width, height)], fill=(5, 5, 15))
    draw.rectangle([(0, card_start_y_footer), (width, card_start_y_footer + 3)], fill=accent)
    draw.text((40, card_start_y_footer + 15), "Aurobinda Ojha", font=font_author, fill=accent)
    draw.text((40, card_start_y_footer + 42), "Independent Researcher | Cybersecurity & Agentic AI", font=font_small, fill=(150, 150, 150))
    draw.text((40, card_start_y_footer + 65), "linkedin.com/in/aurobindaojha", font=font_small, fill=(100, 100, 100))
    date_str = datetime.now().strftime("%B %d, %Y")
    draw.text((width - 220, card_start_y_footer + 15), "#AgenticAI", font=font_small, fill=accent)
    draw.text((width - 220, card_start_y_footer + 38), "#Cybersecurity", font=font_small, fill=accent)
    draw.text((width - 220, card_start_y_footer + 61), date_str, font=font_small, fill=(100, 100, 100))

    return image

def create_animated_gif(post_content, infographic_data):
    print(f"[{datetime.now()}] Creating animated GIF infographic...")

    width, height = 1080, 1350
    seed = get_content_seed(post_content)
    theme = COLOR_THEMES[seed % len(COLOR_THEMES)]

    bg = theme["bg"]
    accent = theme["accent"]
    card_bg = theme["card"]

    # Load fonts
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
        font_author = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
        font_section = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        font_point = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 17)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except:
        font_title = ImageFont.load_default()
        font_author = ImageFont.load_default()
        font_section = ImageFont.load_default()
        font_label = ImageFont.load_default()
        font_point = ImageFont.load_default()
        font_small = ImageFont.load_default()

    fonts = (font_title, font_author, font_section, font_label, font_point, font_small)

    frames = []
    durations = []

    # Frame 1 — title only (hold 1.5s)
    f = create_frame(width, height, bg, accent, card_bg, infographic_data, fonts, 0)
    frames.append(f)
    durations.append(1500)

    # Frames 2-7 — each card appears one by one (hold 0.8s each)
    for i in range(1, 7):
        f = create_frame(width, height, bg, accent, card_bg, infographic_data, fonts, i)
        frames.append(f)
        durations.append(800)

    # Frame 8 — all cards visible (hold 3s)
    f = create_frame(width, height, bg, accent, card_bg, infographic_data, fonts, 6)
    frames.append(f)
    durations.append(3000)

    # Add blinking accent border animation (3 blink frames)
    for blink in range(3):
        f_blink = create_frame(width, height, bg, accent, card_bg, infographic_data, fonts, 6)
        draw_blink = ImageDraw.Draw(f_blink)
        blink_color = accent if blink % 2 == 0 else (255, 255, 255)
        draw_blink.rectangle([(0, 0), (width, 5)], fill=blink_color)
        draw_blink.rectangle([(0, height-5), (width, height)], fill=blink_color)
        frames.append(f_blink)
        durations.append(300)

    # Final frame — full hold (2s)
    frames.append(create_frame(width, height, bg, accent, card_bg, infographic_data, fonts, 6))
    durations.append(2000)

    # Save as GIF
    gif_bytes = io.BytesIO()
    frames[0].save(
        gif_bytes,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True
    )
    gif_bytes.seek(0)
    print(f"Animated GIF created! Frames: {len(frames)}")
    return gif_bytes.read()

def upload_image_to_linkedin(image_data, content_type="image/gif"):
    print(f"[{datetime.now()}] Uploading GIF to LinkedIn...")

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
        "Content-Type": content_type
    }
    upload_response = requests.put(
        upload_url,
        headers=upload_headers,
        data=image_data
    )
    upload_response.raise_for_status()
    print(f"GIF uploaded successfully!")
    return asset

def job_post():
    print(f"[{datetime.now()}] Generating LinkedIn animated GIF post about: {TOPIC}")

    content = ai_generate_post(TOPIC)
    print(f"Generated content: {content[:100]}...")

    infographic_data = ai_generate_infographic_data(content)
    print(f"Infographic title: {infographic_data.get('title')}")

    gif_data = create_animated_gif(content, infographic_data)
    asset = upload_image_to_linkedin(gif_data, content_type="image/gif")

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
                            "text": infographic_data.get("title", TOPIC)
                        },
                        "media": asset,
                        "title": {
                            "text": infographic_data.get("title", TOPIC)[:100]
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
    print(f"[{datetime.now()}] LinkedIn animated GIF post published! ID: {post_id}")

if __name__ == "__main__":
    if RUN_MODE == "post":
        job_post()
