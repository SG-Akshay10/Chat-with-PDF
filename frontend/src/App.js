import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [files, setFiles] = useState([]);
  const [sessionId, setSessionId] = useState('');
  const [processed, setProcessed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [selectedModel, setSelectedModel] = useState('llama3-70b-8192');
  const [models, setModels] = useState({});
  const [showConfirmation, setShowConfirmation] = useState(false);
  const fileInputRef = useRef(null);
  const chatEndRef = useRef(null);

  // Fetch available models on component mount
  useEffect(() => {
    fetchModels();
  }, []);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  const fetchModels = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/models`);
      setModels(response.data.models);
    } catch (error) {
      console.error('Error fetching models:', error);
    }
  };

  const handleFileUpload = (event) => {
    const selectedFiles = Array.from(event.target.files);
    const pdfFiles = selectedFiles.filter(file => file.type === 'application/pdf');
    
    if (pdfFiles.length !== selectedFiles.length) {
      alert('Please select only PDF files');
      return;
    }
    
    setFiles(pdfFiles);
  };

  const processDocuments = async () => {
    if (files.length === 0) {
      alert('Please select PDF files first');
      return;
    }

    setLoading(true);
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    try {
      const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setSessionId(response.data.session_id);
      setProcessed(true);
      setChatHistory([]);
      alert('Documents processed successfully!');
    } catch (error) {
      console.error('Error processing documents:', error);
      alert('Error processing documents. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!currentMessage.trim() || !processed) return;

    const userMessage = currentMessage;
    setCurrentMessage('');
    
    // Add user message to chat
    setChatHistory(prev => [...prev, { type: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/chat/${sessionId}`, {
        question: userMessage,
        model_name: selectedModel
      });

      // Add assistant message to chat
      setChatHistory(prev => [...prev, { 
        type: 'assistant', 
        content: response.data.answer,
        sources: response.data.sources 
      }]);
    } catch (error) {
      console.error('Error sending message:', error);
      setChatHistory(prev => [...prev, { 
        type: 'assistant', 
        content: 'Error processing your question. Please try again.' 
      }]);
    } finally {
      setLoading(false);
    }
  };

  const clearHistory = async () => {
    if (!sessionId) return;

    try {
      await axios.delete(`${API_BASE_URL}/history/${sessionId}`);
      setChatHistory([]);
      setShowConfirmation(false);
      alert('Chat history cleared!');
    } catch (error) {
      console.error('Error clearing history:', error);
      alert('Error clearing history. Please try again.');
    }
  };

  const downloadHistory = async () => {
    if (!sessionId || chatHistory.length === 0) {
      alert('No chat history to download');
      return;
    }

    try {
      const response = await axios.get(`${API_BASE_URL}/download/${sessionId}`, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `chat_history_${sessionId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading history:', error);
      alert('Error downloading history. Please try again.');
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app">
      <div className="sidebar">
        <div className="sidebar-section">
          <h3>Settings</h3>
          
          <div className="form-group">
            <label>Select LLM Model</label>
            <select 
              value={selectedModel} 
              onChange={(e) => setSelectedModel(e.target.value)}
              className="select-input"
            >
              {Object.entries(models).map(([name, value]) => (
                <option key={value} value={value}>{name}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="sidebar-section">
          <h3>Document Processing</h3>
          
          <div className="form-group">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              multiple
              accept=".pdf"
              className="file-input"
            />
            <div className="file-info">
              {files.length > 0 && (
                <div>
                  <strong>Selected files:</strong>
                  <ul>
                    {files.map((file, index) => (
                      <li key={index}>{file.name}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>

          <button 
            onClick={processDocuments} 
            disabled={loading || files.length === 0}
            className="btn btn-primary"
          >
            {loading ? 'Processing...' : 'Process Documents'}
          </button>
        </div>

        <div className="sidebar-section">
          <h3>Chat Management</h3>
          
          {chatHistory.length > 0 && (
            <button 
              onClick={downloadHistory}
              className="btn btn-secondary"
            >
              Download Chat History
            </button>
          )}

          <button 
            onClick={() => setShowConfirmation(true)}
            disabled={chatHistory.length === 0}
            className="btn btn-danger"
          >
            Clear Chat History
          </button>

          {showConfirmation && (
            <div className="confirmation-dialog">
              <p>Are you sure you want to clear the chat history?</p>
              <div className="confirmation-buttons">
                <button onClick={clearHistory} className="btn btn-danger">
                  Confirm
                </button>
                <button 
                  onClick={() => setShowConfirmation(false)} 
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="main-content">
        <div className="header">
          <h1>ChatPDF</h1>
          <p>Upload PDFs and ask questions about their content</p>
        </div>

        <div className="chat-container">
          <div className="chat-messages">
            {chatHistory.map((message, index) => (
              <div key={index} className={`message ${message.type}`}>
                <div className="message-content">
                  <div className="message-text">{message.content}</div>
                  {message.sources && message.sources.length > 0 && (
                    <div className="message-sources">
                      <strong>Sources:</strong> {message.sources.join(', ')}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="message assistant">
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          <div className="chat-input-container">
            {!processed && (
              <div className="warning">
                Please upload and process PDF files first
              </div>
            )}
            <div className="chat-input">
              <textarea
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask a question about the PDFs..."
                disabled={!processed || loading}
                rows="3"
              />
              <button 
                onClick={sendMessage}
                disabled={!processed || !currentMessage.trim() || loading}
                className="btn btn-primary send-btn"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;