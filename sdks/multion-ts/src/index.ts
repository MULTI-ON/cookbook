import axios, { AxiosResponse } from 'axios';
import * as path from 'path';
import { fileURLToPath, URL } from 'url';
import {
  existsSync,
  statSync,
  readFileSync,
  writeFileSync,
  unlinkSync,
} from 'fs';
import fs from 'fs';
import { spawn } from 'child_process';

import { createRequire } from 'node:module';
import { AuthorizationCode } from 'simple-oauth2';
// import * as express from 'express';
import express from 'express';
import { Request, Response } from 'express';

import open from 'open';



interface Dictionary {
  [Key: string]: string;
}
import {secrets} from './secrets.js';


class Multion {
 secrets:Dictionary;
 clientId:string;clientSecret:string;
 tokenFile:string;token:any;
 refreshURL:string;

  constructor(tokenFile = "multion_token.txt") {
    
    this.secrets = secrets();
    this.clientId = this.secrets["MULTION_CLIENT_ID"];
    this.clientSecret = this.secrets["MULTION_CLIENT_SECRET"];
    this.tokenFile = tokenFile;
    this.token = null;
    this.refreshURL = "https://auth.multion.ai/oauth2/token";

// Try to load the token from the token file
if (existsSync(this.tokenFile) && statSync(this.tokenFile).size > 0) {
  // check if file is not empty
  try {
    this.token = JSON.parse(readFileSync(this.tokenFile, "utf-8"));
  } catch (error) {
    console.log(
      "Error reading token from file. The file might be corrupted."
    );
    this.token = null;
  }
}
  }
  async login(): Promise<string> {
    if (this.token !== null) {
      console.log('Already logged in');
      return 'Already logged in';
    }

    const authorizationBaseUrl = 'https://auth.multion.ai/oauth2/authorize';
    const tokenUrl = 'https://auth.multion.ai/oauth2/token';
    const redirectUri = 'http://localhost:8000/callback';

    const oauth = new AuthorizationCode({
      client: {
        id: this.clientId,
        secret: this.clientSecret,
      },
      auth: {
        authorizeHost: 'https://auth.multion.ai',
        authorizePath: '/oauth2/authorize',
        tokenHost: 'https://auth.multion.ai',
        tokenPath: '/oauth2/token',
      },
    });

    const authorizationUri = oauth.authorizeURL({
      redirect_uri: redirectUri,
    });

    open(authorizationUri);

    const app = express();
    const server = app.listen(8000, () => {
      console.log('Server listening on port 8000');
    });

    return new Promise<string>((resolve, reject) => {
      app.get('/callback', async (req : Request, res: Response) => {
        try {
          const code = req.query.code as string;

          const tokenParams = {
            code,
            redirect_uri: redirectUri,
          };
          const result = await oauth.getToken(tokenParams);

          this.token = result.token;
          writeFileSync(this.tokenFile, JSON.stringify(this.token));

          console.log('Login successful!');
          resolve('Login successful!');
        } catch (error) {
          console.log('Error during login:', error);
          reject(error);
        } finally {
          server.close();
        }

        res.send('<script>window.close()</script>');
      });
    });
  }

  async post(url: string, data: any, tabId: string | null = null): Promise<any> {
    if (this.token === null) {
      throw new Error('You must log in before making API calls.');
    }

    let headers = { Authorization: `Bearer ${this.token.access_token}` };

    if (tabId !== null) {
      url = `https://multion-api.fly.dev/sessions/${tabId}`;
    }

    console.log('running post');
    let attempts = 0;

    while (attempts < 5) {
      try {
        const response = await axios.post(url, data, { headers });

        if (response.status >= 200 && response.status < 400) {
          // checks if status_code is 200-400
          return response.data.response.data;
        } else if (response.status === 401) {
          console.log('Invalid token. Refreshing...');
          await this.refreshToken();
          headers.Authorization = `Bearer ${JSON.stringify(this.token.access_token)}`;
          continue;
        }
      } catch (error) {
        if (error instanceof Error) {
          console.error('An error occurred:', error.message);
        } else {
          console.error('An unknown error occurred:', error);
        throw new Error('Failed to get a valid response after 5 attempts');
        }
        
      }

      await new Promise((resolve) => setTimeout(resolve, 1000));
      attempts += 1;
    }
  }

  async get(): Promise<any> {
    if (this.token === null) {
      throw new Error('You must log in before making API calls.');
    }

    const headers = { Authorization: `Bearer ${this.token.access_token}` };
    const url = 'https://multion-api.fly.dev/sessions';

    const response = await axios.get(url, { headers });
    return response.data.response.data;
  }

  async newSession(data: any): Promise<any> {
    const url = 'https://multion-api.fly.dev/sessions';
    return await this.post(url, data);
  }

  async updateSession(tabId: string, data: any): Promise<any> {
    const url = `https://multion-api.fly.dev/session/${tabId}`;
    return await this.post(url, data);
  }

  async listSessions(): Promise<any> {
    return await this.get();
  }

  async refreshToken(): Promise<void> {
    const tokenURL = 'https://auth.multion.ai/oauth2/token';
    const redirectURI = 'http://localhost:8000/callback';

    const auth = {
      username: this.clientId,
      password: this.clientSecret,
    };

    const data = {
      grant_type: 'refresh_token',
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

  deleteToken(): void {
    if (existsSync(this.tokenFile)) {
      unlinkSync(this.tokenFile);
    } else {
      console.log('No active session found. Access token has already been revoked.');
    }
  }
}
export default Multion;

