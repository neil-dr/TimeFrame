import { useEffect, useRef, useState } from 'react';
import { socket } from '../apis/socket';
import useVideoProviderService from '../hooks/__useVideoProviderService';
import ModeBadge from './ModeBadge';

export default function Main() {
  const [mode, setMode] = useState<Modes>("idle");
  const [transcription, setTranscription] = useState<string | null>(null)
  const idleRef = useRef<HTMLVideoElement>(null)
  const remoteRef = useRef<HTMLVideoElement>(null)
  const { connected, connect, sendText, destroy } = useVideoProviderService(idleRef, remoteRef, mode, setMode)
  const pendingTextsRef = useRef<string[]>([]);

  useEffect(() => {
    const ws = socket;

    const handleOpen = () => console.log('Web socket connected');
    const handleClose = () => { setMode('idle'); };
    const handleError = () => console.error('Failed to connect to web socket');
    const handleMsg = (event: MessageEvent<Modes>) => {
      const socketResponse: SocketResponse = JSON.parse(event.data)
      if (socketResponse.event === "start-video-connection") {
        connect();
      } else if (socketResponse.event == "stt-transcription") {
        setTranscription(socketResponse.data!)
      } else if (socketResponse.event == "start-speaking") {
        if (connected) {
          sendText(socketResponse.data!)
        } else {
          pendingTextsRef.current.push(socketResponse.data!);
        }
        setTranscription(null)
      } else if (socketResponse.event == "stop-video-connection") {
        console.log('stop-video-connection')
        destroy()
      } else { // modes
        setMode(socketResponse.event);
      }
    };

    ws.addEventListener('open', handleOpen);
    ws.addEventListener('close', handleClose);
    ws.addEventListener('error', handleError);
    ws.addEventListener('message', handleMsg);

    /* 🔑  If the socket is already open, fire the callback manually */
    if (ws.readyState === WebSocket.OPEN) {
      handleOpen();
    }

    return () => {
      ws.removeEventListener('open', handleOpen);
      ws.removeEventListener('close', handleClose);
      ws.removeEventListener('error', handleError);
      ws.removeEventListener('message', handleMsg);
    };
  }, []);

  useEffect(() => {
    if (!connected && mode != "idle") {
      connect()
    }
  }, [connected])

  useEffect(() => {
    if (!connected) return;
    (async () => {
      const queue = pendingTextsRef.current;
      pendingTextsRef.current = [];
      for (const msg of queue) {
        await sendText(msg);
      }
    })();
  }, [connected, sendText]);


  return (
    <div className='relative w-fit mx-auto'>
      <div className="relative aspect-[9/16] h-screen">
        {<span
          className='absolute top-5 right-5 text-white drop-shadow-lg text-sm font-medium bg-white/10 backdrop-blur-md rounded-xl px-4 py-2 border border-white/20 shadow-xl cursor-pointer hover:bg-white/20 hover:border-white/30 transition-all duration-200 active:scale-95'>
          {mode}
        </span>}
        {/* idle layer */}
        <video
          ref={idleRef}
          // src={'./idle-square.mp4'}
          src={'./idle-portrait.mp4'}
          loop
          muted
          autoPlay
          className="absolute inset-0 w-full h-full object-cover rounded-xl"
        />

        {/* remote layer */}
        <video
          ref={remoteRef}
          muted={false}
          className="absolute inset-0 w-full h-full object-cover rounded-xl
               transition-opacity duration-1000 opacity-0"
        />
      </div>
      <ModeBadge mode={mode} />

      <div className='absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent' />
      {transcription && <span
        className='absolute bottom-24 left-1/2 -translate-x-1/2 text-white drop-shadow-lg text-sm font-medium bg-white/10 backdrop-blur-md rounded-xl px-4 py-2 border border-white/20 shadow-xl cursor-pointer hover:bg-white/20 hover:border-white/30 transition-all duration-200 active:scale-95'>
        {transcription}
      </span>}
      <span
        onClick={async () => {
          console.log(await sendText(
            `
              Good afternoon, everyone, and thank you for joining me on this journey through the hidden stories of everyday technology. I invite you to slow down, look around, and notice the ordinary objects that quietly shape our lives. Consider, for a moment, the humble pencil. At first glance it is a simple stick of cedar, but inside that cedar is graphite mined from ancient rock, clay from distant riverbeds, and a thread of wax that lets the graphite glide across paper. The wood itself was once part of a living tree that spent decades converting sunlight into cellulose. Hundreds of hands, scattered across continents, guided each material through forests, factories, and freight lines before the pencil finally rested in your palm. 
              Now turn your thoughts to the glass screen you may be holding right now. It began as grains of silica—sand that once formed the bed of a prehistoric ocean. Heated to more than fifteen hundred degrees Celsius, those grains melted, flowed, and cooled into a perfectly smooth sheet. Engineers coated that sheet with layers thinner than a human hair, each designed to repel fingerprints, to keep out moisture, and to bend light so precisely that color appears vivid even in bright sunlight. Beneath that glass lies a microchip smaller than a postage stamp, etched with billions of transistors that switch on and off trillions of times every second. That whisper-thin silicon brain required clean rooms, ultraviolet lasers, and the knowledge of thousands of scientists who spent decades chasing Moore’s Law.
              When we see these objects only as finished products, we miss the astonishing web of effort and imagination that brought them to us. We miss the miners in Chile, the chemists in Japan, the designers in Sweden, and the logistics coordinators who chart courses for container ships across stormy seas. We miss the teachers who inspired a child to study physics, and the communities that nurtured that curiosity. Technological progress is rarely the tale of a lone genius working in isolation. It is, instead, a vast coral reef of human collaboration, layer upon layer, generation after generation.
              So, as you leave this presentation, I encourage you to choose one familiar object and trace its lineage. Ask yourself: where did its materials originate? Who touched it before I did? What knowledge, what failures, what triumphs are silently encoded in its form? By answering those questions, you will discover that wonder is hidden in plain sight—waiting patiently for each of us to pay attention.
              `
          ))
        }}
        className='absolute bottom-10 left-1/2 -translate-x-1/2 text-white drop-shadow-lg text-sm font-medium bg-white/10 backdrop-blur-md rounded-xl px-4 py-2 border border-white/20 shadow-xl cursor-pointer hover:bg-white/20 hover:border-white/30 transition-all duration-200 active:scale-95'>
        Ask me a question
      </span>
    </div>
  )
}
