import openai
import requests
import os
import time
from datetime import datetime

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
LINKEDIN_ACCESS_TOKEN = os.environ["LINKEDIN_ACCESS_TOKEN"]
LINKEDIN_PERSON_ID = os.environ["LINKEDIN_PERSON_ID"]
JSON2VIDEO_API_KEY = os.environ["JSON2VIDEO_API_KEY"]
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

def ai_generate_video_text(post_content):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content":
                f"Based on this LinkedIn post, write 3 short punchy lines (max 8 words each) "
                f"for a video slide show. Each line should be a key insight.\n"
                f"Post: {post_content[:300]}\n"
                f"Reply with ONLY 3 lines, nothing else."}
        ],
        max_tokens=60,
    )
    lines = response.choices[0].message.content.strip().split('\n')
    return [l.strip() for l in lines if l.strip()][:3]

def generate_video(post_content):
    print(f"[{datetime.now()}] Generating video with JSON2Video...")

    text_lines = ai_generate_video_text(post_content)
    print(f"Video text lines: {text_lines}")

    # Build video with 3 slides
    scenes = []
    colors = ["#0a192f", "#112240", "#1d3a6e"]

    for i, line in enumerate(text_lines):
        scenes.append({
            "comment": f"Slide {i+1}",
            "duration": 3,
            "elements": [
                {
                    "type": "html",
                    "html": f"""
                    <div style='
                        width:100%; height:100%;
                        background:{colors[i]};
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        padding:40px;
                        box-sizing:border-box;
                    '>
                        <p style='
                            color:white;
                            font-size:52px;
                            font-weight:bold;
                            text-align:center;
                            font-family:Arial,sans-serif;
                            line-height:1.4;
                        '>{line}</p>
                    </div>
                    """,
                    "width": 1280,
                    "height": 720
                }
            ]
        })

    # Add final slide with topic
    scenes.append({
        "comment": "Final slide",
        "duration": 3,
        "elements": [
            {
                "type": "html",
                "html": f"""
                <div style='
                    width:100%; height:100%;
                    background:#0a192f;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    padding:40px;
                    box-sizing:border-box;
                    flex-direction:column;
                '>
                    <p style='
                        color:#64ffda;
                        font-size:36px;
                        font-weight:bold;
                        text-align:center;
                        font-family:Arial,sans-serif;
                    '>Agentic AI Cybersecurity</p>
                    <p style='
                        color:#8892b0;
                        font-size:24px;
                        text-align:center;
                        font-family:Arial,sans-serif;
                        margin-top:20px;
                    '>By Aurobinda Ojha</p>
                </div>
                """,
                "width": 1280,
                "height": 720
            }
        ]
    })

    payload = {
        "resolution": "hd",
        "quality": 7,
        "scenes": scenes
    }

    r = requests.post(
        "https://api.json2video.com/v2/movies",
        headers={
            "x-api-key": JSON2VIDEO_API_KEY,
            "Content-Type": "application/json"
        },
        json=payload
    )
    r.raise_for_status()
    project_id = r.json().get("project")
    print(f"Video project created: {project_id}")

    # Wait for video to render
    print("Waiting for video to render...")
    for i in range(30):
        time.sleep(10)
        status_r = requests.get(
            f"https://api.json2video.com/v2/movies?project={project_id}",
            headers={"x-api-key": JSON2VIDEO_API_KEY}
        )
        status_r.raise_for_status()
        status_data = status_r.json()
        status = status_data.get("movie", {}).get("status")
        print(f"Status: {status}")

        if status == "done":
            video_url = status_data["movie"]["url"]
            print(f"Video ready: {video_url}")
            video_data = requests.get(video_url).content
            return video_data
        elif status == "error":
            raise Exception("Video generation failed!")

    raise Exception("Video render timeout!")

def upload_video_to_linkedin(video_data):
    print(f"[{datetime.now()}] Registering video upload with LinkedIn...")

    # Step 1 - Register upload
    register_payload = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-video"],
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

    # Step 2 - Upload video binary
    upload_headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "video/mp4"
    }
    upload_response = requests.put(
        upload_url,
        headers=upload_headers,
        data=video_data
    )
    upload_response.raise_for_status()
    print(f"Video uploaded successfully!")
    return asset

def job_post():
    print(f"[{datetime.now()}] Generating LinkedIn video post about: {TOPIC}")

    # Generate post text
    content = ai_generate_post(TOPIC)
    print(f"Generated content: {content[:100]}...")

    # Generate video
    video_data = generate_video(content)

    # Upload video to LinkedIn
    asset = upload_video_to_linkedin(video_data)

    # Post with video
    payload = {
        "author": f"urn:li:person:{LINKEDIN_PERSON_ID}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": content
                },
                "shareMediaCategory": "VIDEO",
                "media": [
                    {
                        "status": "READY",
                        "description": {
                            "text": "Cybersecurity AI insights"
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
    print(f"[{datetime.now()}] LinkedIn video post published! ID: {post_id}")

if __name__ == "__main__":
    if RUN_MODE == "post":
        job_post()
