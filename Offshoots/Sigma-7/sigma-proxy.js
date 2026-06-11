const http = require('http');
const https = require('https');

const port = 3000;

const server = http.createServer(async (req, res) => {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS, GET');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  // GET /api/key - return the API key from environment
  if (req.method === 'GET' && req.url === '/api/key') {
    const apiKey = process.env.CLAUDE_API_KEY;
    if (!apiKey) {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'CLAUDE_API_KEY environment variable not set' }));
      return;
    }
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ apiKey }));
    return;
  }

  // POST /api/claude - forward request to Claude API
  if (req.method === 'POST' && req.url === '/api/claude') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', async () => {
      try {
        const { model, maxTokens, messages } = JSON.parse(body);
        const apiKey = process.env.CLAUDE_API_KEY;

        if (!apiKey) {
          res.writeHead(400, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'CLAUDE_API_KEY environment variable not set' }));
          return;
        }

        const options = {
          hostname: 'api.anthropic.com',
          path: '/v1/messages',
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'x-api-key': apiKey,
            'anthropic-version': '2023-06-01',
          }
        };

        const proxyReq = https.request(options, (proxyRes) => {
          let data = '';
          proxyRes.setEncoding('utf8');
          proxyRes.on('data', chunk => {
            data += chunk;
          });
          proxyRes.on('end', () => {
            try {
              if (proxyRes.statusCode >= 400) {
                try {
                  const errData = JSON.parse(data);
                  res.writeHead(proxyRes.statusCode, { 'Content-Type': 'application/json; charset=utf-8' });
                  res.end(JSON.stringify({ error: `${proxyRes.statusCode}: ${errData.error?.message || data}` }));
                } catch {
                  res.writeHead(proxyRes.statusCode, { 'Content-Type': 'application/json; charset=utf-8' });
                  res.end(JSON.stringify({ error: `${proxyRes.statusCode}: ${data}` }));
                }
              } else {
                const parsed = JSON.parse(data);
                // Validate and sanitize the response
                if (parsed.content && Array.isArray(parsed.content) && parsed.content[0]?.text) {
                  const text = parsed.content[0].text.trim();
                  res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
                  res.end(JSON.stringify({ content: [{ text }] }));
                } else {
                  throw new Error('Invalid response format from API');
                }
              }
            } catch (e) {
              res.writeHead(500, { 'Content-Type': 'application/json; charset=utf-8' });
              res.end(JSON.stringify({ error: `Parse error: ${e.message}` }));
            }
          });
        });

        proxyReq.on('error', (err) => {
          res.writeHead(500, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: err.message }));
        });

        console.log(`[${new Date().toISOString()}] API Request - Model: ${model || 'claude-opus-4-1'}, Messages: ${(messages || []).length}`);
        
        proxyReq.write(JSON.stringify({
          model: model || 'claude-opus-4-1',
          max_tokens: maxTokens || 500,
          messages: messages || []
        }));

        proxyReq.end();
      } catch (e) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: e.message }));
      }
    });
  } else {
    res.writeHead(404);
    res.end('Not Found');
  }
});

server.listen(port, () => {
  console.log(`✓ Sigma proxy running at http://localhost:${port}`);
  console.log(`✓ Reading API key from CLAUDE_API_KEY environment variable`);
});
