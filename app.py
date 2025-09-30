import os
import json
import hmac
import hashlib
import requests
from groq import Groq
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# --- Configuration ---
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

# Discord Configuration
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
DISCORD_USER_ID = os.getenv("DISCORD_USER_ID")

# Validate required environment variables
required_vars = ["GITHUB_TOKEN", "GROQ_API_KEY", "DISCORD_WEBHOOK_URL"]
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# --- GitHub Webhook Verification ---
def verify_github_signature(payload_body, signature_header):
    """Verify GitHub webhook signature for security."""
    if not WEBHOOK_SECRET:
        logger.warning("No webhook secret configured - skipping signature verification")
        return True
    
    if not signature_header:
        logger.error("No signature header provided")
        return False
    
    try:
        hash_object = hmac.new(
            WEBHOOK_SECRET.encode('utf-8'),
            payload_body,
            hashlib.sha256
        )
        expected_signature = "sha256=" + hash_object.hexdigest()
        
        if not hmac.compare_digest(expected_signature, signature_header):
            logger.error("Invalid signature")
            return False
        
        return True
    except Exception as e:
        logger.error(f"Error verifying signature: {e}")
        return False

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
    
    try:
        # Get basic PR information
        logger.info(f"Fetching PR details for {owner}/{repo}#{pr_number}")
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
        logger.info("Fetching PR comments...")
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
            logger.warning(f"Could not fetch PR comments: {e}")
            pr_info['comments'] = []
        
        # Get issue comments (general PR discussion)
        logger.info("Fetching issue comments...")
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
            logger.warning(f"Could not fetch issue comments: {e}")
            pr_info['issue_comments'] = []
        
        # Get PR reviews
        logger.info("Fetching PR reviews...")
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
            logger.warning(f"Could not fetch PR reviews: {e}")
            pr_info['reviews'] = []
        
        # Get files changed (with basic info, not full diff)
        logger.info("Fetching changed files list...")
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
            logger.warning(f"Could not fetch files: {e}")
            pr_info['files'] = []
        
        return pr_info
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching PR information: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching PR information: {e}")
        raise

# --- Function to format PR summary for Discord ---
def format_for_discord(pr_info, summary, event_action=None):
    """Format the PR analysis for Discord with proper markdown and embeds."""
    
    # Different colors based on event action
    color_map = {
        'opened': 0x00ff00,      # Green for new PRs
        'synchronize': 0x0099ff,  # Blue for updates
        'reopened': 0xffa500,     # Orange for reopened
        'closed': 0x6f42c1,       # Purple for closed
        'ready_for_review': 0x00ff7f  # Spring green for ready
    }
    
    action_emoji = {
        'opened': '🆕',
        'synchronize': '🔄',
        'reopened': '🔄',
        'closed': '✅' if pr_info['basic'].get('merged') else '❌',
        'ready_for_review': '👀'
    }
    
    # Create main embed for PR overview
    embed = {
        "title": f"{action_emoji.get(event_action, '🔍')} PR {event_action.title() if event_action else 'Analysis'}: {pr_info['basic']['title'][:100]}{'...' if len(pr_info['basic']['title']) > 100 else ''}",
        "description": f"**Author:** {pr_info['basic']['user']}\n**Branch:** `{pr_info['basic']['head_branch']}` → `{pr_info['basic']['base_branch']}`",
        "url": pr_info['basic']['url'],
        "color": color_map.get(event_action, 0x00ff00 if pr_info['basic']['state'] == 'open' else 0x6f42c1),
        "fields": [
            {
                "name": "📊 Statistics",
                "value": f"**Files:** {pr_info['basic']['changed_files']}\n**Changes:** +{pr_info['basic']['additions']} -{pr_info['basic']['deletions']}",
                "inline": True
            },
            {
                "name": "💬 Activity",
                "value": f"**Reviews:** {len(pr_info.get('reviews', []))}\n**Comments:** {len(pr_info.get('comments', [])) + len(pr_info.get('issue_comments', []))}",
                "inline": True
            }
        ],
        "timestamp": pr_info['basic']['updated_at'],
        "footer": {
            "text": f"PR #{pr_info['basic'].get('number', 'Unknown')} • {pr_info['basic']['state'].title()}"
        }
    }
    
    return embed

# --- Function to send message to Discord ---
def send_to_discord(pr_info, summary, event_action=None):
    """Send the PR analysis to Discord using webhook."""
    
    if not DISCORD_WEBHOOK_URL:
        logger.error("Discord webhook URL not found in environment variables")
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
        main_embed = format_for_discord(pr_info, summary, event_action)
        
        # Send main message with first part of summary
        webhook_data = {
            "username": "GitHub PR Bot",
            "avatar_url": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
            "embeds": [main_embed],
            "content": f"<@{DISCORD_USER_ID}> PR {event_action or 'analysis'} notification! 🚀" if DISCORD_USER_ID else f"PR {event_action or 'analysis'} notification! 🚀"
        }
        
        response = requests.post(DISCORD_WEBHOOK_URL, json=webhook_data)
        response.raise_for_status()
        logger.info("Main PR info sent to Discord successfully!")
        
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
            logger.info(f"Summary part {i+1} sent to Discord!")
        
        # Only send additional info if there are significant reviews (optional, based on importance)
        if pr_info.get('reviews') and len(pr_info['reviews']) > 1:  # Only if multiple reviews
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
                logger.info("Key reviews sent to Discord!")
        
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending to Discord: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending to Discord: {e}")
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
    if pr_info.get('comments'):
        context += f"\n## Code Review Comments ({len(pr_info['comments'])} total)\n"
        for comment in pr_info['comments'][:6]:  # Focus on most important comments
            if len(comment['body']) > 20:  # Skip very short comments
                context += f"**{comment['user']}** on `{comment['path']}`: {comment['body'][:250]}\n"
                has_meaningful_context = True
    
    # Priority 2: General discussion comments
    if pr_info.get('issue_comments'):
        context += f"\n## Discussion Comments ({len(pr_info['issue_comments'])} total)\n"
        for comment in pr_info['issue_comments'][:3]:  # Limit discussion
            if len(comment['body']) > 20:  # Skip very short comments
                context += f"**{comment['user']}**: {comment['body'][:200]}\n"
                has_meaningful_context = True
    
    # Priority 3: Reviews (concise format)
    if pr_info.get('reviews'):
        context += f"\n## Reviews\n"
        for review in pr_info['reviews']:
            status_emoji = {"APPROVED": "✅", "CHANGES_REQUESTED": "❌", "COMMENTED": "💭"}.get(review['state'], "📝")
            review_body = review['body'][:150] if review['body'] else 'No comment'
            context += f"{status_emoji} **{review['user']}**: {review_body}\n"
            if review['body']:
                has_meaningful_context = True
    
    # Priority 4: Always include key file changes (essential for understanding the PR)
    if pr_info.get('files'):
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
        logger.error(f"Error getting summary from Groq: {e}")
        # If the context is still too large, provide a minimal summary
        simple_prompt = f"""
BRIEF PR Summary:

**{pr_info['basic']['title']}**
By: {pr_info['basic']['user']} | {pr_info['basic']['changed_files']} files changed

Description: {pr_info['basic']['description'][:300] if pr_info['basic']['description'] else 'No description provided'}

Create a 3-4 sentence summary of what this PR accomplishes.
"""
        
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "user", "content": simple_prompt}
                ],
                model="llama-3.1-8b-instant",
                max_tokens=400,
                temperature=0.1
            )
            return chat_completion.choices[0].message.content
        except Exception as fallback_error:
            logger.error(f"Fallback summary also failed: {fallback_error}")
            return f"**{pr_info['basic']['title']}**\n\nAuthor: {pr_info['basic']['user']}\nFiles changed: {pr_info['basic']['changed_files']}\nChanges: +{pr_info['basic']['additions']} -{pr_info['basic']['deletions']}\n\nDescription: {pr_info['basic']['description'][:200] if pr_info['basic']['description'] else 'No description provided'}"

# --- Process PR Event ---
def process_pr_event(payload):
    """Process a PR event and send analysis to Discord."""
    try:
        action = payload.get('action')
        pr_data = payload.get('pull_request', {})
        repository = payload.get('repository', {})
        
        owner = repository.get('owner', {}).get('login')
        repo = repository.get('name')
        pr_number = pr_data.get('number')
        
        if not all([owner, repo, pr_number]):
            logger.error(f"Missing required data: owner={owner}, repo={repo}, pr_number={pr_number}")
            return False
        
        logger.info(f"Processing PR {action} event for {owner}/{repo}#{pr_number}")
        
        # Skip certain actions that don't need analysis
        skip_actions = ['assigned', 'unassigned', 'labeled', 'unlabeled', 'review_requested', 'review_request_removed']
        if action in skip_actions:
            logger.info(f"Skipping action '{action}' - no analysis needed")
            return True
        
        # Get comprehensive PR information
        pr_info = get_pr_comprehensive_info(owner, repo, pr_number)
        pr_info['basic']['number'] = pr_number  # Add PR number to basic info
        
        # Generate summary
        summary = get_comprehensive_summary_from_groq(pr_info)
        
        # Send to Discord
        discord_success = send_to_discord(pr_info, summary, action)
        
        if discord_success:
            logger.info(f"Successfully processed PR {action} event for #{pr_number}")
            return True
        else:
            logger.error(f"Failed to send Discord notification for PR #{pr_number}")
            return False
            
    except Exception as e:
        logger.error(f"Error processing PR event: {e}")
        return False

# --- Flask Routes ---

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "message": "GitHub PR Bot Webhook Server is running",
        "version": "1.0.0"
    })

@app.route('/webhook', methods=['POST'])
def github_webhook():
    """Handle GitHub webhook events."""
    try:
        # Get raw payload for signature verification
        payload_body = request.get_data()
        signature_header = request.headers.get('X-Hub-Signature-256')
        
        # Verify signature if webhook secret is configured
        if WEBHOOK_SECRET and not verify_github_signature(payload_body, signature_header):
            logger.error("Invalid webhook signature")
            return jsonify({"error": "Invalid signature"}), 401
        
        # Parse JSON payload
        try:
            payload = request.get_json()
        except Exception as e:
            logger.error(f"Invalid JSON payload: {e}")
            return jsonify({"error": "Invalid JSON payload"}), 400
        
        if not payload:
            logger.error("Empty payload received")
            return jsonify({"error": "Empty payload"}), 400
        
        # Check if this is a pull request event
        event_type = request.headers.get('X-GitHub-Event')
        if event_type != 'pull_request':
            logger.info(f"Ignoring event type: {event_type}")
            return jsonify({"message": f"Event type '{event_type}' ignored"}), 200
        
        # Process the PR event
        success = process_pr_event(payload)
        
        if success:
            return jsonify({"message": "PR event processed successfully"}), 200
        else:
            return jsonify({"error": "Failed to process PR event"}), 500
            
    except Exception as e:
        logger.error(f"Unexpected error in webhook handler: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/test', methods=['POST'])
def test_endpoint():
    """Test endpoint for manual PR analysis."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "JSON payload required"}), 400
        
        owner = data.get('owner')
        repo = data.get('repo')
        pr_number = data.get('pr_number')
        
        if not all([owner, repo, pr_number]):
            return jsonify({
                "error": "Missing required fields: owner, repo, pr_number"
            }), 400
        
        logger.info(f"Manual test for PR {owner}/{repo}#{pr_number}")
        
        # Get comprehensive PR information
        pr_info = get_pr_comprehensive_info(owner, repo, pr_number)
        pr_info['basic']['number'] = pr_number
        
        # Generate summary
        summary = get_comprehensive_summary_from_groq(pr_info)
        
        # Send to Discord
        discord_success = send_to_discord(pr_info, summary, 'manual_test')
        
        return jsonify({
            "message": "Test completed successfully",
            "discord_sent": discord_success,
            "summary": summary
        }), 200
        
    except Exception as e:
        logger.error(f"Error in test endpoint: {e}")
        return jsonify({"error": str(e)}), 500

# --- Error Handlers ---

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# --- Main execution ---
if __name__ == "__main__":
    # Ensure we have all required configuration
    if not all([GITHUB_TOKEN, GROQ_API_KEY, DISCORD_WEBHOOK_URL]):
        logger.error("Missing required environment variables")
        exit(1)
    
    # Get port from environment or default to 5000
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting GitHub PR Bot Webhook Server on port {port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Webhook secret configured: {bool(WEBHOOK_SECRET)}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )