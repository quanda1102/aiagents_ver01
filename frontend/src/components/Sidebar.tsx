import React from 'react';
import { LayoutDashboardIcon, MessageCircleIcon, TicketIcon, BarChart2Icon, SettingsIcon, SearchIcon } from 'lucide-react';
import SearchBar from './SearchBar';
const Sidebar = ({
  activeSection,
  onSectionChange
}) => {
  const navItems = [{
    id: 'dashboard',
    label: 'Dashboard',
    icon: <LayoutDashboardIcon size={20} />
  }, {
    id: 'conversations',
    label: 'Conversations',
    icon: <MessageCircleIcon size={20} />
  }, {
    id: 'tickets',
    label: 'Tickets',
    icon: <TicketIcon size={20} />
  }, {
    id: 'analytics',
    label: 'Analytics',
    icon: <BarChart2Icon size={20} />
  }, {
    id: 'settings',
    label: 'Settings',
    icon: <SettingsIcon size={20} />
  }];
  return <div className="flex flex-col h-full">
      <div className="p-4 border-b border-gray-200">
        <h1 className="text-xl font-semibold mb-4">Customer Service</h1>
        <SearchBar />
      </div>
      <nav className="flex-1 overflow-y-auto py-4">
        <ul>
          {navItems.map(item => <li key={item.id}>
              <button onClick={() => onSectionChange(item.id)} className={`flex items-center w-full px-4 py-3 text-left ${activeSection === item.id ? 'bg-[#EBF5FF] text-[#007BFF]' : 'text-gray-700 hover:bg-gray-100'}`}>
                <span className="mr-3">{item.icon}</span>
                <span>{item.label}</span>
              </button>
            </li>)}
        </ul>
      </nav>
      <div className="p-4 border-t border-gray-200">
        <div className="flex items-center">
          <div className="w-8 h-8 rounded-full bg-[#007BFF] text-white flex items-center justify-center mr-2">
            <span>JD</span>
          </div>
          <div>
            <p className="text-sm font-medium">John Doe</p>
            <p className="text-xs text-gray-500">Support Agent</p>
          </div>
        </div>
      </div>
    </div>;
};
export default Sidebar;