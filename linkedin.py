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

# Rotating subtopics — ensures new content every day
SUBTOPICS = [
    "Prompt Injection Attacks on AI Agents",
    "Zero Trust Architecture for AI Systems",
    "Autonomous Threat Hunting with AI",
    "AI Supply Chain Security Risks",
    "Multi-Agent System Vulnerabilities",
    "LLM Security and Jailbreaking",
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
    "Behavioral Analytics with AI",
    "AI Security Operations Center",
    "Deepfake Detection Systems",
    "AI Powered Ransomware Defense",
    "Cognitive Security with AI",
    "AI in Digital Forensics",
    "Autonomous Patch Management",
    "AI Threat Intelligence Platforms",
    "Explainable AI in Security",
    "AI Agent Sandboxing Techniques",
]

LAYER_COLORS = [
    (52, 120, 90),    # green
    (52, 100, 160),   # blue
    (140, 80, 160),   # purple
    (200, 120, 40),   # orange
    (180, 60, 60),    # red
]

AGENT_PERSONA = """You are Aurobinda Ojha, an Independent Researcher on Cybersecurity
and Agentic AI. You write sharp, punchy LinkedIn posts with short lines and emojis.
Your style is direct, conversational and thought provoking.
You use line breaks between thoughts. You add emojis to key points.
Plain text only. No markdown. Short sentences. Max 150 words."""

def get_daily_subtopic():
    day = datetime.now().timetuple().tm_yday
    return SUBTOPICS[day % len(SUBTOPICS)]

def ai_generate_post(topic, subtopic):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": AGENT_PERSONA},
            {"role": "user", "content":
                f"Write a LinkedIn post specifically about: {subtopic}\n"
                f"Context: {topic}\n\n"
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

def ai_generate_layer_data(subtopic):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content":
                f"Create a layered framework diagram for: {subtopic}\n\n"
                f"Reply with JSON only:\n"
                f"{{\n"
                f"  \"title\": \"The [Topic] Framework\",\n"
                f"  \"subtitle\": \"Component1 + Component2 + Component3 + Component4 + Component5\",\n"
                f"  \"author\": \"Aurobinda Ojha\",\n"
                f"  \"layers\": [\n"
                f"    {{\n"
                f"      \"number\": 1,\n"
                f"      \"name\": \"LAYER NAME\",\n"
                f"      \"tag\": \"The X Layer\",\n"
                f"      \"main_items\": [\"item1 max 3 words\", \"item2 max 3 words\", \"item3 max 3 words\"],\n"
                f"      \"sub_items\": [\"sub1 max 4 words\", \"sub2 max 4 words\"],\n"
                f"      \"note\": \"Key insight max 10 words\"\n"
                f"    }}\n"
                f"  ],\n"
                f"  \"left_panel\": {{\n"
                f"    \"title\": \"External Component\",\n"
                f"    \"items\": [\"item1 max 3 words\", \"item2 max 3 words\", \"item3 max 3 words\", \"item4 max 3 words\", \"item5 max 3 words\"]\n"
                f"  }},\n"
                f"  \"right_panel\": {{\n"
                f"    \"title\": \"Output Component\",\n"
                f"    \"items\": [\"item1 max 4 words\", \"item2 max 4 words\", \"item3 max 4 words\", \"item4 max 4 words\"]\n"
                f"  }},\n"
                f"  \"flow\": [\n"
                f"    {{\"from\": \"Component1\", \"action\": \"action max 3 words\", \"to\": \"Component2\"}},\n"
                f"    {{\"from\": \"Component2\", \"action\": \"action max 3 words\", \"to\": \"Component3\"}},\n"
                f"    {{\"from\": \"Component3\", \"action\": \"action max 3 words\", \"to\": \"Component4\"}},\n"
                f"    {{\"from\": \"Component4\", \"action\": \"action max 3 words\", \"to\": \"Component5\"}}\n"
                f"  ]\n"
                f"}}\n\n"
                f"Create exactly 5 layers specific to {subtopic}.\n"
                f"main_items: exactly 3 items.\n"
                f"sub_items: exactly 2 items.\n"
                f"note: one clear key insight.\n"
                f"flow: exactly 4 steps."}
        ],
        max_tokens=1200,
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

def fit_text(text, max_chars):
    if len(text) <= max_chars:
        return text
    return text[:max_chars-3] + "..."

def draw_rounded_rect(draw, x0, y0, x1, y1, radius, fill=None, outline=None, width=2):
    try:
        draw.rounded_rectangle([(x0, y0), (x1, y1)],
                                radius=radius, fill=fill, outline=outline, width=width)
    except:
        draw.rectangle([(x0, y0), (x1, y1)], fill=fill, outline=outline, width=width)

def draw_arrow(draw, x1, y1, x2, y2, color, width=2):
    draw.line([(x1, y1), (x2, y2)], fill=color, width=width)
    angle = math.atan2(y2-y1, x2-x1)
    arrow_size = 10
    draw.polygon([
        (x2, y2),
        (int(x2 - arrow_size * math.cos(angle - 0.4)),
         int(y2 - arrow_size * math.sin(angle - 0.4))),
        (int(x2 - arrow_size * math.cos(angle + 0.4)),
         int(y2 - arrow_size * math.sin(angle + 0.4)))
    ], fill=color)

def draw_number_badge(draw, cx, cy, number, color, font):
    r = 18
    draw.ellipse([(cx-r, cy-r), (cx+r, cy+r)], fill=color)
    num_str = str(number)
    bbox = draw.textbbox((0, 0), num_str, font=font)
    tw = bbox[2]-bbox[0]
    th = bbox[3]-bbox[1]
    draw.text((cx-tw//2, cy-th//2), num_str, font=font, fill=(255, 255, 255))

def create_layer_box(draw, x, y, w, layer, color, fonts, padding=15):
    font_num, font_name, font_tag, font_item, font_note, font_small = fonts

    # Calculate required height dynamically
    main_items = layer.get("main_items", [])[:3]
    sub_items = layer.get("sub_items", [])[:2]
    note = fit_text(layer.get("note", ""), 55)

    h = 50  # header
    h += len(main_items) * 22
    h += 10  # divider gap
    h += len(sub_items) * 22
    h += 10  # note gap
    note_lines = len(textwrap.fill(note, width=35).split('\n'))
    h += note_lines * 20
    h += padding * 2

    # Outer box with light fill
    draw_rounded_rect(draw, x, y, x+w, y+h, 12,
                      fill=(248, 252, 248), outline=color, width=2)

    # Header background
    draw_rounded_rect(draw, x, y, x+w, y+46, 12,
                      fill=(*color, 30) if len(color) == 3 else color,
                      outline=color, width=0)
    draw.rectangle([(x, y+30), (x+w, y+46)],
                   fill=(248, 252, 248))

    # Number badge
    draw_number_badge(draw, x+24, y+23, layer["number"], color, font_num)

    # Layer name
    name = fit_text(layer.get("name", ""), 20)
    draw.text((x+50, y+8), f"Layer {layer['number']} — {name}",
              font=font_name, fill=color)

    # Tag
    tag = fit_text(layer.get("tag", ""), 22)
    draw.text((x+50, y+28), tag, font=font_tag, fill=(120, 140, 120))

    # Divider
    draw.line([(x+10, y+50), (x+w-10, y+50)], fill=(210, 215, 210), width=1)

    # Main items with checkboxes
    iy = y + 58
    for item in main_items:
        item_text = fit_text(item, 28)
        draw_rounded_rect(draw, x+12, iy+2, x+22, iy+14, 2,
                          outline=color, width=1)
        draw.line([(x+14, iy+8), (x+17, iy+11)], fill=color, width=1)
        draw.line([(x+17, iy+11), (x+21, iy+5)], fill=color, width=1)
        draw.text((x+28, iy), item_text, font=font_item, fill=(50, 60, 50))
        iy += 22

    iy += 5

    # Sub items with arrows
    for sub in sub_items:
        sub_text = fit_text(sub, 32)
        draw.text((x+12, iy), "→", font=font_small, fill=color)
        draw.text((x+28, iy), sub_text, font=font_small, fill=(80, 90, 80))
        iy += 22

    iy += 5

    # Note box
    note_wrapped = textwrap.fill(note, width=35)
    note_h = len(note_wrapped.split('\n')) * 20 + 10
    draw_rounded_rect(draw, x+10, iy, x+w-10, iy+note_h, 6,
                      fill=(240, 248, 240), outline=(180, 210, 180), width=1)
    draw.text((x+16, iy+5), note_wrapped, font=font_note, fill=(60, 100, 60))

    return h

def create_flow_bar(draw, x, y, w, flow_steps, colors, fonts):
    font_flow, font_small = fonts
    bar_h = 80
    step_count = len(flow_steps)
    if step_count == 0:
        return bar_h

    step_w = (w - 20) // step_count

    draw_rounded_rect(draw, x, y, x+w, y+bar_h, 10,
                      fill=(245, 242, 235), outline=(200, 190, 170), width=2)

    for i, step in enumerate(flow_steps):
        sx = x + 10 + i * step_w
        color = colors[i % len(colors)]

        # Icon circle
        cx = sx + step_w // 2 - 15
        draw.ellipse([(cx, y+8), (cx+30, y+38)], fill=color)

        # From text
        from_text = fit_text(step.get("from", ""), 12)
        draw.text((sx+5, y+42), from_text, font=font_small, fill=(80, 70, 60))

        # Action text
        action_text = fit_text(step.get("action", ""), 12)
        draw.text((sx+5, y+58), action_text, font=font_small, fill=(120, 110, 100))

        # Arrow between steps
        if i < step_count - 1:
            ax = sx + step_w - 5
            draw.text((ax, y+15), "→", font=font_flow, fill=(150, 140, 130))

    return bar_h

def create_framework_image(post_content, data):
    print(f"[{datetime.now()}] Creating framework image...")

    width = 1080
    BG_COLOR = (252, 248, 242)

    # Load fonts
    try:
        font_main_title = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        font_subtitle = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        font_author = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        font_num = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        font_layer_name = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
        font_layer_tag = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        font_item = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 17)
        font_note = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
        font_small = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        font_panel_title = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        font_flow = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        font_footer = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except:
        font_main_title = ImageFont.load_default()
        font_subtitle = font_main_title
        font_author = font_main_title
        font_num = font_main_title
        font_layer_name = font_main_title
        font_layer_tag = font_main_title
        font_item = font_main_title
        font_note = font_main_title
        font_small = font_main_title
        font_panel_title = font_main_title
        font_flow = font_main_title
        font_footer = font_main_title

    layer_fonts = (font_num, font_layer_name, font_layer_tag,
                   font_item, font_note, font_small)

    # First pass — calculate total height
    layers = data.get("layers", [])[:5]
    left_panel = data.get("left_panel", {})
    right_panel = data.get("right_panel", {})
    flow_steps = data.get("flow", [])[:4]

    MARGIN = 20
    LEFT_W = 130
    RIGHT_W = 150
    MAIN_W = width - LEFT_W - RIGHT_W - MARGIN * 4
    ARROW_H = 30
    GAP = 12

    # Header height
    title = data.get("title", "Framework")
    title_wrapped = textwrap.fill(title, width=28)
    title_lines = len(title_wrapped.split('\n'))
    header_h = 30 + title_lines * 56 + 30 + 26 + 26 + 20

    # Logo area
    logo_h = 40

    # Calculate layer heights
    layer_heights = []
    temp_img = Image.new("RGB", (width, 100), BG_COLOR)
    temp_draw = ImageDraw.Draw(temp_img)

    for layer in layers:
        main_items = layer.get("main_items", [])[:3]
        sub_items = layer.get("sub_items", [])[:2]
        note = fit_text(layer.get("note", ""), 55)
        h = 50
        h += len(main_items) * 22
        h += 10
        h += len(sub_items) * 22
        h += 10
        note_lines = len(textwrap.fill(note, width=35).split('\n'))
        h += note_lines * 20
        h += 30
        layer_heights.append(max(h, 140))

    total_layers_h = sum(layer_heights) + (len(layers)-1) * (ARROW_H + GAP)

    # Flow bar height
    flow_h = 80 + 20

    # Footer height
    footer_h = 60

    total_h = (logo_h + header_h + MARGIN +
               total_layers_h + MARGIN +
               flow_h + footer_h + 40)

    # Create image with calculated height
    image = Image.new("RGB", (width, total_h), BG_COLOR)
    draw = ImageDraw.Draw(image)

    # Subtle dot pattern
    for xx in range(0, width, 35):
        for yy in range(0, total_h, 35):
            draw.ellipse([(xx-1, yy-1), (xx+1, yy+1)], fill=(235, 230, 222))

    current_y = MARGIN

    # ── Logo / Brand ──────────────────────────────────────────────────────────
    draw.text((width//2 - 60, current_y), "✦  AUROBINDA OJHA",
              font=font_author, fill=(100, 90, 80))
    current_y += logo_h

    # ── Title ─────────────────────────────────────────────────────────────────
    for line in title_wrapped.split('\n'):
        bbox = draw.textbbox((0, 0), line, font=font_main_title)
        tw = bbox[2]-bbox[0]
        draw.text(((width-tw)//2, current_y), line,
                  font=font_main_title, fill=(30, 30, 30))
        current_y += 56

    # Subtitle
    subtitle = data.get("subtitle", "")
    subtitle_wrapped = textwrap.fill(subtitle, width=55)
    bbox = draw.textbbox((0, 0), subtitle_wrapped, font=font_subtitle)
    sw = bbox[2]-bbox[0]
    draw.text(((width-sw)//2, current_y), subtitle_wrapped,
              font=font_subtitle, fill=(100, 90, 80))
    current_y += 30

    # Author
    author = data.get("author", "Aurobinda Ojha")
    bbox = draw.textbbox((0, 0), author, font=font_author)
    aw = bbox[2]-bbox[0]
    draw.text(((width-aw)//2, current_y), author,
              font=font_author, fill=(130, 120, 110))
    current_y += 30

    # Divider
    draw.line([(MARGIN*3, current_y), (width-MARGIN*3, current_y)],
              fill=(200, 190, 180), width=1)
    current_y += MARGIN

    # ── Layer area ────────────────────────────────────────────────────────────
    layer_start_y = current_y
    layer_x = LEFT_W + MARGIN * 2
    layer_end_y = layer_start_y

    # Draw vertical connector line on left
    left_cx = LEFT_W // 2 + MARGIN

    for idx, layer in enumerate(layers):
        color = LAYER_COLORS[idx % len(LAYER_COLORS)]
        lh = layer_heights[idx]

        if idx > 0:
            # Arrow down
            draw_arrow(draw, width//2, layer_end_y + 5,
                       width//2, layer_end_y + ARROW_H - 5,
                       (150, 140, 130), width=2)
            layer_end_y += ARROW_H + GAP

        # Draw layer box
        actual_h = create_layer_box(
            draw, layer_x, layer_end_y,
            MAIN_W, layer, color, layer_fonts
        )

        # Left connector arrow
        mid_y = layer_end_y + actual_h // 2
        draw_arrow(draw, left_cx + 10, mid_y,
                   layer_x - 5, mid_y,
                   (150, 140, 130), width=2)

        # Right connector arrow
        right_x = layer_x + MAIN_W + 5
        draw_arrow(draw, right_x, mid_y,
                   width - RIGHT_W - MARGIN + 5, mid_y,
                   (150, 140, 130), width=2)

        layer_end_y += actual_h

    # ── Left panel ────────────────────────────────────────────────────────────
    lp = left_panel
    lp_color = (180, 120, 60)
    lp_x = MARGIN
    lp_w = LEFT_W - MARGIN
    lp_h = layer_end_y - layer_start_y

    draw_rounded_rect(draw, lp_x, layer_start_y,
                      lp_x + lp_w, layer_start_y + lp_h,
                      10, fill=(255,255,250),
                      outline=lp_color, width=2)

    # Left panel icon
    draw.text((lp_x + lp_w//2 - 12, layer_start_y + 15),
              "⚙", font=font_flow, fill=lp_color)

    # Left panel title
    lp_title = fit_text(lp.get("title", "External"), 12)
    title_lines_lp = textwrap.fill(lp_title, width=10).split('\n')
    ty_lp = layer_start_y + 45
    for tl in title_lines_lp:
        bbox = draw.textbbox((0,0), tl, font=font_panel_title)
        tlw = bbox[2]-bbox[0]
        draw.text((lp_x + (lp_w-tlw)//2, ty_lp), tl,
                  font=font_panel_title, fill=lp_color)
        ty_lp += 22

    # Left panel items
    lp_items = lp.get("items", [])[:5]
    iy_lp = ty_lp + 10
    for item in lp_items:
        item_text = fit_text(item, 10)
        draw.ellipse([(lp_x+8, iy_lp+6), (lp_x+14, iy_lp+12)],
                     fill=lp_color)
        draw.text((lp_x+18, iy_lp), item_text,
                  font=font_small, fill=(60, 50, 40))
        iy_lp += 22

    # Left vertical arrow
    draw_arrow(draw, left_cx, layer_start_y - 5,
               left_cx, layer_end_y + 5,
               (150, 140, 130), width=2)

    # ── Right panel ───────────────────────────────────────────────────────────
    rp = right_panel
    rp_color = (180, 120, 60)
    rp_x = width - RIGHT_W - MARGIN + 10
    rp_w = RIGHT_W - MARGIN
    rp_h = layer_end_y - layer_start_y

    draw_rounded_rect(draw, rp_x, layer_start_y,
                      rp_x + rp_w, layer_start_y + rp_h,
                      10, fill=(255, 255, 250),
                      outline=rp_color, width=2)

    # Right panel icon
    draw.text((rp_x + rp_w//2 - 12, layer_start_y + 15),
              "👥", font=font_flow, fill=rp_color)

    # Right panel title
    rp_title = fit_text(rp.get("title", "Output"), 12)
    title_lines_rp = textwrap.fill(rp_title, width=10).split('\n')
    ty_rp = layer_start_y + 45
    for tl in title_lines_rp:
        bbox = draw.textbbox((0,0), tl, font=font_panel_title)
        tlw = bbox[2]-bbox[0]
        draw.text((rp_x + (rp_w-tlw)//2, ty_rp), tl,
                  font=font_panel_title, fill=rp_color)
        ty_rp += 22

    # Right panel items
    rp_items = rp.get("items", [])[:4]
    iy_rp = ty_rp + 10
    for item in rp_items:
        item_text = fit_text(item, 12)
        draw.ellipse([(rp_x+8, iy_rp+6), (rp_x+14, iy_rp+12)],
                     fill=rp_color)
        draw.text((rp_x+18, iy_rp), item_text,
                  font=font_small, fill=(60, 50, 40))
        iy_rp += 22

    # Right vertical arrow
    right_cx = rp_x + rp_w//2
    draw_arrow(draw, right_cx, layer_start_y - 5,
               right_cx, layer_end_y + 5,
               (150, 140, 130), width=2)

    current_y = layer_end_y + MARGIN

    # ── Flow bar ──────────────────────────────────────────────────────────────
    flow_x = MARGIN
    flow_w = width - MARGIN * 2

    draw_rounded_rect(draw, flow_x, current_y,
                      flow_x + flow_w, current_y + 80,
                      10, fill=(240, 235, 225),
                      outline=(180, 170, 150), width=2)

    step_w = flow_w // len(flow_steps)
    for i, step in enumerate(flow_steps):
        sx = flow_x + i * step_w
        color = LAYER_COLORS[i % len(LAYER_COLORS)]

        # Circle icon
        cx_flow = sx + step_w // 2
        draw.ellipse([(cx_flow-18, current_y+8),
                      (cx_flow+18, current_y+44)], fill=color)

        # From text
        from_text = fit_text(step.get("from", ""), 14)
        bbox = draw.textbbox((0,0), from_text, font=font_small)
        ftw = bbox[2]-bbox[0]
        draw.text((cx_flow-ftw//2, current_y+48),
                  from_text, font=font_small, fill=(70, 60, 50))

        # Action text
        action = fit_text(step.get("action", ""), 14)
        bbox = draw.textbbox((0,0), action, font=font_small)
        atw = bbox[2]-bbox[0]
        draw.text((cx_flow-atw//2, current_y+64),
                  action, font=font_small, fill=(110, 100, 90))

        # Arrow between steps
        if i < len(flow_steps) - 1:
            draw_arrow(draw, sx+step_w-15, current_y+26,
                       sx+step_w+5, current_y+26,
                       (150, 140, 130), width=2)

    current_y += 90

    # ── Footer ────────────────────────────────────────────────────────────────
    draw.line([(MARGIN, current_y), (width-MARGIN, current_y)],
              fill=(200, 190, 180), width=1)
    current_y += 10

    footer_text = f"© Aurobinda Ojha  |  Follow for more insights on AI & Cybersecurity"
    bbox = draw.textbbox((0,0), footer_text, font=font_footer)
    fw = bbox[2]-bbox[0]
    draw.text(((width-fw)//2, current_y), footer_text,
              font=font_footer, fill=(120, 110, 100))
    current_y += 22

    date_str = datetime.now().strftime("%B %d, %Y")
    hashtags = f"#AgenticAI  #Cybersecurity  #AIResearch  |  {date_str}"
    bbox = draw.textbbox((0,0), hashtags, font=font_footer)
    hw = bbox[2]-bbox[0]
    draw.text(((width-hw)//2, current_y), hashtags,
              font=font_footer, fill=(150, 140, 130))

    # Save
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="JPEG", quality=95)
    img_bytes.seek(0)
    print(f"Framework image created!")
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

    upload_url = response_json["value"]["uploadMechanism"][
        "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
    asset = response_json["value"]["asset"]
    print(f"Asset ID: {asset}")

    upload_headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/octet-stream"
    }
    upload_response = requests.put(upload_url, headers=upload_headers, data=image_data)
    upload_response.raise_for_status()
    print(f"Image uploaded successfully!")
    return asset

def job_post():
    subtopic = get_daily_subtopic()
    print(f"[{datetime.now()}] Today's subtopic: {subtopic}")

    content = ai_generate_post(TOPIC, subtopic)
    print(f"Generated content: {content[:100]}...")

    data = ai_generate_layer_data(subtopic)
    print(f"Framework title: {data.get('title')}")

    image_bytes = create_framework_image(content, data)
    asset = upload_image_to_linkedin(image_bytes)

    payload = {
        "author": f"urn:li:person:{LINKEDIN_PERSON_ID}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": content},
                "shareMediaCategory": "IMAGE",
                "media": [{
                    "status": "READY",
                    "description": {"text": data.get("title", TOPIC)},
                    "media": asset,
                    "title": {"text": data.get("title", TOPIC)[:100]}
                }]
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
    print(f"[{datetime.now()}] LinkedIn framework post published! ID: {post_id}")

if __name__ == "__main__":
    if RUN_MODE == "post":
        job_post()
