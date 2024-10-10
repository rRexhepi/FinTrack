import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import ExpenseList from './components/ExpenseList';
import InvestmentList from './components/InvestmentList';
import Dashboard from './components/Dashboard';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/expenses" element={<ExpenseList />} />
        <Route path="/investments" element={<InvestmentList />} />
      </Routes>
    </Router>
  );
}

export default App;
