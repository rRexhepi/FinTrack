import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';

import api from '../api';
import AddExpense from './AddExpense';
import ExpenseChart from './ExpenseChart';

const formatUSD = (n) =>
  `$${Number(n).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;

function ExpenseList() {
  const [expenses, setExpenses] = useState([]);

  const fetchExpenses = useCallback(() => {
    // `page_size=100` = enough for the demo, capped by DefaultPagination.
    api
      .get('/api/expenses/?page_size=100')
      .then((res) => setExpenses(res.data.results || []))
      .catch((err) => console.error('expenses', err));
  }, []);

  useEffect(() => {
    fetchExpenses();
  }, [fetchExpenses]);

  const total = expenses.reduce((sum, e) => sum + Number(e.amount || 0), 0);

  return (
    <Box>
      <Stack
        direction="row"
        justifyContent="space-between"
        alignItems="center"
        sx={{ mb: 3 }}
      >
        <Typography variant="h4" component="h1">
          Expenses
        </Typography>
        <AddExpense refreshExpenses={fetchExpenses} />
      </Stack>

      <Box sx={{ display: 'flex', gap: 4, flexWrap: 'wrap', mb: 4 }}>
        <Box sx={{ flex: '1 1 360px', minWidth: 320 }}>
          <ExpenseChart />
        </Box>
        <Box sx={{ flex: '1 1 240px', minWidth: 220, alignSelf: 'center' }}>
          <Typography variant="overline" color="text.secondary">
            Total
          </Typography>
          <Typography variant="h3">{formatUSD(total)}</Typography>
          <Typography variant="body2" color="text.secondary">
            across {expenses.length} transactions
          </Typography>
        </Box>
      </Box>

      <TableContainer component={Paper} variant="outlined">
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Date</TableCell>
              <TableCell>Category</TableCell>
              <TableCell>Description</TableCell>
              <TableCell align="right">Amount</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {expenses.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} align="center">
                  <Typography variant="body2" color="text.secondary">
                    No expenses yet. Add one to see it here.
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              expenses.map((expense) => (
                <TableRow key={expense.id} hover>
                  <TableCell>{expense.date}</TableCell>
                  <TableCell>{expense.category}</TableCell>
                  <TableCell>
                    <Typography variant="body2" color="text.secondary">
                      {expense.description || '—'}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">{formatUSD(expense.amount)}</TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

export default ExpenseList;
