import React from 'react';
import { Card, CardContent, Typography } from '@mui/material';

function SummaryCard({ title, value }) {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" color="textSecondary" gutterBottom>
          {title}
        </Typography>
        <Typography variant="h4">{value}</Typography>
      </CardContent>
    </Card>
  );
}

export default SummaryCard;
