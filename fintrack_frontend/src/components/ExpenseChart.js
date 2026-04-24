import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';

import api from '../api';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#AA336A', '#8884d8'];

function ExpenseChart() {
  const [data, setData] = useState([]);

  useEffect(() => {
    api
      .get('/api/expenses/')
      .then((res) => {
        const results = res.data.results || [];
        const categories = {};
        results.forEach((expense) => {
          const amt = parseFloat(expense.amount || 0);
          categories[expense.category] = (categories[expense.category] || 0) + amt;
        });
        const chartData = Object.entries(categories).map(([name, value]) => ({
          name,
          value: Number(value.toFixed(2)),
        }));
        setData(chartData);
      })
      .catch((err) => console.error('expense chart', err));
  }, []);

  return (
    <div>
      <h3>Expenses by Category</h3>
      <PieChart width={400} height={400}>
        <Pie
          dataKey="value"
          data={data}
          cx={200}
          cy={200}
          outerRadius={150}
          fill="#8884d8"
          label
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </div>
  );
}

export default ExpenseChart;
