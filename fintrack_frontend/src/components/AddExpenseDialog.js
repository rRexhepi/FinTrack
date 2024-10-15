import axios from 'axios';
import React from 'react';
import { Dialog, DialogTitle, DialogContent } from '@mui/material';
import AddExpenseForm from './AddExpenseForm.js';

function AddExpenseDialog({ open, handleClose }) {
  const handleSubmit = (expenseData) => {
    axios.post('/api/expenses/', expenseData)
      .then(response => {
        handleClose();
        // Optionally, refresh the expenses list in the parent component
      })
      .catch(error => console.log(error));
  };

  return (
    <Dialog open={open} onClose={handleClose} fullWidth maxWidth="sm">
      <DialogTitle>Add Expense</DialogTitle>
      <DialogContent>
        <AddExpenseForm onSubmit={handleSubmit} />
      </DialogContent>
    </Dialog>
  );
}

export default AddExpenseDialog;
