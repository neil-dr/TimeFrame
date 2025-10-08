import { useEffect, useRef, useState } from 'react';
import { socket } from '../apis/socket';
import useVideoProviderService from '../hooks/useVideoProviderService';
import ModeIcon from './ModeIcon';
import FullscreenButton from './FullscreenButton';
import Text from './Text';
import useTextDisplay from '../hooks/useTextDisplay';
import subtitles from '../subtitles.json';
import useCameraSender from '../hooks/useCameraSender';

export default function Main() {
  const [mode, setMode] = useState<Modes>("idle");
  const speakingText = useRef('')
  const idleRef = useRef<HTMLVideoElement>(null)
  const remoteRef = useRef<HTMLVideoElement>(null)
  const {
    transcription,
    setTranscription,
    onStartSpeaking
  } = useTextDisplay(speakingText)

  const { connected, connect, sendText, destroy } = useVideoProviderService(idleRef, remoteRef, onStartSpeaking, setMode)
  const pendingTextsRef = useRef<string[]>([]);
  useCameraSender();

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
      } else if (socketResponse.event == "start-offline-speaking") {
        // show offline video - (/offline-fallback.mp4)
        // first fade in the top video using opacity
        // when video end fade it out
        const videoElement = remoteRef.current!
        videoElement.srcObject = null
        videoElement.src = socketResponse.data!
        videoElement.play()
        videoElement.addEventListener("play", () => {
          console.log('play', socketResponse.data!)
          const message = JSON.stringify({ event: "speaking" });
          ws.send(message)
          videoElement.style.opacity = '1'
          setMode("speaking")
          const text = subtitles["1"];
          speakingText.current = text
          onStartSpeaking()
        })
        videoElement.addEventListener("ended", () => {
          console.log('ended')
          videoElement.style.opacity = '0'
          const message = JSON.stringify({ event: "back-to-listening" });
          ws.send(message)
          setMode("listening")
        })
      } else if (socketResponse.event == "error") {
        setMode("error")
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
    if (navigator.onLine && !connected && mode != "idle") {
      connect()
    }
  }, [connected, mode])

  useEffect(() => {
    if (mode == "listening" && speakingText.current != "") {
      setTranscription(null)
    }
  }, [mode])

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
          // src={'./idle-portrait.mp4'}
          src={'./lincoln-3.mp4'}
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
