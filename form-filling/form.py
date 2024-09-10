import PyPDF2
import requests
import json
import time
from openai import OpenAI
import re

#TODO: INPUT MULTION_API_KEY HERE
API_KEY = "your_multion_api_key_here"

#TODO: INPUT OPENAI_API_KEY HERE
client = OpenAI(api_key='your_openai_api_key_here')

def extract_cv_data(cv_file_path):
    with open(cv_file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text.strip()

def create_session(url):
    endpoint = "https://api.multion.ai/v1/web/session/"
    headers = {
        "X_MULTION_API_KEY": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "url": url,
        "local": True, #TODO: Change to False in production
        "include_screenshot": True,
        "optional_params": {
            "source": "playground"
        }
    }
    response = requests.post(endpoint, json=payload, headers=headers)
    return response.json()

def browse(session_id,cmd):
    endpoint = "https://api.multion.ai/v1/web/browse"
    headers = {
        "X_MULTION_API_KEY": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "cmd": cmd,
        "session_id": session_id,
        "local": True,  # Change to False for production
        "optional_params": {
            "source": "playground"
        }
    }
    if url:
        payload["url"] = url
    if session_id:
        payload["session_id"] = session_id

    response = requests.post(endpoint, json=payload, headers=headers)
    return response.json()

def step_session(session_id, cmd):
    endpoint = f"https://api.multion.ai/v1/web/session/{session_id}"
    headers = {
        "X_MULTION_API_KEY": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {"cmd": cmd}
    response = requests.post(endpoint, json=payload, headers=headers)
    return response.json()

def close_session(session_id):
    endpoint = f"https://api.multion.ai/v1/web/session/{session_id}"
    headers = {"X_MULTION_API_KEY": API_KEY}
    requests.delete(endpoint, headers=headers)

# Format the CV data into a structured JSON response
def get_structured_cv_data(cv_text, form_fields):
    prompt = f"""
    Given the following CV text and form fields, create a structured JSON response.
    For fields not found in the CV, use "(USER TO FILL)" as the value.
    
    CV Text:
    {cv_text}
    
    Form Fields:
    {json.dumps(form_fields, indent=2)}
    
    Respond with a JSON in this format:
    {{
        "filled_fields": [
            {{"name": "Field Name", "value": "Filled Value or (USER TO FILL)"}}
        ],
        "requires_user_input": true or false
    }}
    """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return json.loads(response.choices[0].message.content)

def parse_fields_from_message(message):
    # Try to parse the entire message as JSON first
    try:
        json_data = json.loads(message)
        if 'fields' in json_data:
            return json_data['fields']
    except json.JSONDecodeError:
        pass

    # If that fails, try to extract JSON from the message
    json_match = re.search(r'\{[\s\S]*\}', message)
    if json_match:
        try:
            json_data = json.loads(json_match.group(0))
            if 'fields' in json_data:
                return json_data['fields']
        except json.JSONDecodeError:
            pass

    # If both methods fail, fall back to line-by-line parsing
    fields = []
    for line in message.split('\n'):
        match = re.match(r'\d+\.\s*(\{.*\})', line)
        if match:
            try:
                field = json.loads(match.group(1))
                fields.append(field)
            except json.JSONDecodeError:
                print(f"Warning: Could not parse field: {line}")
    return fields

def perform_action_with_retry(action, max_retries=3, delay=5):
    for attempt in range(max_retries):
        result = action()
        if result.get('status') != 'ERROR':
            return result
        print(f"Attempt {attempt + 1} failed. Retrying in {delay} seconds...")
        time.sleep(delay)
    print(f"Action failed after {max_retries} attempts.")
    return result

if __name__ == "__main__":

    #TODO: INPUT CV FILE PATH HERE
    # Extract CV data from PDF
    cv_text = extract_cv_data('YourCV.pdf')
    
    #TODO: INPUT FORM URL HERE
    # Set the form URL
    url = "https://your-form-url-here.com"

    # Create a session with the form URL
    session = create_session(url)
    print("Session creation response:", json.dumps(session, indent=2))

    if 'session_id' not in session:
        print("Error: 'session_id' not found in the response. Cannot proceed.")
        exit(1)

    session_id = session['session_id']
    print(f"Session created with ID: {session_id}")

    # Get form fields
    cmd = """
    Find all the form fields and list them in the following JSON format:
    {
        "fields": [
            {"name": "Field Name", "type": "Field Type", "options": ["Option1", "Option2"] if applicable}
        ]
    }
    Make sure that all the subfields are included as fields to be filled.
    """
    response = perform_action_with_retry(lambda: browse(session_id, cmd))
    print("Form fields response:", json.dumps(response, indent=2))

    if response.get('status') == 'DONE':
        # Parse form fields from the response
        form_fields = parse_fields_from_message(response['message'])
        if not form_fields:
            print("Error: Could not extract form fields from the response message.")
            exit(1)

        print("Extracted form fields:", json.dumps(form_fields, indent=2))

        # Get structured CV data based on form fields
        structured_cv_data = get_structured_cv_data(cv_text, form_fields)
        print("Structured CV data:", json.dumps(structured_cv_data, indent=2))

        # Scroll back to the top of the form
        scroll = browse(session_id, "Scroll back up")
        
        if scroll.get('status') == 'DONE':
            # Fill the form with structured CV data
            fill_cmd = f"""
            Fill the form fields using this data:
            {json.dumps(structured_cv_data, indent=2)}
            For fields marked (USER TO FILL), leave them blank.
            Respond with a JSON in this format:
            {{
                "status": "DONE" or "ASK_USER",
                "filled_fields": [
                    {{"name": "Field Name", "value": "Filled Value"}}
                ],
                "empty_fields": ["Field Name 1", "Field Name 2"]
            }}
            """
            fill = perform_action_with_retry(lambda: browse(session_id, fill_cmd))
            print("Fill response:", json.dumps(fill, indent=2))

            # If user input is needed, wait for 60 seconds
            if fill.get('status') == 'ASK_USER':
                print("Waiting for 60 seconds to allow user interaction...")
                time.sleep(60)

            # Check if all fields are filled correctly
            check_cmd = """
            Check all fields are filled correctly. Respond with a JSON in this format:
            {
                "status": "DONE" or "ASK_USER",
                "empty_fields": ["Field Name 1", "Field Name 2"] if any
            }
            """
            check = perform_action_with_retry(lambda: browse(session_id, check_cmd))
            print("Check response:", json.dumps(check, indent=2))

            if check.get('status') == 'DONE':
                # Submit the form
                submit_cmd = """
                Submit the form and wait for confirmation. Respond with: SUBMITTED}
                """
                submit = perform_action_with_retry(lambda: browse(session_id, submit_cmd))
                print("Submit response:", json.dumps(submit, indent=2))

                if submit.get('status') == 'DONE':
                    print("Form submitted successfully!")
                else:
                    print(f"Error: Form submission failed. Status: {submit.get('status')}")
            elif check.get('status') == 'ASK_USER':
                print("Some fields are still empty. Please fill them manually.")
            else:
                print(f"Unexpected status: {check.get('status')}")
        else:
            print(f"Error: Failed to scroll to the top of the form. Status: {scroll.get('status')}")
    else:
        print(f"Error: Failed to get form fields. Status: {response.get('status')}")

    # Close the session
    close_session(session_id)



