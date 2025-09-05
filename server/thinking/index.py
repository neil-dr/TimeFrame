from utils.websocket_manager import manager
from utils.internet import is_connected
from thinking.llm_online import think as think_online
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
        output_txt = think_online(input_txt)
        # output_txt = "Indeed, confidence in a court relies."
        print("online thinking ended", output_txt)
        chat.append({
            "source": "lincoln",
            "content": output_txt
        })
        manager.broadcast(event="start-speaking",
                          data=output_txt)  # trigger speak mode
    # else:
    #     output_txt = """No internet connection detected, showing demo video instead now."""
    #     manager.broadcast(event="start-offline-speaking",
    #                       data=output_txt)  # trigger speak mode
