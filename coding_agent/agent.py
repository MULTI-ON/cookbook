from openai import OpenAI
from prompts import orchestrator_prompt
from prompts import programmer_notes
from prompts import notetaker_notes
from dotenv import load_dotenv
import time
from multion.client import MultiOn
import os

load_dotenv(".env.local")

# replit_email = os.getenv("REPLIT_EMAIL")
# replit_password = os.getenv("REPLIT_PASSWORD")

# multion_api_key = os.getenv("MULTION_API_KEY")
# multion.login(use_api=True, multion_api_key=multion_api_key)

# runpod_url = os.getenv("RUNPOD_URL")

image_temp = "https://miro.medium.com/v2/resize:fit:1200/0*n-2bW82Z6m6U2bij.jpeg"


class DevOn:
    def __init__(
        self,
        editor_image,
        browser_image,
        scratchpad_image,
        multion_api_key,
        openai_api_key,
        replit_email,
        replit_password,
        local,
    ):
        print(multion_api_key, openai_api_key)
        self.editor_image = editor_image
        self.browser_image = browser_image
        self.scratchpad_image = scratchpad_image
        self.local = local
        # if os.getenv("WHERE_EXECUTE"):
        #     self.local = local
        # else:
        #     self.local = False

        self.multion = MultiOn(api_key=multion_api_key)

        self.replit_email = replit_email
        self.replit_password = replit_password

        self.programmer = self.multion.sessions.create(
            url="https://replit.com/login", local=self.local, include_screenshot=True
        )
        self.programmer_logged_in = False
        # self.editor_image = self.programmer.screenshot
        self.editor_image = self.multion.sessions.screenshot(
            session_id=self.programmer.session_id
        ).screenshot
        print(self.editor_image)
        time.sleep(1)
        # print(self.programmer)

        self.researcher = self.multion.sessions.create(
            url="https://www.google.com", local=self.local, include_screenshot=True
        )
        # self.browser_image = self.researcher.screenshot
        self.browser_image = self.multion.sessions.screenshot(
            session_id=self.researcher.session_id
        ).screenshot
        time.sleep(1)

        self.notetaker = self.multion.sessions.create(
            url="https://anotepad.com/", local=self.local, include_screenshot=True
        )
        # self.scratchpad_image = self.notetaker.screenshot
        self.scratchpad_image = self.multion.sessions.screenshot(
            session_id=self.notetaker.session_id
        ).screenshot
        time.sleep(1)

        self.done = True
        self.task = ""
        self.plan = ""
        self.messages = []
        self.client = OpenAI(api_key=openai_api_key)

    def programmer_login(self):
        if self.local:
            cmd = "Create a new Python REPL."
        else:
            cmd = "Log in with the email {email} and the password {password}. Then create a new Python REPL.".format(
                email=self.replit_email, password=self.replit_password
            )
        while True:
            self.programmer = self.multion.sessions.step(
                self.programmer.session_id,
                cmd=cmd + "\n\n" + programmer_notes,
                url="https://replit.com/login",
                include_screenshot=True,
            )
            print(self.programmer)
            print(
                self.multion.sessions.screenshot(
                    session_id=self.programmer.session_id
                ).screenshot
            )
            # time.sleep(1)
            # yield ("", self.editor_image, self.browser_image, self.scratchpad_image)
            # self.editor_image = self.programmer["screenshot"]
            if self.programmer.status in ["DONE", "NOT SURE"]:
                break

        self.editor_image = self.multion.sessions.screenshot(
            session_id=self.programmer.session_id
        ).screenshot
        time.sleep(1)

    def prepare_messages(self):
        messages = [
            {"role": "user", "content": orchestrator_prompt},
            {
                "role": "user",
                "content": "The Task given to you is: {task}".format(task=self.task),
            },
            {
                "role": "user",
                "content": "The current Plan state is: {plan}".format(plan=""),
            },
        ]
        for message in self.messages:
            messages.append(message)

        messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "This is the current state of the Programmer Intern.",
                    },
                    {"type": "image_url", "image_url": {"url": self.editor_image}},
                ],
            }
        )
        messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "This is the current state of the Researcher Intern.",
                    },
                    {"type": "image_url", "image_url": {"url": self.browser_image}},
                ],
            }
        )
        messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "This is the current state of the Notetaker Intern.",
                    },
                    {"type": "image_url", "image_url": {"url": self.scratchpad_image}},
                ],
            }
        )
        return messages

    def execute_action(self, action):

        action_func = action.split(" ", 1)[0]

        if action_func == "submit":
            self.done = True
            return
        elif action_func == "update_plan":
            action_arg = action.split(" ", 1)[1]
            self.plan = action_arg
            return
        elif action_func == "programmer":
            action_arg = action.split(" ", 1)[1]
            while True:
                self.programmer = self.multion.sessions.step(
                    self.programmer.session_id,
                    cmd=action_arg + "\n\n" + programmer_notes,
                    url="https://replit.com/login",
                    include_screenshot=True,
                )
                print(self.programmer)
                # if self.programmer.status == "NOT SURE":
                #     self.messages.append(
                #         {
                #             "role": "user",
                #             "content": "The Programmer says: {message}\n\nYour next reply will go to the programmer.".format(
                #                 message=self.programmer.message
                #             ),
                #         }
                #     )
                #     chat_completion = self.client.chat.completions.create(
                #         messages=self.prepare_messages(),
                #         model="gpt-4-vision-preview",
                #         # max_tokens=200,
                #     )
                #     action_arg = chat_completion.choices[0].message.content
                #     self.messages.append({"role": "assistant", "content": action_arg})
                # else:
                self.messages.append(
                    {
                        "role": "user",
                        "content": "The Programmer says: {message}".format(
                            message=self.programmer.message
                        ),
                    }
                )
                # time.sleep(1)
                # self.editor_image = self.programmer["screenshot"]
                # yield ("", self.editor_image, self.browser_image, self.scratchpad_image)
                if self.programmer.status in ["DONE", "NOT SURE"]:
                    break
            self.editor_image = self.multion.sessions.screenshot(
                session_id=self.programmer.session_id
            ).screenshot
            print(self.editor_image)
            time.sleep(1)
            return
        elif action_func == "researcher":
            action_arg = action.split(" ", 1)[1]
            while True:
                self.researcher = self.multion.sessions.step(
                    self.researcher.session_id,
                    cmd=action_arg,
                    url="https://www.google.com",
                    include_screenshot=True,
                )
                print(self.researcher)
                self.messages.append(
                    {
                        "role": "user",
                        "content": "The Researcher says: {message}".format(
                            message=self.researcher.message
                        ),
                    }
                )
                # time.sleep(1)
                # self.browser_image = self.researcher["screenshot"]
                # yield ("", self.editor_image, self.browser_image, self.scratchpad_image)
                if self.researcher.status == "DONE":
                    break
            self.browser_image = self.multion.sessions.screenshot(
                session_id=self.researcher.session_id
            ).screenshot
            print(self.browser_image)
            time.sleep(1)
            return
        elif action_func == "notetaker":
            action_arg = action.split(" ", 1)[1]
            while True:
                self.notetaker = self.multion.sessions.step(
                    self.notetaker.session_id,
                    cmd=action_arg + "\n\n" + notetaker_notes,
                    url="https://anotepad.com/",
                    include_screenshot=True,
                )
                print(self.notetaker)
                self.messages.append(
                    {
                        "role": "user",
                        "content": "The Notetaker says: {message}".format(
                            message=self.notetaker.message
                        ),
                    }
                )
                # time.sleep(1)
                # self.scratchpad_image = self.notetaker["screenshot"]
                # yield ("", self.editor_image, self.browser_image, self.scratchpad_image)
                if self.notetaker.status == "DONE":
                    break
            self.scratchpad_image = self.multion.sessions.screenshot(
                session_id=self.notetaker.session_id
            ).screenshot
            print(self.scratchpad_image)
            time.sleep(1)
            return
        elif action_func == "clarify":
            action_arg = action.split(" ", 1)[1]
            return

    def orchestrator(self):
        if not self.programmer_logged_in:
            self.programmer_login()
            self.programmer_logged_in = True
        messages = self.prepare_messages()
        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model="gpt-4o",
            # max_tokens=200,
        )
        response = chat_completion.choices[0].message.content
        action, explanation = response.split("Explanation: ", 1)
        action = action.split("Action: ", 1)[1]

        self.messages.append({"role": "assistant", "content": response})
        self.messages.append(
            {
                "role": "user",
                "content": "The current Plan state is: {plan}".format(plan=self.plan),
            }
        )
        print(self.messages)

        # self.execute_action(action)

        action_func = action.split(" ", 1)[0]

        if action_func == "submit":
            self.done = True
        elif action_func == "update_plan":
            action_arg = action.split(" ", 1)[1]
            self.plan = action_arg
        elif action_func == "programmer":
            action_arg = action.split(" ", 1)[1]
            while True:
                self.programmer = self.multion.sessions.step(
                    self.programmer.session_id,
                    cmd=action_arg + "\n\n" + programmer_notes,
                    url="https://replit.com/login",
                    include_screenshot=True,
                )
                print(self.programmer)
                self.messages.append(
                    {
                        "role": "user",
                        "content": "The Programmer says: {message}".format(
                            message=self.programmer.message
                        ),
                    }
                )
                if self.programmer.status in ["DONE", "NOT SURE"]:
                    break
            self.editor_image = self.multion.sessions.screenshot(
                session_id=self.programmer.session_id
            ).screenshot
            print(self.editor_image)
            time.sleep(1)
        elif action_func == "researcher":
            action_arg = action.split(" ", 1)[1]
            while True:
                self.researcher = self.multion.sessions.step(
                    self.researcher.session_id,
                    cmd=action_arg,
                    url="https://www.google.com",
                    include_screenshot=True,
                )
                print(self.researcher)
                self.messages.append(
                    {
                        "role": "user",
                        "content": "The Researcher says: {message}".format(
                            message=self.researcher.message
                        ),
                    }
                )
                # time.sleep(1)
                # self.browser_image = self.researcher["screenshot"]
                # yield ("", self.editor_image, self.browser_image, self.scratchpad_image)
                if self.researcher.status == "DONE":
                    break
            self.browser_image = self.multion.sessions.screenshot(
                session_id=self.researcher.session_id
            ).screenshot
            print(self.browser_image)
            time.sleep(1)
        elif action_func == "notetaker":
            action_arg = action.split(" ", 1)[1]
            while True:
                self.notetaker = self.multion.sessions.step(
                    self.notetaker.session_id,
                    cmd=action_arg + "\n\n" + notetaker_notes,
                    url="https://anotepad.com/",
                    include_screenshot=True,
                )
                print(self.notetaker)
                self.messages.append(
                    {
                        "role": "user",
                        "content": "The Notetaker says: {message}".format(
                            message=self.notetaker.message
                        ),
                    }
                )
                # time.sleep(1)
                # self.scratchpad_image = self.notetaker["screenshot"]
                # yield ("", self.editor_image, self.browser_image, self.scratchpad_image)
                if self.notetaker.status == "DONE":
                    break
            self.scratchpad_image = self.multion.sessions.screenshot(
                session_id=self.notetaker.session_id
            ).screenshot
            print(self.scratchpad_image)
            time.sleep(1)
        elif action_func == "clarify":
            action_arg = action.split(" ", 1)[1]

        return explanation

    def run(self, prompt):
        self.done = False
        self.task = prompt
        while not self.done:
            # curr_response = self.orchestrator()

            if not self.programmer_logged_in:
                # self.programmer_login()
                if self.local:
                    cmd = "Create a new Python REPL."
                else:
                    cmd = "Log in with the email {email} and the password {password}. Then create a new Python REPL.".format(
                        email=self.replit_email, password=self.replit_password
                    )
                while True:
                    self.programmer = self.multion.sessions.step(
                        self.programmer.session_id,
                        cmd=cmd + "\n\n" + programmer_notes,
                        url="https://replit.com/login",
                        include_screenshot=True,
                    )
                    print(self.programmer)
                    print(
                        self.multion.sessions.screenshot(
                            session_id=self.programmer.session_id
                        ).screenshot
                    )
                    # time.sleep(1)
                    # yield ("", self.editor_image, self.browser_image, self.scratchpad_image)
                    # self.editor_image = self.programmer["screenshot"]
                    if self.programmer.status in ["DONE", "NOT SURE"]:
                        break
                    self.editor_image = self.multion.sessions.screenshot(
                        session_id=self.programmer.session_id
                    ).screenshot
                    time.sleep(1)
                    yield (
                        "I am setting up the programming environment",
                        self.editor_image,
                        self.browser_image,
                        self.scratchpad_image,
                    )

                self.editor_image = self.multion.sessions.screenshot(
                    session_id=self.programmer.session_id
                ).screenshot
                time.sleep(1)
                self.programmer_logged_in = True
            messages = self.prepare_messages()
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model="gpt-4o",
                # max_tokens=200,
            )
            response = chat_completion.choices[0].message.content
            action, explanation = response.split("Explanation: ", 1)
            action = action.split("Action: ", 1)[1]

            self.messages.append({"role": "assistant", "content": response})
            self.messages.append(
                {
                    "role": "user",
                    "content": "The current Plan state is: {plan}".format(
                        plan=self.plan
                    ),
                }
            )
            print(self.messages)

            # self.execute_action(action)

            action_func = action.split(" ", 1)[0]

            if action_func == "submit":
                self.done = True
                yield (
                    explanation,
                    self.editor_image,
                    self.browser_image,
                    self.scratchpad_image,
                )
            elif action_func == "update_plan":
                action_arg = action.split(" ", 1)[1]
                self.plan = action_arg
                yield (
                    explanation,
                    self.editor_image,
                    self.browser_image,
                    self.scratchpad_image,
                )
            elif action_func == "programmer":
                action_arg = action.split(" ", 1)[1]
                while True:
                    self.programmer = self.multion.sessions.step(
                        self.programmer.session_id,
                        cmd=action_arg + "\n\n" + programmer_notes,
                        url="https://replit.com/login",
                        include_screenshot=True,
                    )
                    print(self.programmer)
                    self.messages.append(
                        {
                            "role": "user",
                            "content": "The Programmer says: {message}".format(
                                message=self.programmer.message
                            ),
                        }
                    )
                    if self.programmer.status in ["DONE", "NOT SURE"]:
                        break
                    self.editor_image = self.multion.sessions.screenshot(
                        session_id=self.programmer.session_id
                    ).screenshot
                    print(self.editor_image)
                    time.sleep(1)
                    yield (
                        explanation,
                        self.editor_image,
                        self.browser_image,
                        self.scratchpad_image,
                    )
                self.editor_image = self.multion.sessions.screenshot(
                    session_id=self.programmer.session_id
                ).screenshot
                print(self.editor_image)
                time.sleep(1)
            elif action_func == "researcher":
                action_arg = action.split(" ", 1)[1]
                while True:
                    self.researcher = self.multion.sessions.step(
                        self.researcher.session_id,
                        cmd=action_arg,
                        url="https://www.google.com",
                        include_screenshot=True,
                    )
                    print(self.researcher)
                    self.messages.append(
                        {
                            "role": "user",
                            "content": "The Researcher says: {message}".format(
                                message=self.researcher.message
                            ),
                        }
                    )
                    # time.sleep(1)
                    # self.browser_image = self.researcher["screenshot"]
                    # yield ("", self.editor_image, self.browser_image, self.scratchpad_image)
                    if self.researcher.status == "DONE":
                        break
                    self.browser_image = self.multion.sessions.screenshot(
                        session_id=self.researcher.session_id
                    ).screenshot
                    print(self.browser_image)
                    time.sleep(1)
                    yield (
                        explanation,
                        self.editor_image,
                        self.browser_image,
                        self.scratchpad_image,
                    )
                self.browser_image = self.multion.sessions.screenshot(
                    session_id=self.researcher.session_id
                ).screenshot
                print(self.browser_image)
                time.sleep(1)
            elif action_func == "notetaker":
                action_arg = action.split(" ", 1)[1]
                while True:
                    self.notetaker = self.multion.sessions.step(
                        self.notetaker.session_id,
                        cmd=action_arg + "\n\n" + notetaker_notes,
                        url="https://anotepad.com/",
                        include_screenshot=True,
                    )
                    print(self.notetaker)
                    self.messages.append(
                        {
                            "role": "user",
                            "content": "The Notetaker says: {message}".format(
                                message=self.notetaker.message
                            ),
                        }
                    )
                    # time.sleep(1)
                    # self.scratchpad_image = self.notetaker["screenshot"]
                    # yield ("", self.editor_image, self.browser_image, self.scratchpad_image)
                    if self.notetaker.status == "DONE":
                        break
                    self.scratchpad_image = self.multion.sessions.screenshot(
                        session_id=self.notetaker.session_id
                    ).screenshot
                    print(self.scratchpad_image)
                    time.sleep(1)
                    yield (
                        explanation,
                        self.editor_image,
                        self.browser_image,
                        self.scratchpad_image,
                    )
                self.scratchpad_image = self.multion.sessions.screenshot(
                    session_id=self.notetaker.session_id
                ).screenshot
                print(self.scratchpad_image)
                time.sleep(1)
            elif action_func == "clarify":
                action_arg = action.split(" ", 1)[1]
                yield (
                    explanation,
                    self.editor_image,
                    self.browser_image,
                    self.scratchpad_image,
                )

            # return explanation

            # yield (
            #     curr_response,
            #     self.editor_image,
            #     self.browser_image,
            #     self.scratchpad_image,
            # )
