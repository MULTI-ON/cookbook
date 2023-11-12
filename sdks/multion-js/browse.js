import Multion from "multion-js";
import { createRequire } from "module";
const require = createRequire(import.meta.url);
const Tesseract = require("tesseract.js");
const { Image, createCanvas } = require("canvas");
const fs = require("fs");

class MultionToolSpec {
  constructor(
    tokenFile = "multion_token.txt",
    defaultUrl = "https://google.com",
    mode = "auto"
  ) {
    this.multion = new Multion(tokenFile);
    this.multion.login();
    this.currentStatus = "NOT_ACTIVE";
    this.sessionId = null;
    this.currentUrl = defaultUrl;
    this.mode = mode;
  }

  async browse(instruction, url) {
    this.multion.setRemote(false);

    let session;
    if (this.sessionId) {
      session = await this.multion.updateSession(this.sessionId, {
        input: instruction,
        url: this.currentUrl,
      });
    } else {
      session = await this.multion.newSession({
        input: instruction,
        url: url ? url : this.currentUrl,
      });
      this.sessionId = session.tabId;
    }

    this._updateStatus(session);

    while (this.mode === "auto" && this.currentStatus === "CONTINUE") {
      session = await this.multion.updateSession(this.sessionId, {
        input: instruction,
        url: this.currentUrl,
      });
      this._updateStatus(session);
      console.log(this.currentStatus, this.currentUrl);
    }

    return {
      status: session.status,
      url: session.url,
      action_completed: session.message,
      content: await this._readScreenshot(session.screenshot),
    };
  }

  _updateStatus(session) {
    this.currentStatus = session.status;
    this.currentUrl = session.url;
  }

  async _readScreenshot(screenshot) {
    const image = new Image();
    image.src = screenshot;

    const canvas = createCanvas(image.width, image.height);
    const ctx = canvas.getContext("2d");
    ctx.drawImage(image, 0, 0, image.width, image.height);

    const result = await Tesseract.recognize(canvas.toBuffer(), "eng", {
      logger: (m) => console.log(m),
    });
    return result.data.text;
  }
}
