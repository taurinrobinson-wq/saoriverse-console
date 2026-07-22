const fs = require('fs');
const path = require('path');
const http = require('http');
const https = require('https');

// Step 1: Upload Test.docx for analysis
console.log('Uploading Test.docx for analysis...');

const testFilePath = path.join(__dirname, '../docs/Test.docx');
const fileContent = fs.readFileSync(testFilePath);

const boundary = '----WebKitFormBoundary' + Date.now();
const payload = Buffer.concat([
    Buffer.from(
        `--${boundary}\r\nContent-Disposition: form-data; name="document"; filename="Test.docx"\r\nContent-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document\r\n\r\n`
    ),
    fileContent,
    Buffer.from(`\r\n--${boundary}--\r\n`)
]);

const options = {
    hostname: 'localhost',
    port: 3000,
    path: '/api/analyze',
    method: 'POST',
    headers: {
        'Content-Type': `multipart/form-data; boundary=${boundary}`,
        'Content-Length': payload.length
    }
};

const req = http.request(options, (res) => {
    let data = '';
    res.on('data', chunk => { data += chunk; });
    res.on('end', () => {
        try {
            const analysis = JSON.parse(data);
            console.log('✓ Analysis complete');
            console.log(`  Detected ${analysis.detectedHeadings.length} headings`);

            // Step 2: Reformat with ca_discovery template
            console.log('\nReformatting with ca_discovery template...');
            reformatDocument();
        } catch (e) {
            console.error('Analysis error:', e.message);
            console.log('Response:', data.substring(0, 500));
        }
    });
});

req.on('error', (e) => {
    console.error('Upload failed:', e.message);
});

req.write(payload);
req.end();

// Step 2: Reformat the document
function reformatDocument() {
    const reformatPayload = JSON.stringify({ template: 'ca_discovery' });

    const options = {
        hostname: 'localhost',
        port: 3000,
        path: '/api/reformat',
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Content-Length': reformatPayload.length
        }
    };

    const req = http.request(options, (res) => {
        let data = '';
        res.on('data', chunk => { data += chunk; });
        res.on('end', () => {
            try {
                const result = JSON.parse(data);
                if (result.success) {
                    console.log('✓ Reformatting complete');
                    console.log(`  Output file: ${result.fileName}`);

                    // Copy to analyze location
                    const outputPath = path.join(__dirname, '../output', result.fileName);
                    const analyzeResultPath = path.join(__dirname, '../output/TEST_REFORMATTED.docx');
                    fs.copyFileSync(outputPath, analyzeResultPath);
                    console.log(`  Saved to: ${analyzeResultPath}`);
                } else {
                    console.error('Reformat error:', result.error);
                }
            } catch (e) {
                console.error('Parse error:', e.message);
                console.log('Response:', data.substring(0, 500));
            }
        });
    });

    req.on('error', (e) => {
        console.error('Reformat failed:', e.message);
    });

    req.write(reformatPayload);
    req.end();
}
