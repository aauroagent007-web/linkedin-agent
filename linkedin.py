import os
from datetime import datetime

import openai
import requests


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
LINKEDIN_ACCESS_TOKEN = os.environ["LINKEDIN_ACCESS_TOKEN"]

# Keep this as a fallback, but the authenticated LinkedIn member ID returned
# by /v2/userinfo is preferred so the author matches the token.
LINKEDIN_PERSON_ID = os.environ.get("LINKEDIN_PERSON_ID", "").strip()

TOPIC = os.environ.get(
    "TOPIC",
    "Agentic AI cybersecurity and autonomous threat detection"
)
RUN_MODE = os.environ.get("RUN_MODE", "post")

# LinkedIn API version. Can be overridden in GitHub Actions with:
# LINKEDIN_API_VERSION=202609
LINKEDIN_API_VERSION = os.environ.get(
    "LINKEDIN_API_VERSION",
    "202609"
)

openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)


# ---------------------------------------------------------------------------
# LinkedIn headers / helpers
# ---------------------------------------------------------------------------

LINKEDIN_HEADERS = {
    "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
    "Content-Type": "application/json",
    "X-Restli-Protocol-Version": "2.0.0",
    "Linkedin-Version": LINKEDIN_API_VERSION,
}


def linkedin_error(response, operation):
    """Print the LinkedIn response body without exposing the access token."""
    try:
        body = response.json()
    except Exception:
        body = response.text

    print(
        f"LinkedIn {operation} failed: "
        f"HTTP {response.status_code}: {body}"
    )
    response.raise_for_status()


def validate_linkedin_token():
    """
    Validate the Bearer token and return the authenticated member ID.

    /v2/userinfo requires an OIDC-enabled LinkedIn access token.
    """
    print(f"[{datetime.now()}] Validating LinkedIn access token...")

    response = requests.get(
        "https://api.linkedin.com/v2/userinfo",
        headers={
            "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}"
        },
        timeout=30,
    )

    if response.status_code != 200:
        linkedin_error(response, "authentication")

    profile = response.json()
    member_id = str(profile.get("sub", "")).strip()

    if not member_id:
        raise RuntimeError(
            "LinkedIn authentication succeeded, but no member ID "
            "was returned by /v2/userinfo."
        )

    name = profile.get("name", "Unknown")
    print(f"LinkedIn authentication successful: {name}")
    print(f"Authenticated LinkedIn member ID: {member_id}")

    if LINKEDIN_PERSON_ID and LINKEDIN_PERSON_ID != member_id:
        print(
            "WARNING: LINKEDIN_PERSON_ID does not match the authenticated "
            "token member. The authenticated member ID will be used."
        )

    return member_id


# ---------------------------------------------------------------------------
# Topics
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# AI LinkedIn post
# ---------------------------------------------------------------------------

AGENT_PERSONA = """
You are Aurobinda Ojha, an Independent Researcher on Cybersecurity
and Agentic AI.

Write sharp, technically useful LinkedIn posts.

Style:
- Direct and conversational
- Short paragraphs
- Strong technical insight
- Emojis only where useful
- Plain text only
- No Markdown
- No "About me"
- No contact information
- No email address
- Do not invent personal achievements
"""


def ai_generate_post(subtopic):
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": AGENT_PERSONA,
            },
            {
                "role": "user",
                "content": (
                    f"Write a LinkedIn post about: {subtopic}\n\n"
                    "Requirements:\n"
                    "- Start with a strong hook\n"
                    "- Explain the cybersecurity problem\n"
                    "- Give practical technical insights\n"
                    "- Include 4-6 short key points\n"
                    "- Include practical defensive recommendations\n"
                    "- End with a thought-provoking question\n"
                    "- Maximum 150 words\n"
                    "- Plain text only\n"
                    "- No Markdown\n"
                ),
            },
        ],
        max_tokens=500,
    )

    content = response.choices[0].message.content.strip()

    # Safety cleanup for accidental Markdown.
    for token in ("```", "**", "__", "##"):
        content = content.replace(token, "")

    return content.strip()


# ---------------------------------------------------------------------------
# LinkedIn text-only publishing
# ---------------------------------------------------------------------------

def publish_text_post(member_id, post_text):
    """
    Publish a text-only organic post using LinkedIn's current Posts API.

    POST /rest/posts
    """
    print(f"[{datetime.now()}] Publishing text-only LinkedIn post...")

    payload = {
        "author": f"urn:li:person:{member_id}",
        "commentary": post_text,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }

    response = requests.post(
        "https://api.linkedin.com/rest/posts",
        headers=LINKEDIN_HEADERS,
        json=payload,
        timeout=30,
    )

    if response.status_code not in (200, 201):
        linkedin_error(response, "text post publishing")

    post_id = response.headers.get("x-restli-id")

    if not post_id:
        try:
            post_id = response.json().get("id")
        except Exception:
            post_id = None

    print(
        f"[{datetime.now()}] LinkedIn text post published successfully!"
    )

    if post_id:
        print(f"LinkedIn Post ID: {post_id}")
    else:
        print("LinkedIn returned success but no Post ID was found.")

    return post_id


# ---------------------------------------------------------------------------
# Main job
# ---------------------------------------------------------------------------

def job_post():
    # Authenticate before spending OpenAI/API time.
    member_id = validate_linkedin_token()

    subtopic = get_daily_topic()
    print(f"[{datetime.now()}] Today: {subtopic}")

    content = ai_generate_post(subtopic)

    print(f"[{datetime.now()}] Generated post:")
    print("-" * 70)
    print(content)
    print("-" * 70)

    publish_text_post(member_id, content)

    print(f"[{datetime.now()}] Text-only LinkedIn workflow completed.")


if __name__ == "__main__":
    if RUN_MODE == "post":
        job_post()
    else:
        print(f"RUN_MODE={RUN_MODE}; no LinkedIn post was published.")
