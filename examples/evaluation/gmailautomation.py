import os.path
import base64
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
import os
import openai
from langchain.agents.agent_toolkits import MultionToolkit
import os
import multion

# Get the API key from the environment variable
openai_api_key = os.environ.get('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')

# Now you can use openai_api_key in your script

# OAuth2.0 for Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

creds = None
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json')

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

# Build the Gmail service
service = build('gmail', 'v1', credentials=creds)

# Get today's date in YYYY-MM-DD format
today_date = datetime.today().strftime('%Y-%m-%d')
today = datetime.today().strftime('%Y-%m-%d')
tomorrow = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')
# Search for emails from "Morning Brew" sent today
query = f'from:crew@morningbrew.com after:{today} before:{tomorrow}'
messages = []
next_page_token = None

while True:
    response = service.users().messages().list(userId='me', q=query, pageToken=next_page_token).execute()
    if 'messages' in response:
        messages.extend(response['messages'])
    next_page_token = response.get('nextPageToken', None)
    if not next_page_token:
        break

# Fetch and print the body of each email
for message in messages:
    email_data = service.users().messages().get(userId='me', id=message['id']).execute()
    try:
        # Get the email data from the "parts" of the email
        for part in email_data['payload']['parts']:
            if part['mimeType'] == 'text/plain':
                email_body = part['body']['data']
                break
        # Decode the base64 email body to plain text
        email_body_decoded = base64.urlsafe_b64decode(email_body).decode('utf-8')
        print(email_body_decoded)
    except Exception as e:
        print(f"Couldn't decode email: {e}")
if not messages:
    print("No emails found matching the query.")
else:
    print(f"Found {len(messages)} emails matching the query.")

for message in messages:
    email_data = service.users().messages().get(userId='me', id=message['id']).execute()
    try:
        # Get the email data from the "parts" of the email
        email_body = None
        for part in email_data['payload']['parts']:
            if part['mimeType'] == 'text/plain':
                email_body = part['body']['data']
                break
        if email_body:
            # Decode the base64 email body to plain text
            email_body_decoded = base64.urlsafe_b64decode(email_body).decode('utf-8')
            email_content=email_body_decoded
        else:
            print(f"Email with ID {message['id']} is not in 'text/plain' format.")
    except Exception as e:
        print(f"Couldn't decode email with ID {message['id']}: {e}")

import openai

def split_content_into_ten(content):
    """Split content approximately into ten parts."""
    size = len(content) // 10
    parts = []
    for i in range(9):
        end = content.rfind(' ', i*size, (i+1)*size)  # Find the last space before the next boundary
        parts.append(content[i*size:end])
    parts.append(content[9*size:])
    return parts

# Split content into chunks
parts = split_content_into_ten(email_content)

# Summarize each part
summaries = []

for part in parts:
    response = openai.Completion.create(
        engine="davinci",
        prompt=f"create a linkedin post of bullet pointds to the following email content:\n\n{part}\n",
        max_tokens=100  # Adjust as needed
    )
    summaries.append(response.choices[0].text.strip())

# Combine summaries
combined_summary = ' '.join(summaries)
print(combined_summary)

multion.login()
from langchain import OpenAI
from langchain.agents import initialize_agent, AgentType
llm = OpenAI(temperature=0)
from langchain.agents.agent_toolkits import MultionToolkit
toolkit = MultionToolkit()
tools=toolkit.get_tools()
agent = initialize_agent(
    tools=toolkit.get_tools(),
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose = True
)

agent.run(
    "Open linkedin, signin to the account, post this {combined_summary} by clicking on new post, click post after writing this content."
)
