import React, { useState } from 'react';
import './App.css';

function App() {
  const [message, setMessage] = useState('');
  const [document, setDocument] = useState(null);
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!message || !document) {
      alert('Please enter a message and upload a document.');
      return;
    }

    const formData = new FormData();
    formData.append('message', message);
    formData.append('document', document);

    setLoading(true);

    try {
      const res = await fetch('https://documentorllm.onrender.com/chat/', {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      setResponse(data.response || 'No response received.');
    } catch (error) {
      setResponse('❌ Error: Unable to fetch response.');
    }

    setLoading(false);
  };

  return (
    <div className="app-container">
      <h1 className="title">DocuMentor</h1>
      <form onSubmit={handleSubmit} className="chat-form">
        <textarea
          className="message-input"
          placeholder="Enter your query..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
        />

        <input
          type="file"
          accept=".pdf,.docx"
          onChange={(e) => setDocument(e.target.files[0])}
          className="file-input"
        />

        <button type="submit" className="submit-btn" disabled={loading}>
          {loading ? 'Processing...' : 'Ask'}
        </button>
      </form>

      {response && (
        <div className="response-box">
          <h3>🧠 Response:</h3>
          <pre>{response}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
