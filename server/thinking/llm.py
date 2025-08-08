from utils.websocket_manager import manager
chat = []


def think(input_txt):
    global chat

    manager.broadcast("thinking")
    chat.append({
        "source": "user",
        "content": input_txt
    })

    # LLM and Guardrail Layer
    output_txt = """The thinking mode is currently under development so this is a dummy Speech."""
    chat.append({
        "source": "lincoln",
        "content": output_txt
    })
    manager.broadcast(event="start-speaking", data=output_txt)  # trigger speak mode
