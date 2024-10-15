import React, { useState, useEffect } from 'react';
import { Container, Typography, Grid } from '@mui/material';
import SummaryCard from './SummaryCard';
import ExpenseChart from './ExpenseChart';
import Suggestions from './Suggestions';
import axios from 'axios';

function Dashboard() {
  const [totalExpenses, setTotalExpenses] = useState(0);
  const [totalInvestments, setTotalInvestments] = useState(0);

  useEffect(() => {
    // Fetch total expenses
    axios.get('/api/expenses/')
      .then(res => {
        const total = res.data.reduce((sum, expense) => sum + parseFloat(expense.amount), 0);
        setTotalExpenses(total.toFixed(2));
      })
      .catch(err => console.log(err));

    // Fetch total investments
    axios.get('/api/investments/')
      .then(res => {
        const total = res.data.reduce((sum, investment) => sum + parseFloat(investment.current_value), 0);
        setTotalInvestments(total.toFixed(2));
      })
      .catch(err => console.log(err));
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
        {/* Add more SummaryCards as needed */}
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
