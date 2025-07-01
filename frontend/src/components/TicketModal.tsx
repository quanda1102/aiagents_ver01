import React from 'react';
import { XIcon } from 'lucide-react';
const TicketModal = ({
  ticket,
  onClose
}) => {
  return <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-hidden">
        <div className="flex justify-between items-center p-4 border-b border-gray-200">
          <h2 className="text-xl font-medium">Ticket #{ticket.id}</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <XIcon size={24} />
          </button>
        </div>
        <div className="p-4 overflow-y-auto max-h-[calc(90vh-120px)]">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <h3 className="text-sm font-medium text-gray-500">Customer</h3>
              <p className="mt-1">{ticket.customer}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">Email</h3>
              <p className="mt-1">{ticket.email}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">Status</h3>
              <p className="mt-1">{ticket.status}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">Priority</h3>
              <p className="mt-1">{ticket.priority}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">Created</h3>
              <p className="mt-1">
                {new Date(ticket.created).toLocaleString()}
              </p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">
                Last Updated
              </h3>
              <p className="mt-1">
                {new Date(ticket.lastUpdated).toLocaleString()}
              </p>
            </div>
          </div>
          <div className="mb-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              Issue Summary
            </h3>
            <p className="p-3 bg-gray-50 rounded-md">{ticket.summary}</p>
          </div>
          <div className="mb-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              Description
            </h3>
            <p className="p-3 bg-gray-50 rounded-md">{ticket.description}</p>
          </div>
          <div className="mb-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              Resolution Notes
            </h3>
            <textarea className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-[#007BFF] focus:border-[#007BFF]" rows={4} placeholder="Add resolution notes here..." />
          </div>
        </div>
        <div className="flex justify-end gap-3 p-4 border-t border-gray-200">
          <button onClick={onClose} className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50">
            Cancel
          </button>
          <button className="px-4 py-2 bg-[#28A745] text-white rounded-md hover:bg-green-600">
            Resolve Ticket
          </button>
          <button className="px-4 py-2 bg-[#007BFF] text-white rounded-md hover:bg-blue-600">
            Save Changes
          </button>
        </div>
      </div>
    </div>;
};
export default TicketModal;