import { useRef, type RefObject } from 'react';
import { getSocket } from '../apis/socket';

/**
 * useDIDAgentStream – React hook for manual‑mode D‑ID Agents
 * -----------------------------------------------------------
 * ‑ Opens a WebRTC stream (no LLM).
 * ‑ `sendText()` posts a **video‑stream** request so the avatar voices the EXACT
 *   sentence you supply (bypasses /chat and its GPT pipeline).
 */

// ▸ CONFIG – move to envs in prod
const AGENT_ID = 'v2_agt_xgX-Y0FQ';
const DID = {
  API_KEY_B64: 'ZmVwaWszOTUwOUBmb2JveHMuY29t:flqm-4RFO9SufOL6WhbeF',
  ROOT: 'https://api.d-id.com',
  SERVICE: 'agents',
} as const;

// ▸ TYPES
interface IceServer {
  urls: string | string[];
  username?: string;
  credential?: string;
}
interface CreateStreamRes {
  id: string;
  offer: RTCSessionDescriptionInit;
  ice_servers: IceServer[];
  session_id: string;
}
interface SendMessageRes { id: string; status: string }

export default function useDIDAgentStream(videoRef: RefObject<HTMLVideoElement | null>) {
  const sessionId = useRef<string | null>(null);
  const streamId = useRef<string | null>(null);
  const pc = useRef<RTCPeerConnection | null>(null);

  // helper with auth header
  const didFetch = (path: string, init: RequestInit = {}) =>
    fetch(`${DID.ROOT}${path}`, {
      ...init,
      headers: {
        Authorization: `Basic ${DID.API_KEY_B64}`,
        'Content-Type': 'application/json',
        ...(init.headers || {}),
      },
    });

  const handleIceCandidate = async (e: RTCPeerConnectionIceEvent) => {
    if (!e.candidate || !streamId.current) return;
    const { candidate, sdpMid, sdpMLineIndex } = e.candidate;
    await didFetch(`/${DID.SERVICE}/${AGENT_ID}/streams/${streamId.current}/ice`, {
      method: 'POST',
      body: JSON.stringify({ candidate, sdpMid, sdpMLineIndex, session_id: sessionId.current }),
    });
  };

  function wireDataChannel(dc: RTCDataChannel) {
    dc.onmessage = (event) => {
      const msg = event.data;
      /* 1 ▸ D-ID control messages */
      if (msg === 'stream/done') {
        console.log('🎬 stream/done  ← speech clip finished');
        backToIdle();

        // notify backend to get back to listening
        const ws = getSocket();

        const message = JSON.stringify({ event: "back-to-listening" });
        ws.send(message)
        return;
      }
    };
  }

  const fadeIn = () => {
    if (videoRef.current) videoRef.current.style.opacity = '1';
  };
  const fadeOut = () => {
    if (videoRef.current) videoRef.current.style.opacity = '0';
  };

  function backToIdle() {
    fadeOut();
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  }

  const handleTrack = (ev: RTCTrackEvent) => {
    const [remote] = ev.streams;
    const [videoTrack] = remote.getVideoTracks();

    /* … inside handleTrack … */
    videoTrack.addEventListener('unmute', () => {
      if (!videoRef.current) return;

      // attach stream
      videoRef.current.srcObject = remote;
      videoRef.current.onloadeddata = () => {
        videoRef.current!.onloadeddata = null;
        fadeIn();                      // avatar now visible
        videoRef.current!.play().catch(console.error);
      };
    });

    /* hide again when finished */
    videoTrack.addEventListener('mute', () => {
      console.log('muted')
    }, { once: true });
    videoTrack.addEventListener('ended', fadeOut);
    videoTrack.addEventListener('inactive', fadeOut);
  };

  /** Establish WebRTC & start video */
  const connect = async () => {
    const res = await didFetch(`/${DID.SERVICE}/${AGENT_ID}/streams`, {
      method: 'POST',
      body: JSON.stringify({ "stream_warmup": true, config: { agent: { type: 'manual' } }, }),
    });
    if (!res.ok) throw new Error(`stream create failed ${res.status}`);
    const { id, offer, ice_servers, session_id } = (await res.json()) as CreateStreamRes;
    streamId.current = id;
    sessionId.current = session_id;

    pc.current = new RTCPeerConnection({ iceServers: ice_servers });
    const dc = pc.current.createDataChannel('JanusDataChannel');
    wireDataChannel(dc);

    pc.current.addEventListener('icecandidate', handleIceCandidate);
    pc.current.addEventListener('track', handleTrack);
    pc.current.addEventListener('datachannel', e => {
      console.log('inside data chanel')
      wireDataChannel(e.channel);
    });


    await pc.current.setRemoteDescription(offer);
    const answer = await pc.current.createAnswer();
    await pc.current.setLocalDescription(answer);

    await didFetch(`/${DID.SERVICE}/${AGENT_ID}/streams/${id}/sdp`, {
      method: 'POST',
      body: JSON.stringify({ answer, session_id }),
    });
  };

  /** Speak _exactly_ `text` (no LLM involved) */
  const sendText = async (text: string): Promise<SendMessageRes> => {
    if (!streamId.current || !sessionId.current) throw new Error('Stream not ready');

    const payload = {
      script: { type: 'text', input: text },
      driver_url: 'bank://lively/', // subtle idle motions
      session_id: sessionId.current,
      config: { stitch: true }
    };

    const res = await didFetch(`/${DID.SERVICE}/${AGENT_ID}/streams/${streamId.current}`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });

    if (!res.ok) throw new Error(`sendText failed ${res.status}: ${await res.text()}`);
    return (await res.json()) as SendMessageRes;
  };

  /** Cleanup */
  const destroy = async () => {
    if (streamId.current) {
      await didFetch(`/${DID.SERVICE}/${AGENT_ID}/streams/${streamId.current}`, {
        method: 'DELETE',
        body: JSON.stringify({ session_id: sessionId.current }),
      });
    }
    if (videoRef.current) videoRef.current.srcObject = null;
    if (pc.current) {
      pc.current.close();
      pc.current.removeEventListener('icecandidate', handleIceCandidate);
      pc.current.removeEventListener('track', handleTrack);
      pc.current = null;
    }
    streamId.current = null;
    sessionId.current = null;
  };

  return { connect, sendText, destroy };
}
