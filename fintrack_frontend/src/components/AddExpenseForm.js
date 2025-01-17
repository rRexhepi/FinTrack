import React from 'react';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { TextField, Button, Box } from '@mui/material';

function AddExpenseForm({ handleClose, refreshExpenses }) {
  const formik = useFormik({
    initialValues: {
      date: '',
      category: '',
      amount: '',
      description: '',
    },
    validationSchema: Yup.object({
      date: Yup.date().required('Date is required'),
      category: Yup.string().required('Category is required'),
      amount: Yup.number()
        .required('Amount is required')
        .positive('Amount must be positive'),
      description: Yup.string(),
    }),
    onSubmit: (values, { setSubmitting, resetForm }) => {
      fetch('/api/expenses/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Include authentication headers if necessary
          // 'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(values),
      })
        .then((response) => {
          if (!response.ok) {
            return response.json().then((data) => {
              throw new Error(data.detail || 'An error occurred');
            });
          }
          return response.json();
        })
        .then((data) => {
          setSubmitting(false);
          resetForm();
          handleClose(); // Close the dialog
          refreshExpenses(); // Refresh the expenses list
        })
        .catch((error) => {
          setSubmitting(false);
          console.error('There was an error adding the expense!', error);
          // Optionally, display error messages to the user
        });
    },
  });

  return (
    <form onSubmit={formik.handleSubmit}>
      <TextField
        margin="dense"
        name="date"
        label="Date"
        type="date"
        fullWidth
        InputLabelProps={{ shrink: true }}
        value={formik.values.date}
        onChange={formik.handleChange}
        error={formik.touched.date && Boolean(formik.errors.date)}
        helperText={formik.touched.date && formik.errors.date}
      />
      <TextField
        margin="dense"
        name="category"
        label="Category"
        fullWidth
        value={formik.values.category}
        onChange={formik.handleChange}
        error={formik.touched.category && Boolean(formik.errors.category)}
        helperText={formik.touched.category && formik.errors.category}
      />
      <TextField
        margin="dense"
        name="amount"
        label="Amount"
        type="number"
        fullWidth
        value={formik.values.amount}
        onChange={formik.handleChange}
        error={formik.touched.amount && Boolean(formik.errors.amount)}
        helperText={formik.touched.amount && formik.errors.amount}
      />
      <TextField
        margin="dense"
        name="description"
        label="Description"
        fullWidth
        multiline
        rows={3}
        value={formik.values.description}
        onChange={formik.handleChange}
      />
      <Box mt={2} style={{ textAlign: 'right' }}>
        <Button onClick={handleClose} style={{ marginRight: '8px' }}>
          Cancel
        </Button>
        <Button
          color="primary"
          variant="contained"
          type="submit"
          disabled={formik.isSubmitting}
        >
          Add Expense
        </Button>
      </Box>
    </form>
  );
}

export default AddExpenseForm;
