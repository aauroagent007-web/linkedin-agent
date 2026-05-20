import openai
import requests
import os
import textwrap
import json
import hashlib
import base64
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import io
import math

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
LINKEDIN_ACCESS_TOKEN = os.environ["LINKEDIN_ACCESS_TOKEN"]
LINKEDIN_PERSON_ID = os.environ["LINKEDIN_PERSON_ID"]
TOPIC = os.environ.get("TOPIC", "Agentic AI cybersecurity and autonomous threat detection")
RUN_MODE = os.environ.get("RUN_MODE", "post")

openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

LINKEDIN_HEADERS = {
    "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
    "Content-Type": "application/json",
    "X-Restli-Protocol-Version": "2.0.0"
}

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

def get_daily_topic():
    day = datetime.now().timetuple().tm_yday
    return DAILY_TOPICS[day % len(DAILY_TOPICS)]

def get_seed(text):
    return int(hashlib.md5(text.encode()).hexdigest(), 16)

def ft(text, n):
    text = str(text)
    return text if len(text) <= n else text[:n-2]+".."

# ── Colors ────────────────────────────────────────────────────────────────────
BG = (8, 10, 20)
BG2 = (12, 15, 28)
BG3 = (15, 18, 35)
WHITE = (255, 255, 255)
GRAY = (160, 160, 180)
DARK_GRAY = (40, 45, 65)

ACCENT_SETS = [
    {"primary": (0, 255, 180), "secondary": (0, 180, 255), "highlight": (255, 220, 0)},
    {"primary": (180, 80, 255), "secondary": (255, 50, 150), "highlight": (255, 220, 0)},
    {"primary": (50, 220, 255), "secondary": (0, 150, 255), "highlight": (255, 150, 50)},
    {"primary": (50, 255, 150), "secondary": (0, 200, 100), "highlight": (255, 220, 0)},
    {"primary": (255, 100, 100), "secondary": (220, 50, 50), "highlight": (255, 180, 0)},
]

# ── AI Content ────────────────────────────────────────────────────────────────

def ai_generate_post(subtopic):
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content":
                "You are Aurobinda Ojha, Independent Researcher on Cybersecurity and Agentic AI. "
                "You write deep technical LinkedIn posts with architecture diagrams, "
                "structured sections, and detailed insights."},
            {"role": "user", "content":
                f"Write a detailed long-form LinkedIn post about: {subtopic}\n\n"
                f"STRUCTURE:\n"
                f"1. 🚀 Hook title line\n"
                f"2. 2-3 context lines\n"
                f"3. Problem list (5-6 bullets with emojis)\n"
                f"4. One powerful insight line\n"
                f"5. Solution list (5 ⚡ bullets)\n"
                f"6. ASCII architecture diagram with │ arrows\n"
                f"7. Four technical sections with emoji headers and • bullets\n"
                f"8. 🎯 Goals (5-6 ✅)\n"
                f"9. 🔥 Preferred Stack\n"
                f"10. Future vision line\n"
                f"11. About me as Aurobinda Ojha + aurobindaojha@gmail.com\n"
                f"12. 12-15 hashtags\n\n"
                f"400-600 words. Highly technical."}
        ],
        max_tokens=1500,
    )
    return response.choices[0].message.content.strip()

def ai_generate_infographic_data(subtopic):
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content":
                f"Create infographic data for: {subtopic}\n\n"
                f"Reply JSON only:\n"
                f"{{\n"
                f"  \"main_title\": \"HOW I SECURE [TOPIC] (caps, max 6 words)\",\n"
                f"  \"subtitle_pills\": [\"pill1 max 3 words\", \"pill2\", \"pill3\", \"pill4\", \"pill5\"],\n"
                f"  \"threats\": [\"Threat 1\", \"Threat 2\", \"Threat 3\", \"Threat 4\", \"Threat 5\", \"Threat 6\"],\n"
                f"  \"arch_layers\": [\n"
                f"    {{\"name\": \"Layer Name\", \"components\": [\"comp1\", \"comp2\", \"comp3\"]}}\n"
                f"  ],\n"
                f"  \"left_panel\": {{\n"
                f"    \"title\": \"ACCESS FLOW\",\n"
                f"    \"steps\": [\"Step 1\", \"Step 2\", \"Step 3\", \"Step 4\", \"Step 5\"]\n"
                f"  }},\n"
                f"  \"right_panel\": {{\n"
                f"    \"title\": \"SECURITY CONTROLS\",\n"
                f"    \"items\": [\"Control 1\", \"Control 2\", \"Control 3\", \"Control 4\", \"Control 5\"]\n"
                f"  }},\n"
                f"  \"security_layer\": {{\n"
                f"    \"title\": \"AUTONOMOUS PROTECTION LAYER\",\n"
                f"    \"components\": [\"comp1 max 3 words\", \"comp2\", \"comp3\", \"comp4\", \"comp5\"]\n"
                f"  }},\n"
                f"  \"goals\": [\"Goal 1 max 4 words\", \"Goal 2\", \"Goal 3\", \"Goal 4\", \"Goal 5\", \"Goal 6\"],\n"
                f"  \"stack\": [\"Tech1\", \"Tech2\", \"Tech3\", \"Tech4\", \"Tech5\", \"Tech6\", \"Tech7\", \"Tech8\"],\n"
                f"  \"why_works\": [\"Reason 1 max 6 words\", \"Reason 2\", \"Reason 3\", \"Reason 4\", \"Reason 5\"],\n"
                f"  \"principles\": [\"Principle 1\", \"Principle 2\", \"Principle 3\", \"Principle 4\", \"Principle 5\"]\n"
                f"}}\n\n"
                f"arch_layers: exactly 5 layers. Each layer has 2-3 components.\n"
                f"Make everything specific to {subtopic}."}
        ],
        max_tokens=1200,
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json","").replace("```","").strip()
    return json.loads(raw)

# ── Fonts ─────────────────────────────────────────────────────────────────────

def load_fonts():
    try:
        B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        return {
            "title_lg": ImageFont.truetype(B, 52),
            "title_md": ImageFont.truetype(B, 36),
            "title_sm": ImageFont.truetype(B, 26),
            "section":  ImageFont.truetype(B, 20),
            "body":     ImageFont.truetype(R, 18),
            "small":    ImageFont.truetype(R, 15),
            "tiny":     ImageFont.truetype(R, 13),
        }
    except:
        d = ImageFont.load_default()
        return {k: d for k in ["title_lg","title_md","title_sm",
                                "section","body","small","tiny"]}

# ── Drawing Helpers ───────────────────────────────────────────────────────────

def draw_rounded_box(draw, x0, y0, x1, y1, fill, outline=None, radius=8, width=2):
    try:
        draw.rounded_rectangle([(x0,y0),(x1,y1)], radius=radius,
                                fill=fill, outline=outline, width=width)
    except:
        draw.rectangle([(x0,y0),(x1,y1)], fill=fill, outline=outline, width=width)

def draw_dashed_border(draw, x0, y0, x1, y1, color, dash=8):
    for x in range(x0, x1, dash*2):
        draw.line([(x,y0),(min(x+dash,x1),y0)], fill=color, width=1)
        draw.line([(x,y1),(min(x+dash,x1),y1)], fill=color, width=1)
    for y in range(y0, y1, dash*2):
        draw.line([(x0,y),(x0,min(y+dash,y1))], fill=color, width=1)
        draw.line([(x1,y),(x1,min(y+dash,y1))], fill=color, width=1)

def draw_arrow_down(draw, x, y, color, size=12):
    draw.line([(x,y),(x,y+size)], fill=color, width=2)
    draw.polygon([(x-5,y+size-4),(x+5,y+size-4),(x,y+size+4)], fill=color)

def centered_text(draw, text, cx, y, font, color):
    bbox = draw.textbbox((0,0), text, font=font)
    w = bbox[2]-bbox[0]
    draw.text((cx-w//2, y), text, font=font, fill=color)

# ── Infographic Creator ───────────────────────────────────────────────────────

def create_infographic(subtopic, data):
    print(f"[{datetime.now()}] Creating infographic...")

    width = 1080
    seed = get_seed(subtopic)
    colors = ACCENT_SETS[seed % len(ACCENT_SETS)]
    P = colors["primary"]
    S = colors["secondary"]
    H = colors["highlight"]

    fonts = load_fonts()

    # ── Calculate total height ─────────────────────────────────────────────
    height = 2400
    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)

    # Background gradient
    for y in range(height):
        ratio = y / height
        r = int(BG[0] + ratio * 5)
        g = int(BG[1] + ratio * 5)
        b = int(BG[2] + ratio * 10)
        draw.line([(0,y),(width,y)], fill=(r,g,b))

    # Subtle grid
    for x in range(0, width, 50):
        draw.line([(x,0),(x,height)], fill=(15,18,30), width=1)
    for y in range(0, height, 50):
        draw.line([(0,y),(width,y)], fill=(15,18,30), width=1)

    current_y = 0

    # ── HEADER ────────────────────────────────────────────────────────────
    # Gradient header bar
    for y in range(100):
        ratio = y / 100
        r = int(P[0]*0.3 + S[0]*0.7*ratio)
        g = int(P[1]*0.3 + S[1]*0.7*ratio)
        b = int(P[2]*0.3 + S[2]*0.7*ratio)
        draw.line([(0,y),(width,y)], fill=(max(0,min(255,r)),
                                          max(0,min(255,g)),
                                          max(0,min(255,b))))

    # Author line
    draw.text((width//2-80, 8), "✦  AUROBINDA OJHA",
              font=fonts["small"], fill=WHITE)

    # Main title
    main_title = data.get("main_title","HOW I SECURE AI SYSTEMS")
    title_words = main_title.split()
    # Split into 2 lines
    mid = len(title_words)//2
    line1 = " ".join(title_words[:mid])
    line2 = " ".join(title_words[mid:])

    # First line white
    bbox = draw.textbbox((0,0), line1, font=fonts["title_lg"])
    tw = bbox[2]-bbox[0]
    draw.text(((width-tw)//2, 28), line1, font=fonts["title_lg"], fill=WHITE)

    # Second line colored
    bbox2 = draw.textbbox((0,0), line2, font=fonts["title_lg"])
    tw2 = bbox2[2]-bbox2[0]
    # Draw with two colors
    words2 = line2.split()
    if len(words2) >= 3:
        part1 = " ".join(words2[:2])
        part2 = " ".join(words2[2:])
        bbox_p1 = draw.textbbox((0,0), part1+" ", font=fonts["title_lg"])
        total_w = draw.textbbox((0,0), line2, font=fonts["title_lg"])[2]
        x_start = (width-total_w)//2
        draw.text((x_start, 82), part1, font=fonts["title_lg"], fill=P)
        draw.text((x_start+bbox_p1[2]-bbox_p1[0], 82), " "+part2,
                  font=fonts["title_lg"], fill=H)
    else:
        draw.text(((width-tw2)//2, 82), line2, font=fonts["title_lg"], fill=P)

    current_y = 145

    # Subtitle pills
    pills = data.get("subtitle_pills", [])
    pill_x = 30
    for pill in pills[:5]:
        bbox = draw.textbbox((0,0), pill, font=fonts["tiny"])
        pw = bbox[2]-bbox[0]+20
        draw.rounded_rectangle([(pill_x, current_y),
                                 (pill_x+pw, current_y+22)],
                                radius=11, fill=(30,35,55))
        draw.text((pill_x+10, current_y+4), pill,
                  font=fonts["tiny"], fill=GRAY)
        pill_x += pw + 8
    current_y += 35

    # ── THREATS BAR ───────────────────────────────────────────────────────
    draw.rectangle([(0,current_y),(width,current_y+30)], fill=(20,25,45))
    draw.text((width//2-80, current_y+6), "TOP SECURITY THREATS",
              font=fonts["tiny"], fill=P)
    current_y += 30

    threats = data.get("threats", [])
    threat_w = (width-40) // max(len(threats), 1)
    for i, threat in enumerate(threats[:6]):
        tx = 20 + i*threat_w
        draw_rounded_box(draw, tx, current_y+4, tx+threat_w-8,
                         current_y+50, fill=(20,25,45),
                         outline=P, radius=6, width=1)
        threat_lines = textwrap.fill(ft(threat,12), width=10).split('\n')
        ty2 = current_y+8
        for tl in threat_lines:
            bbox = draw.textbbox((0,0), tl, font=fonts["tiny"])
            tlw = bbox[2]-bbox[0]
            draw.text((tx+(threat_w-8-tlw)//2, ty2), tl,
                      font=fonts["tiny"], fill=WHITE)
            ty2 += 14
    current_y += 60

    # ── THREE COLUMN AREA ─────────────────────────────────────────────────
    LEFT_W = 185
    RIGHT_W = 185
    MID_W = width - LEFT_W - RIGHT_W - 20
    LEFT_X = 10
    MID_X = LEFT_X + LEFT_W + 5
    RIGHT_X = MID_X + MID_W + 5

    arch_start_y = current_y

    # LEFT PANEL — Access Flow
    left_panel = data.get("left_panel", {})
    left_title = left_panel.get("title","ACCESS FLOW")
    left_steps = left_panel.get("steps",[])

    draw_rounded_box(draw, LEFT_X, arch_start_y,
                     LEFT_X+LEFT_W, arch_start_y+520,
                     fill=BG2, outline=P, radius=8, width=1)
    draw.text((LEFT_X+10, arch_start_y+8), left_title,
              font=fonts["section"], fill=P)
    draw.line([(LEFT_X+8,arch_start_y+30),(LEFT_X+LEFT_W-8,arch_start_y+30)],
              fill=DARK_GRAY)

    step_y = arch_start_y+38
    for step in left_steps[:6]:
        draw_rounded_box(draw, LEFT_X+8, step_y,
                         LEFT_X+LEFT_W-8, step_y+42,
                         fill=(20,25,45), outline=DARK_GRAY, radius=6)
        step_wrapped = textwrap.fill(ft(step,18), width=16)
        draw.text((LEFT_X+14, step_y+6), step_wrapped,
                  font=fonts["tiny"], fill=WHITE)
        step_y += 50
        if step_y < arch_start_y+510:
            draw_arrow_down(draw, LEFT_X+LEFT_W//2,
                           step_y-8, P, size=8)

    # LEFT PRINCIPLES
    principles_y = arch_start_y+525
    draw_rounded_box(draw, LEFT_X, principles_y,
                     LEFT_X+LEFT_W, principles_y+200,
                     fill=BG2, outline=S, radius=8, width=1)
    draw.text((LEFT_X+10, principles_y+8), "PRINCIPLES",
              font=fonts["section"], fill=S)
    draw.line([(LEFT_X+8,principles_y+28),(LEFT_X+LEFT_W-8,principles_y+28)],
              fill=DARK_GRAY)
    py2 = principles_y+35
    for principle in data.get("principles",[])[:5]:
        draw.text((LEFT_X+10, py2), f"◆ {ft(principle,20)}",
                  font=fonts["tiny"], fill=GRAY)
        py2 += 22

    # RIGHT PANEL — Security Controls
    right_panel = data.get("right_panel", {})
    right_title = right_panel.get("title","SECURITY CONTROLS")
    right_items = right_panel.get("items",[])

    draw_rounded_box(draw, RIGHT_X, arch_start_y,
                     RIGHT_X+RIGHT_W, arch_start_y+520,
                     fill=BG2, outline=H, radius=8, width=1)
    draw.text((RIGHT_X+6, arch_start_y+8), right_title,
              font=fonts["section"], fill=H)
    draw.line([(RIGHT_X+8,arch_start_y+30),
               (RIGHT_X+RIGHT_W-8,arch_start_y+30)], fill=DARK_GRAY)

    ri_y = arch_start_y+38
    for item in right_items[:6]:
        draw_rounded_box(draw, RIGHT_X+8, ri_y,
                         RIGHT_X+RIGHT_W-8, ri_y+60,
                         fill=(20,25,45), outline=H, radius=6)
        draw.text((RIGHT_X+14, ri_y+8), ft(item,20),
                  font=fonts["tiny"], fill=WHITE)
        ri_y += 68

    # RIGHT GOALS
    goals_y = arch_start_y+525
    draw_rounded_box(draw, RIGHT_X, goals_y,
                     RIGHT_X+RIGHT_W, goals_y+200,
                     fill=BG2, outline=H, radius=8, width=1)
    draw.text((RIGHT_X+10, goals_y+8), "PRODUCTION GOALS",
              font=fonts["section"], fill=H)
    draw.line([(RIGHT_X+8,goals_y+28),(RIGHT_X+RIGHT_W-8,goals_y+28)],
              fill=DARK_GRAY)
    gy = goals_y+35
    for goal in data.get("goals",[])[:6]:
        draw.text((RIGHT_X+8, gy), f"✓ {ft(goal,20)}",
                  font=fonts["tiny"], fill=GRAY)
        gy += 22

    # CENTER — Architecture
    draw_rounded_box(draw, MID_X, arch_start_y,
                     MID_X+MID_W, arch_start_y+520,
                     fill=BG2, outline=S, radius=8, width=1)
    draw.text((MID_X+10, arch_start_y+8),
              "PRODUCTION INFRASTRUCTURE",
              font=fonts["section"], fill=S)
    draw.line([(MID_X+8,arch_start_y+30),
               (MID_X+MID_W-8,arch_start_y+30)], fill=DARK_GRAY)

    arch_layers = data.get("arch_layers",[])
    layer_h = 75
    lay_y = arch_start_y+38
    for idx, layer in enumerate(arch_layers[:5]):
        lcolor = [P,S,H,(100,200,255),(180,255,100)][idx%5]
        draw_rounded_box(draw, MID_X+8, lay_y,
                         MID_X+MID_W-8, lay_y+layer_h,
                         fill=(15,20,38), outline=lcolor, radius=6)
        lname = layer.get("name","Layer")
        draw.text((MID_X+14, lay_y+5), ft(lname,28),
                  font=fonts["small"], fill=lcolor)
        comps = layer.get("components",[])
        comp_str = "  •  ".join([ft(c,15) for c in comps[:3]])
        draw.text((MID_X+14, lay_y+26), comp_str,
                  font=fonts["tiny"], fill=GRAY)
        lay_y += layer_h+6
        if idx < len(arch_layers)-1:
            draw_arrow_down(draw, MID_X+MID_W//2,
                           lay_y-4, S, size=6)
            lay_y += 8

    current_y = arch_start_y + 735

    # ── SECURITY LAYER ────────────────────────────────────────────────────
    sec_layer = data.get("security_layer",{})
    sec_title = sec_layer.get("title","AUTONOMOUS PROTECTION")
    sec_comps = sec_layer.get("components",[])

    draw_rounded_box(draw, 10, current_y, width-10, current_y+100,
                     fill=(15,20,40), outline=P, radius=8, width=2)
    draw.text((width//2-120, current_y+8), sec_title,
              font=fonts["section"], fill=P)
    draw.line([(20,current_y+28),(width-20,current_y+28)], fill=DARK_GRAY)

    comp_w = (width-40) // max(len(sec_comps),1)
    for i, comp in enumerate(sec_comps[:5]):
        cx2 = 20+i*comp_w+comp_w//2
        draw_rounded_box(draw, 20+i*comp_w+4, current_y+34,
                         20+(i+1)*comp_w-4, current_y+90,
                         fill=(20,28,50), outline=S, radius=6)
        comp_wrapped = textwrap.fill(ft(comp,12), width=10)
        clines = comp_wrapped.split('\n')
        cty = current_y+38+(20-len(clines)*14)//2
        for cl in clines:
            bbox = draw.textbbox((0,0), cl, font=fonts["tiny"])
            clw = bbox[2]-bbox[0]
            draw.text((cx2-clw//2, cty), cl, font=fonts["tiny"], fill=WHITE)
            cty += 14
    current_y += 110

    # ── STACK + WHY WORKS + ABOUT ─────────────────────────────────────────
    section_y = current_y
    SEC_W = (width-30) // 3
    SEC1_X = 10
    SEC2_X = SEC1_X+SEC_W+5
    SEC3_X = SEC2_X+SEC_W+5

    # Stack
    draw_rounded_box(draw, SEC1_X, section_y,
                     SEC1_X+SEC_W, section_y+220,
                     fill=BG2, outline=DARK_GRAY, radius=8)
    draw.text((SEC1_X+10, section_y+8), "🔥 PREFERRED STACK",
              font=fonts["section"], fill=H)
    draw.line([(SEC1_X+8,section_y+28),(SEC1_X+SEC_W-8,section_y+28)],
              fill=DARK_GRAY)
    stack = data.get("stack",[])
    sx = SEC1_X+10
    sy2 = section_y+36
    for tech in stack[:12]:
        bbox = draw.textbbox((0,0), tech, font=fonts["tiny"])
        tw2 = bbox[2]-bbox[0]+12
        if sx+tw2 > SEC1_X+SEC_W-8:
            sx = SEC1_X+10
            sy2 += 28
        draw_rounded_box(draw, sx, sy2, sx+tw2, sy2+20,
                         fill=(25,30,55), outline=P, radius=4)
        draw.text((sx+6, sy2+3), tech, font=fonts["tiny"], fill=P)
        sx += tw2+6

    # Why Works
    draw_rounded_box(draw, SEC2_X, section_y,
                     SEC2_X+SEC_W, section_y+220,
                     fill=BG2, outline=DARK_GRAY, radius=8)
    draw.text((SEC2_X+10, section_y+8), "✅ WHY THIS WORKS",
              font=fonts["section"], fill=P)
    draw.line([(SEC2_X+8,section_y+28),(SEC2_X+SEC_W-8,section_y+28)],
              fill=DARK_GRAY)
    wy = section_y+36
    for reason in data.get("why_works",[])[:5]:
        draw.text((SEC2_X+10, wy), f"✓  {ft(reason,28)}",
                  font=fonts["tiny"], fill=GRAY)
        wy += 26

    # About Me
    draw_rounded_box(draw, SEC3_X, section_y,
                     SEC3_X+SEC_W, section_y+220,
                     fill=BG2, outline=DARK_GRAY, radius=8)
    draw.text((SEC3_X+10, section_y+8), "👤 ABOUT ME",
              font=fonts["section"], fill=S)
    draw.line([(SEC3_X+8,section_y+28),(SEC3_X+SEC_W-8,section_y+28)],
              fill=DARK_GRAY)

    draw.ellipse([(SEC3_X+SEC_W//2-30, section_y+35),
                  (SEC3_X+SEC_W//2+30, section_y+95)],
                 outline=S, width=2)
    draw.text((SEC3_X+SEC_W//2-12, section_y+55), "AO",
              font=fonts["title_sm"], fill=S)

    draw.text((SEC3_X+10, section_y+105), "Aurobinda Ojha",
              font=fonts["small"], fill=WHITE)
    draw.text((SEC3_X+10, section_y+124),
              "Independent Researcher",
              font=fonts["tiny"], fill=GRAY)
    draw.text((SEC3_X+10, section_y+140),
              "Cybersecurity & Agentic AI",
              font=fonts["tiny"], fill=GRAY)

    roles = ["Cybersecurity Research", "Agentic AI", "LLMOps"]
    ry = section_y+160
    rx = SEC3_X+10
    for role in roles:
        bbox = draw.textbbox((0,0), role, font=fonts["tiny"])
        rw = bbox[2]-bbox[0]+10
        draw_rounded_box(draw, rx, ry, rx+rw, ry+18,
                         fill=(20,25,50), outline=S, radius=4)
        draw.text((rx+5, ry+2), role, font=fonts["tiny"], fill=S)
        rx += rw+5
        if rx > SEC3_X+SEC_W-10:
            rx = SEC3_X+10
            ry += 22

    current_y = section_y + 230

    # ── FOOTER ────────────────────────────────────────────────────────────
    draw.rectangle([(0,current_y),(width,current_y+4)], fill=P)
    current_y += 8

    draw_rounded_box(draw, 10, current_y, width-10, current_y+60,
                     fill=(12,15,30), outline=DARK_GRAY, radius=8)

    shield = "🛡️"
    draw.text((25, current_y+12), shield, font=fonts["title_sm"], fill=P)
    draw.text((75, current_y+10),
              "LET'S BUILD SECURE AI INFRASTRUCTURE TOGETHER!",
              font=fonts["small"], fill=WHITE)
    draw.text((75, current_y+32), "📩 aurobindaojha@gmail.com",
              font=fonts["small"], fill=P)

    date_str = datetime.now().strftime("%B %d, %Y")
    draw.text((width-200, current_y+35), date_str,
              font=fonts["tiny"], fill=GRAY)
    current_y += 70

    # Hashtags
    draw.rectangle([(0,current_y),(width,current_y+40)], fill=(8,10,20))
    hashtags = "#AgenticAI #Cybersecurity #ZeroTrust #AISecuurity #LLMOps #AIOps #MLOps"
    draw.text((20, current_y+10), hashtags, font=fonts["tiny"], fill=(80,90,120))
    current_y += 45

    # Crop to content
    img = img.crop((0, 0, width, current_y))

    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG", quality=95)
    img_bytes.seek(0)
    print(f"Infographic created!")
    return img_bytes.read()

# ── LinkedIn Upload ───────────────────────────────────────────────────────────

def upload_image_to_linkedin(image_data):
    print(f"[{datetime.now()}] Uploading to LinkedIn...")
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
        headers=LINKEDIN_HEADERS, json=register_payload
    )
    r.raise_for_status()
    response_json = r.json()
    upload_url = response_json["value"]["uploadMechanism"][
        "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
    asset = response_json["value"]["asset"]
    requests.put(
        upload_url,
        headers={"Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
                 "Content-Type": "application/octet-stream"},
        data=image_data
    ).raise_for_status()
    print(f"Uploaded! Asset: {asset}")
    return asset

# ── Main ──────────────────────────────────────────────────────────────────────

def job_post():
    subtopic = get_daily_topic()
    print(f"[{datetime.now()}] Today: {subtopic}")

    content = ai_generate_post(subtopic)
    print(f"Post: {content[:100]}...")

    data = ai_generate_infographic_data(subtopic)
    print(f"Title: {data.get('main_title')}")

    image_data = create_infographic(subtopic, data)
    asset = upload_image_to_linkedin(image_data)

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
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
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
