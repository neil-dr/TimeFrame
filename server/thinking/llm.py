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
    output_txt = """Good afternoon, everyone, and thank you for joining me on this journey through the hidden stories of everyday technology. I invite you to slow down, look around, and notice the ordinary objects that quietly shape our lives. Consider, for a moment, the humble pencil. At first glance it is a simple stick of cedar, but inside that cedar is graphite mined from ancient rock, clay from distant riverbeds, and a thread of wax that lets the graphite glide across paper. The wood itself was once part of a living tree that spent decades converting sunlight into cellulose. Hundreds of hands, scattered across continents, guided each material through forests, factories, and freight lines before the pencil finally rested in your palm. 
                Now turn your thoughts to the glass screen you may be holding right now. It began as grains of silica—sand that once formed the bed of a prehistoric ocean. Heated to more than fifteen hundred degrees Celsius, those grains melted, flowed, and cooled into a perfectly smooth sheet. Engineers coated that sheet with layers thinner than a human hair, each designed to repel fingerprints, to keep out moisture, and to bend light so precisely that color appears vivid even in bright sunlight. Beneath that glass lies a microchip smaller than a postage stamp, etched with billions of transistors that switch on and off trillions of times every second. That whisper-thin silicon brain required clean rooms, ultraviolet lasers, and the knowledge of thousands of scientists who spent decades chasing Moore’s Law.
                When we see these objects only as finished products, we miss the astonishing web of effort and imagination that brought them to us. We miss the miners in Chile, the chemists in Japan, the designers in Sweden, and the logistics coordinators who chart courses for container ships across stormy seas. We miss the teachers who inspired a child to study physics, and the communities that nurtured that curiosity. Technological progress is rarely the tale of a lone genius working in isolation. It is, instead, a vast coral reef of human collaboration, layer upon layer, generation after generation."""
    chat.append({
        "source": "lincoln",
        "content": output_txt
    })
    manager.broadcast(event="start-speaking", data=output_txt)  # trigger speak mode
