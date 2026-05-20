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

# ── Colors ────────────────────────────────────────────────────────────────────
BG        = (8, 10, 20)
BG2       = (14, 18, 35)
BG3       = (20, 25, 48)
WHITE     = (255, 255, 255)
OFF_WHITE = (230, 235, 255)
GRAY      = (170, 175, 200)
DARK_GRAY = (45, 50, 75)

ACCENT_SETS = [
    {"P": (0,255,180),   "S": (0,180,255),  "H": (255,220,0)},
    {"P": (180,80,255),  "S": (255,50,150), "H": (255,220,0)},
    {"P": (50,220,255),  "S": (0,150,255),  "H": (255,150,50)},
    {"P": (50,255,150),  "S": (0,200,100),  "H": (255,220,0)},
    {"P": (255,120,120), "S": (220,60,60),  "H": (255,200,0)},
]

# ── AI ────────────────────────────────────────────────────────────────────────

def ai_generate_post(subtopic):
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content":
                "You are Aurobinda Ojha, Independent Researcher on Cybersecurity "
                "and Agentic AI. Write deep technical LinkedIn posts. "
                "NEVER use ##, **, __, or any markdown. Plain text + emojis only."},
            {"role": "user", "content":
                f"Write a detailed LinkedIn post about: {subtopic}\n\n"
                f"STRUCTURE:\n"
                f"1. Hook: start with emoji + title\n"
                f"2. 2-3 context lines\n"
                f"3. Problem list (5-6 emoji bullets)\n"
                f"4. Powerful insight line\n"
                f"5. Solution list (5 lightning emoji bullets)\n"
                f"6. Simple ASCII architecture with | arrows\n"
                f"7. Four sections with emoji header + bullet points\n"
                f"8. Goals (5-6 checkmark lines)\n"
                f"9. Preferred Stack line\n"
                f"10. Future vision\n"
                f"11. About me as Aurobinda Ojha + aurobindaojha@gmail.com\n"
                f"12. End with 12-15 relevant hashtags on the last line\n\n"
                f"NO markdown at all. Plain text + emojis only. 400-600 words.\n"
                f"Hashtags MUST be at the very end of the post text."}
        ],
        max_tokens=1500,
    )
    content = response.choices[0].message.content.strip()
    for ch in ["##","**","__","# ","* "]:
        content = content.replace(ch, "")
    return content

def ai_generate_infographic_data(subtopic):
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content":
                f"Create infographic data for: {subtopic}\n\n"
                f"Reply JSON only — very short text values:\n"
                f"{{\n"
                f"  \"main_title\": \"HOW I SECURE [TOPIC] (caps max 5 words)\",\n"
                f"  \"subtitle_pills\": [\"max 2 words\",\"max 2 words\",\"max 2 words\",\"max 2 words\",\"max 2 words\"],\n"
                f"  \"threats\": [\"max 2 words\",\"max 2 words\",\"max 2 words\",\"max 2 words\",\"max 2 words\",\"max 2 words\"],\n"
                f"  \"arch_layers\": [\n"
                f"    {{\"name\":\"max 4 words\",\"components\":[\"max 3 words\",\"max 3 words\",\"max 3 words\"]}}\n"
                f"  ],\n"
                f"  \"left_panel\": {{\n"
                f"    \"title\": \"ACCESS FLOW\",\n"
                f"    \"steps\": [\"max 3 words\",\"max 3 words\",\"max 3 words\",\"max 3 words\",\"max 3 words\"]\n"
                f"  }},\n"
                f"  \"right_panel\": {{\n"
                f"    \"title\": \"CONTROLS\",\n"
                f"    \"items\": [\"max 3 words\",\"max 3 words\",\"max 3 words\",\"max 3 words\",\"max 3 words\"]\n"
                f"  }},\n"
                f"  \"security_layer\": {{\n"
                f"    \"title\": \"AUTONOMOUS PROTECTION LAYER\",\n"
                f"    \"components\": [\"max 2 words\",\"max 2 words\",\"max 2 words\",\"max 2 words\",\"max 2 words\"]\n"
                f"  }},\n"
                f"  \"goals\": [\"max 3 words\",\"max 3 words\",\"max 3 words\",\"max 3 words\",\"max 3 words\",\"max 3 words\"],\n"
                f"  \"stack\": [\"max 2 words\",\"max 2 words\",\"max 2 words\",\"max 2 words\",\"max 2 words\",\"max 2 words\",\"max 2 words\",\"max 2 words\"],\n"
                f"  \"why_works\": [\"max 5 words\",\"max 5 words\",\"max 5 words\",\"max 5 words\",\"max 5 words\"],\n"
                f"  \"principles\": [\"max 3 words\",\"max 3 words\",\"max 3 words\",\"max 3 words\",\"max 3 words\"]\n"
                f"}}\n\n"
                f"arch_layers: exactly 5. All text VERY SHORT as specified."}
        ],
        max_tokens=1000,
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
            "h1":   ImageFont.truetype(B, 48),
            "h2":   ImageFont.truetype(B, 32),
            "h3":   ImageFont.truetype(B, 22),
            "h4":   ImageFont.truetype(B, 17),
            "body": ImageFont.truetype(R, 15),
            "sm":   ImageFont.truetype(R, 13),
        }
    except:
        d = ImageFont.load_default()
        return {k: d for k in ["h1","h2","h3","h4","body","sm"]}

# ── Draw Helpers ──────────────────────────────────────────────────────────────

def rbox(draw, x0, y0, x1, y1, fill=None, outline=None, r=8, w=2):
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

def arrow_down(draw, x, y, color, size=10):
    draw.line([(x,y),(x,y+size)], fill=color, width=2)
    draw.polygon([(x-5,y+size),(x+5,y+size),(x,y+size+8)], fill=color)

# ── Infographic ───────────────────────────────────────────────────────────────

def create_infographic(subtopic, data):
    print(f"[{datetime.now()}] Creating infographic...")

    W     = 1080
    seed  = get_seed(subtopic)
    C     = ACCENT_SETS[seed % len(ACCENT_SETS)]
    P, S, H = C["P"], C["S"], C["H"]
    fonts = load_fonts()

    H_HDR    = 155
    H_PILLS  = 35
    H_THREAT = 70
    H_3COL   = 750
    H_SECLYR = 105
    H_BOTTOM = 230
    H_FOOTER = 80
    TOTAL_H  = (H_HDR+H_PILLS+H_THREAT+H_3COL+
                H_SECLYR+H_BOTTOM+H_FOOTER+20)

    img  = Image.new("RGB", (W, TOTAL_H), BG)
    draw = ImageDraw.Draw(img)

    # Gradient BG
    for y in range(TOTAL_H):
        t = y/TOTAL_H
        draw.line([(0,y),(W,y)], fill=(
            int(BG[0]+t*8), int(BG[1]+t*8), int(BG[2]+t*15)))

    # Grid
    for x in range(0, W, 55):
        draw.line([(x,0),(x,TOTAL_H)], fill=(14,17,32), width=1)
    for y in range(0, TOTAL_H, 55):
        draw.line([(0,y),(W,y)], fill=(14,17,32), width=1)

    Y = 0

    # ── HEADER ────────────────────────────────────────────────────────────
    for y in range(H_HDR):
        t = y/H_HDR
        r = int(max(P[0],S[0])*0.4*(1-t)+min(P[0],S[0])*t)
        g = int(max(P[1],S[1])*0.4*(1-t)+min(P[1],S[1])*t)
        b = int(max(P[2],S[2])*0.4*(1-t)+min(P[2],S[2])*t)
        draw.line([(0,y),(W,y)], fill=(
            max(0,min(255,r)),max(0,min(255,g)),max(0,min(255,b))))

    cx_text(draw, "✦  AUROBINDA OJHA  ✦", W//2, Y+6, fonts["body"], WHITE)

    title = data.get("main_title","HOW I SECURE AI SYSTEMS")
    words = title.split()
    mid   = max(1, len(words)//2)
    l1    = " ".join(words[:mid])
    l2    = " ".join(words[mid:])

    cx_text(draw, l1, W//2, Y+28, fonts["h1"], WHITE)

    ws = l2.split()
    bb2 = draw.textbbox((0,0), l2, font=fonts["h1"])
    tw2 = bb2[2]-bb2[0]
    if len(ws) >= 2:
        a  = " ".join(ws[:len(ws)//2])
        b_ = " ".join(ws[len(ws)//2:])
        bba = draw.textbbox((0,0), a+" ", font=fonts["h1"])
        xa  = (W-tw2)//2
        draw.text((xa, Y+82), a, font=fonts["h1"], fill=P)
        draw.text((xa+bba[2]-bba[0], Y+82), " "+b_,
                  font=fonts["h1"], fill=H)
    else:
        cx_text(draw, l2, W//2, Y+82, fonts["h1"], P)

    Y += H_HDR

    # ── PILLS ─────────────────────────────────────────────────────────────
    pills  = data.get("subtitle_pills",[])
    pill_x = 30
    for pill in pills[:5]:
        bb = draw.textbbox((0,0), pill, font=fonts["sm"])
        pw = bb[2]-bb[0]+20
        rbox(draw, pill_x, Y+5, pill_x+pw, Y+28,
             fill=(25,30,55), outline=P, r=12, w=1)
        draw.text((pill_x+10, Y+8), pill,
                  font=fonts["sm"], fill=OFF_WHITE)
        pill_x += pw+8
    Y += H_PILLS

    # ── THREATS ───────────────────────────────────────────────────────────
    rbox(draw, 0, Y, W, Y+H_THREAT, fill=(16,20,40))
    cx_text(draw, "▸  TOP SECURITY THREATS  ◂",
            W//2, Y+5, fonts["sm"], P)

    threats = data.get("threats",[])[:6]
    tw3 = (W-40) // max(len(threats),1)
    for i, t in enumerate(threats):
        tx = 20+i*tw3
        rbox(draw, tx, Y+22, tx+tw3-6, Y+H_THREAT-4,
             fill=(22,27,50), outline=P, r=6, w=1)
        text_in_box(draw, ft(t,14), tx, Y+22,
                    tw3-6, H_THREAT-26,
                    fonts["sm"], WHITE, line_h=14, padding=5)
    Y += H_THREAT

    # ── 3-COLUMN ──────────────────────────────────────────────────────────
    LW     = 178
    RW     = 178
    MW     = W - LW - RW - 18
    LX     = 8
    MX     = LX+LW+5
    RX     = MX+MW+5
    COL_H  = H_3COL
    arch_y = Y

    # LEFT — Access Flow
    rbox(draw, LX, arch_y, LX+LW, arch_y+COL_H,
         fill=BG2, outline=P, r=8, w=1)
    draw.text((LX+8, arch_y+7),
              data.get("left_panel",{}).get("title","ACCESS FLOW"),
              font=fonts["h4"], fill=P)
    draw.line([(LX+6,arch_y+26),(LX+LW-6,arch_y+26)],
              fill=DARK_GRAY)

    sy = arch_y+32
    for step in data.get("left_panel",{}).get("steps",[])[:6]:
        rbox(draw, LX+6, sy, LX+LW-6, sy+38,
             fill=BG3, outline=DARK_GRAY, r=5, w=1)
        text_in_box(draw, ft(step,20), LX+6, sy,
                    LW-12, 38, fonts["sm"], WHITE,
                    line_h=13, padding=5)
        sy += 44
        if sy < arch_y+COL_H-40:
            arrow_down(draw, LX+LW//2, sy-6, P, size=6)

    # LEFT — Principles
    pr_y = arch_y+COL_H+5
    rbox(draw, LX, pr_y, LX+LW, pr_y+185,
         fill=BG2, outline=S, r=8, w=1)
    draw.text((LX+8, pr_y+7), "PRINCIPLES",
              font=fonts["h4"], fill=S)
    draw.line([(LX+6,pr_y+26),(LX+LW-6,pr_y+26)], fill=DARK_GRAY)
    py3 = pr_y+32
    for pr in data.get("principles",[])[:5]:
        draw.text((LX+8, py3), f"◆ {ft(pr,22)}",
                  font=fonts["sm"], fill=OFF_WHITE)
        py3 += 22

    # RIGHT — Controls
    rbox(draw, RX, arch_y, RX+RW, arch_y+COL_H,
         fill=BG2, outline=H, r=8, w=1)
    draw.text((RX+8, arch_y+7),
              data.get("right_panel",{}).get("title","CONTROLS"),
              font=fonts["h4"], fill=H)
    draw.line([(RX+6,arch_y+26),(RX+RW-6,arch_y+26)], fill=DARK_GRAY)
    ri_y = arch_y+32
    for item in data.get("right_panel",{}).get("items",[])[:6]:
        rbox(draw, RX+6, ri_y, RX+RW-6, ri_y+55,
             fill=BG3, outline=H, r=5, w=1)
        text_in_box(draw, ft(item,22), RX+6, ri_y,
                    RW-12, 55, fonts["sm"], WHITE,
                    line_h=14, padding=6)
        ri_y += 62

    # RIGHT — Goals
    go_y = arch_y+COL_H+5
    rbox(draw, RX, go_y, RX+RW, go_y+185,
         fill=BG2, outline=H, r=8, w=1)
    draw.text((RX+8, go_y+7), "GOALS",
              font=fonts["h4"], fill=H)
    draw.line([(RX+6,go_y+26),(RX+RW-6,go_y+26)], fill=DARK_GRAY)
    gy2 = go_y+32
    for goal in data.get("goals",[])[:6]:
        draw.text((RX+8, gy2), f"✓  {ft(goal,22)}",
                  font=fonts["sm"], fill=OFF_WHITE)
        gy2 += 22

    # CENTER — Architecture
    rbox(draw, MX, arch_y, MX+MW, arch_y+COL_H,
         fill=BG2, outline=S, r=8, w=1)
    cx_text(draw, "PRODUCTION INFRASTRUCTURE",
            MX+MW//2, arch_y+7, fonts["h4"], S)
    draw.line([(MX+6,arch_y+26),(MX+MW-6,arch_y+26)], fill=DARK_GRAY)

    layers    = data.get("arch_layers",[])
    lyr_h     = (COL_H-36) // max(len(layers),1) - 6
    lyr_y     = arch_y+32
    lyr_cols  = [P,S,H,(100,210,255),(180,255,120)]
    for idx, layer in enumerate(layers[:5]):
        lc = lyr_cols[idx%5]
        rbox(draw, MX+6, lyr_y, MX+MW-6, lyr_y+lyr_h,
             fill=(14,19,38), outline=lc, r=6, w=1)
        draw.text((MX+12, lyr_y+5),
                  ft(layer.get("name",""),28),
                  font=fonts["h4"], fill=lc)
        comps = layer.get("components",[])
        draw.text((MX+12, lyr_y+24),
                  "  •  ".join(ft(c,14) for c in comps[:3]),
                  font=fonts["sm"], fill=OFF_WHITE)
        lyr_y += lyr_h+6
        if idx < len(layers)-1:
            arrow_down(draw, MX+MW//2, lyr_y-4, S, size=5)
            lyr_y += 6

    Y += COL_H

    # ── SECURITY LAYER ────────────────────────────────────────────────────
    rbox(draw, 8, Y, W-8, Y+H_SECLYR,
         fill=(14,18,38), outline=P, r=8, w=2)
    sl = data.get("security_layer",{})
    cx_text(draw, sl.get("title","AUTONOMOUS PROTECTION"),
            W//2, Y+7, fonts["h4"], P)
    draw.line([(16,Y+26),(W-16,Y+26)], fill=DARK_GRAY)

    sc  = sl.get("components",[])[:5]
    scw = (W-30) // max(len(sc),1)
    for i, comp in enumerate(sc):
        sx2 = 15+i*scw
        rbox(draw, sx2+2, Y+32, sx2+scw-4, Y+H_SECLYR-6,
             fill=(20,26,52), outline=S, r=6, w=1)
        text_in_box(draw, ft(comp,12), sx2+2, Y+32,
                    scw-6, H_SECLYR-38,
                    fonts["sm"], WHITE, line_h=14, padding=6)
    Y += H_SECLYR+5

    # ── BOTTOM 3 BOXES ────────────────────────────────────────────────────
    BW   = (W-25)//3
    BX1  = 8
    BX2  = BX1+BW+5
    BX3  = BX2+BW+5
    BH   = H_BOTTOM

    # Stack
    rbox(draw, BX1, Y, BX1+BW, Y+BH,
         fill=BG2, outline=DARK_GRAY, r=8)
    draw.text((BX1+10, Y+8), "🔥 PREFERRED STACK",
              font=fonts["h4"], fill=H)
    draw.line([(BX1+8,Y+27),(BX1+BW-8,Y+27)], fill=DARK_GRAY)
    bsx = BX1+10
    bsy = Y+34
    for tech in data.get("stack",[])[:10]:
        bb  = draw.textbbox((0,0), tech, font=fonts["sm"])
        bw2 = bb[2]-bb[0]+12
        if bsx+bw2 > BX1+BW-8:
            bsx = BX1+10
            bsy += 26
        if bsy+22 > Y+BH-8:
            break
        rbox(draw, bsx, bsy, bsx+bw2, bsy+20,
             fill=(22,28,55), outline=P, r=4, w=1)
        draw.text((bsx+6, bsy+3), tech,
                  font=fonts["sm"], fill=P)
        bsx += bw2+5

    # Why Works
    rbox(draw, BX2, Y, BX2+BW, Y+BH,
         fill=BG2, outline=DARK_GRAY, r=8)
    draw.text((BX2+10, Y+8), "✅ WHY THIS WORKS",
              font=fonts["h4"], fill=P)
    draw.line([(BX2+8,Y+27),(BX2+BW-8,Y+27)], fill=DARK_GRAY)
    wy2 = Y+34
    for reason in data.get("why_works",[])[:5]:
        if wy2+18 > Y+BH-8:
            break
        text_in_box(draw, f"✓  {ft(reason,30)}",
                    BX2, wy2, BW, 22,
                    fonts["sm"], OFF_WHITE,
                    line_h=15, padding=10)
        wy2 += 28

    # About Me
    rbox(draw, BX3, Y, BX3+BW, Y+BH,
         fill=BG2, outline=DARK_GRAY, r=8)
    draw.text((BX3+10, Y+8), "👤 ABOUT ME",
              font=fonts["h4"], fill=S)
    draw.line([(BX3+8,Y+27),(BX3+BW-8,Y+27)], fill=DARK_GRAY)
    draw.ellipse([(BX3+BW//2-28,Y+34),(BX3+BW//2+28,Y+90)],
                 outline=S, width=2, fill=BG3)
    cx_text(draw, "AO", BX3+BW//2, Y+50, fonts["h3"], S)
    draw.text((BX3+10, Y+98), "Aurobinda Ojha",
              font=fonts["h4"], fill=WHITE)
    draw.text((BX3+10, Y+118), "Independent Researcher",
              font=fonts["sm"], fill=GRAY)
    draw.text((BX3+10, Y+135), "Cybersecurity & Agentic AI",
              font=fonts["sm"], fill=GRAY)
    rl_y = Y+158
    rl_x = BX3+10
    for role in ["Cybersecurity","Agentic AI","LLMOps"]:
        bb  = draw.textbbox((0,0), role, font=fonts["sm"])
        rw2 = bb[2]-bb[0]+10
        if rl_x+rw2 > BX3+BW-8:
            rl_x = BX3+10
            rl_y += 22
        if rl_y+20 > Y+BH-8:
            break
        rbox(draw, rl_x, rl_y, rl_x+rw2, rl_y+18,
             fill=(20,26,52), outline=S, r=4, w=1)
        draw.text((rl_x+5, rl_y+2), role,
                  font=fonts["sm"], fill=S)
        rl_x += rw2+5

    Y += BH+5

    # ── FOOTER ────────────────────────────────────────────────────────────
    draw.rectangle([(0,Y),(W,Y+3)], fill=P)
    Y += 5
    rbox(draw, 8, Y, W-8, Y+65,
         fill=(12,15,32), outline=DARK_GRAY, r=8)
    draw.text((20, Y+10),
              "🛡️  LET'S BUILD SECURE AI INFRASTRUCTURE TOGETHER!",
              font=fonts["h4"], fill=WHITE)
    draw.text((20, Y+34), "📩  aurobindaojha@gmail.com",
              font=fonts["body"], fill=P)
    cx_text(draw, datetime.now().strftime("%B %d, %Y"),
            W-120, Y+42, fonts["sm"], GRAY)
    Y += 75

    img = img.crop((0, 0, W, Y))
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
