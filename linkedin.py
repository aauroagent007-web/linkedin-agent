import openai
import requests
import os
from datetime import datetime

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

CYBERSECURITY_IMAGES = [
    "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=1024",
    "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=1024",
    "https://images.unsplash.com/photo-1614064641938-3bbee52942c7?w=1024",
    "https://images.unsplash.com/photo-1510511459019-5dda7724fd87?w=1024",
    "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1024",
    "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=1024",
    "https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=1024",
]

def ai_generate_post(topic):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": AGENT_PERSONA},
            {"role": "user", "content":
                f"Write a professional LinkedIn post about a fresh angle on: {topic}\n"
                f"Examples: AI agent prompt injection, autonomous malware detection, "
                f"zero-trust for AI agents, LLM vulnerabilities, agentic AI threat hunting, "
                f"multi-agent exploits, AI supply chain attacks.\n"
                f"Be professional and engaging. Plain text only. Max 3 paragraphs.\n"
                f"End with a thought provoking question."}
        ],
        max_tokens=400,
    )
    return response.choices[0].message.content.strip()

def get_image(topic):
    print(f"[{datetime.now()}] Fetching cybersecurity image...")
    # Pick image based on day of month for variety
    day = datetime.now().day
    image_url = CYBERSECURITY_IMAGES[day % len(CYBERSECURITY_IMAGES)]
    print(f"Using image: {image_url[:60]}...")
    image_data = requests.get(image_url).content
    return image_data

def upload_image_to_linkedin(image_data):
    print(f"[{datetime.now()}] Uploading image to LinkedIn...")

    # Step 1 - Register upload
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

    # Step 2 - Upload image binary
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
    print(f"[{datetime.now()}] Generating LinkedIn post about: {TOPIC}")

    # Generate text
    content = ai_generate_post(TOPIC)
    print(f"Generated content: {content[:100]}...")

    # Get and upload image
    image_data = get_image(TOPIC)
    asset = upload_image_to_linkedin(image_data)

    # Post with image
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
                            "text": "Cybersecurity AI visualization"
                        },
                        "media": asset,
                        "title": {
                            "text": TOPIC[:100]
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
    print(f"[{datetime.now()}] LinkedIn post with image published! ID: {post_id}")

if __name__ == "__main__":
    if RUN_MODE == "post":
        job_post()
