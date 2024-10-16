import React, { useState } from 'react';
import { Button } from '@mui/material';
import AddExpenseDialog from './AddExpenseDialog';

function AddExpense({ refreshExpenses }) {
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
        Add Expense
      </Button>
      <AddExpenseDialog
        open={openDialog}
        handleClose={handleCloseDialog}
        refreshExpenses={refreshExpenses}
      />
    </>
  );
}

export default AddExpense;
