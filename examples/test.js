import Multion from "./main.js";

async function run() {
    const multion = new Multion();
    const h = await multion.login(); // Wait for login to complete
    console.log("j",h,"j");
    await multion.newSession({ input: "show sun pictures" });
  }
  
  run()



  // import Multion from "multion-ts";

  // async function run() {
  //     const multion = new Multion();
  //     const h = await multion.login(); // Wait for login to complete
  //     await multion.newSession({ input: "show sun pictures" });
  //   }
    
  //   run()
  