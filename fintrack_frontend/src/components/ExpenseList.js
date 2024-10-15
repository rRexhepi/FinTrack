import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { DataGrid } from '@mui/x-data-grid';
import { Button } from '@mui/material';
import AddExpenseDialog from './AddExpenseDialog';
import AddIcon from '@mui/icons-material/Add';


function ExpenseList() {
  const [expenses, setExpenses] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);

  const fetchExpenses = () => {
    axios.get('/api/expenses/')
      .then(res => setExpenses(res.data))
      .catch(err => console.log(err));
  };

  useEffect(() => {
    fetchExpenses();
  }, []);

  const handleOpenDialog = () => setOpenDialog(true);
  const handleCloseDialog = () => {
    setOpenDialog(false);
    fetchExpenses(); // Refresh the list after adding a new expense
  };

  const columns = [
    { field: 'date', headerName: 'Date', width: 150 },
    { field: 'category', headerName: 'Category', width: 150 },
    { field: 'amount', headerName: 'Amount', width: 100, type: 'number' },
    { field: 'description', headerName: 'Description', width: 300 },
  ];

  return (
    <div style={{ height: 500, width: '100%' }}>
      <Button variant="contained" color="primary" onClick={handleOpenDialog} style={{ marginBottom: '1rem' }} startIcon={<AddIcon />}>
        Add Expense
      </Button>
      <AddExpenseDialog open={openDialog} handleClose={handleCloseDialog} />
      <DataGrid
        rows={expenses}
        columns={columns}
        pageSize={5}
        rowsPerPageOptions={[5]}
        getRowId={(row) => row.id}
      />
    </div>
  );
}

export default ExpenseList;
