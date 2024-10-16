import React from 'react';
import { Button, TextField, Grid } from '@mui/material';
import { useFormik } from 'formik';
import * as yup from 'yup';

const validationSchema = yup.object({
  name: yup.string('Enter investment name').required('Name is required'),
  ticker: yup.string('Enter ticker symbol').required('Ticker is required'),
  amount_invested: yup
    .number('Enter amount invested')
    .required('Amount invested is required')
    .positive('Amount must be positive'),
  date_invested: yup
    .date('Select date invested')
    .required('Date is required')
    .max(new Date(), 'Date cannot be in the future'),
});

function AddInvestmentForm({ handleClose, refreshInvestments }) {
  const formik = useFormik({
    initialValues: {
      name: '',
      ticker: '',
      amount_invested: '',
      date_invested: '',
    },
    validationSchema: validationSchema,
    onSubmit: (values, { setSubmitting, resetForm }) => {
      // Replace axios with fetch
      //const token = localStorage.getItem('access_token'); // If authentication is required

      fetch('/api/investments/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Include the authorization header if required
          // 'Authorization': token ? `Bearer ${token}` : '',
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
          handleClose();
          refreshInvestments(); // Refresh the investments list
        })
        .catch((error) => {
          setSubmitting(false);
          console.error('There was an error adding the investment!', error);
          // Optionally, display error messages to the user
        });
    },
  });

  return (
    <form onSubmit={formik.handleSubmit}>
      <Grid container spacing={2} style={{ marginTop: '8px' }}>
        <Grid item xs={12}>
          <TextField
            fullWidth
            id="name"
            name="name"
            label="Investment Name"
            value={formik.values.name}
            onChange={formik.handleChange}
            error={formik.touched.name && Boolean(formik.errors.name)}
            helperText={formik.touched.name && formik.errors.name}
          />
        </Grid>

        <Grid item xs={12}>
          <TextField
            fullWidth
            id="ticker"
            name="ticker"
            label="Ticker Symbol"
            value={formik.values.ticker}
            onChange={formik.handleChange}
            error={formik.touched.ticker && Boolean(formik.errors.ticker)}
            helperText={formik.touched.ticker && formik.errors.ticker}
          />
        </Grid>

        <Grid item xs={12}>
          <TextField
            fullWidth
            id="amount_invested"
            name="amount_invested"
            label="Amount Invested"
            type="number"
            value={formik.values.amount_invested}
            onChange={formik.handleChange}
            error={
              formik.touched.amount_invested &&
              Boolean(formik.errors.amount_invested)
            }
            helperText={
              formik.touched.amount_invested && formik.errors.amount_invested
            }
          />
        </Grid>

        <Grid item xs={12}>
          <TextField
            fullWidth
            id="date_invested"
            name="date_invested"
            label="Date Invested"
            type="date"
            value={formik.values.date_invested}
            onChange={formik.handleChange}
            error={
              formik.touched.date_invested &&
              Boolean(formik.errors.date_invested)
            }
            helperText={
              formik.touched.date_invested && formik.errors.date_invested
            }
            InputLabelProps={{
              shrink: true,
            }}
          />
        </Grid>

        <Grid item xs={12} style={{ textAlign: 'right', marginTop: '16px' }}>
          <Button onClick={handleClose} style={{ marginRight: '8px' }}>
            Cancel
          </Button>
          <Button
            color="primary"
            variant="contained"
            type="submit"
            disabled={formik.isSubmitting}
          >
            Add Investment
          </Button>
        </Grid>
      </Grid>
    </form>
  );
}

export default AddInvestmentForm;
