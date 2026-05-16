import openai
import requests
import os
import textwrap
import random
import hashlib
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter
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
and Agentic AI. You write sharp, insightful LinkedIn posts about cybersecurity,
AI agents, autonomous threat detection, and emerging tech trends.
Be professional, engaging, and thought provoking.
Use plain text only. No markdown. Max 3 paragraphs.
End with a question to spark discussion."""

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
                f"Write a professional LinkedIn post about a fresh angle on: {topic}\n"
                f"Examples: AI agent prompt injection, autonomous malware detection, "
                f"zero-trust for AI agents, LLM vulnerabilities, agentic AI threat hunting.\n"
                f"Be professional and engaging. Plain text only. Max 3 paragraphs.\n"
                f"End with a thought provoking question."}
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

def ai_generate_key_points(post_content):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content":
                f"Based on this LinkedIn post, extract 3 key bullet points (max 6 words each).\n"
                f"Post: {post_content}\n"
                f"Reply with ONLY 3 lines starting with bullet symbol, nothing else.\n"
                f"Example:\n• AI agents detect threats faster\n• Zero-trust models need updating\n• Human oversight remains critical"}
        ],
        max_tokens=60,
    )
    return response.choices[0].message.content.strip()

def get_content_seed(post_content):
    # Generate unique seed from post content
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

def draw_unique_pattern(draw, width, height, accent, highlight, seed):
    rng = random.Random(seed)

    # Draw unique circuit lines based on post content
    num_lines = rng.randint(15, 30)
    for _ in range(num_lines):
        x = rng.randint(0, width)
        y = rng.randint(0, height)
        length = rng.randint(30, 250)
        direction = rng.choice(['h', 'v'])
        color = accent if rng.random() > 0.5 else highlight
        if direction == 'h':
            draw.line([(x, y), (x + length, y)], fill=color, width=1)
            # Draw connector dot
            draw.ellipse([(x+length-3, y-3), (x+length+3, y+3)], fill=color)
        else:
            draw.line([(x, y), (x, y + length)], fill=color, width=1)
            draw.ellipse([(x-3, y+length-3), (x+3, y+length+3)], fill=color)

    # Draw unique hexagon pattern based on content
    num_hexagons = rng.randint(3, 8)
    for _ in range(num_hexagons):
        cx = rng.randint(width//2, width - 50)
        cy = rng.randint(50, height - 50)
        size = rng.randint(20, 60)
        points = []
        for i in range(6):
            angle = math.pi / 3 * i
            px = cx + size * math.cos(angle)
            py = cy + size * math.sin(angle)
            points.append((px, py))
        color = accent if rng.random() > 0.5 else highlight
        draw.polygon(points, outline=color)

    # Draw unique dots
    num_dots = rng.randint(20, 50)
    for _ in range(num_dots):
        x = rng.randint(0, width)
        y = rng.randint(0, height)
        r = rng.randint(1, 4)
        color = accent if rng.random() > 0.5 else highlight
        draw.ellipse([(x-r, y-r), (x+r, y+r)], fill=color)

    # Draw unique diagonal lines
    num_diagonals = rng.randint(3, 8)
    for _ in range(num_diagonals):
        x1 = rng.randint(width//2, width)
        y1 = rng.randint(0, height//2)
        x2 = rng.randint(width//2, width)
        y2 = rng.randint(height//2, height)
        color = highlight
        draw.line([(x1, y1), (x2, y2)], fill=color, width=1)

    # Draw unique concentric circles
    num_circles = rng.randint(2, 5)
    for _ in range(num_circles):
        cx = rng.randint(width - 200, width)
        cy = rng.randint(0, 200)
        for r in range(20, 100, 20):
            draw.ellipse([(cx-r, cy-r), (cx+r, cy+r)], outline=accent)

def create_post_image(post_content, headline, key_points):
    print(f"[{datetime.now()}] Creating unique image from post content...")

    width, height = 1200, 627

    # Use post content hash for unique seed
    seed = get_content_seed(post_content)

    # Pick unique theme based on post content
    theme = COLOR_THEMES[seed % len(COLOR_THEMES)]
    bg_top = theme["bg_top"]
    bg_bottom = theme["bg_bottom"]
    accent = theme["accent"]
    highlight = theme["highlight"]

    # Create gradient background
    bg_image = create_gradient_background(width, height, bg_top, bg_bottom)
    draw = ImageDraw.Draw(bg_image)

    # Draw unique pattern based on post content
    draw_unique_pattern(draw, width, height, accent, highlight, seed)

    # Draw borders
    draw.rectangle([(0, 0), (width, 5)], fill=accent)
    draw.rectangle([(0, height - 5), (width, height)], fill=accent)
    draw.rectangle([(40, 40), (46, height - 40)], fill=accent)

    # Load fonts
    try:
        font_headline = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 44)
        font_body = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        font_bullet = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        font_author = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
        font_tag = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 19)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 17)
    except:
        font_headline = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_bullet = ImageFont.load_default()
        font_author = ImageFont.load_default()
        font_tag = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Draw headline
    headline_clean = headline.replace('"', '').replace("'", '')
    headline_wrapped = textwrap.fill(headline_clean, width=40)
    draw.text((70, 65), headline_wrapped, font=font_headline, fill=accent)

    # Draw separator
    draw.rectangle([(70, 190), (600, 194)], fill=highlight)

    # Draw key points from post content
    bullet_lines = key_points.strip().split('\n')
    y_pos = 210
    for line in bullet_lines[:3]:
        if line.strip():
            draw.text((70, y_pos), line.strip(), font=font_bullet, fill=(220, 220, 220))
            y_pos += 35

    # Draw second separator
    draw.rectangle([(70, y_pos + 10), (400, y_pos + 13)], fill=accent)

    # Draw post snippet
    first_para = post_content.split('\n')[0][:150]
    body_wrapped = textwrap.fill(first_para, width=55)
    draw.text((70, y_pos + 25), body_wrapped, font=font_body, fill=(180, 180, 180))

    # Draw bottom bar
    draw.rectangle([(0, height - 95), (width, height)], fill=(5, 10, 20))

    # Draw author info
    draw.text((70, height - 78), "Aurobinda Ojha", font=font_author, fill=accent)
    draw.text((70, height - 50), "Independent Researcher | Cybersecurity & Agentic AI", font=font_tag, fill=(180, 180, 180))
    draw.text((70, height - 26), "linkedin.com/in/aurobindaojha", font=font_small, fill=(100, 100, 100))

    # Draw hashtags
    draw.text((width - 330, 18), "#AgenticAI  #Cybersecurity", font=font_tag, fill=accent)

    # Draw date
    date_str = datetime.now().strftime("%B %d, %Y")
    draw.text((width - 210, height - 28), date_str, font=font_small, fill=(100, 100, 100))

    # Save
    img_bytes = io.BytesIO()
    bg_image.save(img_bytes, format="JPEG", quality=95)
    img_bytes.seek(0)
    print(f"Unique image created! Seed: {seed}")
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
    print(f"[{datetime.now()}] Generating LinkedIn post with unique image about: {TOPIC}")

    content = ai_generate_post(TOPIC)
    print(f"Generated content: {content[:100]}...")

    headline = ai_generate_headline(content)
    print(f"Headline: {headline}")

    key_points = ai_generate_key_points(content)
    print(f"Key points: {key_points}")

    image_data = create_post_image(content, headline, key_points)
    asset = upload_image_to_linkedin(image_data)

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
    print(f"[{datetime.now()}] LinkedIn post with unique image published! ID: {post_id}")

if __name__ == "__main__":
    if RUN_MODE == "post":
        job_post()
