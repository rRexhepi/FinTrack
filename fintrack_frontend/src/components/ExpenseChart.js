import React, { useState, useEffect } from 'react';
import { Box, Typography } from '@mui/material';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

import api from '../api';

const COLORS = [
  '#1976d2', // primary blue
  '#26a69a', // teal
  '#ffa726', // amber
  '#ef5350', // red
  '#8e44ad', // purple
  '#5c6bc0', // indigo
];

const formatUSD = (n) =>
  `$${Number(n).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;

function ExpenseChart() {
  const [data, setData] = useState([]);

  useEffect(() => {
    api
      .get('/api/expenses/by-category/')
      .then((res) => {
        const rows = Array.isArray(res.data) ? res.data : [];
        setData(
          rows.map((row) => ({
            name: row.category,
            value: Number(row.total),
          })),
        );
      })
      .catch((err) => console.error('expense chart', err));
  }, []);

  const total = data.reduce((sum, d) => sum + d.value, 0);

  return (
    <Box sx={{ width: '100%' }}>
      <Typography variant="h6" gutterBottom>
        Expenses by Category
      </Typography>
      {data.length === 0 ? (
        <Typography variant="body2" color="text.secondary">
          No expenses yet.
        </Typography>
      ) : (
        <ResponsiveContainer width="100%" height={320}>
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={110}
              paddingAngle={2}
              stroke="none"
            >
              {data.map((entry, index) => (
                <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip
              formatter={(value, name) => [formatUSD(value), name]}
              separator=": "
            />
            <Legend
              verticalAlign="bottom"
              height={36}
              formatter={(value, entry) => {
                const pct = total ? ((entry.payload.value / total) * 100).toFixed(0) : 0;
                return `${value} (${pct}%)`;
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      )}
    </Box>
  );
}

export default ExpenseChart;
