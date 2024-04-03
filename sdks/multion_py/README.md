# Multion Python SDK

## Account setup 
First, create a Multion account or sign in. Next, navigate to the API key page and "Create new secret key", optionally naming the key. Make sure to save this somewhere safe and do not share it with anyone.

## Installing the SDK
To get started with the Multion SDK in your Python project, you can install it using pip. Run the following command in your terminal:

```shell
pip install multion_py -U
```

This command ensures you have the latest version of the Multion SDK installed.

## Running a Sample
After installing the SDK, you can begin making API calls. Below is a simple example demonstrating how to log in, create a session, and perform an action within that session using the Multion SDK.

```python
  from multion_py.client import MultionApi
  from multion_py.types.message import Message

  # Log in to Multion
  multion = MultionApi(api_key="MULTION_API_KEY")

  # browse 
  browse = multion.browse(cmd="hello", url="https://www.google.com")

```

## Learn more
For more examples and detailed API usage, explore the [MultiOn Docs]().