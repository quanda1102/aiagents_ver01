import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';
const AnalyticsDashboard = () => {
  // Sample data for charts
  const ticketData = [{
    name: 'Mon',
    open: 4,
    resolved: 2
  }, {
    name: 'Tue',
    open: 3,
    resolved: 4
  }, {
    name: 'Wed',
    open: 5,
    resolved: 3
  }, {
    name: 'Thu',
    open: 7,
    resolved: 5
  }, {
    name: 'Fri',
    open: 2,
    resolved: 6
  }, {
    name: 'Sat',
    open: 1,
    resolved: 2
  }, {
    name: 'Sun',
    open: 0,
    resolved: 1
  }];
  const satisfactionData = [{
    name: 'Week 1',
    score: 4.2
  }, {
    name: 'Week 2',
    score: 4.5
  }, {
    name: 'Week 3',
    score: 4.3
  }, {
    name: 'Week 4',
    score: 4.7
  }];
  const statsCards = [{
    title: 'Open Tickets',
    value: 23,
    change: '+5%',
    color: 'bg-blue-50 text-blue-700'
  }, {
    title: 'Avg. Response Time',
    value: '1.5h',
    change: '-10%',
    color: 'bg-green-50 text-green-700'
  }, {
    title: 'Customer Satisfaction',
    value: '4.7/5',
    change: '+2%',
    color: 'bg-purple-50 text-purple-700'
  }, {
    title: 'Resolved Today',
    value: 18,
    change: '+12%',
    color: 'bg-yellow-50 text-yellow-700'
  }];
  return <div className="p-6">
      <h2 className="text-2xl font-medium mb-6">Analytics Dashboard</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {statsCards.map((card, index) => <div key={index} className={`${card.color} p-4 rounded-lg shadow-sm`}>
            <h3 className="text-sm font-medium opacity-80">{card.title}</h3>
            <div className="flex items-end justify-between mt-2">
              <span className="text-2xl font-semibold">{card.value}</span>
              <span className="text-sm">{card.change}</span>
            </div>
          </div>)}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-medium mb-4">Ticket Activity</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={ticketData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="open" name="New Tickets" fill="#007BFF" />
                <Bar dataKey="resolved" name="Resolved Tickets" fill="#28A745" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-medium mb-4">Customer Satisfaction</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={satisfactionData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis domain={[3, 5]} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="score" name="Satisfaction Score" stroke="#8884d8" activeDot={{
                r: 8
              }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>;
};
export default AnalyticsDashboard;