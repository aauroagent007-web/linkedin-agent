import openai
import requests
import os
import textwrap
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
and Agentic AI. You write sharp, insightful LinkedIn posts about cybersecurity,
AI agents, autonomous threat detection, and emerging tech trends.
Be professional, engaging, and thought provoking.
Use plain text only. No markdown. Max 3 paragraphs.
End with a question to spark discussion."""

# Different color themes rotating daily
COLOR_THEMES = [
    {"bg_top": (10, 25, 47), "bg_bottom": (0, 10, 30), "accent": (100, 255, 218), "highlight": (0, 180, 255)},
    {"bg_top": (20, 0, 40), "bg_bottom": (5, 0, 20), "accent": (200, 100, 255), "highlight": (255, 50, 150)},
    {"bg_top": (0, 30, 20), "bg_bottom": (0, 10, 5), "accent": (50, 255, 150), "highlight": (0, 200, 100)},
    {"bg_top": (40, 10, 0), "bg_bottom": (20, 5, 0), "accent": (255, 150, 50), "highlight": (255, 80, 0)},
    {"bg_top": (0, 20, 40), "bg_bottom": (0, 5, 20), "accent": (50, 200, 255), "highlight": (0, 150, 255)},
    {"bg_top": (30, 0, 30), "bg_bottom": (10, 0, 10), "accent": (255, 100, 200), "highlight": (200, 0, 200)},
    {"bg_top": (10, 10, 10), "bg_bottom": (0, 0, 0), "accent": (255, 255, 255), "highlight": (200, 200, 200)},
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

def draw_circuit_pattern(draw, width, height, accent_color):
    import random
    random.seed(datetime.now().timetuple().tm_yday)
    alpha_color = accent_color + (30,)

    # Draw circuit lines
    for _ in range(20):
        x = random.randint(0, width)
        y = random.randint(0, height)
        length = random.randint(50, 200)
        direction = random.choice(['h', 'v'])
        if direction == 'h':
            draw.line([(x, y), (x + length, y)], fill=accent_color + (40,) if len(accent_color) == 3 else accent_color, width=1)
        else:
            draw.line([(x, y), (x, y + length)], fill=accent_color, width=1)

    # Draw dots at intersections
    for _ in range(30):
        x = random.randint(0, width)
        y = random.randint(0, height)
        r = random.randint(2, 5)
        draw.ellipse([(x-r, y-r), (x+r, y+r)], fill=accent_color)

def create_post_image(post_content, headline):
    print(f"[{datetime.now()}] Creating creative image...")

    width, height = 1200, 627

    # Pick color theme based on day
    day = datetime.now().timetuple().tm_yday
    theme = COLOR_THEMES[day % len(COLOR_THEMES)]

    bg_top = theme["bg_top"]
    bg_bottom = theme["bg_bottom"]
    accent = theme["accent"]
    highlight = theme["highlight"]

    # Create gradient background
    bg_image = create_gradient_background(width, height, bg_top, bg_bottom)
    draw = ImageDraw.Draw(bg_image)

    # Draw circuit pattern
    draw_circuit_pattern(draw, width, height, accent)

    # Draw accent rectangles
    draw.rectangle([(0, 0), (width, 6)], fill=accent)
    draw.rectangle([(0, height - 6), (width, height)], fill=accent)
    draw.rectangle([(40, 40), (46, height - 40)], fill=accent)

    # Draw diagonal decoration
    for i in range(5):
        x_start = width - 200 + (i * 30)
        draw.line([(x_start, 0), (width, height - x_start)], fill=highlight, width=1)

    # Load fonts
    try:
        font_headline = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        font_body = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
        font_author = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
        font_tag = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except:
        font_headline = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_author = ImageFont.load_default()
        font_tag = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Draw headline box
    draw.rectangle([(60, 60), (900, 180)], fill=(0, 0, 0, 120) if hasattr(draw, 'rectangle') else (0,0,0))
    headline_clean = headline.replace('"', '').replace("'", '')
    headline_wrapped = textwrap.fill(headline_clean, width=38)
    draw.text((70, 70), headline_wrapped, font=font_headline, fill=accent)

    # Draw separator
    draw.rectangle([(70, 195), (550, 199)], fill=highlight)

    # Draw post excerpt
    first_para = post_content.split('\n')[0][:220]
    body_wrapped = textwrap.fill(first_para, width=58)
    draw.text((70, 215), body_wrapped, font=font_body, fill=(220, 220, 220))

    # Draw stats bar
    draw.rectangle([(60, height - 110), (width - 60, height - 115)], fill=accent)

    # Draw bottom info box
    draw.rectangle([(0, height - 100), (width, height)], fill=(5, 10, 20))

    # Draw author info
    draw.text((70, height - 80), "Aurobinda Ojha", font=font_author, fill=accent)
    draw.text((70, height - 52), "Independent Researcher | Cybersecurity & Agentic AI", font=font_tag, fill=(180, 180, 180))
    draw.text((70, height - 28), "linkedin.com/in/aurobindaojha", font=font_small, fill=(120, 120, 120))

    # Draw hashtags top right
    draw.text((width - 320, 20), "#AgenticAI  #Cybersecurity", font=font_tag, fill=accent)

    # Draw date
    date_str = datetime.now().strftime("%B %d, %Y")
    draw.text((width - 200, height - 30), date_str, font=font_small, fill=(120, 120, 120))

    # Save
    img_bytes = io.BytesIO()
    bg_image.save(img_bytes, format="JPEG", quality=95)
    img_bytes.seek(0)
    print(f"Image created successfully!")
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
    print(f"[{datetime.now()}] Generating LinkedIn post with creative image about: {TOPIC}")

    content = ai_generate_post(TOPIC)
    print(f"Generated content: {content[:100]}...")

    headline = ai_generate_headline(content)
    print(f"Headline: {headline}")

    image_data = create_post_image(content, headline)
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
    print(f"[{datetime.now()}] LinkedIn post with creative image published! ID: {post_id}")

if __name__ == "__main__":
    if RUN_MODE == "post":
        job_post()
