import React, { useEffect, useState } from 'react';

export default function StatusViewer({ videoId }) {
  const [status, setStatus] = useState('pending');

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`/api/status/${videoId}`);
        const json = await res.json();
        setStatus(json.status);
      } catch (err) {
        console.error(err);
      }
    }, 3000);
    return () => clearInterval(interval);
  }, [videoId]);

  return <p>Status: {status}</p>;
}
