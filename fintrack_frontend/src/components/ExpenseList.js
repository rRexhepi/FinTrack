import React, { useState, useEffect } from 'react';
import axios from 'axios';

function ExpenseList() {
  const [expenses, setExpenses] = useState([]);

  useEffect(() => {
    axios.get('/api/expenses/')
      .then(res => {
        setExpenses(res.data);
      })
      .catch(err => {
        console.log(err);
      });
  }, []);

  return (
    <div>
      <h2>Expenses</h2>
      <ul>
        {expenses.map(expense => (
          <li key={expense.id}>{expense.description}: ${expense.amount}</li>
        ))}
      </ul>
    </div>
  );
}

export default ExpenseList;
