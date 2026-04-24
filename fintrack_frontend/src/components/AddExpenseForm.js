import React from 'react';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { TextField, Button, Box } from '@mui/material';

import api from '../api';

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
      api
        .post('/api/expenses/', values)
        .then(() => {
          resetForm();
          handleClose();
          refreshExpenses();
        })
        .catch((error) => {
          console.error('add expense failed', error);
        })
        .finally(() => setSubmitting(false));
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
