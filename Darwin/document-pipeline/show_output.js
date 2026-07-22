const mammoth = require('mammoth');

async function show() {
    try {
        const result = await mammoth.extractRawText({ path: './output/darwin-reformatted-ca_discovery-1784764351613.docx' });
        const lines = result.value.split('\n');
        console.log("=".repeat(80));
        console.log("REFORMATTED OUTPUT (FIRST 50 LINES)");
        console.log("=".repeat(80));
        lines.slice(0, 50).forEach((line, idx) => {
            console.log(`${String(idx + 1).padStart(3)}: ${line}`);
        });
    } catch (err) {
        console.error(err);
    }
}

show();
