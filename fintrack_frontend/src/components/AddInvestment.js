import React, { useState } from 'react';
import { Button, Dialog, DialogTitle, DialogContent } from '@mui/material';
import AddInvestmentForm from './AddInvestmentForm';

function AddInvestment({ refreshInvestments }) {
  const [openDialog, setOpenDialog] = useState(false);

  const handleOpenDialog = () => setOpenDialog(true);
  const handleCloseDialog = () => setOpenDialog(false);

  return (
    <>
      <Button
        variant="contained"
        color="primary"
        onClick={handleOpenDialog}
        style={{ marginBottom: '16px' }}
      >
        Add Investment
      </Button>
      <Dialog open={openDialog} onClose={handleCloseDialog} fullWidth maxWidth="sm">
        <DialogTitle>Add Investment</DialogTitle>
        <DialogContent>
          <AddInvestmentForm
            handleClose={handleCloseDialog}
            refreshInvestments={refreshInvestments}
          />
        </DialogContent>
      </Dialog>
    </>
  );
}

export default AddInvestment;
