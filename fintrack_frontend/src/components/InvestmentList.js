import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Chip,
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
import AddInvestment from './AddInvestment';
import InvestmentChart from './InvestmentChart';

const formatUSD = (n) =>
  `$${Number(n).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;

function returnCell(investment) {
  const current = investment.current_value;
  const cost = Number(investment.amount_invested || 0);
  if (current == null) {
    // yfinance couldn't resolve the ticker — `null` means unavailable,
    // not zero. Render a dash rather than a fake 0%.
    return (
      <Typography variant="body2" color="text.secondary">
        —
      </Typography>
    );
  }
  const delta = Number(current) - cost;
  const pct = cost > 0 ? (delta / cost) * 100 : 0;
  const positive = delta >= 0;
  return (
    <Chip
      size="small"
      label={`${positive ? '+' : ''}${formatUSD(delta)} (${positive ? '+' : ''}${pct.toFixed(1)}%)`}
      color={positive ? 'success' : 'error'}
      variant="outlined"
    />
  );
}

function InvestmentList() {
  const [investments, setInvestments] = useState([]);

  const fetchInvestments = useCallback(() => {
    api
      .get('/api/investments/?page_size=100')
      .then((res) => setInvestments(res.data.results || []))
      .catch((err) => console.error('investments', err));
  }, []);

  useEffect(() => {
    fetchInvestments();
  }, [fetchInvestments]);

  const totalInvested = investments.reduce(
    (sum, i) => sum + Number(i.amount_invested || 0),
    0,
  );
  const totalCurrent = investments.reduce(
    (sum, i) => sum + (i.current_value != null ? Number(i.current_value) : 0),
    0,
  );
  const someValuesMissing = investments.some((i) => i.current_value == null);

  return (
    <Box>
      <Stack
        direction="row"
        justifyContent="space-between"
        alignItems="center"
        sx={{ mb: 3 }}
      >
        <Typography variant="h4" component="h1">
          Investments
        </Typography>
        <AddInvestment refreshInvestments={fetchInvestments} />
      </Stack>

      <Box sx={{ display: 'flex', gap: 4, flexWrap: 'wrap', mb: 4 }}>
        <Box sx={{ flex: '1 1 360px', minWidth: 320 }}>
          <InvestmentChart />
        </Box>
        <Box sx={{ flex: '1 1 240px', minWidth: 220, alignSelf: 'center' }}>
          <Typography variant="overline" color="text.secondary">
            Cost basis
          </Typography>
          <Typography variant="h4">{formatUSD(totalInvested)}</Typography>
          <Box sx={{ mt: 2 }}>
            <Typography variant="overline" color="text.secondary">
              Current value
            </Typography>
            <Typography variant="h4">
              {totalCurrent > 0 ? formatUSD(totalCurrent) : '—'}
            </Typography>
            {someValuesMissing && (
              <Typography variant="caption" color="text.secondary">
                Some prices unavailable (Yahoo Finance rate-limit)
              </Typography>
            )}
          </Box>
        </Box>
      </Box>

      <TableContainer component={Paper} variant="outlined">
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Ticker</TableCell>
              <TableCell>Date</TableCell>
              <TableCell align="right">Invested</TableCell>
              <TableCell align="right">Current value</TableCell>
              <TableCell align="right">Return</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {investments.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  <Typography variant="body2" color="text.secondary">
                    No investments yet. Add one to see it here.
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              investments.map((investment) => (
                <TableRow key={investment.id} hover>
                  <TableCell>{investment.name}</TableCell>
                  <TableCell>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                      {investment.ticker}
                    </Typography>
                  </TableCell>
                  <TableCell>{investment.date_invested}</TableCell>
                  <TableCell align="right">
                    {formatUSD(investment.amount_invested)}
                  </TableCell>
                  <TableCell align="right">
                    {investment.current_value != null
                      ? formatUSD(investment.current_value)
                      : '—'}
                  </TableCell>
                  <TableCell align="right">{returnCell(investment)}</TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

export default InvestmentList;
