import React, { useState, useEffect } from 'react';
import { Typography, List, ListItem, ListItemText } from '@mui/material';

import api from '../api';

function Suggestions() {
  const [suggestions, setSuggestions] = useState([]);

  useEffect(() => {
    api
      .get('/api/suggestions/')
      .then((res) => setSuggestions(res.data.results || []))
      .catch((err) => console.error('suggestions', err));
  }, []);

  return (
    <div>
      <Typography variant="h5" gutterBottom>
        Financial Suggestions
      </Typography>
      {suggestions.length > 0 ? (
        <List>
          {suggestions.map((s) => (
            <ListItem key={s.id}>
              <ListItemText primary={s.message} />
            </ListItem>
          ))}
        </List>
      ) : (
        <Typography variant="body1">
          No suggestions at this time. Keep up the good work!
        </Typography>
      )}
    </div>
  );
}

export default Suggestions;
