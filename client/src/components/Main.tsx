import { useEffect, useRef, useState } from 'react';
import { getSocket } from '../apis/socket';
import useVideoProviderService from '../hooks/useVideoProviderService';

type WSStatus = "Connected" | "Disconnected" | "Error";
export default function Main() {
  const [wsStatus, setWsStatus] = useState<WSStatus>("Disconnected");
  const [mode, setMode] = useState<Modes>("idle");
  const [transcription, setTranscription] = useState<string | null>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const { connect, sendText } = useVideoProviderService(videoRef)

  useEffect(() => {
    // connect();
    const ws = getSocket();
    ws.onopen = () => setWsStatus("Connected");
    ws.onclose = () => {
      setWsStatus("Disconnected");
      setMode("idle");
    };
    ws.onerror = () => setWsStatus("Error");
    ws.onmessage = async (event: MessageEvent<string>) => {
      const socketResponse: SocketResponse = JSON.parse(event.data)
      if (socketResponse.event === "start-video-connection") {
        await connect();
      } else if (socketResponse.event == "stt-transcription") {
        console.log(socketResponse.data)
        setTranscription(socketResponse.data!)
      } else { // modes
        if (socketResponse.event == "speaking") {
          console.log(socketResponse.data)
          sendText(socketResponse.data!)
          setTranscription(null)
        }
        setMode(socketResponse.event);
      }
    };
    return () => ws.close();
  }, []);

  return (
    <div className='relative w-fit mx-auto'>
      <div className="relative aspect-[9/16] h-screen">
        {<span
          className='absolute top-5 right-5 text-white drop-shadow-lg text-sm font-medium bg-white/10 backdrop-blur-md rounded-xl px-4 py-2 border border-white/20 shadow-xl cursor-pointer hover:bg-white/20 hover:border-white/30 transition-all duration-200 active:scale-95'>
          {mode}
        </span>}
        {/* idle layer */}
        <video
          src={'./idle.mp4'}
          loop
          muted
          autoPlay
          className="absolute inset-0 w-full h-full object-contain rounded-xl"
        />

        {/* remote layer */}
        <video
          ref={videoRef}
          muted={false}
          className="absolute inset-0 w-full h-full object-contain rounded-xl
               transition-opacity duration-150 opacity-0"
        />
      </div>

      <div className='absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent' />
      {transcription && <span
        className='absolute bottom-24 left-1/2 -translate-x-1/2 text-white drop-shadow-lg text-sm font-medium bg-white/10 backdrop-blur-md rounded-xl px-4 py-2 border border-white/20 shadow-xl cursor-pointer hover:bg-white/20 hover:border-white/30 transition-all duration-200 active:scale-95'>
        {transcription}
      </span>}
      <span
        onClick={async () => {
          console.log(await sendText("On offering to help the blind man, the man who then stole his car."))
        }}
        className='absolute bottom-10 left-1/2 -translate-x-1/2 text-white drop-shadow-lg text-sm font-medium bg-white/10 backdrop-blur-md rounded-xl px-4 py-2 border border-white/20 shadow-xl cursor-pointer hover:bg-white/20 hover:border-white/30 transition-all duration-200 active:scale-95'>
        Ask me a question
      </span>
    </div>
  )
}
