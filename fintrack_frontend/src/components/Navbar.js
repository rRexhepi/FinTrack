import React from 'react';
import { AppBar, Toolbar, Typography, Button } from '@mui/material';
import { Link } from 'react-router-dom';

function Navbar() {
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" style={{ flexGrow: 1 }}>
          FinTrack
        </Typography>
        <Button color="inherit" component={Link} to="/">
          Dashboard
        </Button>
        <Button color="inherit" component={Link} to="/expenses">
          Expenses
        </Button>
        <Button color="inherit" component={Link} to="/investments">
          Investments
        </Button>
        {/* Add more navigation links as needed */}
      </Toolbar>
    </AppBar>
  );
}

export default Navbar;
