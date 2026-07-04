import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Send, Paperclip, Plus, LogOut, User } from 'lucide-react';
import api from '../api';

export default function Dashboard() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [profile, setProfile] = useState({});
  const [conversationId, setConversationId] = useState(null);
  const navigate = useNavigate();
  const fileInputRef = useRef();
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Initial setup
    createNewConversation();
  }, []);

  useEffect(() => {
    if (conversationId) {
      fetchProfile(conversationId);
    }
  }, [conversationId]);

  const fetchProfile = async (cId) => {
    try {
      const res = await api.get(`/profile/${cId}`);
      setProfile(res.data);
    } catch (err) {
      if (err.response?.status === 401) {
        navigate('/login');
      }
    }
  };

  const createNewConversation = async () => {
    try {
      const res = await api.post('/conversations/');
      setConversationId(res.data.id);
      setMessages([{ role: 'assistant', content: 'Hello! I am FinSahayak, your personal financial advisor. How can I help you today?' }]);
    } catch (err) {
      console.error("Error creating conversation", err);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || !conversationId) return;
    
    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setLoading(true);

    try {
      const res = await api.post(`/conversations/${conversationId}/chat`, { message: userMsg });
      
      // Update profile in case it changed
      fetchProfile(conversationId);

      // Add AI response
      if (res.data.response) {
        setMessages(prev => [...prev, { role: 'assistant', content: res.data.response }]);
      }
      
      // If a final report was generated, show it
      if (res.data.final_report) {
        setMessages(prev => [...prev, { role: 'assistant', content: res.data.final_report }]);
      }

    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' }]);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file || !conversationId) return;

    const formData = new FormData();
    formData.append('file', file);
    
    setMessages(prev => [...prev, { role: 'user', content: `[Uploaded File: ${file.name}]` }]);
    setLoading(true);

    try {
      await api.post(`/conversations/${conversationId}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      // Optionally trigger a chat request right after upload to acknowledge
      const res = await api.post(`/conversations/${conversationId}/chat`, { message: `I have uploaded ${file.name}. Please confirm you can read it.` });
      setMessages(prev => [...prev, { role: 'assistant', content: res.data.response }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: `Error uploading file: ${err.response?.data?.detail || err.message}` }]);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <div className="app-container">
      {/* Left Sidebar */}
      <div className="sidebar">
        <button className="primary-btn" onClick={createNewConversation} style={{display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', marginBottom: '2rem'}}>
          <Plus size={16} /> New Chat
        </button>
        <div style={{flex: 1}}></div>
        <button className="icon-btn" onClick={handleLogout} style={{display: 'flex', alignItems: 'center', gap: '0.5rem', width: '100%', justifyContent: 'flex-start'}}>
          <LogOut size={16} /> Logout
        </button>
      </div>

      {/* Main Chat Area */}
      <div className="main-content">
        <div className="chat-messages">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message-wrapper ${msg.role}`}>
              <div className="message-content">
                <div className={`avatar ${msg.role}`}>
                  {msg.role === 'user' ? <User size={18} /> : 'AI'}
                </div>
                <div className="markdown-body">
                  {msg.role === 'user' ? (
                    <p>{msg.content}</p>
                  ) : (
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                  )}
                </div>
              </div>
            </div>
          ))}
          {loading && (
            <div className={`message-wrapper assistant`}>
              <div className="message-content">
                <div className="avatar assistant">AI</div>
                <div className="markdown-body"><p>Thinking...</p></div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="input-area-container">
          <div className="input-box">
            <input 
              type="file" 
              ref={fileInputRef} 
              style={{display: 'none'}} 
              onChange={handleFileUpload}
              accept=".pdf,.png,.jpg,.jpeg"
            />
            <button className="icon-btn" onClick={() => fileInputRef.current.click()} title="Upload Document">
              <Paperclip size={20} />
            </button>
            <textarea
              placeholder="Message FinSahayak..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              rows={1}
            />
            <div className="input-actions">
              <button className="icon-btn send-btn" onClick={handleSend} disabled={!input.trim() || loading}>
                <Send size={18} />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Right Sidebar - Financial Profile */}
      <div className="profile-sidebar">
        <h2 style={{fontSize: '1rem', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
          <User size={18} /> Financial Profile
        </h2>
        
        <div className="profile-card">
          <h3>Personal</h3>
          <div className="profile-item"><span className="profile-label">Age</span><span className="profile-value">{profile.age || '-'}</span></div>
          <div className="profile-item"><span className="profile-label">Occupation</span><span className="profile-value" style={{textTransform: 'capitalize'}}>{profile.occupation || '-'}</span></div>
          <div className="profile-item"><span className="profile-label">Risk</span><span className="profile-value" style={{textTransform: 'capitalize'}}>{profile.risk_tolerance || '-'}</span></div>
        </div>

        <div className="profile-card">
          <h3>Financials</h3>
          <div className="profile-item"><span className="profile-label">Type</span><span className="profile-value" style={{textTransform: 'capitalize'}}>{profile.income_type || '-'}</span></div>
          <div className="profile-item"><span className="profile-label">Income</span><span className="profile-value">{profile.income ? `₹${profile.income.toLocaleString()}` : '-'}</span></div>
          <div className="profile-item"><span className="profile-label">Expenses</span><span className="profile-value">{profile.expenses ? `₹${profile.expenses.toLocaleString()}` : '-'}</span></div>
          <div className="profile-item"><span className="profile-label">Debt</span><span className="profile-value">{profile.debt ? `₹${profile.debt.toLocaleString()}` : '-'}</span></div>
        </div>

        <div className="profile-card">
          <h3>Goals</h3>
          <p style={{fontSize: '0.875rem'}}>{profile.goals || 'No goals specified yet.'}</p>
        </div>

        {profile.special_circumstances && (
          <div className="profile-card">
            <h3>Special Circumstances</h3>
            <p style={{fontSize: '0.875rem', color: '#ffb86c'}}>{profile.special_circumstances}</p>
          </div>
        )}
      </div>
    </div>
  );
}
