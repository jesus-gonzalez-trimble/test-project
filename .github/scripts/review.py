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

# 2. Fetch the custom prompt from the remote repository
prompt_url = 'https://raw.githubusercontent.com/trimble-xchange/connector-app-builder/refs/heads/master/CodeIntake/Connectivity.CodeIntake.Shared/CodeRepository/Templates/gemini-instructions.md?token=GHSAT0AAAAAAEHDLPI7FVF3TP463YRBQ3ZU2XA6LXA'
prompt_response = requests.get(prompt_url)

if prompt_response.status_code != 200:
    print(f"Failed to load prompt. Status: {prompt_response.status_code}")
    exit(1)

base_prompt = prompt_response.text

# 3. Combine the remote prompt with the PR diff
full_prompt = f"{base_prompt}\n\n{diff_text}"

# 4. Send to Gemini
client = genai.Client(api_key=gemini_key)
response = client.models.generate_content(
    model='gemini-3.8-flash',
    contents=full_prompt
)
review_comment = response.text

# 5. Post the review as a PR comment
post_url = f'https://api.github.com/repos/{repo}/issues/{pr_number}/comments'
requests.post(
    post_url, 
    headers={'Authorization': f'Bearer {gh_token}'}, 
    json={'body': f"### 🤖 Gemini Code Review\n\n{review_comment}"}
)