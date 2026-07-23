const mammoth = require('mammoth');

async function show() {
    try {
        const result = await mammoth.extractRawText({ path: './output/darwin-reformatted-ca_discovery-1784764494538.docx' });
        const lines = result.value.split('\n');
        console.log("=".repeat(80));
        console.log("REFORMATTED OUTPUT - LINE BY LINE (FIRST 70 LINES)");
        console.log("=".repeat(80));
        lines.slice(0, 70).forEach((line, idx) => {
            const display = line.length > 75 ? line.substring(0, 75) + '...' : line;
            console.log(`${String(idx + 1).padStart(3)}: ${display}`);
        });
    } catch (err) {
        console.error(err);
    }
}

show();
