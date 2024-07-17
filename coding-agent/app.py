import gradio as gr
import os
import time
from agent import DevOn

image_temp = "https://miro.medium.com/v2/resize:fit:1200/0*n-2bW82Z6m6U2bij.jpeg"
# devon = DevOn(
#     editor_image=image_temp, browser_image=image_temp, scratchpad_image=image_temp
# )
devon = None
# multion_api_key = ""
# openai_api_key = ""
# replit_email = ""
# replit_password = ""


def add_message(history, message):
    # for x in message["files"]:
    #     history.append(((x,), None))
    if message["text"] is not None:
        history.append((message["text"], None))
    return history, gr.MultimodalTextbox(value=None, interactive=False)


# def multion_api_key_update(x):
#     # global multion_api_key
#     multion_api_key = x


# def openai_api_key_update(x):
#     # global openai_api_key
#     openai_api_key = x


# def replit_email_update(x):
#     # global replit_email
#     replit_email = x


# def replit_password_update(x):
#     # global replit_password
#     replit_password = x


def bot(
    history,
    multion_api_key_in,
    openai_api_key_in,
    replit_email_in,
    replit_password_in,
    local,
):
    if len(multion_api_key_in) == 0:
        raise gr.Error("MultiOn API Key is Required.")
    if len(openai_api_key_in) == 0:
        raise gr.Error("OpenAI API Key is Required.")
    start_time = time.time()
    devon = DevOn(
        editor_image=image_temp,
        browser_image=image_temp,
        scratchpad_image=image_temp,
        multion_api_key=multion_api_key_in,
        openai_api_key=openai_api_key_in,
        replit_email=replit_email_in,
        replit_password=replit_password_in,
        local=local,
    )

    for r in devon.run(history[-1][0]):
        curr_time = time.time()
        print(curr_time - start_time)
        # if curr_time - start_time >= 300:
        #     break
        text, editor_image, browser_image, scratchpad_image = r
        if type(text) == str:
            history.append((None, text))
        if editor_image is None:
            editor_image = devon.editor_image
            browser_image = devon.browser_image
            scratchpad_image = devon.scratchpad_image
        yield history, editor_image, browser_image, scratchpad_image


with gr.Blocks(css="footer {visibility: hidden}") as demo:
    md = gr.Markdown(
        """Notes:
                     - Use "Execute Locally" for better results.
                     - For local execution, you need to download the [MultiOn Browser Extension](https://chromewebstore.google.com/detail/multion/ddmjhdbknfidiopmbaceghhhbgbpenmm) and have "API Enabled" in the settings.
                     - The Huggingface Spaces demo will timeout after 5 minutes by default. To test with longer tasks, [clone the repo](https://github.com/lordspline/DevOn) and run DevOn locally."""
    )
    with gr.Row():
        with gr.Column():
            multion_api_key_in = gr.Textbox(label="MultiOn API Key")
            openai_api_key_in = gr.Textbox(label="OpenAI API Key")
        with gr.Column():
            replit_email_in = gr.Textbox(
                label="Replit Email (not needed if running locally)"
            )
            replit_password_in = gr.Textbox(
                label="Replit Password (not needed if running locally)"
            )
    with gr.Row():
        with gr.Column():
            chatbot = gr.Chatbot(
                [], elem_id="chatbot", bubble_full_width=False, height=300
            )

            chat_input = gr.MultimodalTextbox(
                value={
                    "text": "benchmark the perplexity api's resposne time with the api key abcdef"
                },
                interactive=True,
                file_types=["text"],
                placeholder="Enter message or upload file...",
                show_label=False,
            )

            with gr.Row():
                local = gr.Checkbox(True, label="Execute Locally")
                terminate = gr.Button("Terminate")
        with gr.Column():
            if devon:
                editor_view = gr.Image(
                    devon.editor_image,
                    label="Editor",
                )
            else:
                editor_view = gr.Image()
    with gr.Row():
        with gr.Column():
            if devon:
                browser_view = gr.Image(
                    devon.browser_image,
                    label="Browser",
                )
            else:
                browser_view = gr.Image()
        with gr.Column():
            if devon:
                scratchpad_view = gr.Image(
                    devon.scratchpad_image,
                    label="Scratchpad",
                )
            else:
                scratchpad_view = gr.Image()

    chat_msg = chat_input.submit(
        add_message, [chatbot, chat_input], [chatbot, chat_input]
    )
    bot_msg = chat_msg.then(
        bot,
        [
            chatbot,
            multion_api_key_in,
            openai_api_key_in,
            replit_email_in,
            replit_password_in,
            local,
        ],
        [chatbot, editor_view, browser_view, scratchpad_view],
        api_name="bot_response",
    )
    bot_msg.then(lambda: gr.MultimodalTextbox(interactive=True), None, [chat_input])

    # multion_api_key_in.change(multion_api_key_update, multion_api_key_in)
    # openai_api_key_in.change(openai_api_key_update, openai_api_key_in)
    # replit_email_in.change(replit_email_update, replit_email_in)
    # replit_password_in.change(replit_password_update, replit_password_in)

    terminate.click(fn=None, inputs=None, outputs=None, cancels=[bot_msg])

    # chatbot.like(print_like_dislike, None, None)

if __name__ == "__main__":
    demo.queue()
    demo.launch(debug=True)
