import React, { useState } from 'react';
import Layout from './components/Layout';
import Sidebar from './components/Sidebar';
import ConversationPanel from './components/ConversationPanel';
import TicketList from './components/TicketList';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import TicketModal from './components/TicketModal';
export function App() {
  const [activeSection, setActiveSection] = useState('conversations');
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [showTicketModal, setShowTicketModal] = useState(false);
  const handleTicketClick = ticket => {
    setSelectedTicket(ticket);
    setShowTicketModal(true);
  };
  const renderContent = () => {
    switch (activeSection) {
      case 'dashboard':
        return <AnalyticsDashboard />;
      case 'conversations':
        return <ConversationPanel />;
      case 'tickets':
        return <TicketList onTicketClick={handleTicketClick} />;
      case 'analytics':
        return <AnalyticsDashboard />;
      case 'settings':
        return <div className="p-6">
            <h2 className="text-2xl font-medium mb-4">Settings</h2>
            <p>Settings content goes here</p>
          </div>;
      default:
        return <ConversationPanel />;
    }
  };
  return <div className="font-sans text-[#333333] bg-[#F5F5F5] min-h-screen">
      <Layout sidebar={<Sidebar activeSection={activeSection} onSectionChange={setActiveSection} />} content={renderContent()} />
      {showTicketModal && selectedTicket && <TicketModal ticket={selectedTicket} onClose={() => setShowTicketModal(false)} />}
    </div>;
}