import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test Discord webhook
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
DISCORD_USER_ID = os.getenv("DISCORD_USER_ID")

def test_discord_message():
    """Send a test message to Discord to verify formatting."""
    
    if not DISCORD_WEBHOOK_URL:
        print("❌ Discord webhook URL not found")
        return
    
    # Test embed
    test_embed = {
        "title": "🧪 Discord Integration Test",
        "description": "Testing the GitHub PR Bot Discord integration!",
        "color": 0x00ff00,
        "fields": [
            {
                "name": "✅ Status",
                "value": "Integration working perfectly!",
                "inline": True
            },
            {
                "name": "🤖 Bot",
                "value": "GitHub PR Analyzer",
                "inline": True
            }
        ],
        "footer": {
            "text": "Test completed successfully"
        }
    }
    
    webhook_data = {
        "username": "GitHub PR Bot",
        "avatar_url": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
        "content": f"<@{DISCORD_USER_ID}> Test message! 🚀",
        "embeds": [test_embed]
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=webhook_data)
        response.raise_for_status()
        print("✅ Test message sent to Discord successfully!")
        return True
    except Exception as e:
        print(f"❌ Error sending test message: {e}")
        return False

if __name__ == "__main__":
    test_discord_message()