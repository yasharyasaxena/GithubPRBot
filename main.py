import os
import requests
from groq import Groq
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# --- Configuration ---
# It's better to load these from environment variables for security
# e.g., os.environ.get("GITHUB_TOKEN")
GITHUB_TOKEN = "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"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Discord Configuration
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")
DISCORD_USER_ID = os.getenv("DISCORD_USER_ID")

# PR Information
REPO_OWNER = "FounderFeedAdmin" # e.g., "facebook"
REPO_NAME = "TheBundle-AI"         # e.g., "react"
PR_NUMBER = 380               # The number of the PR you want to summarize

# --- Function to get comprehensive PR information ---
def get_pr_comprehensive_info(owner, repo, pr_number):
    """Fetches comprehensive PR information including comments, reviews, and metadata."""
    base_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    pr_info = {}
    
    # Get basic PR information
    print("Fetching PR details...")
    response = requests.get(base_url, headers=headers)
    response.raise_for_status()
    pr_data = response.json()
    
    pr_info['basic'] = {
        'title': pr_data.get('title', ''),
        'description': pr_data.get('body', ''),
        'state': pr_data.get('state', ''),
        'created_at': pr_data.get('created_at', ''),
        'updated_at': pr_data.get('updated_at', ''),
        'user': pr_data.get('user', {}).get('login', ''),
        'base_branch': pr_data.get('base', {}).get('ref', ''),
        'head_branch': pr_data.get('head', {}).get('ref', ''),
        'additions': pr_data.get('additions', 0),
        'deletions': pr_data.get('deletions', 0),
        'changed_files': pr_data.get('changed_files', 0),
        'url': pr_data.get('html_url', '')
    }
    
    # Get PR comments
    print("Fetching PR comments...")
    try:
        comments_url = f"{base_url}/comments"
        comments_response = requests.get(comments_url, headers=headers)
        comments_response.raise_for_status()
        comments_data = comments_response.json()
        
        pr_info['comments'] = []
        for comment in comments_data:
            pr_info['comments'].append({
                'user': comment.get('user', {}).get('login', ''),
                'body': comment.get('body', ''),
                'created_at': comment.get('created_at', ''),
                'path': comment.get('path', ''),
                'line': comment.get('line', '')
            })
    except Exception as e:
        print(f"Could not fetch PR comments: {e}")
        pr_info['comments'] = []
    
    # Get issue comments (general PR discussion)
    print("Fetching issue comments...")
    try:
        issue_comments_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
        issue_comments_response = requests.get(issue_comments_url, headers=headers)
        issue_comments_response.raise_for_status()
        issue_comments_data = issue_comments_response.json()
        
        pr_info['issue_comments'] = []
        for comment in issue_comments_data:
            pr_info['issue_comments'].append({
                'user': comment.get('user', {}).get('login', ''),
                'body': comment.get('body', ''),
                'created_at': comment.get('created_at', '')
            })
    except Exception as e:
        print(f"Could not fetch issue comments: {e}")
        pr_info['issue_comments'] = []
    
    # Get PR reviews
    print("Fetching PR reviews...")
    try:
        reviews_url = f"{base_url}/reviews"
        reviews_response = requests.get(reviews_url, headers=headers)
        reviews_response.raise_for_status()
        reviews_data = reviews_response.json()
        
        pr_info['reviews'] = []
        for review in reviews_data:
            pr_info['reviews'].append({
                'user': review.get('user', {}).get('login', ''),
                'state': review.get('state', ''),
                'body': review.get('body', ''),
                'submitted_at': review.get('submitted_at', '')
            })
    except Exception as e:
        print(f"Could not fetch PR reviews: {e}")
        pr_info['reviews'] = []
    
    # Get files changed (with basic info, not full diff)
    print("Fetching changed files list...")
    try:
        files_url = f"{base_url}/files"
        files_response = requests.get(files_url, headers=headers)
        files_response.raise_for_status()
        files_data = files_response.json()
        
        pr_info['files'] = []
        for file_info in files_data:
            pr_info['files'].append({
                'filename': file_info.get('filename', ''),
                'status': file_info.get('status', ''),
                'additions': file_info.get('additions', 0),
                'deletions': file_info.get('deletions', 0),
                'changes': file_info.get('changes', 0)
            })
    except Exception as e:
        print(f"Could not fetch files: {e}")
        pr_info['files'] = []
    
    return pr_info

# --- Function to format PR summary for Discord ---
def format_for_discord(pr_info, summary):
    """Format the PR analysis for Discord with proper markdown and embeds."""
    
    # Create main embed for PR overview
    embed = {
        "title": f"🔍 PR Analysis: {pr_info['basic']['title'][:100]}{'...' if len(pr_info['basic']['title']) > 100 else ''}",
        "description": f"**Author:** {pr_info['basic']['user']}\n**Branch:** `{pr_info['basic']['head_branch']}` → `{pr_info['basic']['base_branch']}`",
        "url": pr_info['basic']['url'],
        "color": 0x00ff00 if pr_info['basic']['state'] == 'open' else 0x6f42c1,
        "fields": [
            {
                "name": "📊 Statistics",
                "value": f"**Files:** {pr_info['basic']['changed_files']}\n**Changes:** +{pr_info['basic']['additions']} -{pr_info['basic']['deletions']}",
                "inline": True
            },
            {
                "name": "💬 Activity",
                "value": f"**Reviews:** {len(pr_info['reviews'])}\n**Comments:** {len(pr_info['comments']) + len(pr_info['issue_comments'])}",
                "inline": True
            }
        ],
        "timestamp": pr_info['basic']['updated_at'],
        "footer": {
            "text": f"PR #{PR_NUMBER} • {pr_info['basic']['state'].title()}"
        }
    }
    
    return embed

# --- Function to send message to Discord ---
def send_to_discord(pr_info, summary):
    """Send the PR analysis to Discord using webhook."""
    
    if not DISCORD_WEBHOOK_URL:
        print("❌ Discord webhook URL not found in environment variables")
        return False
    
    try:
        # Format the summary for Discord (split into chunks if too long)
        summary_chunks = []
        if len(summary) > 1900:  # Discord embed description limit is ~2048
            # Split summary into sections
            sections = summary.split('\n\n')
            current_chunk = ""
            
            for section in sections:
                if len(current_chunk + section) > 1900:
                    if current_chunk:
                        summary_chunks.append(current_chunk.strip())
                    current_chunk = section
                else:
                    current_chunk += "\n\n" + section if current_chunk else section
            
            if current_chunk:
                summary_chunks.append(current_chunk.strip())
        else:
            summary_chunks = [summary]
        
        # Create main embed
        main_embed = format_for_discord(pr_info, summary)
        
        # Send main message with first part of summary
        webhook_data = {
            "username": "GitHub PR Bot",
            "avatar_url": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
            "embeds": [main_embed],
            "content": f"<@{DISCORD_USER_ID}> New PR Analysis Ready! 🚀"
        }
        
        response = requests.post(DISCORD_WEBHOOK_URL, json=webhook_data)
        response.raise_for_status()
        print("✅ Main PR info sent to Discord successfully!")
        
        # Send summary in separate messages/embeds
        for i, chunk in enumerate(summary_chunks):
            summary_embed = {
                "title": f"📋 Analysis Summary {f'(Part {i+1}/{len(summary_chunks)})' if len(summary_chunks) > 1 else ''}",
                "description": chunk,
                "color": 0x0099ff,
                "footer": {
                    "text": f"Generated by AI • {len(chunk)} chars"
                }
            }
            
            chunk_data = {
                "username": "GitHub PR Bot",
                "avatar_url": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
                "embeds": [summary_embed]
            }
            
            response = requests.post(DISCORD_WEBHOOK_URL, json=chunk_data)
            response.raise_for_status()
            print(f"✅ Summary part {i+1} sent to Discord!")
        
        # Only send additional info if there are significant reviews (optional, based on importance)
        if pr_info['reviews'] and len(pr_info['reviews']) > 1:  # Only if multiple reviews
            review_text = ""
            for review in pr_info['reviews'][-2:]:  # Last 2 reviews only
                status_emoji = {"APPROVED": "✅", "CHANGES_REQUESTED": "❌", "COMMENTED": "💭"}.get(review['state'], "📝")
                review_text += f"{status_emoji} **{review['user']}**: {review['body'][:80] if review['body'] else 'No comment'}\n"
            
            if review_text:
                activity_embed = {
                    "title": "🔍 Key Reviews",
                    "description": review_text[:500],  # Keep it short
                    "color": 0xffa500,
                    "footer": {"text": f"{len(pr_info['reviews'])} total reviews"}
                }
                
                activity_data = {
                    "username": "GitHub PR Bot",
                    "avatar_url": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
                    "embeds": [activity_embed]
                }
                
                response = requests.post(DISCORD_WEBHOOK_URL, json=activity_data)
                response.raise_for_status()
                print("✅ Key reviews sent to Discord!")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending to Discord: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error sending to Discord: {e}")
        return False

# --- Function to get concise summary from Groq ---
def get_comprehensive_summary_from_groq(pr_info):
    """Creates a concise summary prioritizing comments, descriptions, and key changes."""
    client = Groq(api_key=GROQ_API_KEY)
    
    # Prioritize information based on importance
    description = pr_info['basic']['description'] or ''
    has_meaningful_description = len(description.strip()) > 50
    
    # Build comprehensive but focused context for the AI
    context = f"""
# PR Analysis: {pr_info['basic']['title']}

**Author**: {pr_info['basic']['user']} | **Branch**: {pr_info['basic']['head_branch']} → {pr_info['basic']['base_branch']}
**Stats**: {pr_info['basic']['changed_files']} files, +{pr_info['basic']['additions']} -{pr_info['basic']['deletions']}
**Change Scale**: {"Large" if pr_info['basic']['changed_files'] > 20 else "Medium" if pr_info['basic']['changed_files'] > 5 else "Small"} PR
"""
    
    # Always include description if it exists
    if description.strip():
        context += f"\n## Description\n{description}\n"
    
    # Track if we have meaningful context beyond basic info
    has_meaningful_context = False
    
    # Priority 1: Code review comments (most valuable insights)
    if pr_info['comments']:
        context += f"\n## Code Review Comments ({len(pr_info['comments'])} total)\n"
        for comment in pr_info['comments'][:6]:  # Focus on most important comments
            if len(comment['body']) > 20:  # Skip very short comments
                context += f"**{comment['user']}** on `{comment['path']}`: {comment['body'][:250]}\n"
                has_meaningful_context = True
    
    # Priority 2: General discussion comments
    if pr_info['issue_comments']:
        context += f"\n## Discussion Comments ({len(pr_info['issue_comments'])} total)\n"
        for comment in pr_info['issue_comments'][:3]:  # Limit discussion
            if len(comment['body']) > 20:  # Skip very short comments
                context += f"**{comment['user']}**: {comment['body'][:200]}\n"
                has_meaningful_context = True
    
    # Priority 3: Reviews (concise format)
    if pr_info['reviews']:
        context += f"\n## Reviews\n"
        for review in pr_info['reviews']:
            status_emoji = {"APPROVED": "✅", "CHANGES_REQUESTED": "❌", "COMMENTED": "💭"}.get(review['state'], "📝")
            review_body = review['body'][:150] if review['body'] else 'No comment'
            context += f"{status_emoji} **{review['user']}**: {review_body}\n"
            if review['body']:
                has_meaningful_context = True
    
    # Priority 4: Always include key file changes (essential for understanding the PR)
    if pr_info['files']:
        context += f"\n## Key Files Changed\n"
        # Always show the most significant changes
        sorted_files = sorted(pr_info['files'], key=lambda x: x.get('changes', 0), reverse=True)
        
        # Categories for better understanding
        new_files = [f for f in sorted_files if f.get('status') == 'added']
        modified_files = [f for f in sorted_files if f.get('status') == 'modified']
        deleted_files = [f for f in sorted_files if f.get('status') == 'removed']
        
        # Always show top changed files regardless of status
        for file_info in sorted_files[:8]:
            if file_info.get('changes', 0) > 0:
                status_emoji = {"added": "🆕", "modified": "✏️", "removed": "🗑️", "renamed": "📝"}.get(file_info['status'], "📄")
                context += f"{status_emoji} `{file_info['filename']}` (+{file_info['additions']} -{file_info['deletions']})\n"
        
        # Add summary of file types and highlight critical changes
        if len(pr_info['files']) > 8:
            context += f"\n... and {len(pr_info['files']) - 8} more files ({len(new_files)} new, {len(modified_files)} modified, {len(deleted_files)} deleted)\n"
        
        # Identify critical file types for better analysis
        critical_files = []
        config_files = []
        dependency_files = []
        
        for file_info in pr_info['files']:
            filename = file_info['filename'].lower()
            if any(dep in filename for dep in ['package.json', 'package-lock.json', 'requirements.txt', 'composer.json', 'gemfile', 'go.mod', 'cargo.toml', 'poetry.lock']):
                dependency_files.append(file_info['filename'])
            elif any(critical in filename for critical in ['dockerfile', '.env', 'config.js', 'next.config', 'vite.config', 'webpack.config']):
                critical_files.append(file_info['filename'])
            elif any(ext in filename for ext in ['.json', '.yml', '.yaml', '.toml', '.config']):
                config_files.append(file_info['filename'])
        
        if dependency_files:
            context += f"\n📦 Dependencies: {', '.join(dependency_files[:3])}\n"
        if critical_files:
            context += f"\n⚠️ Critical files: {', '.join(critical_files[:3])}\n"
        if config_files and len(config_files) > 3:
            context += f"\n🔧 Configuration changes: {len(config_files)} config files modified\n"
    
    prompt = f"""
Create a CONCISE but COMPLETE PR summary. Ensure ALL major changes are captured.

{context}

Provide a brief summary with these sections:

**🎯 What This PR Does**
- 1-2 sentences explaining the main purpose and scope

**🔧 Key Changes** 
- ALWAYS list the most important technical changes (4-6 bullet points max)
- Include both code changes AND file structure changes (new/deleted files)
- Mention significant features, bug fixes, refactoring, or configuration changes
- DO NOT miss major modifications even if there are comments

**💬 Review Feedback** (only if meaningful comments/reviews exist)
- Summarize key feedback, concerns, or approvals from reviewers

**📁 Major Files** (if significant file operations occurred)
- Highlight important new files, deletions, or major modifications

CRITICAL: 
- Never skip important changes just because comments exist
- Balance comments/reviews with actual code changes
- Ensure technical changes are always prominently featured
- Keep under 1000 characters but don't sacrifice completeness
"""

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",
            max_tokens=800,  # Increased to ensure completeness while staying concise
            temperature=0.1
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        # If the context is still too large, provide a minimal summary
        simple_prompt = f"""
BRIEF PR Summary:

**{pr_info['basic']['title']}**
By: {pr_info['basic']['user']} | {pr_info['basic']['changed_files']} files changed

Description: {pr_info['basic']['description'][:300] if pr_info['basic']['description'] else 'No description provided'}

Create a 3-4 sentence summary of what this PR accomplishes.
"""
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": simple_prompt}
            ],
            model="llama-3.1-8b-instant",
            max_tokens=400,
            temperature=0.1
        )
        return chat_completion.choices[0].message.content

# --- Main execution ---
if __name__ == "__main__":
    try:
        print(f"Gathering comprehensive information for PR #{PR_NUMBER} from {REPO_OWNER}/{REPO_NAME}...")
        pr_info = get_pr_comprehensive_info(REPO_OWNER, REPO_NAME, PR_NUMBER)
        
        print("\nSending comprehensive PR data to Groq for analysis...")
        summary = get_comprehensive_summary_from_groq(pr_info)
        
        print("\n" + "="*80)
        print("                    COMPREHENSIVE PR ANALYSIS")
        print("="*80)
        print(summary)
        
        print("\n" + "="*80)
        print("                    SENDING TO DISCORD")
        print("="*80)
        
        # Send to Discord
        discord_success = send_to_discord(pr_info, summary)
        
        if discord_success:
            print("🎉 PR analysis successfully sent to Discord!")
        else:
            print("⚠️ Failed to send to Discord, but analysis completed successfully.")

    except requests.exceptions.HTTPError as e:
        print(f"Error fetching from GitHub: {e}")
    except Exception as e:
        if "groq" in str(e).lower() or "api" in str(e).lower():
            print(f"Error with Groq API: {e}")
        else:
            print(f"An unexpected error occurred: {e}")