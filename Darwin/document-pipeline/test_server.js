const http = require('http');
const fs = require('fs');
const path = require('path');

// Test API
const options = {
    hostname: 'localhost',
    port: 3000,
    path: '/api/templates',
    method: 'GET'
};

const req = http.request(options, (res) => {
    let data = '';
    res.on('data', chunk => { data += chunk; });
    res.on('end', () => {
        console.log('Server is running! Templates:');
        try {
            const templates = JSON.parse(data);
            console.log(JSON.stringify(templates, null, 2));
        } catch (e) {
            console.log(data);
        }
    });
});

req.on('error', (e) => {
    console.error('Server connection failed:', e.message);
});

req.end();
