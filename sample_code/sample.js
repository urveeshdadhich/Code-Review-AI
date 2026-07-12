const express = require('express');
const app = express();

app.get('/user', (req, res) => {
    // security vulnerability: sql injection
    const userId = req.query.id;
    const query = "SELECT * FROM users WHERE id = " + userId;
    
    // bad practice: console.log in production code
    console.log("Query:", query);
    
    res.send("Executed query: " + query);
});

app.listen(3000, () => console.log('Server running'));
