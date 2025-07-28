import { useRef, useState } from 'react';

const agentId = 'v2_agt_b2oYUFz6';
const chatId = 'cht_-IghlT9lx1xzkM-fwIpNc';
const DID_API = {
  key: 'dW1hckB6ZWRzdGFjay5jb20:1SfIyoAg4PAlXgKx0QMtt',
  url: 'https://api.d-id.com',
  websocketUrl: 'wss://ws-api.d-id.com',
  service: 'agents',
};

export default function useLogic(videoRef: React.RefObject<HTMLVideoElement | null>) {
  const sessionId = useRef(null);
  const streamId = useRef(null);
  const sessionClientAnswer = useRef(null);
  const peerConnection = useRef(null);
  const [chatLog, setChatLog] = useState([]);

  async function connectD_ID() {
    const sessionResponse = await fetch(`${DID_API.url}/${DID_API.service}/${agentId}/streams`, {
      method: 'POST',
      headers: {
        Authorization: `Basic ${DID_API.key}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        source_url: 'https://create-images-results.d-id.com/DefaultPresenters/Emma_f/v1_image.jpeg',
      }),
    });

    const { id, offer, ice_servers, session_id } = await sessionResponse.json();
    streamId.current = id;
    sessionId.current = session_id;

    await createPeerConnection(offer, ice_servers);

    await fetch(`${DID_API.url}/${DID_API.service}/${agentId}/streams/${id}/sdp`, {
      method: 'POST',
      headers: {
        Authorization: `Basic ${DID_API.key}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        answer: {
          sdp: sessionClientAnswer.current.sdp,
          type: sessionClientAnswer.current.type,
        },
        session_id: sessionId.current,
      }),
    });
  }

  async function createPeerConnection(offer, iceServers) {
    if (!peerConnection.current) {
      peerConnection.current = new RTCPeerConnection({ iceServers });
      peerConnection.current.addEventListener('icecandidate', onIceCandidate, true);
      peerConnection.current.addEventListener('track', handleOnTrack, true);
    }

    await peerConnection.current.setRemoteDescription(offer);
    sessionClientAnswer.current = await peerConnection.current.createAnswer();
    await peerConnection.current.setLocalDescription(sessionClientAnswer.current);

    const dc = peerConnection.current.createDataChannel('JanusDataChannel');
    dc.onopen = () => console.log('datachannel open');
    dc.onclose = () => console.log('datachannel close');

    dc.onmessage = (event) => {
      const prefix = 'chat/answer:';
      if (event.data.includes(prefix)) {
        const msg = decodeURIComponent(event.data.replace(prefix, ''));
        console.log('Agent:', msg);
        setChatLog(prev => [...prev, { role: 'agent', text: msg }]);
      } else {
        console.log(event.data);
      }
    };
  }

  function onIceCandidate(event) {
    if (event.candidate) {
      const { candidate, sdpMid, sdpMLineIndex } = event.candidate;
      fetch(`${DID_API.url}/${DID_API.service}/${agentId}/streams/${streamId.current}/ice`, {
        method: 'POST',
        headers: {
          Authorization: `Basic ${DID_API.key}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          candidate,
          sdpMid,
          sdpMLineIndex,
          session_id: sessionId.current,
        }),
      });
    }
  }

  function handleOnTrack(event) {
    const [stream] = event.streams;
    if (videoRef.current) {
      videoRef.current.srcObject = stream;
      videoRef.current.muted = false;
      videoRef.current
        .play()
        .then(() => console.log('🔊 Video playing'))
        .catch(err => console.error('Video play error:', err));
    }
  }

  async function sendMessage(message = null) {
    // setChatLog(prev => [...prev, { role: 'user', text: message }]);
    const response = await fetch(`${DID_API.url}/agents/${agentId}/chat/${chatId}`, {
      method: 'POST',
      headers: {
        Authorization: `Basic ${DID_API.key}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        streamId: streamId.current,
        sessionId: sessionId.current,
        messages: [
          {
            role: 'user',
            content: message,
            created_at: new Date().toString(),
          },
        ],
      }),
    });

    const data = await response.json();
    console.log('Chat response:', data);
  }

  async function onDestroyClick() {
    await fetch(`${DID_API.url}/${DID_API.service}/${agentId}/streams/${streamId.current}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Basic ${DID_API.key}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ session_id: sessionId }),
    });

    stopAllStreams();
    closePC();
  };

  function stopAllStreams() {
    if (videoRef.current) {
      videoRef.current.srcObject = null;
      videoRef.current.muted = true;
    }
  }

  function closePC() {
    if (!peerConnection.current) return;
    console.log('stopping peer connection');
    peerConnection.current.close();
    peerConnection.current.removeEventListener('icecandidate', onIceCandidate, true);
    peerConnection.current.removeEventListener('track', handleOnTrack, true);
    peerConnection.current = null
  }


  // useEffect(() => {
  //   videoRef.current = {
  //     srcObject: 'idle_1751450988029.mp4'
  //   }
  // }, [])

  return {
    connectD_ID,
    sendMessage,
    onDestroyClick,
    chatLog,
    setChatLog
  };
}
