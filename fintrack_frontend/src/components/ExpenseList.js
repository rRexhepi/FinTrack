import React, { useState, useEffect, useCallback } from 'react';
import { Typography } from '@mui/material';

import api from '../api';
import AddExpense from './AddExpense';

function ExpenseList() {
  const [expenses, setExpenses] = useState([]);

  const fetchExpenses = useCallback(() => {
    api
      .get('/api/expenses/')
      .then((res) => setExpenses(res.data.results || []))
      .catch((err) => console.error('expenses', err));
  }, []);

  useEffect(() => {
    fetchExpenses();
  }, [fetchExpenses]);

  return (
    <div>
      <Typography variant="h5" gutterBottom>
        Expenses
      </Typography>
      <AddExpense refreshExpenses={fetchExpenses} />
      <ul>
        {expenses.map((expense) => (
          <li key={expense.id}>
            {expense.date}: {expense.category} — ${expense.amount}
            {expense.description ? ` (${expense.description})` : ''}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default ExpenseList;
