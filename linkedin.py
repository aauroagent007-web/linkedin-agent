import openai
import requests
import os
import textwrap
import json
import hashlib
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import subprocess
import tempfile

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

AGENT_PERSONA = """You are Aurobinda Ojha, an Independent Researcher on Cybersecurity
and Agentic AI. You write sharp, punchy LinkedIn posts with short lines and emojis.
Your style is direct, conversational and thought provoking.
You use line breaks between thoughts. You add emojis to key points.
Plain text only. No markdown. Short sentences. Max 150 words."""

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

PANEL_COLORS = [
    (0, 255, 200),
    (255, 220, 0),
    (180, 80, 255),
    (50, 255, 150),
    (255, 150, 50),
    (255, 100, 200),
]

def get_daily_topic():
    day = datetime.now().timetuple().tm_yday
    return DAILY_TOPICS[day % len(DAILY_TOPICS)]

def get_seed(text):
    return int(hashlib.md5(text.encode()).hexdigest(), 16)

def ft(text, n):
    text = str(text)
    return text if len(text) <= n else text[:n-2]+".."

def ai_generate_post(subtopic):
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": AGENT_PERSONA},
            {"role": "user", "content":
                f"Write a LinkedIn post about: {subtopic}\n\n"
                f"- SHORT lines with line breaks\n"
                f"- Emojis at key lines\n"
                f"- Hook opening\n"
                f"- End with question\n"
                f"- Max 150 words"}
        ],
        max_tokens=400,
    )
    return response.choices[0].message.content.strip()

def ai_generate_stack_data(subtopic):
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content":
                f"Create infographic data for: {subtopic}\n\n"
                f"Reply JSON only:\n"
                f"{{\n"
                f"  \"main_title\": \"TOPIC STACK (caps, max 3 words)\",\n"
                f"  \"panels\": [\n"
                f"    {{\n"
                f"      \"title\": \"Panel Title max 3 words\",\n"
                f"      \"purpose\": \"max 7 words\",\n"
                f"      \"section1_title\": \"Label max 2 words\",\n"
                f"      \"section1_items\": [\"max 3 words\", \"max 3 words\", \"max 3 words\"],\n"
                f"      \"section2_title\": \"Label max 2 words\",\n"
                f"      \"section2_items\": [\"max 3 words\", \"max 3 words\", \"max 3 words\"]\n"
                f"    }}\n"
                f"  ]\n"
                f"}}\n\n"
                f"Exactly 6 panels. Each section has exactly 3 short items."}
        ],
        max_tokens=1000,
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

def generate_background_image(subtopic, post_content):
    print(f"[{datetime.now()}] Generating DALL-E 3 background...")
    try:
        vision_response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content":
                f"From this post extract 3 things:\n"
                f"1. Main threat: 3 words\n2. AI action: 3 words\n3. Target: 3 words\n"
                f"Post: {post_content}\n"
                f"JSON only: {{\"threat\":\"...\",\"action\":\"...\",\"target\":\"...\"}}"}],
            max_tokens=60,
        )
        raw = vision_response.choices[0].message.content.strip()
        raw = raw.replace("```json","").replace("```","").strip()
        concepts = json.loads(raw)
        threat = concepts.get("threat", subtopic[:20])
        action = concepts.get("action", "detecting threats")
        target = concepts.get("target", "AI systems")
        print(f"Concepts: {threat} | {action} | {target}")

        prompt = (
            f"Advanced cybersecurity AI command center at night. "
            f"Large holographic screen showing {threat} global network map. "
            f"AI robots and analysts at curved desks monitoring {action}. "
            f"Screens showing {target} analytics dashboards. "
            f"Cinematic dark room, vivid neon blue cyan purple glow. "
            f"Photorealistic movie quality. Wide establishing shot. "
            f"No text visible anywhere in image."
        )
        print(f"Prompt: {prompt[:100]}...")

        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        print(f"Image URL received, downloading...")
        img_data = requests.get(image_url, timeout=30).content
        img = Image.open(io.BytesIO(img_data)).convert("RGB")
        # Resize to portrait for the infographic
        img = img.resize((900, 1100), Image.LANCZOS)
        print(f"DALL-E image ready: {img.size}")
        return img

    except Exception as e:
        print(f"DALL-E failed: {type(e).__name__}: {e}")
        return None

def draw_dashed_rect(draw, x0, y0, x1, y1, color, dash=10):
    for x in range(x0, x1, dash*2):
        draw.line([(x, y0), (min(x+dash, x1), y0)], fill=color, width=2)
        draw.line([(x, y1), (min(x+dash, x1), y1)], fill=color, width=2)
    for y in range(y0, y1, dash*2):
        draw.line([(x0, y), (x0, min(y+dash, y1))], fill=color, width=2)
        draw.line([(x1, y), (x1, min(y+dash, y1))], fill=color, width=2)

def load_fonts():
    try:
        B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        return {
            "title": ImageFont.truetype(B, 72),
            "author": ImageFont.truetype(B, 20),
            "follow": ImageFont.truetype(R, 16),
            "panel": ImageFont.truetype(B, 22),
            "section": ImageFont.truetype(B, 16),
            "item": ImageFont.truetype(R, 15),
            "small": ImageFont.truetype(R, 13),
        }
    except:
        d = ImageFont.load_default()
        return {k: d for k in ["title","author","follow","panel",
                                "section","item","small"]}

def render_frame_rgb(width, height, bg_img, accent, title,
                     panels, visible_count, fonts, blink=False):
    """Render a full RGB frame — no palette conversion yet"""

    if bg_img is not None:
        img = bg_img.copy().convert("RGBA")
        # lighter overlay so background photo shows through clearly
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 120))
        img = Image.alpha_composite(img, overlay).convert("RGB")
    else:
        img = Image.new("RGB", (width, height), (5, 5, 15))
        d = ImageDraw.Draw(img)
        for x in range(0, width, 40):
            d.line([(x, 0), (x, height)], fill=(20, 20, 30))
        for y in range(0, height, 40):
            d.line([(0, y), (width, y)], fill=(20, 20, 30))

    draw = ImageDraw.Draw(img)

    # Semi-transparent top bar for header readability
    header_bar = Image.new("RGBA", (width, 130), (0, 0, 0, 160))
    img.paste(Image.new("RGB", (width, 130), (0,0,0)),
              (0, 0),
              header_bar)
    draw = ImageDraw.Draw(img)

    # Header
    draw.ellipse([(width//2-28, 18), (width//2+28, 74)],
                 outline=accent, width=2, fill=(15, 15, 25))
    draw.text((width//2-14, 36), "AO", font=fonts["author"], fill=accent)
    draw.text((width//2-62, 82), "Aurobinda Ojha",
              font=fonts["author"], fill=(220, 220, 220))
    draw.text((width//2-48, 106), "Follow For More",
              font=fonts["follow"], fill=(160, 160, 160))

    # Title bar
    title_wrapped = textwrap.fill(title, width=16)
    title_lines = title_wrapped.split('\n')
    title_h = len(title_lines) * 82 + 20
    title_bar = Image.new("RGBA", (width, title_h), (0, 0, 0, 140))
    img.paste(Image.new("RGB", (width, title_h), (0,0,0)),
              (0, 130), title_bar)
    draw = ImageDraw.Draw(img)

    ty = 138
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=fonts["title"])
        tw = bbox[2]-bbox[0]
        draw.text(((width-tw)//2, ty), line,
                  font=fonts["title"], fill=(255, 255, 255))
        ty += 82

    ul_color = (255, 255, 255) if blink else accent
    draw.rectangle([(40, ty+4), (width-40, ty+7)], fill=ul_color)
    ty += 18

    # Panels
    M = 18
    card_w = (width - M*4) // 3
    card_h = 295
    start_y = ty + M

    for idx in range(min(visible_count, 6)):
        if idx >= len(panels):
            break
        col = idx % 3
        row = idx // 3
        px = M + col*(card_w+M)
        py = start_y + row*(card_h+M)
        panel = panels[idx]
        color = PANEL_COLORS[idx % len(PANEL_COLORS)]

        # Semi-transparent card
        card_overlay = Image.new("RGBA", (card_w, card_h), (8, 12, 22, 210))
        img.paste(Image.new("RGB", (card_w, card_h), (8, 12, 22)),
                  (px, py), card_overlay)
        draw = ImageDraw.Draw(img)

        draw_dashed_rect(draw, px, py, px+card_w, py+card_h, color)
        draw.rectangle([(px, py), (px+card_w, py+42)], fill=color)

        t = ft(panel.get("title", ""), 18)
        for tl in textwrap.fill(t, width=16).split('\n'):
            bbox = draw.textbbox((0, 0), tl, font=fonts["panel"])
            tlw = bbox[2]-bbox[0]
            draw.text((px+(card_w-tlw)//2, py+8), tl,
                      font=fonts["panel"], fill=(0, 0, 0))

        draw.text((px+8, py+48), "Purpose:",
                  font=fonts["section"], fill=color)
        draw.text((px+8, py+66), ft(panel.get("purpose",""), 30),
                  font=fonts["item"], fill=(200, 200, 200))

        s1_y = py+90
        draw.text((px+8, s1_y),
                  ft(panel.get("section1_title",""),18)+":",
                  font=fonts["section"], fill=color)
        s1_y += 20
        for item in panel.get("section1_items",[])[:3]:
            draw.ellipse([(px+10,s1_y+5),(px+16,s1_y+11)], fill=color)
            draw.text((px+22,s1_y), ft(item,20),
                      font=fonts["item"], fill=(200,200,200))
            s1_y += 18

        s2_y = s1_y+8
        draw.text((px+8, s2_y),
                  ft(panel.get("section2_title",""),18)+":",
                  font=fonts["section"], fill=color)
        s2_y += 20
        for item in panel.get("section2_items",[])[:3]:
            draw.ellipse([(px+10,s2_y+5),(px+16,s2_y+11)], fill=color)
            draw.text((px+22,s2_y), ft(item,20),
                      font=fonts["item"], fill=(200,200,200))
            s2_y += 18

        draw.text((px+8, py+card_h-22), "Key Tools:",
                  font=fonts["section"], fill=color)

    # Footer
    footer_y = start_y + 2*(card_h+M) + M
    footer_bar = Image.new("RGBA", (width, height-footer_y), (5,5,15,240))
    img.paste(Image.new("RGB", (width, height-footer_y), (5,5,15)),
              (0, footer_y), footer_bar)
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0,footer_y),(width,footer_y+3)], fill=accent)
    draw.text((30,footer_y+10), "Aurobinda Ojha",
              font=fonts["author"], fill=accent)
    draw.text((30,footer_y+34),
              "Independent Researcher | Cybersecurity & Agentic AI",
              font=fonts["small"], fill=(140,140,140))
    date_str = datetime.now().strftime("%B %d, %Y")
    draw.text((30,footer_y+54),
              f"#AgenticAI  #Cybersecurity  |  {date_str}",
              font=fonts["small"], fill=(100,100,100))

    if blink:
        draw.rectangle([(0,0),(width,4)], fill=(255,255,255))
        draw.rectangle([(0,height-4),(width,height)], fill=(255,255,255))

    return img

def create_animated_gif(subtopic, data, post_content=""):
    print(f"[{datetime.now()}] Creating animated GIF...")
    width, height = 900, 1100
    seed = get_seed(subtopic)
    ACCENTS = [(0,255,200),(255,220,0),(180,80,255),(50,255,150),(255,100,100)]
    accent = ACCENTS[seed % len(ACCENTS)]
    fonts = load_fonts()
    panels = data.get("panels", [])[:6]
    main_title = data.get("main_title", "AI SECURITY STACK")

    bg_img = generate_background_image(subtopic, post_content)
    if bg_img:
        print(f"Background loaded: {bg_img.size}, mode: {bg_img.mode}")
        # Sample center pixel to confirm it's not black
        px = bg_img.getpixel((450, 550))
        print(f"Background center pixel: {px}")
    else:
        print("No background - using dark fallback")

    rgb_frames = []
    durations = []

    # Frame 0 — title only
    rgb_frames.append(render_frame_rgb(
        width, height, bg_img, accent, main_title, panels, 0, fonts))
    durations.append(1200)

    # Frames 1-6 — panels appear one by one
    for i in range(1, 7):
        rgb_frames.append(render_frame_rgb(
            width, height, bg_img, accent, main_title, panels, i, fonts))
        durations.append(700)

    # Hold
    rgb_frames.append(render_frame_rgb(
        width, height, bg_img, accent, main_title, panels, 6, fonts))
    durations.append(2500)

    # Blink
    for b in range(6):
        rgb_frames.append(render_frame_rgb(
            width, height, bg_img, accent, main_title,
            panels, 6, fonts, blink=b%2==0))
        durations.append(250)

    # Final hold
    rgb_frames.append(render_frame_rgb(
        width, height, bg_img, accent, main_title, panels, 6, fonts))
    durations.append(2000)

    # Convert to GIF — use first frame palette for consistency
    print("Converting to GIF...")
    palette_frames = []
    # Use ADAPTIVE quantization per frame for best quality
    for frame in rgb_frames:
        p = frame.quantize(
            colors=256,
            method=Image.Quantize.MEDIANCUT,
            dither=Image.Dither.NONE
        )
        palette_frames.append(p)

    gif_bytes = io.BytesIO()
    palette_frames[0].save(
        gif_bytes,
        format="GIF",
        save_all=True,
        append_images=palette_frames[1:],
        duration=durations,
        loop=0,
        optimize=False,
        disposal=2,
    )
    gif_bytes.seek(0)
    gif_data = gif_bytes.read()
    print(f"GIF created: {len(rgb_frames)} frames, {len(gif_data)//1024}KB")
    return gif_data

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
                 "Content-Type": "image/gif"},
        data=image_data
    ).raise_for_status()
    print(f"Uploaded! Asset: {asset}")
    return asset

def job_post():
    subtopic = get_daily_topic()
    print(f"[{datetime.now()}] Today: {subtopic}")

    content = ai_generate_post(subtopic)
    print(f"Post: {content[:80]}...")

    data = ai_generate_stack_data(subtopic)
    print(f"Title: {data.get('main_title')}")

    gif_data = create_animated_gif(subtopic, data, content)
    asset = upload_image_to_linkedin(gif_data)

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
