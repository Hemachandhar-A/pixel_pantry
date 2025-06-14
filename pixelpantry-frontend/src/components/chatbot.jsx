import { useState, useEffect, useRef } from 'react';
import './chatbot.css';

const Chatbot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const messagesEndRef = useRef(null);
  
  // Explicitly define the API key
  const apiKey = "AIzaSyAAFKI2vwESBrFJZfl5X5daXrepc72TftM"; // 🔹 Replace this with your actual key

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Add user message to chat
    const userMessage = { text: input, sender: 'user' };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Check if API key is available
      if (!apiKey) {
        throw new Error('API key is missing. Please set your API key.');
      }

      // Add agriculture context to the prompt
      const prompt = `You are an agricultural expert chatbot. Please provide helpful advice about farming, crops, soil health, sustainable practices, and other agriculture-related topics, and keep your answers concise and short if possible. User query: ${input}`;
      
      // Make API call to Gemini
      const response = await fetch('https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=AIzaSyAAFKI2vwESBrFJZfl5X5daXrepc72TftM', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-goog-api-key': apiKey // 🔹 Explicitly using API key here
        },
        body: JSON.stringify({
          contents: [
            {
              parts: [
                {
                  text: prompt
                }
              ]
            }
          ]
        })
      });

      const data = await response.json();
      
      // Handle response
      if (data.candidates && data.candidates.length > 0) {
        const botResponse = data.candidates[0].content.parts[0].text;
        const botMessage = { text: botResponse, sender: 'bot' };
        setMessages(prev => [...prev, botMessage]);
      } else {
        throw new Error('No response from Gemini');
      }
    } catch (error) {
      console.error('Error communicating with Gemini:', error);
      const errorMessage = { text: `Sorry, I encountered an error: ${error.message}`, sender: 'bot' };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div className="chatbot-container">
      <button className="chatbot-toggle" onClick={toggleChat}>
        {isOpen ? '✕' : '🌱'}
      </button>
      
      {isOpen && (
        <div className="chatbot-window">
          <div className="chatbot-header">
            <h3>AgriAssist</h3>
          </div>
          
          <div className="chatbot-messages">
            {messages.length === 0 ? (
              <div className="welcome-message">
                <p>🌾 Hello! Im your agriculture assistant. Ask me anything about farming, crops, soil health, or sustainable practices!</p>
              </div>
            ) : (
              messages.map((message, index) => (
                <div key={index} className={`message ${message.sender}`}>
                  <div className="message-content">{message.text}</div>
                </div>
              ))
            )}
            {isLoading && (
              <div className="message bot">
                <div className="message-content loading">
                  <span>.</span><span>.</span><span>.</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
          
          <form className="chatbot-input" onSubmit={handleSubmit}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about crops, soil, farming..."
              disabled={isLoading}
            />
            <button type="submit" disabled={isLoading || !input.trim()}>
              {isLoading ? '...' : '➤'}
            </button>
          </form>
        </div>
      )}
    </div>
  );
};

export default Chatbot;
