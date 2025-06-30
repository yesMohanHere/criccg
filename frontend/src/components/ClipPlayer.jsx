import React, { useEffect, useState } from 'react';

export default function ClipPlayer({ videoId }) {
  const [url, setUrl] = useState(null);

  useEffect(() => {
    const fetchUrl = async () => {
      try {
        const res = await fetch(`/api/merged/${videoId}`);
        const blob = await res.blob();
        setUrl(URL.createObjectURL(blob));
      } catch (err) {
        console.error(err);
      }
    };
    fetchUrl();
  }, [videoId]);

  if (!url) return null;
  return (
    <div>
      <h3>Merged Clip</h3>
      <video src={url} controls style={{ maxWidth: '100%' }} />
    </div>
  );
}
