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

# 30 rotating daily topics
DAILY_TOPICS = [
    "Prompt Injection Attacks on AI Agents",
    "Zero Trust Architecture for AI Systems",
    "Autonomous Threat Hunting with AI",
    "AI Supply Chain Security Risks",
    "Multi-Agent System Vulnerabilities",
    "LLM Security and Jailbreaking Prevention",
    "Agentic AI in SOC Operations",
    "AI-Powered Malware Detection",
    "Adversarial Machine Learning Attacks",
    "AI Agent Authentication Frameworks",
    "Autonomous Incident Response Systems",
    "AI Red Teaming Methodologies",
    "Neural Network Security Layers",
    "AI Governance and Compliance",
    "Federated Learning Security",
    "AI Model Poisoning Prevention",
    "Autonomous Vulnerability Assessment",
    "AI-Driven Phishing Detection",
    "Machine Learning in SIEM Systems",
    "AI Agent Identity Management",
    "Behavioral Analytics with AI Agents",
    "AI Security Operations Center",
    "Deepfake Detection with AI",
    "AI Powered Ransomware Defense",
    "Cognitive Security with Agentic AI",
    "AI in Digital Forensics",
    "Autonomous Patch Management Systems",
    "AI Threat Intelligence Platforms",
    "Explainable AI in Cybersecurity",
    "AI Agent Sandboxing Techniques",
]

COLOR_THEMES = [
    {"bg": (5, 5, 15), "accent": (0, 255, 200), "highlight": (0, 180, 255), "card": (10, 20, 40)},
    {"bg": (5, 5, 15), "accent": (255, 220, 0), "highlight": (255, 150, 0), "card": (20, 18, 5)},
    {"bg": (5, 5, 15), "accent": (180, 80, 255), "highlight": (255, 50, 150), "card": (20, 5, 35)},
    {"bg": (5, 5, 15), "accent": (50, 255, 150), "highlight": (0, 200, 100), "card": (5, 25, 15)},
    {"bg": (5, 5, 15), "accent": (255, 100, 100), "highlight": (220, 50, 50), "card": (25, 5, 5)},
]

def get_daily_topic():
    day = datetime.now().timetuple().tm_yday
    return DAILY_TOPICS[day % len(DAILY_TOPICS)]

def get_content_seed(text):
    return int(hashlib.md5(text.encode()).hexdigest(), 16)

def ai_generate_post(subtopic):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": AGENT_PERSONA},
            {"role": "user", "content":
                f"Write a LinkedIn post specifically about: {subtopic}\n\n"
                f"FORMAT RULES:\n"
                f"- SHORT lines with line breaks\n"
                f"- Add relevant emojis\n"
                f"- Hook opening line\n"
                f"- End with question\n"
                f"- Max 150 words\n"
                f"- Make it UNIQUE and specific to {subtopic}"}
        ],
        max_tokens=400,
    )
    return response.choices[0].message.content.strip()

def ai_generate_stack_data(subtopic):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content":
                f"Create a 6-panel security stack infographic for: {subtopic}\n\n"
                f"Reply with JSON only:\n"
                f"{{\n"
                f"  \"main_title\": \"TOPIC STACK (all caps, max 4 words)\",\n"
                f"  \"panels\": [\n"
                f"    {{\n"
                f"      \"title\": \"Panel Title (max 4 words)\",\n"
                f"      \"color\": \"one of: cyan, yellow, green, orange, pink, blue\",\n"
                f"      \"purpose\": \"One line purpose max 8 words\",\n"
                f"      \"section1_title\": \"Section label max 3 words\",\n"
                f"      \"section1_items\": [\"item max 4 words\", \"item max 4 words\", \"item max 4 words\"],\n"
                f"      \"section2_title\": \"Section label max 3 words\",\n"
                f"      \"section2_items\": [\"item max 4 words\", \"item max 4 words\", \"item max 4 words\"],\n"
                f"      \"tools_label\": \"Key Tools:\"\n"
                f"    }}\n"
                f"  ]\n"
                f"}}\n\n"
                f"Create exactly 6 panels specific to {subtopic}.\n"
                f"Each panel must have exactly 3 items in section1 and section2.\n"
                f"Make content highly specific and technical.\n"
                f"Vary the colors across panels."}
        ],
        max_tokens=1200,
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

def get_color(name, theme_accent):
    colors = {
        "cyan": (0, 255, 200),
        "yellow": (255, 220, 0),
        "green": (50, 255, 150),
        "orange": (255, 150, 50),
        "pink": (255, 100, 200),
        "blue": (50, 200, 255),
    }
    return colors.get(name, theme_accent)

def fit_text(text, max_chars):
    if len(text) <= max_chars:
        return text
    return text[:max_chars-2] + ".."

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

def draw_grid(draw, width, height, color):
    for x in range(0, width, 40):
        draw.line([(x, 0), (x, height)], fill=color, width=1)
    for y in range(0, height, 40):
        draw.line([(0, y), (width, y)], fill=color, width=1)

def draw_circuit(draw, width, height, accent, seed):
    rng = random.Random(seed)
    for _ in range(25):
        x = rng.randint(0, width)
        y = rng.randint(0, height)
        l = rng.randint(30, 120)
        d = rng.choice(['h', 'v'])
        if d == 'h':
            draw.line([(x, y), (x+l, y)], fill=accent, width=1)
            draw.ellipse([(x+l-2, y-2), (x+l+2, y+2)], fill=accent)
        else:
            draw.line([(x, y), (x, y+l)], fill=accent, width=1)
            draw.ellipse([(x-2, y+l-2), (x+2, y+l+2)], fill=accent)

def load_fonts():
    try:
        return {
            "title": ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80),
            "author": ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22),
            "follow": ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18),
            "panel_title": ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26),
            "section": ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18),
            "item": ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16),
            "purpose": ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15),
            "small": ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14),
        }
    except:
        default = ImageFont.load_default()
        return {k: default for k in ["title","author","follow","panel_title",
                                      "section","item","purpose","small"]}

def draw_panel(draw, x, y, w, h, panel, color, fonts, visible=True):
    if not visible:
        return

    # Card background
    draw.rectangle([(x, y), (x+w, y+h)], fill=(10, 15, 25))

    # Dashed border
    draw_dashed_rect(draw, x, y, x+w, y+h, color, dash=8, width=2)

    # Header background
    draw.rectangle([(x, y), (x+w, y+44)], fill=color)

    # Panel title
    title = fit_text(panel.get("title", ""), 20)
    title_lines = textwrap.fill(title, width=18).split('\n')
    ty = y + 5
    for line in title_lines:
        bbox = draw.textbbox((0,0), line, font=fonts["panel_title"])
        tw = bbox[2]-bbox[0]
        draw.text((x+(w-tw)//2, ty), line, font=fonts["panel_title"], fill=(0,0,0))
        ty += 22

    # Purpose
    purpose = fit_text(panel.get("purpose", ""), 35)
    draw.text((x+8, y+50), "Purpose:", font=fonts["section"], fill=color)
    purpose_wrapped = textwrap.fill(purpose, width=22)
    draw.text((x+8, y+70), purpose_wrapped, font=fonts["purpose"], fill=(200,200,200))

    # Section 1
    s1_y = y + 70 + len(purpose_wrapped.split('\n')) * 18 + 8
    s1_title = fit_text(panel.get("section1_title", ""), 20)
    draw.text((x+8, s1_y), s1_title + ":", font=fonts["section"], fill=color)
    s1_y += 22
    for item in panel.get("section1_items", [])[:3]:
        item_text = fit_text(item, 22)
        draw.ellipse([(x+10, s1_y+5), (x+16, s1_y+11)], fill=color)
        draw.text((x+22, s1_y), item_text, font=fonts["item"], fill=(200,200,200))
        s1_y += 20

    # Section 2
    s2_y = s1_y + 8
    s2_title = fit_text(panel.get("section2_title", ""), 20)
    draw.text((x+8, s2_y), s2_title + ":", font=fonts["section"], fill=color)
    s2_y += 22
    for item in panel.get("section2_items", [])[:3]:
        item_text = fit_text(item, 22)
        draw.ellipse([(x+10, s2_y+5), (x+16, s2_y+11)], fill=color)
        draw.text((x+22, s2_y), item_text, font=fonts["item"], fill=(200,200,200))
        s2_y += 20

    # Tools label
    tools_y = y + h - 28
    draw.text((x+8, tools_y), panel.get("tools_label", "Key Tools:"),
              font=fonts["section"], fill=color)

def create_base_frame(width, height, bg, accent, title_text, seed, fonts):
    img = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(img)

    # Grid
    draw_grid(draw, width, height, (18, 18, 28))

    # Circuit lines
    draw_circuit(draw, width, height, (*accent[:3], 40) if len(accent) == 4
                 else accent, seed)

    # Author circle
    draw.ellipse([(width//2-30, 20), (width//2+30, 80)],
                 outline=accent, width=2)
    draw.text((width//2-16, 38), "AO", font=fonts["author"], fill=accent)

    # Author name
    draw.text((width//2-65, 88), "Aurobinda Ojha", font=fonts["author"],
              fill=(200,200,200))
    draw.text((width//2-52, 112), "Follow For More", font=fonts["follow"],
              fill=(120,120,120))

    # Main title
    title_wrapped = textwrap.fill(title_text, width=16)
    title_lines = title_wrapped.split('\n')
    ty = 145
    for line in title_lines:
        bbox = draw.textbbox((0,0), line, font=fonts["title"])
        tw = bbox[2]-bbox[0]
        draw.text(((width-tw)//2, ty), line, font=fonts["title"],
                  fill=(255,255,255))
        ty += 88

    # Underline
    draw.rectangle([(40, ty+5), (width-40, ty+8)], fill=accent)

    return img, draw, ty + 20

def create_animated_gif(subtopic, data):
    print(f"[{datetime.now()}] Creating animated GIF for: {subtopic}")

    width, height = 1080, 1350
    seed = get_content_seed(subtopic)
    theme = COLOR_THEMES[seed % len(COLOR_THEMES)]

    bg = theme["bg"]
    accent = theme["accent"]
    highlight = theme["highlight"]

    fonts = load_fonts()

    panels = data.get("panels", [])[:6]
    main_title = data.get("main_title", subtopic.upper())

    # Panel layout
    MARGIN = 20
    card_w = (width - MARGIN*4) // 3
    card_h = 310
    card_start_y = 0  # will be set after title

    # Pre-calculate title height
    title_wrapped = textwrap.fill(main_title, width=16)
    title_h = 145 + len(title_wrapped.split('\n')) * 88 + 30

    card_start_y = title_h
    panel_colors = []
    for panel in panels:
        panel_colors.append(get_color(panel.get("color", "cyan"), accent))

    def make_frame(visible_count, blink_accent=None):
        img, draw, content_y = create_base_frame(
            width, height, bg, accent, main_title, seed, fonts)

        for idx in range(6):
            col = idx % 3
            row = idx // 2
            px = MARGIN + col * (card_w + MARGIN)
            py = card_start_y + row * (card_h + MARGIN)

            if idx < visible_count and idx < len(panels):
                panel = panels[idx]
                color = blink_accent if blink_accent and idx == visible_count-1 \
                    else panel_colors[idx]
                draw_panel(draw, px, py, card_w, card_h,
                           panel, color, fonts, True)

        # Footer
        footer_y = card_start_y + 2*(card_h+MARGIN) + 15
        draw.rectangle([(0, footer_y), (width, height)], fill=(5,5,15))
        draw.rectangle([(0, footer_y), (width, footer_y+3)], fill=accent)
        draw.text((30, footer_y+12), "Aurobinda Ojha",
                  font=fonts["author"], fill=accent)
        draw.text((30, footer_y+38),
                  "Independent Researcher | Cybersecurity & Agentic AI",
                  font=fonts["small"], fill=(150,150,150))
        date_str = datetime.now().strftime("%B %d, %Y")
        draw.text((30, footer_y+60),
                  f"#AgenticAI  #Cybersecurity  |  {date_str}",
                  font=fonts["small"], fill=(100,100,100))

        # Blink border
        if blink_accent:
            draw.rectangle([(0, 0), (width, 4)], fill=blink_accent)
            draw.rectangle([(0, height-4), (width, height)], fill=blink_accent)

        return img

    frames = []
    durations = []

    # Frame 1 — title only
    frames.append(make_frame(0))
    durations.append(1200)

    # Frames 2-7 — panels appear one by one
    for i in range(1, 7):
        frames.append(make_frame(i))
        durations.append(700)

    # Frame 8 — all visible hold
    frames.append(make_frame(6))
    durations.append(2500)

    # Blink frames
    for b in range(4):
        blink_color = accent if b % 2 == 0 else (255, 255, 255)
        frames.append(make_frame(6, blink_accent=blink_color))
        durations.append(250)

    # Final hold
    frames.append(make_frame(6))
    durations.append(2000)

    # Save GIF
    gif_bytes = io.BytesIO()
    frames[0].save(
        gif_bytes,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=False
    )
    gif_bytes.seek(0)
    print(f"Animated GIF created! {len(frames)} frames")
    return gif_bytes.read()

def upload_image_to_linkedin(image_data, content_type="image/gif"):
    print(f"[{datetime.now()}] Uploading GIF to LinkedIn...")

    register_payload = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": f"urn:li:person:{LINKEDIN_PERSON_ID}",
            "serviceRelationships": [{
                "relationshipType": "OWNER",
                "identifier": "urn:li:userGeneratedContent"
            }]
        }
    }

    r = requests.post(
        "https://api.linkedin.com/v2/assets?action=registerUpload",
        headers=LINKEDIN_HEADERS,
        json=register_payload
    )
    r.raise_for_status()
    response_json = r.json()

    upload_url = response_json["value"]["uploadMechanism"][
        "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
    asset = response_json["value"]["asset"]

    upload_headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": content_type
    }
    requests.put(upload_url, headers=upload_headers, data=image_data).raise_for_status()
    print(f"GIF uploaded!")
    return asset

def job_post():
    subtopic = get_daily_topic()
    print(f"[{datetime.now()}] Today's topic: {subtopic}")

    content = ai_generate_post(subtopic)
    print(f"Post: {content[:80]}...")

    data = ai_generate_stack_data(subtopic)
    print(f"Stack title: {data.get('main_title')}")

    gif_data = create_animated_gif(subtopic, data)
    asset = upload_image_to_linkedin(gif_data, "image/gif")

    payload = {
        "author": f"urn:li:person:{LINKEDIN_PERSON_ID}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": content},
                "shareMediaCategory": "IMAGE",
                "media": [{
                    "status": "READY",
                    "description": {"text": data.get("main_title", subtopic)},
                    "media": asset,
                    "title": {"text": data.get("main_title", subtopic)[:100]}
                }]
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    r = requests.post(
        "https://api.linkedin.com/v2/ugcPosts",
        headers=LINKEDIN_HEADERS, json=payload
    )
    r.raise_for_status()
    print(f"[{datetime.now()}] Published! ID: {r.json().get('id')}")

if __name__ == "__main__":
    if RUN_MODE == "post":
        job_post()
