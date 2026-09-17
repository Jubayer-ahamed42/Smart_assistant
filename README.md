# 🤖 24/7 Autonomous Facebook Page Social Media Agent

An autonomous, AI-powered social media manager that publishes high-engagement Bengali posts with AI-generated visual cards directly to a Facebook Page 3 times a day on schedule.

Zero maintenance, zero server costs, and 100% cloud-hosted via **GitHub Actions**.

---

## 🕒 Daily Schedule & Topic Themes (Bangladesh Standard Time - UTC+6)

| Time (BST) | UTC | Theme | Description |
| :--- | :--- | :--- | :--- |
| **07:00 AM** | 01:00 UTC | 🤖 **Artificial Intelligence** | AI news, tools, machine learning, future impact & practical tips. |
| **12:00 PM** | 06:00 UTC | 💻 **Technology & Gadgets** | Tech innovations, cybersecurity, hardware, smart gadgets, IT facts. |
| **08:00 PM** | 14:00 UTC | 🔬 **Science & Discovery** | Space exploration, astrophysics, physics, medical breakthroughs. |

---

## 🚀 Key Features

- **100% Autonomous**: Runs on GitHub Actions scheduled cron. No PC, server, or manual triggers needed.
- **Engaging Bangla Copywriting**: Structured posts with catchy headlines, hooks, clear bullet points, open questions, and hashtags.
- **AI-Powered Visuals**: Real-time photo generation using Pollinations AI (Flux model) matching post topics.
- **Smart Duplicate Prevention**: Stores previous topics in `post_history.json` and feeds past context into the LLM prompt to guarantee fresh, non-repeating content.
- **Fallback Resilience**: Automatic fallback to text feed posts or Pillow-generated graphic cards if image or network services fluctuate.
- **Manual Trigger**: Supports one-click manual posting directly from GitHub Actions web interface.

---

## 📖 Setup Instructions

Detailed Bengali instructions are available in:
👉 **[SETUP_GUIDE_BANGLA.md](file:///c:/test/test-1/SETUP_GUIDE_BANGLA.md)**

### Required Secrets
1. `GEMINI_API_KEY`: Free Google AI Studio API key
2. `FB_PAGE_ID`: Target Facebook Page numeric ID
3. `FB_PAGE_ACCESS_TOKEN`: Long-lived Meta Graph API Page Access Token

---

## 💻 Local CLI Usage

```bash
# Verify credentials
python main.py --verify

# Dry run preview (does not publish to Facebook)
python main.py --dry-run

# Run morning AI slot preview
python main.py --slot morning --dry-run

# Run full post now
python main.py
```
