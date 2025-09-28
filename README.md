# GitHub PR Analysis Bot - Automated Workflow

This setup allows your PR analysis bot to automatically run whenever there's a new PR in any target repository, even if the bot code is in a different repository.

## 🏗️ Architecture

```
Target Repository (FounderFeedAdmin/TheBundle-AI)
    ├── New PR created
    ├── Trigger workflow runs
    └── Sends repository_dispatch to Bot Repository

Bot Repository (YourUsername/GithubPRBot)
    ├── Receives repository_dispatch
    ├── Runs PR analysis workflow
    ├── Fetches PR data from target repo
    ├── Generates AI summary
    └── Sends results to Discord
```

## 🚀 Quick Setup

### 1. Set Up Bot Repository (This Repository)

1. **Add GitHub Secrets** (Settings → Secrets and variables → Actions):

   ```
   GROQ_API_KEY=
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
   DISCORD_USER_ID=
   PERSONAL_ACCESS_TOKEN=ghp_... (GitHub token with repo permissions)
   ```

2. **The workflow is already set up** in `.github/workflows/pr-analysis.yml`

### 2. Set Up Target Repository (FounderFeedAdmin/TheBundle-AI)

1. **Create workflow file**: `.github/workflows/trigger-pr-bot.yml`

   ```yaml
   name: Trigger PR Analysis Bot

   on:
     pull_request:
       types: [opened, reopened, synchronize]

   jobs:
     trigger-analysis:
       runs-on: ubuntu-latest

       steps:
         - name: Trigger PR Analysis Bot
           uses: peter-evans/repository-dispatch@v2
           with:
             token: ${{ secrets.PERSONAL_ACCESS_TOKEN }}
             repository: YourUsername/GithubPRBot # Replace with your bot repo
             event-type: pr-opened
             client-payload: |
               {
                 "pr_number": ${{ github.event.pull_request.number }},
                 "repo_owner": "${{ github.repository_owner }}",
                 "repo_name": "${{ github.event.repository.name }}",
                 "action": "${{ github.event.action }}",
                 "pr_title": "${{ github.event.pull_request.title }}",
                 "pr_author": "${{ github.event.pull_request.user.login }}"
               }
   ```

2. **Add the PERSONAL_ACCESS_TOKEN secret** to the target repository

## 🔑 Required Secrets

### Bot Repository Secrets

- `GROQ_API_KEY` - Your Groq API key
- `DISCORD_WEBHOOK_URL` - Discord webhook URL
- `DISCORD_USER_ID` - Your Discord user ID for mentions
- `PERSONAL_ACCESS_TOKEN` - GitHub token (not used in bot repo, but good to have)

### Target Repository Secrets

- `PERSONAL_ACCESS_TOKEN` - GitHub Personal Access Token with `repo` permissions

## 🧪 Testing

### Manual Testing

1. Go to your bot repository → Actions → "PR Analysis Bot"
2. Click "Run workflow"
3. Enter:
   - PR Number: `357`
   - Repository Owner: `FounderFeedAdmin`
   - Repository Name: `TheBundle-AI`
4. Click "Run workflow"

### Automatic Testing

1. Create a new PR in the target repository
2. The trigger workflow should run automatically
3. Check the bot repository Actions tab for the analysis workflow
4. Check Discord for the analysis results

### Local Testing

```bash
# Set environment variables
export REPO_OWNER=FounderFeedAdmin
export REPO_NAME=TheBundle-AI
export PR_NUMBER=357
export GITHUB_TOKEN=your_github_token

# Run the workflow script
python main_workflow.py
```

## 📁 File Structure

```
GithubPRBot/
├── .github/workflows/
│   └── pr-analysis.yml          # Main workflow (runs in bot repo)
├── main_workflow.py             # Workflow-compatible version of main.py
├── trigger-workflow-template.yml # Template for target repo
├── setup_workflow.py            # Setup guide script
├── main.py                      # Original standalone script
├── .env                         # Local environment variables
└── README_WORKFLOW.md           # This file
```

## 🔄 How It Works

1. **PR Created**: New PR created in target repository (FounderFeedAdmin/TheBundle-AI)
2. **Trigger**: Target repo workflow sends `repository_dispatch` event to bot repo
3. **Analysis**: Bot repo workflow receives event and runs PR analysis
4. **Processing**: Fetches PR data, generates AI summary with Groq
5. **Notification**: Sends formatted results to Discord with mentions

## ⚡ Features

- **Automatic triggering** on new PRs, reopened PRs, and PR updates
- **Cross-repository support** - bot can analyze PRs in any repository
- **Manual execution** for testing or analyzing specific PRs
- **Comprehensive analysis** including comments, reviews, file changes
- **Discord integration** with rich embeds and user mentions
- **Error handling** and logging for debugging
- **Artifact storage** saves analysis results for later review

## 🛠️ Customization

### Monitor Different Repositories

Change the repository details in the target repo's trigger workflow:

```yaml
repository: YourUsername/GithubPRBot # Your bot repository
```

### Modify Trigger Events

Edit the `on:` section in the target repo workflow:

```yaml
on:
  pull_request:
    types: [opened, reopened, synchronize, closed] # Add more events
```

### Adjust Analysis Settings

Modify `main_workflow.py`:

- Change AI model or parameters
- Customize Discord message format
- Add more data sources (issues, commits, etc.)

## 🚨 Troubleshooting

### Workflow Not Triggering

- Check if PERSONAL_ACCESS_TOKEN has `repo` permissions
- Verify the bot repository name is correct in target repo workflow
- Ensure both repositories have Actions enabled

### Analysis Fails

- Check GitHub token permissions
- Verify all secrets are set correctly
- Look at workflow logs in Actions tab

### Discord Not Working

- Verify webhook URL is correct
- Check if Discord server allows webhooks
- Ensure user ID is correct for mentions

## 📊 Monitoring

- **GitHub Actions**: Check workflow runs in both repositories
- **Discord**: Monitor for analysis messages
- **Artifacts**: Download saved analysis files from workflow runs
- **Logs**: Review workflow logs for debugging

## 🔐 Security

- All sensitive data stored as GitHub secrets
- Tokens have minimal required permissions
- No sensitive data in logs or artifacts
- Webhook URLs are not exposed in code
