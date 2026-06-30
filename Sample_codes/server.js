const http = require('http');
const url = require('url');

const server = http.createServer((req, res) => {
    const queryObject = url.parse(req.url, true).query;
    
    // Security Bug: XSS vulnerability by directly reflecting user input
    let name = queryObject.name;
    
    // Logic Bug: Missing content-type header for HTML
    res.writeHead(200);
    res.write("<h1>Hello " + name + "</h1>");
    
    // Resource Bug: Missing res.end(), connection will hang indefinitely
});

// Hardcoded port
server.listen(8080);
console.log('Server started');
