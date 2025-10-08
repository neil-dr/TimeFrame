from utils.websocket_manager import manager
from utils.internet import is_connected
from thinking.llm_online import think as think_online
from thinking.ll_offline import think as think_offline
chat = []


def think(input_txt):
    global chat

    manager.broadcast("thinking")
    push_message({
        "role": "user",
        "content": input_txt
    })
    if is_connected():
        # LLM and Guardrail Layer
        output_txt = "the books I could borrow and the stories I heard. The wilderness taught resilience. It was a humble"#think_online(input_txt, chat)
        # output_txt = "Indeed, confidence in a court relies."
        push_message({
            "role": "lincoln",
            "content": output_txt
        })
        manager.broadcast(event="start-speaking",
                          data=output_txt)  # trigger speak mode
    else:
        video_id = think_offline(input_txt, chat)
        video_src = video_id + ".mp4"
        # output_txt = """No internet connection detected, showing demo video instead now."""
        manager.broadcast(event="start-offline-speaking",
                          data=video_src)  # trigger speak mode


def push_message(message: dict, max_messages: int = 10):
    global chat
    chat.append(message)

    # trim oldest if too long
    if len(chat) > max_messages:
        chat[:] = chat[-max_messages:]

    return chat
