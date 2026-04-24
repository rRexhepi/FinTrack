import React, { useState, useEffect, useCallback } from 'react';
import { Typography } from '@mui/material';

import api from '../api';
import AddInvestment from './AddInvestment';

function InvestmentList() {
  const [investments, setInvestments] = useState([]);

  const fetchInvestments = useCallback(() => {
    api
      .get('/api/investments/')
      .then((res) => setInvestments(res.data.results || []))
      .catch((err) => console.error('investments', err));
  }, []);

  useEffect(() => {
    fetchInvestments();
  }, [fetchInvestments]);

  return (
    <div>
      <Typography variant="h5" gutterBottom>
        Investments
      </Typography>
      <AddInvestment refreshInvestments={fetchInvestments} />
      <ul>
        {investments.map((investment) => {
          const currentValue = investment.current_value;
          return (
            <li key={investment.id}>
              {investment.name} ({investment.ticker}) — invested $
              {investment.amount_invested}
              {currentValue != null
                ? `, current value $${Number(currentValue).toFixed(2)}`
                : ', current value unavailable'}
            </li>
          );
        })}
      </ul>
    </div>
  );
}

export default InvestmentList;
