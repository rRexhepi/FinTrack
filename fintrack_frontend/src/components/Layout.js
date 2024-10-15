import React from 'react';
import { Container, Box } from '@mui/material';
import Navbar from './Navbar';

function Layout({ children }) {
  return (
    <div>
      <Navbar />
      <Container maxWidth="lg">
        <Box my={4}>{children}</Box>
      </Container>
    </div>
  );
}

export default Layout;