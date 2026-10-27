import os
import requests
from google import genai

repo = os.environ['REPO']
pr_number = os.environ['PR_NUMBER']
gh_token = os.environ['GITHUB_TOKEN']
gemini_key = os.environ['GEMINI_API_KEY']

# 1. Fetch the Pull Request Diff from GitHub
headers = {
    'Authorization': f'Bearer {gh_token}',
    'Accept': 'application/vnd.github.v3.diff'
}
diff_url = f'https://api.github.com/repos/{repo}/pulls/{pr_number}'
diff_response = requests.get(diff_url, headers=headers)
diff_text = diff_response.text

# Skip empty diffs
if not diff_text.strip():
    print("No diff found. Exiting.")
    exit(0)

# 2. Send the diff to Gemini
client = genai.Client(api_key=gemini_key)
prompt = (
    "You are a strict but helpful senior developer. Review the following pull request diff. "
    "Focus on bugs, security vulnerabilities, performance issues, and architectural flaws. "
    "Skip trivial style nits. Output your review in Markdown format.\n\n"
    f"{diff_text}"
)

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt
)
review_comment = response.text

# 3. Post the review as a PR comment
post_url = f'https://api.github.com/repos/{repo}/issues/{pr_number}/comments'
requests.post(
    post_url, 
    headers={'Authorization': f'Bearer {gh_token}'}, 
    json={'body': f"### 🤖 Gemini Code Review\n\n{review_comment}"}
)