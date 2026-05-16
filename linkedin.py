import openai
import requests
import os
import textwrap
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
LINKEDIN_ACCESS_TOKEN = os.environ["LINKEDIN_ACCESS_TOKEN"]
LINKEDIN_PERSON_ID = os.environ["LINKEDIN_PERSON_ID"]
PEXELS_API_KEY = os.environ["PEXELS_API_KEY"]
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

def ai_generate_search_keyword(post_content):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content":
                f"Based on this LinkedIn post, give me 2-3 keywords to search for a matching "
                f"professional dark cybersecurity background photo.\n"
                f"Post: {post_content[:300]}\n"
                f"Reply with ONLY the keywords. Example: cybersecurity network dark"}
        ],
        max_tokens=20,
    )
    return response.choices[0].message.content.strip()

def get_background_image(post_content):
    print(f"[{datetime.now()}] Getting background image from Pexels...")
    keyword = ai_generate_search_keyword(post_content)
    print(f"Search keyword: {keyword}")

    day_of_year = datetime.now().timetuple().tm_yday

    r = requests.get(
        "https://api.pexels.com/v1/photos/search",
        params={
            "query": keyword,
            "per_page": 15,
            "orientation": "landscape"
        },
        headers={"Authorization": PEXELS_API_KEY}
    )
    r.raise_for_status()
    photos = r.json().get("photos", [])

    if not photos:
        print("No photos found, using fallback...")
        r = requests.get(
            "https://api.pexels.com/v1/photos/search",
            params={"query": "cybersecurity dark technology", "per_page": 10},
            headers={"Authorization": PEXELS_API_KEY}
        )
        r.raise_for_status()
        photos = r.json().get("photos", [])

    photo = photos[day_of_year % len(photos)]
    image_url = photo["src"]["large2x"]
    print(f"Background image: {image_url[:60]}...")

    image_data = requests.get(image_url).content
    return Image.open(io.BytesIO(image_data)).convert("RGB")

def create_post_image(post_content, headline):
    print(f"[{datetime.now()}] Creating creative image...")

    bg_image = get_background_image(post_content)

    width, height = 1200, 627
    bg_image = bg_image.resize((width, height), Image.LANCZOS)

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 180))
    bg_image = bg_image.convert("RGBA")
    bg_image = Image.alpha_composite(bg_image, overlay)
    bg_image = bg_image.convert("RGB")
    draw = ImageDraw.Draw(bg_image)

    draw.rectangle([(40, 40), (48, height - 40)], fill=(100, 255, 218))

    try:
        font_headline = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
        font_body = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        font_author = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_tag = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    except:
        font_headline = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_author = ImageFont.load_default()
        font_tag = ImageFont.load_default()

    headline_wrapped = textwrap.fill(headline, width=35)
    draw.text((70, 80), headline_wrapped, font=font_headline, fill=(100, 255, 218))

    draw.rectangle([(70, 200), (500, 203)], fill=(100, 255, 218))

    first_para = post_content.split('\n')[0][:200]
    body_wrapped = textwrap.fill(first_para, width=55)
    draw.text((70, 220), body_wrapped, font=font_body, fill=(255, 255, 255))

    draw.rectangle([(0, height - 80), (width, height)], fill=(10, 25, 47))

    draw.text((70, height - 58), "Aurobinda Ojha", font=font_author, fill=(100, 255, 218))
    draw.text((70, height - 32), "Independent Researcher | Cybersecurity & Agentic AI", font=font_tag, fill=(136, 146, 176))

    tag_text = "#AgenticAI #Cybersecurity"
    draw.text((width - 350, 50), tag_text, font=font_tag, fill=(100, 255, 218))

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
