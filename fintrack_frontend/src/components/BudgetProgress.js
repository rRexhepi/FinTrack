import React, { useState, useEffect } from 'react';
import {
  Box,
  LinearProgress,
  Stack,
  Typography,
} from '@mui/material';

import api from '../api';

const formatUSD = (n) =>
  `$${Number(n).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;

function BudgetProgress() {
  const [rows, setRows] = useState([]);

  useEffect(() => {
    api
      .get('/api/budgets/progress/')
      .then((res) => setRows(Array.isArray(res.data) ? res.data : []))
      .catch((err) => console.error('budget progress', err));
  }, []);

  return (
    <Box sx={{ width: '100%' }}>
      <Typography variant="h6" gutterBottom>
        Budget Progress
      </Typography>
      {rows.length === 0 ? (
        <Typography variant="body2" color="text.secondary">
          No budgets set.
        </Typography>
      ) : (
        <Stack spacing={2.5}>
          {rows.map((row) => {
            const pct = row.amount > 0 ? (row.spent / row.amount) * 100 : 0;
            const over = pct > 100;
            const color = over ? 'error' : pct > 80 ? 'warning' : 'primary';
            return (
              <Box key={row.id}>
                <Box
                  sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'baseline',
                    mb: 0.5,
                  }}
                >
                  <Typography variant="subtitle2">
                    {row.category}{' '}
                    <Typography
                      component="span"
                      variant="caption"
                      color="text.secondary"
                    >
                      ({row.period.toLowerCase()})
                    </Typography>
                  </Typography>
                  <Typography variant="body2" color={over ? 'error.main' : 'text.secondary'}>
                    {formatUSD(row.spent)} / {formatUSD(row.amount)}
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={Math.min(pct, 100)}
                  color={color}
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>
            );
          })}
        </Stack>
      )}
    </Box>
  );
}

export default BudgetProgress;
