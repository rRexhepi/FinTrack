import React, { useState, useEffect } from 'react';
import { Container, Typography, Grid } from '@mui/material';

import api from '../api';
import SummaryCard from './SummaryCard';
import ExpenseChart from './ExpenseChart';
import InvestmentChart from './InvestmentChart';
import BudgetProgress from './BudgetProgress';
import Suggestions from './Suggestions';

const formatUSD = (n) =>
  `$${Number(n).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;

function Dashboard() {
  const [totalExpenses, setTotalExpenses] = useState('0.00');
  const [totalInvestments, setTotalInvestments] = useState('0.00');

  useEffect(() => {
    // Use the aggregate for a correct total that ignores pagination.
    api
      .get('/api/expenses/by-category/')
      .then((res) => {
        const rows = Array.isArray(res.data) ? res.data : [];
        const total = rows.reduce((sum, r) => sum + Number(r.total || 0), 0);
        setTotalExpenses(total.toFixed(2));
      })
      .catch((err) => console.error('expenses total', err));

    api
      .get('/api/investments/allocation/')
      .then((res) => {
        const rows = Array.isArray(res.data) ? res.data : [];
        // Falls back to cost basis. `current_value` needs yfinance,
        // which is rate-limited from Render's shared IPs. The allocation
        // endpoint gives us cost-basis totals that are always available.
        const total = rows.reduce((sum, r) => sum + Number(r.total || 0), 0);
        setTotalInvestments(total.toFixed(2));
      })
      .catch((err) => console.error('investments total', err));
  }, []);

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" component="h1" gutterBottom>
        FinTrack Dashboard
      </Typography>
      <Grid container spacing={4}>
        <Grid item xs={12} sm={6}>
          <SummaryCard title="Total Expenses" value={formatUSD(totalExpenses)} />
        </Grid>
        <Grid item xs={12} sm={6}>
          <SummaryCard title="Total Invested" value={formatUSD(totalInvestments)} />
        </Grid>
      </Grid>
      <Grid container spacing={4} style={{ marginTop: '1rem' }}>
        <Grid item xs={12} md={6}>
          <ExpenseChart />
        </Grid>
        <Grid item xs={12} md={6}>
          <InvestmentChart />
        </Grid>
      </Grid>
      <Grid container spacing={4} style={{ marginTop: '1rem' }}>
        <Grid item xs={12} md={6}>
          <BudgetProgress />
        </Grid>
        <Grid item xs={12} md={6}>
          <Suggestions />
        </Grid>
      </Grid>
    </Container>
  );
}

export default Dashboard;
