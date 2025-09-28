#!/usr/bin/env python3
"""
GitHub PR Bot Workflow Setup Script
This script helps you set up the GitHub workflow for automatic PR analysis.
"""

import os
import json

def create_secrets_template():
    """Create a template for GitHub secrets that need to be set."""
    secrets = {
        "GROQ_API_KEY": "Your Groq API key from .env file",
        "DISCORD_WEBHOOK_URL": "Your Discord webhook URL from .env file",
        "DISCORD_BOT_TOKEN": "Your Discord bot token from .env file (optional)",
        "DISCORD_CHANNEL_ID": "Your Discord channel ID from .env file (optional)",
        "DISCORD_USER_ID": "Your Discord user ID from .env file",
        "PERSONAL_ACCESS_TOKEN": "GitHub Personal Access Token with repo permissions (for triggering workflows)"
    }
    
    print("🔐 GitHub Secrets to Configure:")
    print("=" * 60)
    print("Go to your bot repository -> Settings -> Secrets and variables -> Actions")
    print("Add these repository secrets:\n")
    
    for secret, description in secrets.items():
        print(f"📝 {secret}")
        print(f"   Description: {description}")
        print()

def create_target_repo_workflow():
    """Instructions for setting up the trigger workflow in target repository."""
    print("🎯 Target Repository Setup:")
    print("=" * 60)
    print("1. Go to the repository you want to monitor (FounderFeedAdmin/TheBundle-AI)")
    print("2. Create: .github/workflows/trigger-pr-bot.yml")
    print("3. Copy the content from 'trigger-workflow-template.yml'")
    print("4. Replace 'YOUR_USERNAME/GithubPRBot' with your actual bot repository")
    print("5. Add PERSONAL_ACCESS_TOKEN secret to that repository")
    print()
    print("⚠️  Important Notes:")
    print("- The PERSONAL_ACCESS_TOKEN must have 'repo' permissions")
    print("- It should be created by a user with access to both repositories")
    print("- The target repository must have workflow permissions enabled")
    print()

def show_manual_trigger_instructions():
    """Show how to manually trigger the workflow."""
    print("🚀 Manual Trigger Instructions:")
    print("=" * 60)
    print("1. Go to your bot repository -> Actions -> PR Analysis Bot")
    print("2. Click 'Run workflow'")
    print("3. Enter:")
    print("   - PR Number: (e.g., 357)")
    print("   - Repository Owner: (e.g., FounderFeedAdmin)")
    print("   - Repository Name: (e.g., TheBundle-AI)")
    print("4. Click 'Run workflow'")
    print()

def test_workflow_locally():
    """Test the workflow script locally."""
    print("🧪 Local Testing:")
    print("=" * 60)
    print("To test the workflow locally:")
    print()
    print("1. Set environment variables:")
    print("   export REPO_OWNER=FounderFeedAdmin")
    print("   export REPO_NAME=TheBundle-AI")
    print("   export PR_NUMBER=357")
    print("   export GITHUB_TOKEN=your_github_token")
    print()
    print("2. Run the workflow script:")
    print("   python main_workflow.py")
    print()

def main():
    print("🤖 GitHub PR Bot - Workflow Setup Guide")
    print("=" * 80)
    print()
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print("✅ Found .env file")
        with open('.env', 'r') as f:
            env_content = f.read()
            required_keys = ['GROQ_API_KEY', 'DISCORD_WEBHOOK_URL', 'DISCORD_USER_ID']
            missing_keys = [key for key in required_keys if key not in env_content]
            
            if missing_keys:
                print(f"⚠️  Missing keys in .env: {', '.join(missing_keys)}")
            else:
                print("✅ All required keys found in .env")
    else:
        print("❌ .env file not found! Please create it first.")
        return
    
    print()
    
    # Check if workflow file exists
    workflow_path = '.github/workflows/pr-analysis.yml'
    if os.path.exists(workflow_path):
        print("✅ Workflow file exists")
    else:
        print("❌ Workflow file not found!")
        
    print()
    
    create_secrets_template()
    create_target_repo_workflow()
    show_manual_trigger_instructions()
    test_workflow_locally()
    
    print("🎉 Setup Complete!")
    print("=" * 80)
    print("Next steps:")
    print("1. Add all secrets to your GitHub repository")
    print("2. Set up the trigger workflow in your target repository")
    print("3. Test with a manual workflow run")
    print("4. Create a new PR in the target repo to test automatic triggering")

if __name__ == "__main__":
    main()