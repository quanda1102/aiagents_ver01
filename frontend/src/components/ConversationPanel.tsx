import React, { useState } from 'react';
import { SendIcon, PaperclipIcon } from 'lucide-react';
const ConversationPanel = () => {
  const [message, setMessage] = useState('');
  // Sample conversation data
  const conversation = [{
    id: 1,
    sender: 'user',
    text: "Hello, I'm having an issue with my account.",
    time: '10:32 AM'
  }, {
    id: 2,
    sender: 'agent',
    text: "Hi there! I'm sorry to hear that. Could you please provide more details about the issue you're experiencing?",
    time: '10:33 AM'
  }, {
    id: 3,
    sender: 'user',
    text: 'I can\'t access my subscription settings. It says "error 404" when I try to view them.',
    time: '10:35 AM'
  }, {
    id: 4,
    sender: 'agent',
    text: "Thank you for the information. Let me check that for you right away. Can you confirm which account you're trying to access?",
    time: '10:36 AM'
  }, {
    id: 5,
    sender: 'user',
    text: "It's the premium account under email john.doe@example.com",
    time: '10:38 AM'
  }, {
    id: 6,
    sender: 'agent',
    text: "I appreciate your patience. I've checked your account and there appears to be a temporary issue with the subscription portal. Our team is working on fixing it. In the meantime, I can help you adjust any subscription settings directly. What would you like to change?",
    time: '10:40 AM'
  }];
  const handleSend = e => {
    e.preventDefault();
    // Handle sending message
    if (message.trim()) {
      console.log('Sending message:', message);
      setMessage('');
    }
  };
  return <div className="flex flex-col h-screen md:h-full">
      <div className="p-4 bg-white border-b border-gray-200">
        <h2 className="text-xl font-medium">Conversation with John Doe</h2>
        <p className="text-sm text-gray-500">
          Ticket #1234 - Account Access Issue
        </p>
      </div>
      <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
        <div className="max-w-3xl mx-auto space-y-4">
          {conversation.map(msg => <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] rounded-lg p-3 ${msg.sender === 'user' ? 'bg-[#007BFF] text-white' : 'bg-gray-200 text-gray-800'}`}>
                <p>{msg.text}</p>
                <p className={`text-xs mt-1 ${msg.sender === 'user' ? 'text-blue-100' : 'text-gray-500'}`}>
                  {msg.time}
                </p>
              </div>
            </div>)}
        </div>
      </div>
      <div className="p-4 bg-white border-t border-gray-200">
        <form onSubmit={handleSend} className="flex items-center">
          <button type="button" className="p-2 text-gray-500 hover:text-gray-700">
            <PaperclipIcon size={20} />
          </button>
          <input type="text" value={message} onChange={e => setMessage(e.target.value)} placeholder="Type your message..." className="flex-1 p-2 border border-gray-300 rounded-l-md focus:outline-none focus:border-[#007BFF]" />
          <button type="submit" className="bg-[#007BFF] text-white p-2 rounded-r-md hover:bg-blue-600 transition-colors">
            <SendIcon size={20} />
          </button>
        </form>
      </div>
    </div>;
};
export default ConversationPanel;