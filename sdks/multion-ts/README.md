# Multion TypeScript SDK

## Account setup 
First, create a Multion account or sign in. Next, navigate to the API key page and "Create new secret key", optionally naming the key. Make sure to save this somewhere safe and do not share it with anyone.

## Installing the SDK
To use the Multion SDK in your TypeScript project, start by installing the package via npm:

```shell
npm install multion-ts
```

This command adds Multion as a dependency to your project, allowing you to utilize its capabilities.

## Running a Sample
Here's a quick example to get you started with the Multion SDK in a Node.js environment. This sample demonstrates how to log in, create a session, and perform an operation within that session.

```typescript
  import { MultionApiClient } from "multion-ts";

  const multion = new MultionApiClient({ apiKey: "MULTION_API_KEY" });

  const browse = await multion.browse({
    cmd: "hello",
    url: "https://www.google.com",
  });
```

## API reference
For more examples and detailed API usage, explore the [MultiOn Docs]().