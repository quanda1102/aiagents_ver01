import React, { useState, useEffect, useRef } from 'react';
import { SendIcon, PaperclipIcon } from 'lucide-react';

const ConversationPanel = () => {
  const [message, setMessage] = useState('');
  const [conversation, setConversation] = useState([
    {
      id: 1,
      sender: 'user',
      text: "Hello, I'm having an issue with my account.",
      time: '10:32 AM'
    },
    {
      id: 2,
      sender: 'agent',
      text: "Hi there! I'm sorry to hear that. Could you please provide more details about the issue you're experiencing?",
      time: '10:33 AM'
    }
  ]);
  const messagesEndRef = useRef(null);

  // Tự động cuộn xuống tin nhắn mới nhất
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversation]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;

    // Thêm tin nhắn người dùng vào conversation
    const newUserMessage = {
      id: conversation.length + 1,
      sender: 'user',
      text: message,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setConversation([...conversation, newUserMessage]);
    setMessage('');

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 1,
          user_name: 'John Doe',
          user_email: 'john.doe@example.com',
          user_phone: '0909090909',
          user_address: '123 Nguyen Van Linh, Q9, TP.HCM',
          user_city: 'TP.HCM',
          user_state: 'Q9',
          user_zip: '123456',
          user_country: 'Vietnam',
          user_role: 'admin',
          session_id: '',
          user_input: newUserMessage.text
        })
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      const newAgentMessage = {
        id: conversation.length + 2,
        sender: 'agent',
        text: data.response,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setConversation(prev => [...prev, newAgentMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: conversation.length + 2,
        sender: 'agent',
        text: 'Sorry, something went wrong. Please try again.',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setConversation(prev => [...prev, errorMessage]);
    }
  };

  return (
    <div className="flex flex-col h-screen md:h-full">
      <div className="p-4 bg-white border-b border-gray-200">
        <h2 className="text-xl font-medium">Conversation with John Doe</h2>
        <p className="text-sm text-gray-500">Ticket #1234 - Account Access Issue</p>
      </div>
      <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
        <div className="max-w-3xl mx-auto space-y-4">
          {conversation.map(msg => (
            <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] rounded-lg p-3 ${msg.sender === 'user' ? 'bg-[#007BFF] text-white' : 'bg-gray-200 text-gray-800'}`}>
                <p>{msg.text}</p>
                <p className={`text-xs mt-1 ${msg.sender === 'user' ? 'text-blue-100' : 'text-gray-500'}`}>
                  {msg.time}
                </p>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>
      <div className="p-4 bg-white border-t border-gray-200">
        <form onSubmit={handleSend} className="flex items-center">
          <button type="button" className="p-2 text-gray-500 hover:text-gray-700">
            <PaperclipIcon size={20} />
          </button>
          <input
            type="text"
            value={message}
            onChange={e => setMessage(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 p-2 border border-gray-300 rounded-l-md focus:outline-none focus:border-[#007BFF]"
          />
          <button
            type="submit"
            className="bg-[#007BFF] text-white p-2 rounded-r-md hover:bg-blue-600 transition-colors"
            disabled={!message.trim()}
          >
            <SendIcon size={20} />
          </button>
        </form>
      </div>
    </div>
  );
};

export default ConversationPanel;