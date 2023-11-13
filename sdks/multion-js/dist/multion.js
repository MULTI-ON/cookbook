"use strict";

var _interopRequireDefault = require("@babel/runtime/helpers/interopRequireDefault");
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = exports.Multion = void 0;
var _axios = _interopRequireDefault(require("axios"));
var _path = _interopRequireDefault(require("path"));
var _url = require("url");
var _fs = require("fs");
var _open = _interopRequireDefault(require("open"));
var _simpleOauth = _interopRequireDefault(require("simple-oauth2"));
var _express = _interopRequireDefault(require("express"));
var _sharp = _interopRequireDefault(require("sharp"));
const {
  AuthorizationCode
} = _simpleOauth.default;
const _filename = (0, _url.fileURLToPath)(import.meta.url);
const _dirname = _path.default.dirname(_filename);
class Multion {
  constructor(tokenFile = "multion_token.txt") {
    this.secrets = JSON.parse((0, _fs.readFileSync)("./secrets.json", "utf8"));
    this.clientId = this.secrets.MULTION_CLIENT_ID;
    this.clientSecret = this.secrets.MULTION_CLIENT_SECRET;
    this.tokenFile = _path.default.resolve(_dirname, tokenFile);
    this.token = null;
    this.refreshURL = "https://auth.multion.ai/oauth2/token";
    if ((0, _fs.existsSync)(this.tokenFile) && (0, _fs.statSync)(this.tokenFile).size > 0) {
      try {
        this.token = JSON.parse((0, _fs.readFileSync)(this.tokenFile, "utf-8"));
      } catch (error) {
        console.log("Error reading token from file. The file might be corrupted.");
        this.token = null;
      }
    }
  }
  async login() {
    if (this.token !== null) {
      console.log("Already logged in");
      return;
    }
    const authorizationBaseUrl = "https://auth.multion.ai/oauth2/authorize";
    const tokenUrl = "https://auth.multion.ai/oauth2/token";
    const redirectUri = "http://localhost:8000/callback";
    const oauth = new AuthorizationCode({
      client: {
        id: this.clientId,
        secret: this.clientSecret
      },
      auth: {
        authorizeHost: "https://auth.multion.ai",
        authorizePath: "/oauth2/authorize",
        tokenHost: "https://auth.multion.ai",
        tokenPath: "/oauth2/token"
      }
    });
    const authorizationUri = oauth.authorizeURL({
      redirect_uri: redirectUri
    });
    (0, _open.default)(authorizationUri);
    const app = (0, _express.default)();
    const server = app.listen(8000, () => {
      console.log("Server listening on port 8000");
    });
    return new Promise((resolve, reject) => {
      app.get("/callback", async (req, res) => {
        try {
          const code = req.query.code;
          const tokenParams = {
            code,
            redirect_uri: redirectUri
          };
          const result = await oauth.getToken(tokenParams);
          this.token = result.token;
          (0, _fs.writeFileSync)(this.tokenFile, JSON.stringify(this.token));
          console.log("Login successful!");
          resolve("Login completed");
        } catch (error) {
          console.log("Error during login:", error.message);
          reject(error);
        } finally {
          server.close();
        }
        res.send("<script>window.close()</script>");
      });
    });
  }
  async post(url, data, tabId = null) {
    if (this.token === null) {
      throw new Error("You must log in before making API calls.");
    }
    let headers = {
      Authorization: `Bearer ${this.token["access_token"]}`
    };
    if (tabId !== null) {
      url = `https://api.multion.ai/sessions/${tabId}`;
    }
    console.log("running post");
    let attempts = 0;
    while (attempts < 5) {
      try {
        const response = await _axios.default.post(url, data, {
          headers
        });
        if (response.status >= 200 && response.status < 400) {
          return response.data.response.data;
        } else if (response.status === 401) {
          console.log("Invalid token. Refreshing...");
          await this.refreshToken();
          headers["Authorization"] = `Bearer ${this.token["access_token"]}`;
          continue;
        }
      } catch (error) {
        await this.refreshToken();
        if (error.response) {
          console.log(`Request failed with status code: ${error.response.status}`);
        } else {
          console.log("Request failed without a response", error);
        }
        console.log(`Response text: ${JSON.stringify(error.response.data)}`);
        throw new Error("Failed to get a valid response after 5 attempts");
      }
      await new Promise(resolve => setTimeout(resolve, 1000));
      attempts += 1;
    }
  }
  async get() {
    if (this.token === null) {
      throw new Error("You must log in before making API calls.");
    }
    const headers = {
      Authorization: `Bearer ${this.token["access_token"]}`
    };
    const url = "https://api.multion.ai/sessions";
    const response = await _axios.default.get(url, {
      headers
    });
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
      password: this.clientSecret
    };
    const data = {
      grant_type: "refresh_token",
      refresh_token: this.token.refresh_token,
      redirect_uri: redirectURI
    };
    try {
      const response = await _axios.default.post(tokenURL, data, {
        auth
      });
      this.token = response.data;
      (0, _fs.writeFileSync)(this.tokenFile, JSON.stringify(this.token));
    } catch (error) {
      console.error(`Failed to refresh token: ${error}`);
    }
  }
  deleteToken() {
    if ((0, _fs.existsSync)(this.tokenFile)) {
      (0, _fs.unlinkSync)(this.tokenFile);
    } else {
      console.log("No active session found. Access token has already been revoked.");
    }
  }
  async closeSession(tabId) {
    if (this.token === null) {
      throw new Error("You must log in before closing a session.");
    }
    const headers = {
      Authorization: `Bearer ${this.token["access_token"]}`
    };
    const url = `https://api.multion.ai/sessions/${tabId}`;
    try {
      const response = await _axios.default.delete(url, {
        headers
      });
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
        resizedBuffer = await (0, _sharp.default)(imgBuffer).resize(width, height).png().toBuffer();
      } else if (height !== null) {
        resizedBuffer = await (0, _sharp.default)(imgBuffer).resize({
          height
        }).png().toBuffer();
      } else if (width !== null) {
        resizedBuffer = await (0, _sharp.default)(imgBuffer).resize({
          width
        }).png().toBuffer();
      } else {
        resizedBuffer = imgBuffer; // no resizing
      }

      // If you want to save the image to a file
      // await sharp(resizedBuffer).toFile('output.png');

      // If you want to get the image data URL
      const imageDataURL = `data:image/png;base64,${resizedBuffer.toString("base64")}`;
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
    const headers = {
      Authorization: `Bearer ${this.token["access_token"]}`
    };
    try {
      const response = await _axios.default.get(url, {
        headers,
        responseType: "stream"
      });
      if (response.status >= 200 && response.status < 400) {
        const videoStream = response.data;
        const path = "video.webm";
        const writer = (0, _fs.createWriteStream)(path);
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
exports.Multion = Multion;
var _default = exports.default = Multion; // module.exports = Multion;  // Uncomment this line if you prefer to use CommonJS module.exports