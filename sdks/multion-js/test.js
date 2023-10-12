import Multion from './multion.js';
import { writeFileSync } from 'fs';
import open from 'open';

// Function to generate HTML and save it to a file
async function generateHtmlAndOpen(screenshotDataUrl) {
  // Create HTML content
  const htmlContent = `
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Screenshot</title>
    </head>
    <body>
        <img src="${screenshotDataUrl}" alt="Screenshot">
    </body>
    </html>
  `;

  // Save HTML content to a file
  const filePath = 'screenshot.html';
  writeFileSync(filePath, htmlContent);

  // Open HTML file in the default web browser
  await open(filePath);
}

// Your main function
async function main() {
  let multion = new Multion();
  await multion.login();
  
  let response = await multion.newSession({ "input": "what is the weather today", "url": "https://www.google.com" });
  console.log(response.message)
  let tabId = response.tabId;
  

  response = await multion.updateSession(tabId, { "input": "what is the weather today", "url": "https://www.google.com" });
  console.log(response.message)
  let screenshotDataUrl = await multion.getScreenshot(response, 800);

  // Generate HTML and open it in the browser
  await generateHtmlAndOpen(screenshotDataUrl);

  await multion.closeSession(tabId);
}

// Execute the main function
main();

