const mammoth = require('mammoth');
const fs = require('fs');

async function analyzeTestDoc() {
    try {
        console.log("=".repeat(80));
        console.log("TEST.DOCX CONTENT");
        console.log("=".repeat(80));
        const result = await mammoth.extractRawText({ path: '../docs/Test.docx' });
        console.log(result.value);
        console.log("\n[END OF DOCUMENT]");
    } catch (err) {
        console.error(err);
    }
}

analyzeTestDoc();
