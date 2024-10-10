import React from 'react';
import ExpenseChart from './ExpenseChart';
import Suggestions from './Suggestions';

function Dashboard() {
  return (
    <div>
      <h1>FinTrack Dashboard</h1>
      <ExpenseChart />
      <Suggestions />
      {/* Add more charts and components as needed */}
    </div>
  );
}

export default Dashboard;
