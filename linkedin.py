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
    "https://media.licdn.com/dms/image/v2/D5603AQHeZYPrmMcLGQ/"
    "profile-displayphoto-crop_800_800/B56Z5UeqHWJIAI-/0/1779533785179"
    "?e=1781136000&v=beta&t=PC4Iz_0gJfRN1A3MfE_WQLMabqdc6enCTApyw-LBbSg"
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

HASHTAG_SETS = {
    "Prompt Injection": "#PromptInjection #AIAgents #LLMSecurity #AgenticAI #Cybersecurity #AIAttacks #PromptHacking #ZeroTrust #AISecurity #MLOps #DevSecOps #CloudSecurity #AIResearch #ThreatDetection #InfoSec",
    "Zero Trust":       "#ZeroTrust #ZeroTrustSecurity #IAM #AgenticAI #Cybersecurity #CloudSecurity #NetworkSecurity #AISecurity #DevSecOps #MLOps #ZeroTrustArchitecture #IdentitySecurity #InfoSec #AIResearch #SecurityArchitecture",
    "default":          "#AgenticAI #Cybersecurity #AISecurity #LLMOps #AIOps #MLOps #AIAgents #ZeroTrust #ThreatDetection #DevSecOps #CloudSecurity #InfoSec #AIResearch #MachineLearning #SecurityOps",
}

def get_hashtags(subtopic):
    for key in HASHTAG_SETS:
        if key.lower() in subtopic.lower():
            return HASHTAG_SETS[key]
    return HASHTAG_SETS["default"]

def get_daily_topic():
    day = datetime.now().timetuple().tm_yday
    return DAILY_TOPICS[day % len(DAILY_TOPICS)]

def get_seed(text):
    return int(hashlib.md5(text.encode()).hexdigest(), 16)

def ft(text, n):
    text = str(text).strip()
    return text if len(text) <= n else text[:n-2]+".."

def text_in_box(draw, text, x, y, max_w, max_h, font, color,
                line_h=15, padding=3):
    text = str(text).strip()
    chars = max(1, (max_w-padding*2) // 7)
    lines = textwrap.fill(text, width=chars).split('\n')
    cy = y + padding
    for line in lines:
        if cy + line_h > y + max_h - padding:
            break
        draw.text((x+padding, cy), line, font=font, fill=color)
        cy += line_h

# ── Icons ─────────────────────────────────────────────────────────────────────

def draw_icon(draw, name, cx, cy, size, color):
    s = size
    x = cx - s//2
    y = cy - s//2
    if name == "shield":
        pts = [(cx,y),(x+s,y+s//3),(x+s,y+s*2//3),(cx,y+s),(x,y+s*2//3),(x,y+s//3)]
        draw.polygon(pts, outline=color, width=2)
    elif name == "brain":
        draw.ellipse([(x,y+s//4),(x+s,y+s*3//4)], outline=color, width=2)
        draw.line([(cx,y+s//4),(cx,y+s*3//4)], fill=color, width=1)
        draw.arc([(x+s//4,y),(x+s*3//4,y+s//2)], 180, 0, fill=color, width=2)
    elif name == "lock":
        draw.rectangle([(x+s//4,cy),(x+s*3//4,y+s)], outline=color, width=2)
        draw.arc([(x+s//4,y),(x+s*3//4,cy+s//6)], 180, 0, fill=color, width=2)
        draw.ellipse([(cx-3,cy+s//6-3),(cx+3,cy+s//6+3)], fill=color)
    elif name == "eye":
        draw.arc([(x,y+s//4),(x+s,y+s*3//4)], 0, 180, fill=color, width=2)
        draw.arc([(x,y+s//4),(x+s,y+s*3//4)], 180, 360, fill=color, width=2)
        draw.ellipse([(cx-s//6,cy-s//6),(cx+s//6,cy+s//6)], fill=color)
    elif name == "network":
        draw.ellipse([(cx-4,cy-4),(cx+4,cy+4)], fill=color)
        for ang in [0,72,144,216,288]:
            rad = math.radians(ang)
            ex = int(cx+s//2*math.cos(rad))
            ey = int(cy+s//2*math.sin(rad))
            draw.line([(cx,cy),(ex,ey)], fill=color, width=1)
            draw.ellipse([(ex-3,ey-3),(ex+3,ey+3)], fill=color)
    elif name == "warning":
        draw.polygon([(cx,y),(x+s,y+s),(x,y+s)], outline=color, width=2)
        draw.line([(cx,y+s//3),(cx,y+s*2//3)], fill=color, width=2)
        draw.ellipse([(cx-2,y+s*3//4-2),(cx+2,y+s*3//4+2)], fill=color)
    elif name == "gear":
        draw.ellipse([(cx-s//4,cy-s//4),(cx+s//4,cy+s//4)], outline=color, width=2)
        for ang in range(0,360,60):
            rad = math.radians(ang)
            x1 = int(cx+s//4*math.cos(rad)); y1 = int(cy+s//4*math.sin(rad))
            x2 = int(cx+s//2*math.cos(rad)); y2 = int(cy+s//2*math.sin(rad))
            draw.line([(x1,y1),(x2,y2)], fill=color, width=3)
    elif name == "check":
        draw.ellipse([(x,y),(x+s,y+s)], outline=color, width=2)
        draw.line([(x+s//4,cy),(x+s*2//5,y+s*2//3),(x+s*3//4,y+s//3)],
                  fill=color, width=2)
    elif name == "search":
        draw.ellipse([(x,y),(x+s*2//3,y+s*2//3)], outline=color, width=2)
        draw.line([(x+s*2//3-3,y+s*2//3-3),(x+s,y+s)], fill=color, width=3)
    elif name == "monitor":
        draw.rectangle([(x,y),(x+s,y+s*3//4)], outline=color, width=2)
        draw.line([(cx,y+s*3//4),(cx,y+s)], fill=color, width=2)
        draw.line([(x+s//4,y+s),(x+s*3//4,y+s)], fill=color, width=2)
    elif name == "robot":
        draw.rectangle([(x+s//4,y),(x+s*3//4,y+s//3)], outline=color, width=2)
        draw.rectangle([(x+s//6,y+s//3),(x+s*5//6,y+s*5//6)],
                       outline=color, width=2)
        draw.ellipse([(cx-s//4-3,y+s//6-3),(cx-s//4+3,y+s//6+3)], fill=color)
        draw.ellipse([(cx+s//4-3,y+s//6-3),(cx+s//4+3,y+s//6+3)], fill=color)
    elif name == "database":
        draw.ellipse([(x,y),(x+s,y+s//4)], outline=color, width=2)
        draw.line([(x,y+s//8),(x,y+s*3//4)], fill=color, width=2)
        draw.line([(x+s,y+s//8),(x+s,y+s*3//4)], fill=color, width=2)
        draw.arc([(x,y+s//2),(x+s,y+s)], 0, 180, fill=color, width=2)
        draw.arc([(x,y+s//4),(x+s,y+s*5//8)], 0, 180, fill=color, width=2)

# ── Colors ────────────────────────────────────────────────────────────────────
BG        = (8, 12, 28)
BG2       = (13, 17, 38)
BG3       = (18, 24, 52)
WHITE     = (255, 255, 255)
OFF_WHITE = (215, 225, 255)
GRAY      = (150, 160, 195)
DARK_GRAY = (38, 45, 78)

ACCENT_SETS = [
    {"P":(0,200,255),  "S":(0,255,180), "H":(255,220,0)},
    {"P":(180,80,255), "S":(255,50,150),"H":(255,220,0)},
    {"P":(50,220,255), "S":(0,180,255), "H":(255,150,50)},
    {"P":(50,255,150), "S":(0,220,120), "H":(255,220,0)},
    {"P":(255,130,50), "S":(220,80,0),  "H":(255,220,0)},
]

CELL_COLORS = [
    (0,200,255),(0,255,180),(255,220,0),
    (180,80,255),(255,150,50),(50,220,255),
    (50,255,150),(255,100,150),(100,200,100),
]

# ── AI ────────────────────────────────────────────────────────────────────────

def ai_generate_post(subtopic):
    hashtags = get_hashtags(subtopic)
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
                f"6. ASCII architecture with | arrows\n"
                f"7. Four technical sections with emoji headers\n"
                f"8. Goals (5-6 checkmarks)\n"
                f"9. Preferred Stack\n"
                f"10. Future vision\n\n"
                f"STRICT RULES:\n"
                f"- NO about me, NO contact info\n"
                f"- NO markdown at all\n"
                f"- Plain text + emojis only\n"
                f"- 400-500 words\n\n"
                f"After the post content add EXACTLY this hashtag line:\n"
                f"{hashtags}"}
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
    content = '\n'.join(lines).strip()
    # Ensure hashtags at end
    if hashtags.split()[0] not in content:
        content = content + "\n\n" + hashtags
    return content

def ai_generate_infographic_data(subtopic):
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content":
                f"Create infographic data for: {subtopic}\n\n"
                f"Reply JSON only:\n"
                f"{{\n"
                f"  \"main_title\": \"TOPIC COMPLETE DEEP DIVE (caps max 5 words)\",\n"
                f"  \"tagline\": \"tagline max 8 words\",\n"
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
                f"      \"bullets\": [\"max 4 words\",\"max 4 words\",\"max 4 words\",\"max 4 words\"]\n"
                f"    }}\n"
                f"  ],\n"
                f"  \"bottom_quote\": \"Powerful closing quote max 10 words\"\n"
                f"}}\n\n"
                f"Exactly 9 sections. Each has exactly 4 short bullets.\n"
                f"Make everything specific to {subtopic}."}
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
            "h5":   ImageFont.truetype(B, 14),
            "body": ImageFont.truetype(R, 14),
            "sm":   ImageFont.truetype(R, 12),
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

def load_profile_image(size=110):
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

# ── Infographic ───────────────────────────────────────────────────────────────

def create_infographic(subtopic, data):
    print(f"[{datetime.now()}] Creating infographic...")

    W       = 1080
    seed    = get_seed(subtopic)
    C       = ACCENT_SETS[seed % len(ACCENT_SETS)]
    P, S, H = C["P"], C["S"], C["H"]
    fonts   = load_fonts()

    profile_img = load_profile_image(size=120)

    COLS    = 3
    ROWS    = 3
    PAD     = 8
    CELL_W  = (W - (COLS+1)*PAD) // COLS
    CELL_H  = 290
    GRID_H  = ROWS*CELL_H + (ROWS+1)*PAD

    H_HDR   = 190
    H_BADGE = 55
    H_TAG   = 38
    H_FOOT  = 85
    TOTAL_H = H_HDR+H_BADGE+H_TAG+GRID_H+H_FOOT

    img  = Image.new("RGB", (W, TOTAL_H), BG)
    draw = ImageDraw.Draw(img)

    # BG gradient
    for y in range(TOTAL_H):
        t = y/TOTAL_H
        draw.line([(0,y),(W,y)], fill=(
            int(BG[0]+t*5), int(BG[1]+t*5), int(BG[2]+t*8)))

    # Grid
    for x in range(0, W, 45):
        draw.line([(x,0),(x,TOTAL_H)], fill=(13,17,38), width=1)
    for y in range(0, TOTAL_H, 45):
        draw.line([(0,y),(W,y)], fill=(13,17,38), width=1)

    Y = 0

    # ── HEADER ────────────────────────────────────────────────────────────
    # Gradient
    for y in range(H_HDR):
        t = y/H_HDR
        r = int(P[0]*0.5*(1-t)+BG[0]*t)
        g = int(P[1]*0.5*(1-t)+BG[1]*t)
        b = int(P[2]*0.5*(1-t)+BG[2]*t)
        draw.line([(0,Y+y),(W,Y+y)], fill=(
            max(0,min(255,r)),max(0,min(255,g)),max(0,min(255,b))))

    # Profile image — top right, no overlap with text
    PROF_SIZE = 120
    PROF_X    = W - PROF_SIZE - 20
    PROF_Y    = Y + 20

    if profile_img is not None:
        img_rgba = img.convert("RGBA")
        img_rgba.paste(profile_img, (PROF_X, PROF_Y), profile_img)
        img = img_rgba.convert("RGB")
        draw = ImageDraw.Draw(img)
        # Accent ring
        draw.ellipse([
            (PROF_X-4, PROF_Y-4),
            (PROF_X+PROF_SIZE+4, PROF_Y+PROF_SIZE+4)
        ], outline=P, width=3)

    # Name block — directly below photo, right aligned
    name_x = PROF_X - 10
    draw.text((name_x, PROF_Y+PROF_SIZE+8),
              "AUROBINDA OJHA",
              font=fonts["h5"], fill=WHITE)
    draw.text((name_x, PROF_Y+PROF_SIZE+26),
              "Cybersecurity Expert",
              font=fonts["xs"], fill=P)

    # Title — LEFT side only, safe from photo
    # Keep title width limited to avoid photo overlap
    title_max_w = PROF_X - 30
    title = data.get("main_title","AI SECURITY DEEP DIVE")
    words = title.split()
    mid   = max(1, len(words)//2)
    l1    = " ".join(words[:mid])
    l2    = " ".join(words[mid:])

    # Truncate if title too long
    while draw.textbbox((0,0),l1,font=fonts["h1"])[2] > title_max_w:
        l1 = l1[:max(5,len(l1)-3)]+".."
        break
    while draw.textbbox((0,0),l2,font=fonts["h1"])[2] > title_max_w:
        l2 = l2[:max(5,len(l2)-3)]+".."
        break

    draw.text((18, Y+18), l1, font=fonts["h1"], fill=WHITE)
    draw.text((18, Y+75), l2, font=fonts["h1"], fill=P)

    # Underline
    bb = draw.textbbox((0,0), l2, font=fonts["h1"])
    draw.rectangle([(18,Y+130),(18+min(bb[2]-bb[0]+30,title_max_w),Y+134)],
                   fill=H)

    draw.text((20, Y+142), "CYBERSECURITY RESEARCHER & AGENTIC AI EXPERT",
              font=fonts["xs"], fill=GRAY)

    Y += H_HDR

    # ── BADGES ────────────────────────────────────────────────────────────
    rbox(draw, 0, Y, W, Y+H_BADGE, fill=(13,17,40))
    badges = data.get("top_badges",[])[:4]
    bw = W // max(len(badges),1)
    for i, badge in enumerate(badges):
        bcx = i*bw + bw//2
        icon_cx = bcx - 40
        text_x  = bcx - 20

        # Icon — centered in its own space, NOT overlapping label
        draw_icon(draw, badge.get("icon","shield"),
                  icon_cx, Y+H_BADGE//2, 18, P)

        # Label — to the right of icon
        draw.text((text_x, Y+H_BADGE//2-7),
                  ft(badge.get("label",""),14),
                  font=fonts["sm"], fill=WHITE)

        if i < len(badges)-1:
            draw.line([((i+1)*bw, Y+10),((i+1)*bw, Y+H_BADGE-10)],
                      fill=DARK_GRAY, width=1)
    Y += H_BADGE

    # ── TAGLINE ───────────────────────────────────────────────────────────
    rbox(draw, 0, Y, W, Y+H_TAG, fill=(10,13,32))
    tagline = data.get("tagline","Protect. Detect. Respond. Secure.")
    cx_text(draw, tagline.upper(), W//2, Y+11, fonts["xs"], GRAY)
    Y += H_TAG

    # ── GRID ──────────────────────────────────────────────────────────────
    sections = data.get("sections",[])[:9]

    for idx, section in enumerate(sections):
        col = idx % COLS
        row = idx // COLS
        cx  = PAD + col*(CELL_W+PAD)
        cy  = Y + PAD + row*(CELL_H+PAD)
        color = CELL_COLORS[idx % len(CELL_COLORS)]

        # Cell
        rbox(draw, cx, cy, cx+CELL_W, cy+CELL_H,
             fill=BG2, outline=color, r=8, w=2)

        # Header zone — number + title only (NO icon here)
        rbox(draw, cx, cy, cx+CELL_W, cy+48,
             fill=BG3, r=8, w=0)
        draw.rectangle([(cx,cy+38),(cx+CELL_W,cy+48)], fill=BG2)

        # Number badge
        draw.ellipse([(cx+8,cy+8),(cx+30,cy+30)], fill=color)
        num = str(section.get("number",idx+1))
        bbox = draw.textbbox((0,0), num, font=fonts["h5"])
        nw = bbox[2]-bbox[0]
        draw.text((cx+19-nw//2, cy+12), num,
                  font=fonts["h5"], fill=(0,0,0))

        # Section title — next to number, clear of icon area
        title_text = ft(section.get("title","Section"), 24)
        draw.text((cx+38, cy+12), title_text,
                  font=fonts["h5"], fill=color)

        # Icon — BELOW header, in its own dedicated row
        ICON_ROW_Y = cy+50
        draw_icon(draw, section.get("icon","shield"),
                  cx+CELL_W//2, ICON_ROW_Y+16, 24, color)

        # Divider below icon
        draw.line([(cx+8, ICON_ROW_Y+36),(cx+CELL_W-8, ICON_ROW_Y+36)],
                  fill=DARK_GRAY, width=1)

        # Bullets — start AFTER icon row
        by = ICON_ROW_Y + 44
        for bullet in section.get("bullets",[])[:4]:
            if by+16 > cy+CELL_H-8:
                break
            # Bullet dot
            draw.ellipse([(cx+10,by+4),(cx+16,by+10)], fill=color)
            # Bullet text — strictly within cell width
            text_in_box(draw, ft(bullet,30),
                        cx+20, by, CELL_W-28, 18,
                        fonts["sm"], OFF_WHITE,
                        line_h=14, padding=2)
            by += 20

    Y += GRID_H

    # ── FOOTER ────────────────────────────────────────────────────────────
    draw.rectangle([(0,Y),(W,Y+H_FOOT)], fill=(7,9,22))
    draw.rectangle([(0,Y),(W,Y+3)], fill=P)

    # Small profile photo in footer
    if profile_img is not None:
        small = profile_img.resize((48,48), Image.LANCZOS)
        img_rgba = img.convert("RGBA")
        img_rgba.paste(small, (15, Y+18), small)
        img = img_rgba.convert("RGB")
        draw = ImageDraw.Draw(img)
        draw.ellipse([(13,Y+16),(65,Y+68)], outline=P, width=2)
        draw.text((72, Y+22), "AUROBINDA OJHA",
                  font=fonts["h5"], fill=WHITE)
        draw.text((72, Y+40), "Independent Researcher | Cybersecurity & Agentic AI",
                  font=fonts["xs"], fill=GRAY)
    else:
        draw.text((20, Y+20), "AUROBINDA OJHA", font=fonts["h4"], fill=WHITE)

    # Quote
    quote = data.get("bottom_quote","Secure AI. Protect the Future.")
    cx_text(draw, f'"{ft(quote,55)}"', W//2, Y+30, fonts["sm"], P)

    # Social buttons
    rbox(draw, W-100, Y+22, W-58, Y+56,
         fill=(0,119,181), r=6, w=0)
    cx_text(draw, "in", W-79, Y+30, fonts["h5"], WHITE)

    rbox(draw, W-52, Y+22, W-10, Y+56,
         fill=(200,0,0), r=6, w=0)
    cx_text(draw, "▶", W-31, Y+30, fonts["h5"], WHITE)

    draw.rectangle([(0,Y+H_FOOT-3),(W,Y+H_FOOT)], fill=P)

    img = img.crop((0, 0, W, TOTAL_H))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=96)
    buf.seek(0)
    print("Infographic created!")
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
