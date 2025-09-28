import requests

GITHUB_TOKEN = "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"
REPO_OWNER = "FounderFeedAdmin"
REPO_NAME = "TheBundle-AI"
PR_NUMBER = 357

def test_repo_access():
    """Test if we can access the repository"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    response = requests.get(url, headers=headers)
    print(f"Repository access test: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    return response.status_code == 200

def test_pr_access():
    """Test if we can access the specific PR"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{PR_NUMBER}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    response = requests.get(url, headers=headers)
    print(f"PR access test: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    else:
        data = response.json()
        print(f"PR Title: {data.get('title', 'N/A')}")
        print(f"PR State: {data.get('state', 'N/A')}")
    return response.status_code == 200

def test_token_validity():
    """Test if the token is valid"""
    url = "https://api.github.com/user"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    
    response = requests.get(url, headers=headers)
    print(f"Token validity test: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Authenticated as: {data.get('login', 'N/A')}")
    else:
        print(f"Token error: {response.text}")
    return response.status_code == 200

if __name__ == "__main__":
    print("Testing GitHub API access...")
    print("=" * 50)
    
    if test_token_validity():
        print("\n✓ Token is valid")
    else:
        print("\n✗ Token is invalid")
        exit(1)
    
    if test_repo_access():
        print("✓ Repository is accessible")
    else:
        print("✗ Repository is not accessible")
        exit(1)
    
    if test_pr_access():
        print("✓ PR is accessible")
    else:
        print("✗ PR is not accessible")