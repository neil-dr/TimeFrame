from utils.websocket_manager import manager
from utils.internet import is_connected
chat = []


def think(input_txt):
    global chat

    manager.broadcast("thinking")
    chat.append({
        "source": "user",
        "content": input_txt
    })

    if is_connected():
        # LLM and Guardrail Layer
        output_txt = """The thinking mode is currently under development so this is a dummy Speech."""
        chat.append({
            "source": "lincoln",
            "content": output_txt
        })
        manager.broadcast(event="start-speaking", data=output_txt)  # trigger speak mode
    else:
        output_txt = """No internet connection detected, showing demo video instead now."""
        manager.broadcast(event="start-offline-speaking", data=output_txt)  # trigger speak mode
