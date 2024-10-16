import React, { useState, useEffect } from 'react';
import { Typography } from '@mui/material';
import AddExpense from './AddExpense';

function ExpenseList() {
  const [expenses, setExpenses] = useState([]);

  const fetchExpenses = () => {
    fetch('/api/expenses/')
      .then((response) => {
        if (!response.ok) {
          throw new Error('Failed to fetch expenses');
        }
        return response.json();
      })
      .then((data) => {
        setExpenses(data);
      })
      .catch((error) => {
        console.error('Error fetching expenses:', error);
      });
  };

  useEffect(() => {
    fetchExpenses();
  }, []);

  return (
    <div>
      <Typography variant="h5" gutterBottom>
        Expenses
      </Typography>
      <AddExpense refreshExpenses={fetchExpenses} />
      {/* Render the list of expenses */}
      <ul>
        {expenses.map((expense) => (
          <li key={expense.id}>
            {expense.date}: {expense.category} - ${expense.amount}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default ExpenseList;
