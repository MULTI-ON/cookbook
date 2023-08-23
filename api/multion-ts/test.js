import Multion from "multion-ts";

async function run() {
    const multion = new Multion();
    const h = await multion.login(); // Wait for login to complete
    await multion.newSession({ input: "show sun pictures" });
  }
  
  run()
