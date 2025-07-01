import React from 'react';
import { ChevronRightIcon } from 'lucide-react';
const TicketList = ({
  onTicketClick
}) => {
  // Sample ticket data
  const tickets = [{
    id: '1234',
    customer: 'John Doe',
    email: 'john.doe@example.com',
    summary: 'Account Access Issue',
    status: 'Open',
    priority: 'High',
    created: '2023-10-15T10:30:00',
    lastUpdated: '2023-10-15T14:45:00',
    description: 'Customer is unable to access subscription settings, receiving 404 error.'
  }, {
    id: '1235',
    customer: 'Jane Smith',
    email: 'jane.smith@example.com',
    summary: 'Billing Question',
    status: 'Open',
    priority: 'Medium',
    created: '2023-10-14T09:15:00',
    lastUpdated: '2023-10-15T11:20:00',
    description: 'Customer has questions about their recent invoice and charges.'
  }, {
    id: '1236',
    customer: 'Robert Johnson',
    email: 'robert.j@example.com',
    summary: 'Feature Request',
    status: 'In Progress',
    priority: 'Low',
    created: '2023-10-12T14:22:00',
    lastUpdated: '2023-10-14T16:30:00',
    description: 'Customer is requesting a new feature for data export functionality.'
  }, {
    id: '1237',
    customer: 'Sarah Williams',
    email: 'sarah.w@example.com',
    summary: 'Login Issues',
    status: 'Resolved',
    priority: 'High',
    created: '2023-10-10T08:45:00',
    lastUpdated: '2023-10-11T13:15:00',
    description: 'Customer was experiencing login issues due to cached credentials.'
  }, {
    id: '1238',
    customer: 'Michael Brown',
    email: 'michael.b@example.com',
    summary: 'Account Cancellation',
    status: 'Open',
    priority: 'Medium',
    created: '2023-10-15T11:50:00',
    lastUpdated: '2023-10-15T12:30:00',
    description: 'Customer wants to cancel their subscription and needs assistance.'
  }];
  const getStatusColor = status => {
    switch (status.toLowerCase()) {
      case 'open':
        return 'bg-yellow-100 text-yellow-800';
      case 'in progress':
        return 'bg-blue-100 text-blue-800';
      case 'resolved':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };
  return <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-medium">Support Tickets</h2>
        <button className="px-4 py-2 bg-[#007BFF] text-white rounded-md hover:bg-blue-600 transition-colors">
          New Ticket
        </button>
      </div>
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                ID
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Customer
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Issue
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {tickets.map(ticket => <tr key={ticket.id} className="hover:bg-gray-50 cursor-pointer" onClick={() => onTicketClick(ticket)}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  #{ticket.id}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {ticket.customer}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {ticket.summary}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(ticket.status)}`}>
                    {ticket.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <button className="text-[#007BFF] hover:text-blue-700">
                    <ChevronRightIcon size={20} />
                  </button>
                </td>
              </tr>)}
          </tbody>
        </table>
      </div>
    </div>;
};
export default TicketList;