import React, { useState, useEffect } from 'react';
import axios from 'axios';

function BudgetList() {
  const [budgets, setBudgets] = useState([]);

  useEffect(() => {
    axios.get('/api/budgets/')
      .then(res => {
        setBudgets(res.data);
      })
      .catch(err => {
        console.log(err);
      });
  }, []);

  return (
    <div>
      <h2>Budgets</h2>
      <ul>
        {budgets.map(budget => (
          <li key={budget.id}>
            {budget.category}: ${budget.amount} per {budget.period}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default BudgetList;
