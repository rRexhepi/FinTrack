import React, { useState, useEffect } from 'react';
import axios from 'axios';

function InvestmentList() {
  const [investments, setInvestments] = useState([]);

  useEffect(() => {
    axios.get('/api/investments/')
      .then(res => {
        setInvestments(res.data);
      })
      .catch(err => {
        console.log(err);
      });
  }, []);

  return (
    <div>
      <h2>Investments</h2>
      <ul>
        {investments.map(investment => (
          <li key={investment.id}>
            {investment.name} ({investment.ticker}): Current Value: ${investment.current_value}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default InvestmentList;
