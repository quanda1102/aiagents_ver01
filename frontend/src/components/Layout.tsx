import React, { useState } from 'react';
import { MenuIcon, XIcon } from 'lucide-react';
const Layout = ({
  sidebar,
  content
}) => {
  const [showMobileSidebar, setShowMobileSidebar] = useState(false);
  return <div className="flex flex-col md:flex-row min-h-screen">
      {/* Mobile Header */}
      <div className="md:hidden flex items-center justify-between p-4 bg-white border-b border-gray-200">
        <h1 className="text-xl font-semibold">Customer Service</h1>
        <button onClick={() => setShowMobileSidebar(!showMobileSidebar)} className="p-2 rounded-md hover:bg-gray-100">
          {showMobileSidebar ? <XIcon size={24} /> : <MenuIcon size={24} />}
        </button>
      </div>
      {/* Sidebar - hidden on mobile unless toggled */}
      <div className={`
        fixed md:static inset-0 z-20 bg-white transform 
        ${showMobileSidebar ? 'translate-x-0' : '-translate-x-full'} 
        md:translate-x-0 transition-transform duration-300 ease-in-out
        w-[250px] min-w-[250px] border-r border-gray-200
      `}>
        {sidebar}
      </div>
      {/* Backdrop for mobile sidebar */}
      {showMobileSidebar && <div className="md:hidden fixed inset-0 z-10 bg-black bg-opacity-50" onClick={() => setShowMobileSidebar(false)} />}
      {/* Main Content */}
      <div className="flex-1 min-w-0 md:min-w-[800px]">{content}</div>
    </div>;
};
export default Layout;