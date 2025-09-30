# GitHub PR Bot - Flask Webhook Server

A Flask-based webhook server that automatically analyzes GitHub pull requests and sends comprehensive summaries to Discord when PR events occur.

## Features

- 🔄 **Real-time PR Analysis**: Automatically triggers when PRs are opened, updated, reopened, or closed
- 🔐 **Secure Webhooks**: HMAC-SHA256 signature verification for webhook security
- 🤖 **AI-Powered Summaries**: Uses Groq AI to generate comprehensive PR analyses
- 💬 **Discord Integration**: Rich embed notifications with PR details and summaries
- 📊 **Comprehensive Analysis**: Includes PR metadata, file changes, comments, and reviews
- 🧪 **Test Endpoint**: Manual testing capability for specific PRs

## Quick Start (Railway Deployment)

### 1. Prepare Your Repository

Ensure you have these files in your repository:

- `app.py` (Flask webhook server)
- `requirements.txt` (Python dependencies)
- `.env.example` (Environment variable template)

### 2. Deploy to Railway

1. **Fork/Clone this repository** to your GitHub account

2. **Create Railway account** at [railway.app](https://railway.app)

3. **Deploy from GitHub**:

   - Click "New Project" → "Deploy from GitHub repo"
   - Select your forked repository
   - Railway will automatically detect the Python app and deploy

4. **Configure Environment Variables**:

   - In Railway dashboard, go to "Variables" tab
   - Add your credentials from `.env.example`:
     ```
     GITHUB_TOKEN=ghp_your_github_token_here
     GROQ_API_KEY=gsk_your_groq_api_key_here
     DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_url
     DISCORD_USER_ID=your_discord_user_id
     WEBHOOK_SECRET=your_random_secret_string
     ```

5. **Get Your Webhook URL**:
   - Copy your Railway app URL (e.g., `https://your-app.railway.app`)
   - Your webhook endpoint will be: `https://your-app.railway.app/webhook`

### 3. Setup GitHub Webhook

1. Go to your target repository settings
2. Navigate to **Settings** → **Webhooks** → **Add webhook**
3. Configure the webhook:
   - **Payload URL**: `https://your-app.railway.app/webhook`
   - **Content type**: `application/json`
   - **Secret**: Your `WEBHOOK_SECRET` from Railway variables
   - **Events**: Select "Pull requests" only
   - **Active**: ✅ Checked

### 4. Test Your Setup

1. **Health Check**: Visit `https://your-app.railway.app/` to verify the server is running
2. **Manual Test**: Use the test endpoint with a POST request to `/test`
3. **Live Test**: Create a test PR in your repository to see the webhook in action

That's it! Your PR bot is now live and will automatically analyze PRs and send notifications to Discord.

## API Endpoints

### `GET /`

Health check endpoint.

**Response:**

```json
{
  "status": "healthy",
  "message": "GitHub PR Bot Webhook Server is running",
  "version": "1.0.0"
}
```

### `POST /webhook`

Main webhook endpoint for GitHub events.

**Headers Required:**

- `X-GitHub-Event: pull_request`
- `X-Hub-Signature-256: sha256=...` (if webhook secret is configured)

**Supported PR Actions:**

- `opened` - New PR created
- `synchronize` - PR updated with new commits
- `reopened` - PR reopened
- `closed` - PR closed/merged
- `ready_for_review` - Draft PR marked ready

### `POST /test`

Manual testing endpoint.

**Request Body:**

```json
{
  "owner": "username",
  "repo": "repository-name",
  "pr_number": 123
}
```

**Response:**

```json
{
  "message": "Test completed successfully",
  "discord_sent": true,
  "summary": "Generated PR summary..."
}
```

## Deployment Options

### 1. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials

# Run development server
python app.py
```

### 2. Production with Gunicorn

```bash
# Install production server
pip install gunicorn

# Run with multiple workers
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# With logging
gunicorn -w 4 -b 0.0.0.0:5000 --access-logfile - --error-logfile - app:app
```

### 3. Railway Deployment

Railway automatically detects Python applications and handles deployment seamlessly.

#### Step-by-Step Railway Deployment:

1. **Create Railway Account**: Sign up at [railway.app](https://railway.app)

2. **Connect GitHub Repository**:

   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your GitHub PR Bot repository

3. **Configure Environment Variables**:

   - Go to your project dashboard
   - Click on "Variables" tab
   - Add the following environment variables:
     ```
     GITHUB_TOKEN=ghp_your_github_token_here
     GROQ_API_KEY=gsk_your_groq_api_key_here
     DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_url
     DISCORD_USER_ID=your_discord_user_id
     WEBHOOK_SECRET=your_random_secret_string
     ```

4. **Deploy**:
   - Railway will automatically detect `requirements.txt`
   - It will install dependencies and start your Flask app
   - Your app will be available at `https://your-app-name.railway.app`

#### Railway Configuration:

Railway automatically:

- Detects Python and installs dependencies from `requirements.txt`
- Runs your Flask app using `python app.py`
- Provides HTTPS URLs for webhooks
- Handles scaling and health checks
- Offers built-in monitoring and logs

#### Custom Start Command (Optional):

If you need a custom start command, create a `railway.toml` file:

```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "gunicorn -w 4 -b 0.0.0.0:$PORT app:app"
```

## Security Configuration

### Webhook Secret Setup

1. Generate a secure random string:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

2. Add to your `.env` file:

```env
WEBHOOK_SECRET=your_generated_secret_here
```

3. Configure the same secret in your GitHub webhook settings

### GitHub Token Permissions

Your GitHub Personal Access Token needs these scopes:

- `repo` (for private repositories) OR `public_repo` (for public repositories)
- `pull_requests:read`
- `issues:read` (for PR discussions)

### Environment Security

- Never commit `.env` files to version control
- Use environment variables in production
- Rotate tokens and secrets regularly
- Use HTTPS for webhook URLs

## Monitoring and Logging

Railway provides built-in monitoring and logging:

### Viewing Logs in Railway:

1. Go to your project dashboard
2. Click on "Deployments" tab
3. Select your active deployment
4. View real-time logs and metrics

### Log Levels

- `INFO`: Normal operations, PR processing
- `WARNING`: Missing optional data, fallback behaviors
- `ERROR`: Failed API calls, Discord delivery failures
- `DEBUG`: Detailed request/response data (development only)

### Railway Monitoring Features:

- **CPU/Memory Usage**: Monitor resource consumption
- **Request Metrics**: Track webhook requests and response times
- **Error Tracking**: Automatic error detection and alerting
- **Health Checks**: Built-in health monitoring

## Troubleshooting

### Common Issues

**1. Webhook not receiving events**

- Check webhook URL is accessible (use tools like ngrok for local testing)
- Verify GitHub webhook configuration
- Check webhook secret matches

**2. Discord messages not sending**

- Verify Discord webhook URL is correct
- Check Discord server permissions
- Ensure webhook URL hasn't expired

**3. GitHub API errors**

- Verify GitHub token has required permissions
- Check API rate limits
- Ensure repository access

**4. Groq API failures**

- Verify API key is valid
- Check Groq service status
- Monitor token usage/limits

### Testing Your Railway Deployment

**Health Check:**

```bash
curl https://your-app.railway.app/
```

**Manual PR Testing:**

```bash
curl -X POST https://your-app.railway.app/test \\
  -H "Content-Type: application/json" \\
  -d '{"owner": "username", "repo": "repository", "pr_number": 123}'
```

**View Railway Logs:**

- Go to your Railway project dashboard
- Click on "Deployments" tab
- Click on the latest deployment to view logs
- Monitor webhook events and any errors

## Advanced Configuration

### Custom Event Filtering

Modify the `process_pr_event` function to handle additional events:

```python
# Skip certain actions
skip_actions = ['assigned', 'unassigned', 'labeled', 'unlabeled']

# Add custom logic for specific actions
if action == 'review_requested':
    # Custom handling for review requests
    pass
```

### Summary Customization

Adjust the Groq prompt in `get_comprehensive_summary_from_groq()`:

```python
prompt = f"""
Your custom prompt here...
Focus on: {specific_areas_of_interest}
"""
```

### Discord Formatting

Customize Discord embeds in `format_for_discord()`:

```python
# Add custom fields
embed["fields"].append({
    "name": "Custom Field",
    "value": "Custom Value",
    "inline": True
})
```

## Migration from GitHub Actions

If migrating from the GitHub Actions version:

1. **Keep existing environment variables** - Most configuration carries over
2. **Remove workflow files** - Delete `.github/workflows/` if no longer needed
3. **Update webhook URL** - Point to your Flask server instead of repository dispatch
4. **Test thoroughly** - Verify all functionality works as expected

## Support

For issues and questions:

1. Check the troubleshooting section above
2. Review application logs for error details
3. Test with the `/test` endpoint for debugging
4. Verify all environment variables are correctly set

## License

MIT License - See LICENSE file for details.
