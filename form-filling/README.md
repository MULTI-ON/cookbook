# Form Filling Example

This Python script automates submitting a CV (resume) to an online form. It reads your PDF CV, fills out a web form, and submits it automatically.

This example demonstrates direct interaction with the API endpoints. Alternatively, you can use the MultiOn SDK in your preferred programming language. For more information, refer to the [MultiOn Quickstart](https://docs.multion.ai/quick-start) documentation.

<div style="width: 100%; height: 0; padding-bottom: 56.25%; position: relative;">
  <img src="demo.gif" alt="Form Filling Demo" style="position: absolute; width: 100%; height: 100%; left: 0; top: 0;">
</div>

## MultiOn Documentation

This example demonstrates direct interaction with the API endpoints. Alternatively, you can use the MultiOn SDK in your preferred programming language. For more information, refer to the [MultiOn Quickstart](https://docs.multion.ai/welcome) documentation.

## What You Need

- Python 3.x
- MultiOn API key
- Python packages: PyPDF2, requests
- URL of the form you're submitting to

## How to Use

1. Put your CV (PDF) in the same folder as the script.
2. Install required packages:
```bash
pip install PyPDF2 requests
```
3. Add your MultiOn API key to the script:
```python
API_KEY = "your_api_key_here"
```
4. Update the CV file name in the script:
```python
cv_text = extract_cv_data('YourCV.pdf')
```
5. Set the URL of the form you're submitting to:
```python
url = "https://your-form-url-here.com"
```
6. Run the script:
```bash
python cv_submission_script.py
```
7. Follow the prompts to add any missing info.
8. Confirm to submit the form.

## What It Does

1. Reads your PDF CV
2. Connects to the online form
3. Fills in form fields with info from your CV
4. Asks you for any missing information
5. Submits the form
6. Checks if submission was successful

## Note

- Keep your API key private
- Make sure to use the correct form URL
- The script might not catch all info from your CV, so be ready to type some in
- For local execution, you need to download the MultiOn Browser Extension and have "API Enabled" in the settings