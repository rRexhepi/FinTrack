import React, { useState, useEffect } from 'react';
import { Container, Typography, Grid } from '@mui/material';

import api from '../api';
import SummaryCard from './SummaryCard';
import ExpenseChart from './ExpenseChart';
import Suggestions from './Suggestions';

function Dashboard() {
  const [totalExpenses, setTotalExpenses] = useState('0.00');
  const [totalInvestments, setTotalInvestments] = useState('0.00');

  useEffect(() => {
    api
      .get('/api/expenses/')
      .then((res) => {
        const results = res.data.results || [];
        const total = results.reduce(
          (sum, expense) => sum + parseFloat(expense.amount || 0),
          0,
        );
        setTotalExpenses(total.toFixed(2));
      })
      .catch((err) => console.error('expenses', err));

    api
      .get('/api/investments/')
      .then((res) => {
        const results = res.data.results || [];
        // `current_value` is null when yfinance can't resolve the ticker
        // (rate-limited from Render's shared IPs). Fall back to
        // `amount_invested` so the summary isn't empty.
        const total = results.reduce((sum, inv) => {
          const value = inv.current_value ?? inv.amount_invested ?? 0;
          return sum + parseFloat(value);
        }, 0);
        setTotalInvestments(total.toFixed(2));
      })
      .catch((err) => console.error('investments', err));
  }, []);

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" component="h1" gutterBottom>
        FinTrack Dashboard
      </Typography>
      <Grid container spacing={4}>
        <Grid item xs={12} sm={6} md={4}>
          <SummaryCard title="Total Expenses" value={`$${totalExpenses}`} />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <SummaryCard title="Total Investments" value={`$${totalInvestments}`} />
        </Grid>
      </Grid>
      <Grid container spacing={4} style={{ marginTop: '2rem' }}>
        <Grid item xs={12} md={6}>
          <ExpenseChart />
        </Grid>
        <Grid item xs={12} md={6}>
          <Suggestions />
        </Grid>
      </Grid>
    </Container>
  );
}

export default Dashboard;
