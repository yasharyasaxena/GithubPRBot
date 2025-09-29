# GitHub PR Analysis Bot 🤖

An intelligent GitHub PR analyzer that provides comprehensive summaries using AI, with Discord integration for team notifications.

## 🚀 Features

- **AI-Powered Analysis**: Uses Groq AI to generate concise, intelligent PR summaries
- **Comprehensive Context**: Analyzes PR descriptions, comments, reviews, and file changes
- **Discord Integration**: Sends formatted analysis results to Discord with rich embeds
- **Cross-Repository Support**: Can analyze PRs from any public/accessible repository
- **Multiple Execution Options**: Manual execution or automated via GitHub Actions

## 📁 Project Structure

```
GithubPRBot/
├── main.py                           # Main script for manual execution
├── main_workflow.py                  # GitHub Actions compatible version
├── .github/workflows/pr-analysis.yml # GitHub Actions workflow
├── trigger-workflow-template.yml     # Template for target repository
├── .env                             # Environment variables (local)
├── README.md                        # This file
└── venv/                           # Python virtual environment
```

## �️ Setup

### Environment Variables

Create a `.env` file with:

```env
GROQ_API_KEY=your_groq_api_key
DISCORD_WEBHOOK_URL=your_discord_webhook_url
DISCORD_USER_ID=your_discord_user_id
```

### Dependencies

Install required packages:

```bash
pip install requests groq python-dotenv
```

## 🎯 Usage Options

### Option 1: Manual Execution

1. **Configure the PR details** in `main.py`:

   ```python
   REPO_OWNER = "FounderFeedAdmin"
   REPO_NAME = "TheBundle-AI"
   PR_NUMBER = 357
   ```

2. **Run the script**:
   ```bash
   python main.py
   ```

### Option 2: GitHub Actions (When Enabled)

1. **Add GitHub Secrets** (Settings → Secrets and variables → Actions):

   ```
   GROQ_API_KEY=your_groq_api_key
   DISCORD_WEBHOOK_URL=your_discord_webhook_url
   DISCORD_USER_ID=your_discord_user_id
   PERSONAL_ACCESS_TOKEN=github_token_with_repo_permissions
   ```

2. **The workflow is already set up** in `.github/workflows/pr-analysis.yml`

3. **Set up target repository** with trigger workflow:
   - Copy `trigger-workflow-template.yml` to target repo
   - Place in `.github/workflows/trigger-pr-bot.yml`
   - Update repository reference to your bot repo
   - Add `PERSONAL_ACCESS_TOKEN` secret to target repository

### Option 3: Manual Workflow Execution

Run specific PR analysis via GitHub Actions UI:

1. Go to Actions → PR Analysis Bot
2. Click "Run workflow"
3. Enter PR details manually

## � Configuration

### Target Repository

Edit these values in `main.py`:

```python
REPO_OWNER = "YourOrg"      # Repository owner
REPO_NAME = "YourRepo"      # Repository name
PR_NUMBER = 123             # PR number to analyze
```

### Discord Integration

The bot sends rich Discord embeds with:

- PR overview and statistics
- AI-generated analysis summary
- Key file changes
- Review feedback (when available)
- User mentions for notifications

## 📊 Analysis Output

The bot provides:

**🎯 What This PR Does**

- Brief explanation of the PR's main purpose

**🔧 Key Changes**

- Technical changes and modifications
- New features, bug fixes, refactoring
- File structure changes

**💬 Review Feedback**

- Summary of reviewer comments and concerns
- Code review insights

**📁 Major Files**

- Significant file additions, modifications, deletions
- Critical configuration changes

## 🤖 AI Analysis

- **Smart Context Building**: Prioritizes meaningful comments and descriptions
- **Comprehensive Coverage**: Never misses important technical changes
- **Concise Output**: Focused summaries under 1000 characters
- **Multi-source Analysis**: Combines PR description, comments, reviews, and file changes

## � Security

- All sensitive data stored in environment variables
- GitHub token with minimal required permissions
- Discord webhook URLs kept secure
- No sensitive information logged

## 🧪 Testing

### Local Testing

```bash
# For manual execution
python main.py

# For workflow testing (set environment variables first)
python main_workflow.py
```

### GitHub Actions Testing (When Enabled)

1. Go to Actions → PR Analysis Bot → Run workflow
2. Enter PR details manually
3. Check Discord for results

## � Future Enhancements

- Support for multiple target repositories
- Customizable analysis templates
- Integration with more AI models
- Slack integration option
- Scheduled analysis reports
- Webhook-based automation (alternative to GitHub Actions)

## 📝 License

MIT License - feel free to use and modify for your projects.

---

**Made with ❤️ for better PR reviews and team collaboration**
