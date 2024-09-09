import PyPDF2
import requests
import json
import time

#TODO: INPUT MULTION_API_KEY HERE
API_KEY = "your_api_key_here"

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

if __name__ == "__main__":

    #TODO: INPUT CV FILE PATH HERE
    cv_text = extract_cv_data('YourCV.pdf')
    #TODO: INPUT FORM URL HERE
    url = "https://your-form-url-here.com"

    #Create a session with the form URL
    session = create_session(url)
    print("Session creation response:", json.dumps(session, indent=2))

    if 'session_id' not in session:
        print("Error: 'session_id' not found in the response. Cannot proceed.")
        exit(1)

    session_id = session['session_id']
    print(f"Session created with ID: {session_id}")

    # Send command to check MultiOn with the CV text and ask it to fill the form fields
    check_cv_cmd = f"""
    Analyze this CV text: "{cv_text}"

    Use it to fill the form fields. 
    
    If any of the fields are empty on the form, ask me for the information. DO NOT ASK ME FOR ANY INFORMATION THAT IS NOT RELATED TO THE FORM.

    """

    cv_check = step_session(session_id, check_cv_cmd)
    print("CV check response:", json.dumps(cv_check, indent=2))

    # Continue the session until we get ASK_USER status
    while cv_check.get('status') != 'ASK_USER':
        if cv_check.get('status') == 'DONE':
            print("Process completed without requiring user input.")
            break
        elif cv_check.get('status') == 'CONTINUE':
            print("Continuing the session...")
            #Check if all the fields are filled
            cv_check = step_session(session_id, "Have you filled in all the fields in the form?")
            field_complete = True
            print("Step response:", json.dumps(cv_check, indent=2))
        else:
            print(f"Unexpected status: {cv_check.get('status')}")
            break
        time.sleep(2)  

    # Ask user for input if the form is not complete
    if cv_check.get('status') == 'ASK_USER':
        print("User input required. Message:", cv_check.get('message'))
        user_input = input("Please provide the required information: ")
        cv_check = step_session(session_id, user_input)
        print("User input response:", json.dumps(cv_check, indent=2))

    #Submit the form and wait for the confirmation message
    if field_complete:
        cv_check = step_session(session_id, "Submit the form and wait for the confirmation message")
        submit = True
        print("Step response:", json.dumps(cv_check, indent=2))

    #Close the session if the form is submitted
    if submit:
        close_session(session_id)
        print("Session closed.")

