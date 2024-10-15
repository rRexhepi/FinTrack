import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';

function ExpenseChart() {
  const [data, setData] = useState([]);

  useEffect(() => {
    axios.get('/api/expenses/')
      .then(res => {
        const categories = {};
        res.data.forEach(expense => {
          if (categories[expense.category]) {
            categories[expense.category] += parseFloat(expense.amount);
          } else {
            categories[expense.category] = parseFloat(expense.amount);
          }
        });
        const chartData = Object.keys(categories).map(key => ({
          name: key,
          value: categories[key],
        }));
        setData(chartData);
      })
      .catch(err => console.log(err));
  }, []);

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#AA336A'];

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
