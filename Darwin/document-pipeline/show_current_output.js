const mammoth = require('mammoth');

mammoth.extractRawText({ path: './output/darwin-reformatted-ca_discovery-1784764176718.docx' })
    .then(result => {
        console.log("=".repeat(80));
        console.log("CURRENT REFORMATTED OUTPUT");
        console.log("=".repeat(80));
        console.log(result.value);
    })
    .catch(err => console.error(err));
