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

LAYER_COLORS = [
    (34, 139, 87),    # green
    (52, 120, 180),   # blue
    (150, 80, 180),   # purple
    (200, 120, 40),   # orange
    (180, 60, 60),    # red
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

def ai_generate_diagram_data(post_content):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content":
                f"Based on this LinkedIn post, create a layered diagram structure.\n"
                f"Post: {post_content}\n\n"
                f"Reply with JSON only, no extra text:\n"
                f"{{\n"
                f"  \"title\": \"The [Topic] Framework\",\n"
                f"  \"subtitle\": \"Component1 + Component2 + Component3 + Component4\",\n"
                f"  \"layers\": [\n"
                f"    {{\n"
                f"      \"number\": 1,\n"
                f"      \"name\": \"LAYER NAME\",\n"
                f"      \"subtitle\": \"The X Layer\",\n"
                f"      \"description\": \"One line description max 8 words\",\n"
                f"      \"points\": [\"point 1\", \"point 2\", \"point 3\"],\n"
                f"      \"note\": \"Short important note max 8 words\"\n"
                f"    }}\n"
                f"  ],\n"
                f"  \"flow\": [\"Step 1 max 3 words\", \"Step 2 max 3 words\", \"Step 3 max 3 words\", \"Step 4 max 3 words\", \"Step 5 max 3 words\"]\n"
                f"}}\n\n"
                f"Create exactly 5 layers that explain the post content as a framework.\n"
                f"Make it specific to the post topic.\n"
                f"flow has exactly 5 steps."}
        ],
        max_tokens=800,
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

def get_content_seed(post_content):
    return int(hashlib.md5(post_content.encode()).hexdigest(), 16)

def draw_rounded_rect(draw, x0, y0, x1, y1, radius, fill=None, outline=None, width=2):
    draw.rounded_rectangle([(x0, y0), (x1, y1)], radius=radius, fill=fill, outline=outline, width=width)

def draw_arrow_down(draw, x, y, size, color):
    draw.line([(x, y), (x, y + size)], fill=color, width=3)
    draw.polygon([(x-8, y+size-10), (x+8, y+size-10), (x, y+size+5)], fill=color)

def draw_arrow_right(draw, x, y, size, color):
    draw.line([(x, y), (x + size, y)], fill=color, width=3)
    draw.polygon([(x+size-10, y-8), (x+size-10, y+8), (x+size+5, y)], fill=color)

def draw_number_badge(draw, x, y, number, color, font):
    draw.ellipse([(x, y), (x+36, y+36)], fill=color)
    draw.text((x + 10, y + 6), str(number), font=font, fill=(255, 255, 255))

def draw_layer(draw, x, y, width, layer, color, fonts):
    font_layer_title, font_subtitle, font_body, font_small, font_badge = fonts
    height = 160

    # Main box
    draw_rounded_rect(draw, x, y, x + width, y + height, 12,
                      fill=(245, 250, 245), outline=color, width=2)

    # Number badge
    draw_number_badge(draw, x + 15, y + 15, layer["number"], color, font_badge)

    # Layer name
    name = layer.get("name", "")
    draw.text((x + 60, y + 15), f"Layer {layer['number']} — {name}", font=font_layer_title, fill=color)

    # Subtitle
    subtitle = layer.get("subtitle", "")
    draw.text((x + 60, y + 48), subtitle, font=font_subtitle, fill=(120, 120, 120))

    # Separator line
    draw.line([(x + 15, y + 68), (x + width - 15, y + 68)], fill=(200, 200, 200), width=1)

    # Points
    points = layer.get("points", [])
    point_y = y + 78
    for point in points[:3]:
        draw.ellipse([(x + 20, point_y + 5), (x + 28, point_y + 13)], fill=color)
        draw.text((x + 36, point_y), point, font=font_body, fill=(60, 60, 60))
        point_y += 24

    # Note box on right
    note = layer.get("note", "")
    if note:
        note_x = x + width - 220
        note_y = y + 75
        draw_rounded_rect(draw, note_x, note_y, x + width - 15, y + height - 15,
                          8, fill=(235, 245, 235), outline=color, width=1)
        note_wrapped = textwrap.fill(note, width=18)
        draw.text((note_x + 8, note_y + 8), note_wrapped, font=font_small, fill=(80, 80, 80))

def create_diagram_image(post_content, diagram_data):
    print(f"[{datetime.now()}] Creating flowchart diagram image...")

    width, height = 1080, 1500
    seed = get_content_seed(post_content)

    # Light background
    image = Image.new("RGB", (width, height), (252, 248, 242))
    draw = ImageDraw.Draw(image)

    # Subtle dot grid
    for x in range(0, width, 30):
        for y in range(0, height, 30):
            draw.ellipse([(x-1, y-1), (x+1, y+1)], fill=(220, 215, 210))

    # Load fonts
    try:
        font_main_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
        font_subtitle = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        font_author = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        font_layer_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
        font_layer_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        font_body = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 19)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        font_badge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        font_flow = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 17)
    except:
        font_main_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
        font_author = ImageFont.load_default()
        font_layer_title = ImageFont.load_default()
        font_layer_sub = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_small = ImageFont.load_default()
        font_badge = ImageFont.load_default()
        font_flow = ImageFont.load_default()

    fonts = (font_layer_title, font_layer_sub, font_body, font_small, font_badge)

    # ── Header ────────────────────────────────────────────────────────────────
    # Logo star symbol
    draw.text((width//2 - 15, 20), "✦", font=font_author, fill=(100, 100, 100))
    draw.text((width//2 - 60, 45), "AUROBINDA OJHA", font=font_author, fill=(80, 80, 80))

    # Main title
    title = diagram_data.get("title", "The AI Security Framework")
    title_wrapped = textwrap.fill(title, width=28)
    title_lines = title_wrapped.split('\n')
    title_y = 85
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=font_main_title)
        title_w = bbox[2] - bbox[0]
        draw.text(((width - title_w) // 2, title_y), line, font=font_main_title, fill=(30, 30, 30))
        title_y += 60

    # Subtitle
    subtitle = diagram_data.get("subtitle", "")
    sub_wrapped = textwrap.fill(subtitle, width=55)
    bbox = draw.textbbox((0, 0), sub_wrapped, font=font_subtitle)
    sub_w = bbox[2] - bbox[0]
    draw.text(((width - sub_w) // 2, title_y + 5), sub_wrapped, font=font_subtitle, fill=(120, 120, 120))

    # Author line
    draw.text((width//2 - 80, title_y + 40), "Aurobinda Ojha", font=font_author, fill=(100, 100, 100))

    # Separator
    draw.line([(60, title_y + 70), (width - 60, title_y + 70)], fill=(200, 200, 200), width=1)

    # ── Left side bar ─────────────────────────────────────────────────────────
    left_bar_x = 30
    right_bar_x = width - 60

    # ── Layers ────────────────────────────────────────────────────────────────
    layers = diagram_data.get("layers", [])[:5]
    layer_w = width - 140
    layer_x = 70
    layer_start_y = title_y + 90
    layer_gap = 185

    for idx, layer in enumerate(layers):
        color = LAYER_COLORS[idx % len(LAYER_COLORS)]
        ly = layer_start_y + idx * layer_gap

        draw_layer(draw, layer_x, ly, layer_w, layer, color, fonts)

        # Draw arrow down between layers
        if idx < len(layers) - 1:
            arrow_x = layer_x + layer_w // 2
            arrow_y = ly + 165
            draw_arrow_down(draw, arrow_x, arrow_y, 15, (150, 150, 150))

    # ── Left connector bar ────────────────────────────────────────────────────
    bar_top = layer_start_y + 20
    bar_bottom = layer_start_y + (len(layers) - 1) * layer_gap + 80
    draw.rectangle([(left_bar_x, bar_top), (left_bar_x + 4, bar_bottom)], fill=(180, 180, 180))
    draw.polygon([(left_bar_x-6, bar_bottom-10), (left_bar_x+10, bar_bottom-10),
                  (left_bar_x+2, bar_bottom+10)], fill=(180, 180, 180))

    # ── Right connector bar ───────────────────────────────────────────────────
    draw.rectangle([(right_bar_x, bar_top), (right_bar_x + 4, bar_bottom)], fill=(180, 180, 180))
    draw.polygon([(right_bar_x-6, bar_bottom-10), (right_bar_x+10, bar_bottom-10),
                  (right_bar_x+2, bar_bottom+10)], fill=(180, 180, 180))

    # ── Flow bar at bottom ────────────────────────────────────────────────────
    flow_y = layer_start_y + len(layers) * layer_gap + 10
    flow_steps = diagram_data.get("flow", [])[:5]
    flow_box_w = (width - 80) // len(flow_steps) - 10
    flow_x = 40

    # Flow background
    draw_rounded_rect(draw, 30, flow_y, width - 30, flow_y + 80, 10,
                      fill=(240, 235, 230), outline=(200, 195, 190), width=1)

    for i, step in enumerate(flow_steps):
        sx = flow_x + i * (flow_box_w + 10)
        color = LAYER_COLORS[i % len(LAYER_COLORS)]

        # Step icon circle
        draw.ellipse([(sx + flow_box_w//2 - 18, flow_y + 10),
                      (sx + flow_box_w//2 + 18, flow_y + 46)], fill=color)

        # Step text
        step_wrapped = textwrap.fill(step, width=10)
        draw.text((sx + 5, flow_y + 50), step_wrapped, font=font_flow, fill=(60, 60, 60))

        # Arrow between steps
        if i < len(flow_steps) - 1:
            ax = sx + flow_box_w + 2
            draw_arrow_right(draw, ax, flow_y + 28, 8, (150, 150, 150))

    # ── Footer ────────────────────────────────────────────────────────────────
    footer_y = flow_y + 95
    draw.line([(40, footer_y), (width - 40, footer_y)], fill=(200, 200, 200), width=1)
    draw.text((40, footer_y + 10), "Aurobinda Ojha  |  Independent Researcher  |  Cybersecurity & Agentic AI",
              font=font_small, fill=(120, 120, 120))
    date_str = datetime.now().strftime("%B %d, %Y")
    draw.text((40, footer_y + 32), f"#AgenticAI  #Cybersecurity  |  {date_str}",
              font=font_small, fill=(150, 150, 150))

    img_bytes = io.BytesIO()
    image.save(img_bytes, format="JPEG", quality=95)
    img_bytes.seek(0)
    print(f"Diagram image created!")
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
    print(f"[{datetime.now()}] Generating LinkedIn diagram post about: {TOPIC}")

    content = ai_generate_post(TOPIC)
    print(f"Generated content: {content[:100]}...")

    diagram_data = ai_generate_diagram_data(content)
    print(f"Diagram title: {diagram_data.get('title')}")

    image_bytes = create_diagram_image(content, diagram_data)
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
                            "text": diagram_data.get("title", TOPIC)
                        },
                        "media": asset,
                        "title": {
                            "text": diagram_data.get("title", TOPIC)[:100]
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
    print(f"[{datetime.now()}] LinkedIn diagram post published! ID: {post_id}")

if __name__ == "__main__":
    if RUN_MODE == "post":
        job_post()
