import axios from "axios";
import path from "path";
import { fileURLToPath } from "url";
import {
  existsSync,
  statSync,
  readFileSync,
  writeFileSync,
  unlinkSync,
  createWriteStream,
} from "fs";
import open from "open";
import simple_oauth2 from "simple-oauth2";
import sharp from "sharp";
import crypto from "crypto";
import { Fernet } from "fernet";
import { CognitoJwtVerifier } from "aws-jwt-verify";
import os from "os";
import uuid from "uuid";

const { AuthorizationCode } = simple_oauth2;
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class Multion {
  constructor(tokenFile = "multion_token.txt", secretsFile = "secrets.json") {
    this.token = null;
    this.tokenFile = path.resolve(__dirname, tokenFile);
    this.apiURL = "https://api.multion.ai";
    this.authURL = "https://auth.multion.ai";

    // Get the API key from the environment variable
    this.apiKey = process.env.MULTION_API_KEY;

    this.loadSecrets(secretsFile);
    this.createMultionDirectory();

    // Load token if it exists
    this.loadToken();
  }

  loadSecrets(secretsFile) {
    secretsFile = path.join(__dirname, secretsFile);
    this.secrets = JSON.parse(readFileSync(secretsFile, "utf8"));
    this.clientId = this.secrets.MULTION_CLIENT_ID;
    this.clientSecret = this.secrets.MULTION_CLIENT_SECRET;
    this.userPoolId = this.secrets.COGNITO_USER_POOL_ID;
    this.region = this.secrets.AWS_REGION;
    this.refreshURL = "https://auth.multion.ai/oauth2/token";

    this.fernetKey = this.secrets.FERNET_KEY;
    if (!this.fernetKey) {
      this.fernetKey = this.generateFernetKey();
      this.secrets.FERNET_KEY = this.fernetKey;
      writeFileSync(secretsFile, JSON.stringify(this.secrets), "utf8");
    }
  }

  generateFernetKey() {
    return Fernet.generate();
  }

  createMultionDirectory() {
    this.homeDir = path.resolve("~");
    this.multionDir = path.join(this.homeDir, ".multion");
    if (!existsSync(this.multionDir)) {
      try {
        fs.mkdirSync(this.multionDir, { recursive: true });
      } catch (error) {
        console.log("Error creating .multion directory: ", error);
        this.multionDir = os.tmpdir();
      }
    }
    this.tokenFile = path.join(this.multionDir, "multion_token.txt");
    this.isRemote = false;
  }

  loadToken() {
    if (existsSync(this.tokenFile) && statSync(this.tokenFile).size > 0) {
      try {
        const encryptedToken = readFileSync(this.tokenFile, "utf-8");
        const fernet = new Fernet(this.fernetKey);
        const decryptedToken = fernet.decrypt(encryptedToken);
        this.token = JSON.parse(decryptedToken);
      } catch (error) {
        console.log(
          "Error reading token from file. The file might be corrupted."
        );
        this.token = null;
      }
    }
  }

  saveToken() {
    const fernet = new Fernet(this.fernetKey);
    const encryptedToken = fernet.encrypt(JSON.stringify(this.token));
    writeFileSync(this.tokenFile, encryptedToken, "utf8");
  }

  async verifyCognitoToken() {
    const verifier = CognitoJwtVerifier.create({
      userPoolId: this.userPoolId,
      tokenUse: "access",
      clientId: this.clientId,
    });

    try {
      const payload = await verifier.verify(this.token["id_token"]);
      console.log("Token is valid. Payload:", payload);
      return payload;
    } catch (error) {
      console.log("Token not valid!", error);
      return null;
    }
  }

  async login(useAPI = false) {
    if (useAPI) {
      if (this.apiKey !== null) {
        console.log("Already logged in using API key.");
        return;
      } else {
        this.issueAPIKey();
        return;
      }
    }

    if (this.token !== null) {
      try {
        const verifiedClaims = this.verifyCognitoToken();
        if (verifiedClaims) {
          console.log("Already logged in.");
          return;
        }
      } catch (error) {
        console.log("Error verifying token: ", error);
      }
    }

    // Create a unique client id
    this.clientId = this.registerClient();

    // OAuth endpoints
    const authorizationBaseURL = "https://auth.multion.ai/oauth2/authorize";
    const redirectURI = "https://api.multion.ai/callback";

    // Create an OAuth2 session
    const oauth = new OAuth2Session(this.clientId, redirectURI, this.clientId);
    // Get the authorization URL
    const authorizationURL = oauth.authorizationURL(authorizationBaseURL);

    try {
      // Try to open the authorization URL in a new browser tab
      open(authorizationURL);
    } catch (error) {
      // If an error occurs, print the authorization URL
      console.log(
        "Please visit this URL to authorize the application: " +
          authorizationURL
      );
    }

    // Poll the server for the token
    let attempts = 0;
    while (attempts < 5) {
      const data = await this.getToken();
      if (data) {
        this.token = data;
        this.saveToken(); // Save the token after updating it
        break;
      }
      attempts += 1;
      await new Promise((resolve) => setTimeout(resolve, 1000)); // Wait before the next poll
    }
  }

  issueApiKey() {
    // Get the authorization URL
    const appUrl = "https://app.multion.ai";

    try {
      // Try to open the authorization URL in a new browser tab
      open(appUrl);
    } catch (error) {
      // If an error occurs, print the authorization URL
      console.log("Please visit this URL to generate an API Key: " + appUrl);
    }

    // Wait for user input to get the API key
    this.api_key = prompt("Please enter your API Key: ");
  }

  registerClient() {
    // Get the MAC address and use it to generate a UUID
    const macNum = os.networkInterfaces()["eth0"][0]["mac"].replace(/:/g, "");
    const mac = macNum.match(/.{1,2}/g).join(":");
    const deviceUuid = uuid.v5(mac, uuid.DNS);
    console.log(deviceUuid);

    // TODO: Register the client with the backend to the user
    return deviceUuid;
  }

  setHeaders() {
    let headers = {};
    if (this.api_key !== null) {
      headers["X_MULTION_API_KEY"] = this.api_key;
    }
    if (this.token !== null) {
      headers["Authorization"] = `Bearer ${this.token["access_token"]}`;
    }
    return headers;
  }

  async post(url, data, tabId = null) {
    if (this.token === null && this.api_key === null) {
      throw new Error(
        "You must log in or provide an API key before making API calls."
      );
    }

    let headers = this.setHeaders();

    if (tabId !== null) {
      url = `https://api.multion.ai/sessions/${tabId}`;
    }

    console.log("running post");
    let attempts = 0;

    while (attempts < 5) {
      try {
        const response = await axios.post(url, data, { headers });

        if (response.status >= 200 && response.status < 400) {
          return response.data.response.data;
        } else if (response.status === 401) {
          console.log("Invalid token. Refreshing...");
          await this.refreshToken();
          headers = this.setHeaders();
          continue;
        }
      } catch (error) {
        await this.refreshToken();
        if (error.response) {
          console.log(
            `Request failed with status code: ${error.response.status}`
          );
        } else {
          console.log("Request failed without a response", error);
        }
        console.log(`Response text: ${JSON.stringify(error.response.data)}`);
        throw new Error("Failed to get a valid response after 5 attempts");
      }

      await new Promise((resolve) => setTimeout(resolve, 1000));
      attempts += 1;
    }
  }

  async get() {
    if (this.token === null && this.api_key === null) {
      throw new Error(
        "You must log in or provide an API key before making API calls."
      );
    }

    const headers = this.setHeaders();
    const url = "https://api.multion.ai/sessions";

    const response = await axios.get(url, { headers });
    return response.data.response.data;
  }

  async newSession(data) {
    const url = "https://api.multion.ai/sessions";
    return await this.post(url, data);
  }

  async updateSession(tabId, data) {
    const url = `https://api.multion.ai/session/${tabId}`;
    return await this.post(url, data);
  }

  async listSessions() {
    return await this.get();
  }

  async refreshToken() {
    const tokenURL = "https://auth.multion.ai/oauth2/token";
    const redirectURI = "http://localhost:8000/callback";

    const auth = {
      username: this.clientId,
      password: this.clientSecret,
    };

    const data = {
      grant_type: "refresh_token",
      refresh_token: this.token.refresh_token,
      redirect_uri: redirectURI,
    };

    try {
      const response = await axios.post(tokenURL, data, { auth });
      this.token = response.data;
      writeFileSync(this.tokenFile, JSON.stringify(this.token));
    } catch (error) {
      console.error(`Failed to refresh token: ${error}`);
    }
  }

  deleteToken() {
    if (existsSync(this.tokenFile)) {
      unlinkSync(this.tokenFile);
    } else {
      console.log(
        "No active session found. Access token has already been revoked."
      );
    }
  }

  async closeSession(tabId) {
    if (this.token === null && this.api_key === null) {
      throw new Error(
        "You must log in or provide an API key before making API calls."
      );
    }

    const headers = this.setHeaders();
    const url = `https://api.multion.ai/sessions/${tabId}`;

    try {
      const response = await axios.delete(url, { headers });

      if (response.status >= 200 && response.status < 400) {
        return response.data.response.data;
      } else {
        console.log(`Failed to close session. Status code: ${response.status}`);
      }
    } catch (error) {
      if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        console.log(error.response.data);
        console.log(error.response.status);
        console.log(error.response.headers);
      } else if (error.request) {
        // The request was made but no response was received
        // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
        // http.ClientRequest in node.js
        console.log(error.request);
      } else {
        // Something happened in setting up the request that triggered an Error
        console.log("Error", error.message);
      }
      console.log(error.config);
    }
  }

  async getScreenshot(response, height = null, width = null) {
    const screenshot = response.screenshot;
    const base64ImgBytes = screenshot.replace("data:image/png;base64,", "");
    const imgBuffer = Buffer.from(base64ImgBytes, "base64");

    try {
      let resizedBuffer;
      if (height !== null && width !== null) {
        resizedBuffer = await sharp(imgBuffer)
          .resize(width, height)
          .png()
          .toBuffer();
      } else if (height !== null) {
        resizedBuffer = await sharp(imgBuffer)
          .resize({ height })
          .png()
          .toBuffer();
      } else if (width !== null) {
        resizedBuffer = await sharp(imgBuffer)
          .resize({ width })
          .png()
          .toBuffer();
      } else {
        resizedBuffer = imgBuffer; // no resizing
      }

      // If you want to save the image to a file
      // await sharp(resizedBuffer).toFile('output.png');

      // If you want to get the image data URL
      const imageDataURL = `data:image/png;base64,${resizedBuffer.toString(
        "base64"
      )}`;
      return imageDataURL;
    } catch (error) {
      console.error("Error processing image:", error.message);
      throw error;
    }
  }

  async getVideo(session_id) {
    const url = `https://api.multion.ai/sessionVideo/${session_id}`;
    if (this.token === null) {
      console.log("You must log in before getting a video.");
      return null;
    }

    const headers = { Authorization: `Bearer ${this.token["access_token"]}` };

    try {
      const response = await axios.get(url, {
        headers,
        responseType: "stream",
      });
      if (response.status >= 200 && response.status < 400) {
        const videoStream = response.data;
        const path = "video.webm";
        const writer = createWriteStream(path);
        videoStream.pipe(writer);

        return new Promise((resolve, reject) => {
          writer.on("finish", resolve);
          writer.on("error", reject);
        });
      } else {
        console.log(`Failed to get video. Status code: ${response.status}`);
        return null;
      }
    } catch (error) {
      console.log(`Error: ${error.message}`);
      return null;
    }
  }

  async setApiUrl(url) {
    this.apiURL = url;
  }
}

export default Multion;
// module.exports = Multion;  // Uncomment this line if you prefer to use CommonJS module.exports
