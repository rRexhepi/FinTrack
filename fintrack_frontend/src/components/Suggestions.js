import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Suggestions() {
  const [suggestions, setSuggestions] = useState([]);

  useEffect(() => {
    axios.get('/api/suggestions/')
      .then(res => {
        setSuggestions(res.data.suggestions);
      })
      .catch(err => {
        console.log(err);
      });
  }, []);

  return (
    <div>
      <h2>Financial Suggestions</h2>
      {suggestions.length > 0 ? (
        <ul>
          {suggestions.map((message, index) => (
            <li key={index}>{message}</li>
          ))}
        </ul>
      ) : (
        <p>No suggestions at this time. Keep up the good work!</p>
      )}
    </div>
  );
}

export default Suggestions;
