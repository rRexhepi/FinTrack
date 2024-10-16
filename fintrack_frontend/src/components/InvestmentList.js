import React, { useState, useEffect } from 'react';
import { Typography } from '@mui/material';
import AddInvestment from './AddInvestment';

function InvestmentList() {
  const [investments, setInvestments] = useState([]);

  const fetchInvestments = () => {
    fetch('/api/investments/')
      .then((response) => {
        if (!response.ok) {
          throw new Error('Failed to fetch investments');
        }
        return response.json();
      })
      .then((data) => {
        setInvestments(data);
      })
      .catch((error) => {
        console.error('Error fetching investments:', error);
      });
  };

  useEffect(() => {
    fetchInvestments();
  }, []);

  return (
    <div>
      <Typography variant="h5" gutterBottom>
        Investments
      </Typography>
      <AddInvestment refreshInvestments={fetchInvestments} />
      {/* Render the list of investments */}
      <ul>
        {investments.map((investment) => (
          <li key={investment.id}>
            {investment.name} ({investment.ticker}): Current Value: $
            {investment.current_value ? investment.current_value.toFixed(2) : 'N/A'}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default InvestmentList;
