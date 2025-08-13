import { useEffect, useRef, useState } from 'react';
import { socket } from '../apis/socket';
import useVideoProviderService from '../hooks/__useVideoProviderService';
import ModeIcon from './ModeIcon';
import FullscreenButton from './FullscreenButton';

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
        <FullscreenButton />
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
      <div className='absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent' />
      <div className='absolute bottom-10 left-2 flex items-center gap-2'>
        <ModeIcon mode={mode} />
        <span
          className='text-white drop-shadow-lg text-sm font-medium bg-white/10 backdrop-blur-md rounded-xl px-4 py-2 border border-white/20 shadow-xl cursor-pointer hover:bg-white/20 hover:border-white/30 transition-all duration-200 active:scale-95'>
          {mode == "idle" ? 'Ask me a question' :
            mode == "listening" ? (transcription || "I'm listening....") :
              mode == "thinking" ? "I'm thinking...." :
                mode == "speaking" ? "The thinking mode is currently under development so this is a dummy Speech." : "Ask me a question"}
        </span>
      </div>
    </div>
  )
}
