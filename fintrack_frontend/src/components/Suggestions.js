import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Typography, List, ListItem, ListItemText } from '@mui/material';

function Suggestions() {
  const [suggestions, setSuggestions] = useState([]);

  useEffect(() => {
    axios.get('/api/suggestions/')
      .then(res => {
        setSuggestions(res.data.suggestions);
      })
      .catch(err => console.log(err));
  }, []);

  return (
    <div>
      <Typography variant="h5" gutterBottom>
        Financial Suggestions
      </Typography>
      {suggestions.length > 0 ? (
        <List>
          {suggestions.map((message, index) => (
            <ListItem key={index}>
              <ListItemText primary={message} />
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
