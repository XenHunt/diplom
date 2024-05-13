import gradio as gr


def video_identity(process_video, video):
    print(process_video)
    return video


def playing_video():
    print("playing")


new = True
with gr.Blocks() as demo:
    with gr.Row():
        v1 = gr.Video()
        v2 = gr.Video(interactive=False)

        v1.play(playing_video)
        v1.upload(lambda x: video_identity(new, x), v1, v2)

if __name__ == "__main__":
    demo.launch()
