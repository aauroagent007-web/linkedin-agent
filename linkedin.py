import openai
import requests
import os
from datetime import datetime

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

def ai_generate_search_keyword(post_content):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content":
                f"Based on this LinkedIn post, give me 2-3 keywords to search for a matching "
                f"professional motion video.\n"
                f"Post: {post_content[:300]}\n"
                f"Reply with ONLY the keywords. Example: cybersecurity network hacker"}
        ],
        max_tokens=20,
    )
    return response.choices[0].message.content.strip()

def get_matching_video(post_content):
    print(f"[{datetime.now()}] Finding matching video from Pexels...")

    keyword = ai_generate_search_keyword(post_content)
    print(f"Search keyword: {keyword}")

    # Search Pexels for matching video
    r = requests.get(
        "https://api.pexels.com/v1/videos/search",
        params={
            "query": keyword,
            "per_page": 5,
            "orientation": "landscape",
            "size": "medium"
        },
        headers={"Authorization": PEXELS_API_KEY}
    )
    r.raise_for_status()
    videos = r.json().get("videos", [])

    if not videos:
        # Fallback search
        print("No results found, trying fallback search...")
        r = requests.get(
            "https://api.pexels.com/v1/videos/search",
            params={"query": "cybersecurity technology", "per_page": 3},
            headers={"Authorization": PEXELS_API_KEY}
        )
        r.raise_for_status()
        videos = r.json().get("videos", [])

    if not videos:
        raise Exception("No videos found on Pexels!")

    # Get HD video file
    video = videos[0]
    video_files = video.get("video_files", [])

    # Find HD or SD file
    hd_file = None
    for vf in video_files:
        if vf.get("quality") in ["hd", "sd"] and vf.get("file_type") == "video/mp4":
            hd_file = vf
            break

    if not hd_file:
        hd_file = video_files[0]

    video_url = hd_file.get("link")
    print(f"Found video: {video_url[:60]}...")

    # Download video
    video_data = requests.get(video_url).content
    print(f"Video downloaded: {len(video_data)} bytes")
    return video_data

def upload_video_to_linkedin(video_data):
    print(f"[{datetime.now()}] Registering video upload with LinkedIn...")

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

    content = ai_generate_post(TOPIC)
    print(f"Generated content: {content[:100]}...")

    video_data = get_matching_video(content)
    asset = upload_video_to_linkedin(video_data)

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
