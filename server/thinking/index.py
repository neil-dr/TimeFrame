from utils.websocket_manager import manager
from utils.internet import is_connected
from thinking.llm_online import think as think_online
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
        output_txt = think_online(input_txt, chat)
        # output_txt = "Indeed, confidence in a court relies."
        push_message({
            "role": "lincoln",
            "content": output_txt
        })
        manager.broadcast(event="start-speaking",
                          data=output_txt)  # trigger speak mode
    # else:
    #     output_txt = """No internet connection detected, showing demo video instead now."""
    #     manager.broadcast(event="start-offline-speaking",
    #                       data=output_txt)  # trigger speak mode


def push_message(message: dict, max_messages: int = 10):
    global chat
    chat.append(message)

    # trim oldest if too long
    if len(chat) > max_messages:
        chat[:] = chat[-max_messages:]

    return chat
