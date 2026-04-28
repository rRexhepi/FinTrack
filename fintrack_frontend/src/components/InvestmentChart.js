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
  '#1976d2',
  '#26a69a',
  '#ffa726',
  '#ef5350',
  '#8e44ad',
  '#5c6bc0',
  '#66bb6a',
];

const formatUSD = (n) =>
  `$${Number(n).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;

function InvestmentChart() {
  const [data, setData] = useState([]);

  useEffect(() => {
    api
      .get('/api/investments/allocation/')
      .then((res) => {
        const rows = Array.isArray(res.data) ? res.data : [];
        setData(
          rows.map((row) => ({
            // Label uses ticker, fits legends. Tooltip has the full name.
            name: row.ticker,
            fullName: row.name,
            value: Number(row.total),
          })),
        );
      })
      .catch((err) => console.error('investment chart', err));
  }, []);

  const total = data.reduce((sum, d) => sum + d.value, 0);

  return (
    <Box sx={{ width: '100%' }}>
      <Typography variant="h6" gutterBottom>
        Investment Allocation
      </Typography>
      {data.length === 0 ? (
        <Typography variant="body2" color="text.secondary">
          No investments yet.
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
              formatter={(value, _name, item) => [
                formatUSD(value),
                item?.payload?.fullName || item?.payload?.name,
              ]}
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

export default InvestmentChart;
