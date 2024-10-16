import React from 'react';
import { Dialog, DialogTitle, DialogContent } from '@mui/material';
import AddExpenseForm from './AddExpenseForm';

function AddExpenseDialog({ open, handleClose, refreshExpenses }) {
  return (
    <Dialog open={open} onClose={handleClose} fullWidth maxWidth="sm">
      <DialogTitle>Add Expense</DialogTitle>
      <DialogContent>
        <AddExpenseForm
          handleClose={handleClose}
          refreshExpenses={refreshExpenses}
        />
      </DialogContent>
    </Dialog>
  );
}

export default AddExpenseDialog;
