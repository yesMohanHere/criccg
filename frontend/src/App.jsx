import React, { useState } from 'react';
import VideoUploader from './components/VideoUploader.jsx';
import StatusViewer from './components/StatusViewer.jsx';
import LabelSelector from './components/LabelSelector.jsx';
import ClipPlayer from './components/ClipPlayer.jsx';

export default function App() {
  const [videoId, setVideoId] = useState(null);

  return (
    <div style={{ padding: '1rem', fontFamily: 'sans-serif' }}>
      <h1>Video Labeler</h1>
      <VideoUploader onUploaded={setVideoId} />
      {videoId && (
        <>
          <StatusViewer videoId={videoId} />
          <LabelSelector videoId={videoId} />
          <ClipPlayer videoId={videoId} />
        </>
      )}
    </div>
  );
}
