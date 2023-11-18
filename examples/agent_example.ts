export async function executeMultiOn(actionPrompt: string): Promise<void> {
  if (!process.env.MULTION_API_KEY) {
    throw new Error("MULTION_API_KEY not set");
  }

  console.log("Starting MultiOn session");
  const response = await fetch("https://api.multion.ai/sessions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      X_MULTION_API_KEY: process.env.MULTION_API_KEY,
    } as any,
    body: JSON.stringify({
      input: actionPrompt,
      url: "https://www.google.com",
    }),
  });

  const res = await response.json();

  const sessionId = res.response.data.session_id;
  let status = res.response.data.status;

  console.log("SESSION ID", sessionId);
  console.log("STATUS", status);

  const data = JSON.stringify(res.response.data, null, 2);
  console.log("DATA", data);

  while (status === "CONTINUE") {
    const response = await fetch(
      `https://api.multion.ai/session/${sessionId}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          X_MULTION_API_KEY: process.env.MULTION_API_KEY,
        } as any,
        body: JSON.stringify({
          input: actionPrompt,
          url: "https://www.google.com",
        }),
      }
    );

    const res = await response.json();
    const data = JSON.stringify(res.response.data, null, 2);
    console.log("DATA", data);

    status = res.response.data.status;
  }
}
