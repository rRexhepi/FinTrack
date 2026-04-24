import React, { useState, useEffect } from 'react';

import api from '../api';

function BudgetList() {
  const [budgets, setBudgets] = useState([]);

  useEffect(() => {
    api
      .get('/api/budgets/')
      .then((res) => setBudgets(res.data.results || []))
      .catch((err) => console.error('budgets', err));
  }, []);

  return (
    <div>
      <h2>Budgets</h2>
      <ul>
        {budgets.map((budget) => (
          <li key={budget.id}>
            {budget.category}: ${budget.amount} per {budget.period}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default BudgetList;
