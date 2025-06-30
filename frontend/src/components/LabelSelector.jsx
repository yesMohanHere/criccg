import React, { useEffect, useState } from 'react';

export default function LabelSelector({ videoId }) {
  const [labels, setLabels] = useState([]);
  const [selected, setSelected] = useState([]);

  useEffect(() => {
    const fetchLabels = async () => {
      try {
        const res = await fetch('/api/labels');
        const json = await res.json();
        setLabels(json.labels || []);
      } catch (err) {
        console.error(err);
      }
    };
    fetchLabels();
  }, []);

  const handleSubmit = async () => {
    try {
      await fetch(`/api/labels/${videoId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ labels: selected }),
      });
    } catch (err) {
      console.error(err);
    }
  };

  const toggle = (label) => {
    setSelected((prev) =>
      prev.includes(label) ? prev.filter((l) => l !== label) : [...prev, label]
    );
  };

  return (
    <div>
      <h3>Select Labels</h3>
      {labels.map((label) => (
        <label key={label} style={{ marginRight: '1rem' }}>
          <input
            type="checkbox"
            checked={selected.includes(label)}
            onChange={() => toggle(label)}
          />
          {label}
        </label>
      ))}
      <div>
        <button onClick={handleSubmit}>Submit Labels</button>
      </div>
    </div>
  );
}
