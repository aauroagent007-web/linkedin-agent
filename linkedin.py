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

PROFILE_IMAGE_URL = (
    "https://media.licdn.com/dms/image/v2/C4D03AQHnswiAnQJbMg/"
    "profile-displayphoto-shrink_800_800/"
    "profile-displayphoto-shrink_800_800/0/1516492188066"
    "?e=1781136000&v=beta&t=fSaDr16J6btRG0W3a32V__c-slLPrTscWAGJGI6vxEE"
)

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

# Icon definitions — drawn with PIL primitives
ICONS = {
    "shield":   lambda d,x,y,s,c: _icon_shield(d,x,y,s,c),
    "brain":    lambda d,x,y,s,c: _icon_brain(d,x,y,s,c),
    "lock":     lambda d,x,y,s,c: _icon_lock(d,x,y,s,c),
    "eye":      lambda d,x,y,s,c: _icon_eye(d,x,y,s,c),
    "network":  lambda d,x,y,s,c: _icon_network(d,x,y,s,c),
    "warning":  lambda d,x,y,s,c: _icon_warning(d,x,y,s,c),
    "gear":     lambda d,x,y,s,c: _icon_gear(d,x,y,s,c),
    "check":    lambda d,x,y,s,c: _icon_check(d,x,y,s,c),
    "search":   lambda d,x,y,s,c: _icon_search(d,x,y,s,c),
    "monitor":  lambda d,x,y,s,c: _icon_monitor(d,x,y,s,c),
    "robot":    lambda d,x,y,s,c: _icon_robot(d,x,y,s,c),
    "database": lambda d,x,y,s,c: _icon_database(d,x,y,s,c),
}

SECTION_ICONS = [
    "shield","brain","lock","eye",
    "network","warning","gear","check",
    "search","monitor","robot","database",
    "shield","brain","lock","eye",
    "network","warning",
]

def _icon_shield(d,x,y,s,c):
    pts = [(x+s//2,y),(x+s,y+s//3),(x+s,y+s*2//3),(x+s//2,y+s),(x,y+s*2//3),(x,y+s//3)]
    d.polygon(pts, outline=c, fill=(*c[:3],30) if len(c)==4 else None)
    d.line([(x+s//2,y+s//3),(x+s//3,y+s//2),(x+s//2,y+s*2//3)], fill=c, width=2)

def _icon_brain(d,x,y,s,c):
    d.ellipse([(x,y+s//4),(x+s,y+s*3//4)], outline=c, width=2)
    d.line([(x+s//2,y+s//4),(x+s//2,y+s*3//4)], fill=c, width=1)
    d.arc([(x+s//4,y),(x+s*3//4,y+s//2)], 180, 0, fill=c, width=2)

def _icon_lock(d,x,y,s,c):
    d.rectangle([(x+s//4,y+s//2),(x+s*3//4,y+s)], outline=c, width=2)
    d.arc([(x+s//4,y+s//6),(x+s*3//4,y+s*2//3)], 180, 0, fill=c, width=2)
    d.ellipse([(x+s//2-3,y+s*2//3-3),(x+s//2+3,y+s*2//3+3)], fill=c)

def _icon_eye(d,x,y,s,c):
    d.arc([(x,y+s//4),(x+s,y+s*3//4)], 0, 180, fill=c, width=2)
    d.arc([(x,y+s//4),(x+s,y+s*3//4)], 180, 360, fill=c, width=2)
    d.ellipse([(x+s//2-s//6,y+s//2-s//6),(x+s//2+s//6,y+s//2+s//6)], fill=c)

def _icon_network(d,x,y,s,c):
    cx,cy = x+s//2, y+s//2
    d.ellipse([(cx-4,cy-4),(cx+4,cy+4)], fill=c)
    for ang in [0,72,144,216,288]:
        rad = math.radians(ang)
        ex,ey = int(cx+s//3*math.cos(rad)), int(cy+s//3*math.sin(rad))
        d.line([(cx,cy),(ex,ey)], fill=c, width=1)
        d.ellipse([(ex-3,ey-3),(ex+3,ey+3)], fill=c)

def _icon_warning(d,x,y,s,c):
    d.polygon([(x+s//2,y),(x+s,y+s),(x,y+s)], outline=c, width=2)
    d.line([(x+s//2,y+s//3),(x+s//2,y+s*2//3)], fill=c, width=2)
    d.ellipse([(x+s//2-2,y+s*3//4-2),(x+s//2+2,y+s*3//4+2)], fill=c)

def _icon_gear(d,x,y,s,c):
    cx,cy = x+s//2, y+s//2
    d.ellipse([(cx-s//4,cy-s//4),(cx+s//4,cy+s//4)], outline=c, width=2)
    for ang in range(0,360,45):
        rad = math.radians(ang)
        x1 = int(cx+s//4*math.cos(rad)); y1 = int(cy+s//4*math.sin(rad))
        x2 = int(cx+s//3*math.cos(rad)); y2 = int(cy+s//3*math.sin(rad))
        d.line([(x1,y1),(x2,y2)], fill=c, width=3)

def _icon_check(d,x,y,s,c):
    d.ellipse([(x,y),(x+s,y+s)], outline=c, width=2)
    d.line([(x+s//4,y+s//2),(x+s*2//5,y+s*2//3),(x+s*3//4,y+s//3)], fill=c, width=2)

def _icon_search(d,x,y,s,c):
    d.ellipse([(x,y),(x+s*2//3,y+s*2//3)], outline=c, width=2)
    d.line([(x+s*2//3-3,y+s*2//3-3),(x+s,y+s)], fill=c, width=3)

def _icon_monitor(d,x,y,s,c):
    d.rectangle([(x,y),(x+s,y+s*3//4)], outline=c, width=2)
    d.line([(x+s//2,y+s*3//4),(x+s//2,y+s)], fill=c, width=2)
    d.line([(x+s//4,y+s),(x+s*3//4,y+s)], fill=c, width=2)

def _icon_robot(d,x,y,s,c):
    d.rectangle([(x+s//4,y),(x+s*3//4,y+s//3)], outline=c, width=2)
    d.rectangle([(x+s//6,y+s//3),(x+s*5//6,y+s*4//5)], outline=c, width=2)
    d.ellipse([(x+s//3-3,y+s//6-3),(x+s//3+3,y+s//6+3)], fill=c)
    d.ellipse([(x+s*2//3-3,y+s//6-3),(x+s*2//3+3,y+s//6+3)], fill=c)

def _icon_database(d,x,y,s,c):
    d.ellipse([(x,y),(x+s,y+s//4)], outline=c, width=2)
    d.rectangle([(x,y+s//8),(x+s,y+s*3//4)], fill=None, outline=None)
    d.line([(x,y+s//8),(x,y+s*3//4)], fill=c, width=2)
    d.line([(x+s,y+s//8),(x+s,y+s*3//4)], fill=c, width=2)
    d.arc([(x,y+s//2),(x+s,y+s)], 0, 180, fill=c, width=2)
    d.arc([(x,y+s//4),(x+s,y+s*5//8)], 0, 180, fill=c, width=2)

def draw_icon(draw, name, x, y, size, color):
    fn = ICONS.get(name, ICONS["shield"])
    fn(draw, x, y, size, color)

def get_daily_topic():
    day = datetime.now().timetuple().tm_yday
    return DAILY_TOPICS[day % len(DAILY_TOPICS)]

def get_seed(text):
    return int(hashlib.md5(text.encode()).hexdigest(), 16)

def ft(text, n):
    text = str(text).strip()
    return text if len(text) <= n else text[:n-2]+".."

def text_in_box(draw, text, x, y, max_w, max_h, font, color,
                line_h=16, padding=4):
    text = str(text).strip()
    chars = max(1, (max_w-padding*2) // 8)
    lines = textwrap.fill(text, width=chars).split('\n')
    cy = y + padding
    for line in lines:
        if cy + line_h > y + max_h - padding:
            break
        draw.text((x+padding, cy), line, font=font, fill=color)
        cy += line_h

def load_profile_image(size=100):
    try:
        resp = requests.get(PROFILE_IMAGE_URL, timeout=15)
        resp.raise_for_status()
        profile = Image.open(io.BytesIO(resp.content)).convert("RGB")
        profile = profile.resize((size, size), Image.LANCZOS)
        mask = Image.new("L", (size, size), 0)
        md = ImageDraw.Draw(mask)
        md.ellipse([(0,0),(size,size)], fill=255)
        result = Image.new("RGBA", (size, size), (0,0,0,0))
        result.paste(profile, (0,0))
        result.putalpha(mask)
        print("Profile image loaded!")
        return result
    except Exception as e:
        print(f"Profile image failed: {e}")
        return None

# ── Colors ────────────────────────────────────────────────────────────────────
BG        = (8, 12, 28)
BG2       = (12, 16, 36)
BG3       = (18, 24, 50)
WHITE     = (255, 255, 255)
OFF_WHITE = (220, 230, 255)
GRAY      = (160, 170, 200)
DARK_GRAY = (40, 48, 80)

ACCENT_SETS = [
    {"P":(0,200,255),  "S":(0,255,180), "H":(255,220,0), "D":(30,40,80)},
    {"P":(180,80,255), "S":(255,50,150),"H":(255,220,0), "D":(40,20,60)},
    {"P":(50,220,255), "S":(0,180,255), "H":(255,150,50),"D":(20,35,60)},
    {"P":(50,255,150), "S":(0,220,120), "H":(255,220,0), "D":(15,40,30)},
    {"P":(255,130,50), "S":(220,80,0),  "H":(255,220,0), "D":(50,25,10)},
]

# ── AI ────────────────────────────────────────────────────────────────────────

def ai_generate_post(subtopic):
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content":
                "You are Aurobinda Ojha, Independent Researcher on Cybersecurity "
                "and Agentic AI. Write deep technical LinkedIn posts. "
                "NEVER write any about me, reach out, or contact section. "
                "NEVER use ##, **, __, or any markdown. Plain text + emojis only."},
            {"role": "user", "content":
                f"Write a detailed LinkedIn post about: {subtopic}\n\n"
                f"STRUCTURE:\n"
                f"1. Hook: emoji + powerful title\n"
                f"2. 2-3 context lines\n"
                f"3. Problem list (5-6 emoji bullets)\n"
                f"4. Powerful insight\n"
                f"5. Solution list (5 bullets)\n"
                f"6. ASCII architecture\n"
                f"7. Four technical sections\n"
                f"8. Goals (5-6 checkmarks)\n"
                f"9. Preferred Stack\n"
                f"10. Future vision\n"
                f"11. End with 12-15 hashtags\n\n"
                f"NO about me. NO contact. NO markdown. 400-600 words."}
        ],
        max_tokens=1500,
    )
    content = response.choices[0].message.content.strip()
    for ch in ["##","**","__","# ","* "]:
        content = content.replace(ch, "")
    skip_kw = ["reach out","contact me","about me","i am aurobinda",
                "aurobindaojha@","gmail.com","collaborat","freelance"]
    lines = [l for l in content.split('\n')
             if not any(k in l.lower() for k in skip_kw)]
    return '\n'.join(lines).strip()

def ai_generate_infographic_data(subtopic):
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content":
                f"Create infographic data for: {subtopic}\n\n"
                f"Reply JSON only:\n"
                f"{{\n"
                f"  \"main_title\": \"TOPIC COMPLETE DEEP DIVE (caps max 5 words)\",\n"
                f"  \"tagline\": \"short tagline max 8 words\",\n"
                f"  \"top_badges\": [\n"
                f"    {{\"icon\":\"shield\",\"label\":\"max 2 words\"}},\n"
                f"    {{\"icon\":\"eye\",\"label\":\"max 2 words\"}},\n"
                f"    {{\"icon\":\"monitor\",\"label\":\"max 2 words\"}},\n"
                f"    {{\"icon\":\"warning\",\"label\":\"max 2 words\"}}\n"
                f"  ],\n"
                f"  \"sections\": [\n"
                f"    {{\n"
                f"      \"number\": 1,\n"
                f"      \"title\": \"Section Title max 4 words\",\n"
                f"      \"icon\": \"one of: shield,brain,lock,eye,network,warning,gear,check,search,monitor,robot,database\",\n"
                f"      \"bullets\": [\"max 5 words\",\"max 5 words\",\"max 5 words\",\"max 5 words\"]\n"
                f"    }}\n"
                f"  ],\n"
                f"  \"bottom_quote\": \"Powerful closing quote max 10 words\"\n"
                f"}}\n\n"
                f"Create exactly 9 sections specific to {subtopic}.\n"
                f"Each section has exactly 4 bullet points.\n"
                f"Use varied icons from the list."}
        ],
        max_tokens=1500,
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
            "h1":   ImageFont.truetype(B, 52),
            "h2":   ImageFont.truetype(B, 36),
            "h3":   ImageFont.truetype(B, 24),
            "h4":   ImageFont.truetype(B, 18),
            "h5":   ImageFont.truetype(B, 15),
            "body": ImageFont.truetype(R, 15),
            "sm":   ImageFont.truetype(R, 13),
            "xs":   ImageFont.truetype(R, 11),
        }
    except:
        d = ImageFont.load_default()
        return {k: d for k in ["h1","h2","h3","h4","h5","body","sm","xs"]}

# ── Draw Helpers ──────────────────────────────────────────────────────────────

def rbox(draw, x0, y0, x1, y1, fill=None, outline=None, r=6, w=1):
    try:
        draw.rounded_rectangle([(x0,y0),(x1,y1)],
                                radius=r, fill=fill,
                                outline=outline, width=w)
    except:
        draw.rectangle([(x0,y0),(x1,y1)],
                       fill=fill, outline=outline, width=w)

def cx_text(draw, text, cx, y, font, color):
    bbox = draw.textbbox((0,0), text, font=font)
    w = bbox[2]-bbox[0]
    draw.text((cx-w//2, y), text, font=font, fill=color)

# ── Infographic ───────────────────────────────────────────────────────────────

def create_infographic(subtopic, data):
    print(f"[{datetime.now()}] Creating infographic...")

    W       = 1080
    seed    = get_seed(subtopic)
    C       = ACCENT_SETS[seed % len(ACCENT_SETS)]
    P, S, H = C["P"], C["S"], C["H"]
    fonts   = load_fonts()

    profile_img = load_profile_image(size=110)

    # Layout
    H_HEADER = 180
    H_BADGES = 55
    H_TAGLINE = 40
    ROWS      = 3
    COLS      = 3
    CELL_H    = 280
    CELL_PAD  = 6
    CELL_W    = (W - (COLS+1)*CELL_PAD) // COLS
    GRID_H    = ROWS * CELL_H + (ROWS+1)*CELL_PAD
    H_FOOTER  = 90
    TOTAL_H   = H_HEADER+H_BADGES+H_TAGLINE+GRID_H+H_FOOTER

    img  = Image.new("RGB", (W, TOTAL_H), BG)
    draw = ImageDraw.Draw(img)

    # Background gradient
    for y in range(TOTAL_H):
        t = y/TOTAL_H
        draw.line([(0,y),(W,y)], fill=(
            int(BG[0]+t*6), int(BG[1]+t*6), int(BG[2]+t*10)))

    # Subtle grid pattern
    for x in range(0, W, 45):
        draw.line([(x,0),(x,TOTAL_H)], fill=(13,17,38), width=1)
    for y in range(0, TOTAL_H, 45):
        draw.line([(0,y),(W,y)], fill=(13,17,38), width=1)

    Y = 0

    # ── HEADER ────────────────────────────────────────────────────────────
    # Gradient header
    for y in range(H_HEADER):
        t = y/H_HEADER
        r = int(P[0]*0.6*(1-t) + BG[0]*t)
        g = int(P[1]*0.6*(1-t) + BG[1]*t)
        b = int(P[2]*0.6*(1-t) + BG[2]*t)
        draw.line([(0,y),(W,y)], fill=(
            max(0,min(255,r)),max(0,min(255,g)),max(0,min(255,b))))

    # Left side — Title
    title = data.get("main_title","AI SECURITY DEEP DIVE")
    words = title.split()
    mid   = max(1, len(words)//2)
    l1    = " ".join(words[:mid])
    l2    = " ".join(words[mid:])

    draw.text((20, Y+15), l1, font=fonts["h1"], fill=WHITE)
    draw.text((20, Y+72), l2, font=fonts["h1"], fill=P)

    # Underline
    bb = draw.textbbox((0,0), l2, font=fonts["h1"])
    draw.rectangle([(20, Y+125),(20+bb[2]-bb[0]+40, Y+129)], fill=H)

    draw.text((22, Y+138), "CYBERSECURITY RESEARCHER & AI EXPERT",
              font=fonts["h5"], fill=GRAY)

    # Right side — Profile image
    if profile_img is not None:
        img_rgba = img.convert("RGBA")
        prof_x = W - 140
        prof_y = Y + 20
        img_rgba.paste(profile_img, (prof_x, prof_y), profile_img)
        img = img_rgba.convert("RGB")
        draw = ImageDraw.Draw(img)

        # Accent ring
        draw.ellipse([
            (prof_x-4, prof_y-4),
            (prof_x+114, prof_y+114)
        ], outline=P, width=3)

        # Name beside photo
        draw.text((W-240, Y+35), "AUROBINDA OJHA",
                  font=fonts["h4"], fill=WHITE)
        draw.text((W-240, Y+58), "Cybersecurity Expert",
                  font=fonts["sm"], fill=P)
        draw.text((W-240, Y+78), "Independent Researcher",
                  font=fonts["sm"], fill=GRAY)
    else:
        draw.text((W-240, Y+35), "AUROBINDA OJHA",
                  font=fonts["h4"], fill=WHITE)
        draw.text((W-240, Y+58), "Cybersecurity Expert",
                  font=fonts["sm"], fill=P)

    Y += H_HEADER

    # ── TOP BADGES ────────────────────────────────────────────────────────
    rbox(draw, 0, Y, W, Y+H_BADGES, fill=(14,18,40))
    badges = data.get("top_badges",[])
    bw = W // max(len(badges),1)
    for i, badge in enumerate(badges[:4]):
        bx = i*bw + bw//2
        icon_name = badge.get("icon","shield")
        draw_icon(draw, icon_name, bx-24, Y+8, 20, P)
        draw.text((bx-10, Y+9), ft(badge.get("label",""),12),
                  font=fonts["sm"], fill=WHITE)
        if i < len(badges)-1:
            draw.line([(i+1)*bw, Y+10, (i+1)*bw, Y+H_BADGES-10],
                      fill=DARK_GRAY, width=1)
    Y += H_BADGES

    # ── TAGLINE ───────────────────────────────────────────────────────────
    rbox(draw, 0, Y, W, Y+H_TAGLINE, fill=(10,14,32))
    tagline = data.get("tagline","Protect. Detect. Respond. Secure.")
    cx_text(draw, tagline.upper(), W//2, Y+12,
            fonts["h5"], GRAY)
    Y += H_TAGLINE

    # ── GRID SECTIONS ─────────────────────────────────────────────────────
    sections = data.get("sections",[])[:9]

    for idx, section in enumerate(sections):
        col = idx % COLS
        row = idx // COLS
        cx  = CELL_PAD + col*(CELL_W+CELL_PAD)
        cy  = Y + CELL_PAD + row*(CELL_H+CELL_PAD)

        color = [P,S,H,(100,200,255),(180,255,120),
                 (255,150,80),(200,100,255),(80,220,180),(255,100,150)][idx%9]

        # Cell background
        rbox(draw, cx, cy, cx+CELL_W, cy+CELL_H,
             fill=BG2, outline=color, r=8, w=2)

        # Cell header bg
        rbox(draw, cx, cy, cx+CELL_W, cy+52,
             fill=C["D"] if "D" in C else BG3, r=8, w=0)
        draw.rectangle([(cx, cy+40),(cx+CELL_W, cy+52)],
                       fill=BG2)

        # Number badge
        draw.ellipse([(cx+10,cy+8),(cx+34,cy+32)], fill=color)
        num = str(section.get("number",idx+1))
        bbox = draw.textbbox((0,0), num, font=fonts["h5"])
        nw = bbox[2]-bbox[0]
        draw.text((cx+22-nw//2, cy+12), num,
                  font=fonts["h5"], fill=(0,0,0))

        # Icon
        icon_name = section.get("icon","shield")
        draw_icon(draw, icon_name, cx+CELL_W-42, cy+8, 28, color)

        # Section title
        title_text = ft(section.get("title","Section"),22)
        draw.text((cx+40, cy+10), title_text,
                  font=fonts["h5"], fill=color)

        # Divider
        draw.line([(cx+8, cy+52),(cx+CELL_W-8, cy+52)],
                  fill=DARK_GRAY, width=1)

        # Bullets
        by = cy+60
        for bullet in section.get("bullets",[])[:4]:
            if by+18 > cy+CELL_H-10:
                break
            # Bullet dot
            draw.ellipse([(cx+12,by+5),(cx+18,by+11)], fill=color)
            # Bullet text
            text_in_box(draw, ft(bullet,32),
                        cx+22, by, CELL_W-30, 20,
                        fonts["sm"], OFF_WHITE,
                        line_h=14, padding=2)
            by += 22

    Y += GRID_H

    # ── FOOTER ────────────────────────────────────────────────────────────
    # Dark footer bar
    draw.rectangle([(0,Y),(W,Y+H_FOOTER)], fill=(8,10,22))
    draw.rectangle([(0,Y),(W,Y+3)], fill=P)

    # Left — Profile small
    if profile_img is not None:
        small_prof = profile_img.resize((50,50), Image.LANCZOS)
        img_rgba = img.convert("RGBA")
        img_rgba.paste(small_prof, (15, Y+20), small_prof)
        img = img_rgba.convert("RGB")
        draw = ImageDraw.Draw(img)
        draw.ellipse([(13,Y+18),(67,Y+72)], outline=P, width=2)
        draw.text((75, Y+22), "AUROBINDA OJHA",
                  font=fonts["h5"], fill=WHITE)
        draw.text((75, Y+40), "Independent Researcher | Cybersecurity & Agentic AI",
                  font=fonts["xs"], fill=GRAY)
    else:
        draw.text((20, Y+20), "AUROBINDA OJHA",
                  font=fonts["h4"], fill=WHITE)

    # Center — Quote
    quote = data.get("bottom_quote","Secure AI. Protect the Future.")
    cx_text(draw, f'"{quote}"', W//2, Y+30,
            fonts["sm"], P)

    # Right — Social icons placeholder
    draw.text((W-280, Y+20), "Follow for more insights on",
              font=fonts["xs"], fill=GRAY)
    draw.text((W-280, Y+36), "Cybersecurity & Agentic AI",
              font=fonts["xs"], fill=GRAY)

    # LinkedIn icon
    rbox(draw, W-95, Y+20, W-55, Y+55,
         fill=(0,119,181), r=6, w=0)
    draw.text((W-88, Y+28), "in", font=fonts["h5"], fill=WHITE)

    # YouTube icon
    rbox(draw, W-48, Y+20, W-8, Y+55,
         fill=(200,0,0), r=6, w=0)
    draw.text((W-40, Y+28), "▶", font=fonts["h5"], fill=WHITE)

    # Bottom accent line
    draw.rectangle([(0,Y+H_FOOTER-3),(W,Y+H_FOOTER)], fill=P)

    img = img.crop((0, 0, W, TOTAL_H))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=96)
    buf.seek(0)
    print(f"Infographic created!")
    return buf.read()

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
    rj = r.json()
    upload_url = rj["value"]["uploadMechanism"][
        "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"][
        "uploadUrl"]
    asset = rj["value"]["asset"]
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
                "shareCommentary": {"text": content[:3000]},
                "shareMediaCategory": "IMAGE",
                "media": [{
                    "status": "READY",
                    "description": {
                        "text": data.get("main_title", subtopic)},
                    "media": asset,
                    "title": {
                        "text": data.get("main_title", subtopic)[:100]}
                }]
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
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
