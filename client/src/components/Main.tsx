import { useEffect, useRef, useState } from 'react';
import { socket } from '../apis/socket';
import useVideoProviderService from '../hooks/__useVideoProviderService';
import ModeIcon from './ModeIcon';
import FullscreenButton from './FullscreenButton';
import Text from './Text';

export default function Main() {
  const [mode, setMode] = useState<Modes>("idle");
  const [transcription, setTranscription] = useState<string | null>(null)
  const speakingText = useRef('')
  const idleRef = useRef<HTMLVideoElement>(null)
  const remoteRef = useRef<HTMLVideoElement>(null)

  function onStartSpeaking() {
    setTranscription(''); // reset output

    if (speakingText.current.length === 0) return;
    const words = speakingText.current.trim().split(/\s+/);

    let i = 0;
    let currentText = ''; // local accumulator

    const id = setInterval(() => {
      currentText += (currentText ? ' ' : '') + words[i];
      if (currentText != '' && currentText != ' ')
        setTranscription(currentText);
      i++;
      if (i >= words.length) {
        clearInterval(id);
        setTimeout(() => {
          setTranscription(null); // ✅ clear after last word delay
        }, 500); // optional delay before clearing (tweakable)
      }

    }, 300);
  }

  const { connected, connect, sendText, destroy } = useVideoProviderService(idleRef, remoteRef, onStartSpeaking, setMode)
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
          speakingText.current = socketResponse.data!
        } else {
          pendingTextsRef.current.push(socketResponse.data!);
        }
        setTranscription(null)
      } else if (socketResponse.event == "stop-video-connection") {
        console.log('stop-video-connection')
        destroy()
      } else { // modes
        if (socketResponse.event == "listening" && speakingText.current != "") {
          setTranscription(null)
        }
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
        speakingText.current = msg
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
      <div className='absolute bottom-[5%] left-0 right-0 p-6'>
        <div className='flex items-center gap-2'>
          <ModeIcon mode={mode} className='shrink-0' />
          <Text mode={mode} transcription={transcription} />
        </div>
      </div>
    </div>
  )
}
