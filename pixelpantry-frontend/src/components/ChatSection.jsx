// src/components/ChatSection.jsx
import React, { useState } from 'react';
import { sendChatMessage } from '../api';

const ChatSection = ({ modelResults }) => {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [sending, setSending] = useState(false);
  
  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!newMessage.trim() || !modelResults) return;
    
    const userMessage = newMessage.trim();
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setNewMessage('');
    setSending(true);
    
    try {
      // Create context from model results
      const context = {
        recommended_crops: modelResults.recommended_crops || [],
        location: modelResults.location,
        latitude: modelResults.latitude,
        longitude: modelResults.longitude,
        N: modelResults.N,
        P: modelResults.P,
        K: modelResults.K,
        predicted_avg_temp: modelResults.predictions && modelResults.predictions.length > 0 
          ? modelResults.predictions[0].predicted_avg_temp 
          : 'Unknown',
        predicted_total_rainfall: modelResults.predictions && modelResults.predictions.length > 0 
          ? modelResults.predictions[0].predicted_total_rainfall 
          : 'Unknown'
      };
      
      const response = await sendChatMessage(userMessage, context);
      
      setMessages(prev => [...prev, { role: 'assistant', content: response.response }]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error processing your request. Please try again.' 
      }]);
    } finally {
      setSending(false);
    }
  };
  
  return (
    <div className="card" style={{ marginBottom: '2rem' }}>
      <h2 style={{ color: 'var(--dark)', marginBottom: '1rem' }}>
        Ask About Your Recommendations
      </h2>
      
      <div style={{ 
        maxHeight: '300px',
        overflowY: 'auto',
        marginBottom: '1rem',
        padding: '0.5rem',
        backgroundColor: modelResults ? 'white' : 'var(--light)',
        borderRadius: '4px',
        border: '1px solid var(--border)'
      }}>
        {messages.length > 0 ? (
          messages.map((msg, index) => (
            <div 
              key={index} 
              style={{
                marginBottom: '0.8rem',
                padding: '0.8rem',
                borderRadius: '4px',
                backgroundColor: msg.role === 'user' ? 'var(--light)' : 'white',
                border: msg.role === 'assistant' ? '1px solid var(--border)' : 'none',
                textAlign: msg.role === 'user' ? 'right' : 'left'
              }}
            >
              <div style={{ fontWeight: msg.role === 'user' ? '500' : '400' }}>
                {msg.content}
              </div>
            </div>
          ))
        ) : (
          <div style={{ 
            textAlign: 'center', 
            padding: '2rem', 
            color: 'var(--text-secondary)',
            fontStyle: 'italic'
          }}>
            {modelResults 
              ? 'Ask questions about your crop recommendations or farming advice' 
              : 'Run the model first to get crop recommendations'}
          </div>
        )}
        {sending && (
          <div style={{ display: 'flex', alignItems: 'center', padding: '0.5rem' }}>
            <div className="loading-spinner" style={{ 
              width: '1rem', 
              height: '1rem', 
              borderWidth: '2px',
              marginRight: '0.5rem',
              border: '2px solid rgba(76, 175, 80, 0.3)',
              borderTopColor: 'var(--primary)'
            }}></div>
            <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
              Processing...
            </span>
          </div>
        )}
      </div>
      
      <form onSubmit={handleSendMessage} style={{ display: 'flex' }}>
        
        <input
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          placeholder={modelResults ? "Ask about your recommendations..." : "Run the model first..."}
          disabled={!modelResults || sending}
          style={{
            flex: 1,
            padding: '0.8rem',
            borderRadius: '4px 0 0 4px',
            border: '1px solid var(--border)',
            fontSize: '1rem'
          }}
        />
        <button 
          type="submit" 
          className="btn"
          disabled={!modelResults || !newMessage.trim() || sending}
          style={{ borderRadius: '0 4px 4px 0' }}
        >
          Send
        </button>
        
      </form>
    </div>
  );
};

export default ChatSection;