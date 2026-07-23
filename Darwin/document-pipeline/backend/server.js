/**
 * Darwin Document Pipeline - Express Server
 * Handles document upload, analysis, and reformatting
 */

const express = require("express");
const multer = require("multer");
const { Packer } = require("docx");
const fs = require("fs");
const path = require("path");
const mammoth = require("mammoth");

const app = express();
const PORT = process.env.PORT || 3000;

// In-memory storage for uploaded files (for MVP)
let lastUploadedFile = null;

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname, "../public")));

// File upload configuration
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        const uploadDir = path.join(__dirname, "../uploads");
        if (!fs.existsSync(uploadDir)) {
            fs.mkdirSync(uploadDir, { recursive: true });
        }
        cb(null, uploadDir);
    },
    filename: (req, file, cb) => {
        cb(null, `${Date.now()}-${file.originalname}`);
    }
});

const upload = multer({
    storage, fileFilter: (req, file, cb) => {
        if (file.mimetype === "application/vnd.openxmlformats-officedocument.wordprocessingml.document") {
            cb(null, true);
        } else {
            cb(new Error("Only .docx files are supported"));
        }
    }
});

const TEMPLATES = require("./templates");
const HEADING_PATTERNS = require("./headingPatterns");

/**
 * GET /api/templates
 * Return list of available templates
 */
app.get("/api/templates", (req, res) => {
    const templates = Object.keys(TEMPLATES).map(key => ({
        id: key,
        name: TEMPLATES[key].name,
        description: TEMPLATES[key].description
    }));
    res.json(templates);
});

/**
 * POST /api/analyze
 * Upload and analyze a document
 */
app.post("/api/analyze", upload.single("document"), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: "No file uploaded" });
        }

        const filePath = req.file.path;

        // Store file path for later reformatting
        lastUploadedFile = {
            path: filePath,
            originalName: req.file.originalname,
            uploadedAt: Date.now()
        };

        // Extract text and basic info from Word document
        const result = await mammoth.extractRawText({ path: filePath });

        const analysis = {
            fileName: req.file.originalname,
            fileSize: req.file.size,
            uploadTime: new Date(),
            text: result.value,
            paragraphs: result.value.split('\n').filter(p => p.trim().length > 0).length,
            detectedHeadings: detectHeadings(result.value),
            recommendations: generateRecommendations(result.value)
        };

        res.json(analysis);
    } catch (error) {
        console.error("Analysis error:", error);
        res.status(500).json({ error: "Failed to analyze document: " + error.message });
    }
});

/**
 * POST /api/reformat
 * Reformat document according to template
 */
app.post("/api/reformat", async (req, res) => {
    try {
        const { template } = req.body;

        if (!template || !TEMPLATES[template]) {
            return res.status(400).json({ error: "Invalid template" });
        }

        if (!lastUploadedFile) {
            return res.status(400).json({ error: "No document uploaded" });
        }

        // Create output directory if needed
        const outputDir = path.join(__dirname, "../output");
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }

        // Extract text from the uploaded document
        const result = await mammoth.extractRawText({ path: lastUploadedFile.path });
        const text = result.value;

        // Import docx functions
        const { Document, Packer, Paragraph, TextRun, UnderlineType, AlignmentType, Table, TableRow, TableCell, BorderStyle, WidthType } = require("docx");
        const templateConfig = TEMPLATES[template];

        // Parse document structure
        const docStructure = parseDiscoveryDocument(text);

        // Build document with proper sections
        const paragraphs = [];

        // 1. ADD ATTORNEY HEADER (plain paragraphs, no special formatting)
        if (docStructure.attorneyHeader) {
            docStructure.attorneyHeader.split('\n').filter(l => l.trim().length > 0).forEach(line => {
                paragraphs.push(new Paragraph({
                    children: [new TextRun({
                        text: line.trim(),
                        bold: false,
                        size: 12 * 2,
                        font: "Times New Roman"
                    })],
                    alignment: AlignmentType.LEFT,
                    line: 12 * 240,
                    spacing: { before: 0, after: 0 }
                }));
            });
            paragraphs.push(new Paragraph({ text: "", spacing: { before: 120 } }));
        }

        // 2. ADD PREAMBLE HEADERS (centered, "IN THE MATTER OF...")
        if (docStructure.preambleHeader) {
            docStructure.preambleHeader.split('\n').filter(l => l.trim().length > 0).forEach(line => {
                paragraphs.push(new Paragraph({
                    children: [new TextRun({
                        text: line.trim(),
                        bold: false,
                        size: 12 * 2,
                        font: "Times New Roman"
                    })],
                    alignment: AlignmentType.CENTER,
                    line: 12 * 240,
                    spacing: { before: 0, after: 60 }
                }));
            });
            paragraphs.push(new Paragraph({ text: "", spacing: { before: 120 } }));
        }

        // 3. ADD MAIN SECTION TITLE (centered, BOLD, UNDERLINED) - caption page uses 12pt
        if (docStructure.mainSectionTitle) {
            paragraphs.push(new Paragraph({
                children: [
                    new TextRun({
                        text: docStructure.mainSectionTitle,
                        bold: true,  // BOLD
                        underline: { type: UnderlineType.SINGLE },  // UNDERLINED
                        size: 12 * 2,
                        font: "Times New Roman"
                    })
                ],
                alignment: AlignmentType.CENTER,
                line: 12 * 240,  // 12pt on caption page
                spacing: { before: 0, after: 120 }  // 1 blank line after
            }));
        }

        // 4. ADD CASE CAPTION TABLE (2-column: parties on left, case info on right)
        if (docStructure.caseCaption) {
            paragraphs.push(...buildCaptionTable(docStructure.caseCaption));
            paragraphs.push(new Paragraph({ text: "", spacing: { before: 120 } }));
        }

        // 5. ADD PREAMBLE TEXT ("Pursuant to Code of Civil Procedure...")
        if (docStructure.preambleText) {
            docStructure.preambleText.split('\n').filter(l => l.trim().length > 0).forEach(line => {
                paragraphs.push(new Paragraph({
                    children: [new TextRun({
                        text: line.trim(),
                        bold: false,
                        size: 12 * 2,
                        font: "Times New Roman"
                    })],
                    alignment: AlignmentType.LEFT,
                    line: 12 * 240,  // Single line spacing
                    spacing: { before: 0, after: 0 }
                }));
            });
            paragraphs.push(new Paragraph({ text: "", spacing: { before: 60 } }));
        }

        // 6. ADD REQUESTS AND RESPONSES (Body pages: 24pt, 0.5" indent, bold+underline headings)
        if (docStructure.requests && docStructure.requests.length > 0) {
            docStructure.requests.forEach((request, idx) => {
                // REQUEST HEADING - BOLD, UNDERLINED, 24pt, no indent
                paragraphs.push(new Paragraph({
                    children: [new TextRun({
                        text: request.heading,
                        bold: true,  // BOLD heading
                        underline: { type: UnderlineType.SINGLE },  // UNDERLINED
                        size: 12 * 2,
                        font: "Times New Roman"
                    })],
                    alignment: AlignmentType.LEFT,
                    line: 24 * 240,  // 24pt line spacing
                    spacing: { before: 0, after: 0 }
                }));

                // REQUEST TEXT - 24pt spacing with 0.5" indent
                if (request.text && request.text.trim().length > 0) {
                    paragraphs.push(new Paragraph({
                        children: [new TextRun({
                            text: request.text.trim(),
                            bold: false,
                            size: 12 * 2,
                            font: "Times New Roman"
                        })],
                        alignment: AlignmentType.LEFT,
                        line: 24 * 240,  // 24pt line spacing
                        indent: { firstLine: 720 },  // 0.5" indent
                        spacing: { before: 0, after: 0 }
                    }));
                }

                // RESPONSE HEADING - BOLD, UNDERLINED, 24pt, no indent
                if (request.responseHeading && request.responseHeading.trim().length > 0) {
                    paragraphs.push(new Paragraph({
                        children: [new TextRun({
                            text: request.responseHeading.trim(),
                            bold: true,  // BOLD heading
                            underline: { type: UnderlineType.SINGLE },  // UNDERLINED
                            size: 12 * 2,
                            font: "Times New Roman"
                        })],
                        alignment: AlignmentType.LEFT,
                        line: 24 * 240,  // 24pt line spacing
                        spacing: { before: 0, after: 0 }
                    }));
                }

                // RESPONSE TEXT - 24pt spacing with 0.5" indent
                if (request.responseText && request.responseText.trim().length > 0) {
                    paragraphs.push(new Paragraph({
                        children: [new TextRun({
                            text: request.responseText.trim(),
                            bold: false,
                            size: 12 * 2,
                            font: "Times New Roman"
                        })],
                        alignment: AlignmentType.LEFT,
                        line: 24 * 240,  // 24pt line spacing
                        indent: { firstLine: 720 },  // 0.5" indent
                        spacing: { before: 0, after: 0 }
                    }));
                }
            });
        }

        // 7. ADD SIGNATURE BLOCK (12pt spacing)
        if (docStructure.signatureBlock && docStructure.signatureBlock.trim().length > 0) {
            paragraphs.push(new Paragraph({ text: "", spacing: { before: 300 } }));
            docStructure.signatureBlock.split('\n').filter(l => l.trim().length > 0).forEach(line => {
                paragraphs.push(new Paragraph({
                    children: [new TextRun({
                        text: line.trim(),
                        bold: false,
                        size: 12 * 2,
                        font: "Times New Roman"
                    })],
                    alignment: AlignmentType.LEFT,
                    line: 12 * 240,
                    spacing: { before: 0, after: 0 }
                }));
            });
        }

        // Create new Word document
        const doc = new Document({
            sections: [
                {
                    properties: {
                        page: {
                            margins: {
                                top: templateConfig.margins.top,
                                bottom: templateConfig.margins.bottom,
                                left: templateConfig.margins.left,
                                right: templateConfig.margins.right
                            }
                        }
                    },
                    children: paragraphs
                }
            ]
        });

        // Generate and save the document
        const fileName = `darwin-reformatted-${template}-${Date.now()}.docx`;
        const filePath = path.join(outputDir, fileName);

        const buffer = await Packer.toBuffer(doc);
        fs.writeFileSync(filePath, buffer);

        res.json({
            success: true,
            message: "Document reformatted successfully",
            fileName: fileName,
            template: templateConfig.name,
            downloadUrl: `/download/${fileName}`
        });
    } catch (error) {
        console.error("Reformat error:", error);
        res.status(500).json({ error: "Failed to reformat document: " + error.message });
    }
});

/**
 * GET /download/:fileName
 * Download reformatted document
 */
app.get("/download/:fileName", (req, res) => {
    try {
        const filePath = path.join(__dirname, "../output", req.params.fileName);

        // Security check: prevent directory traversal
        if (!filePath.startsWith(path.join(__dirname, "../output"))) {
            return res.status(403).json({ error: "Access denied" });
        }

        if (!fs.existsSync(filePath)) {
            return res.status(404).json({ error: "File not found" });
        }

        res.download(filePath, req.params.fileName);
    } catch (error) {
        console.error("Download error:", error);
        res.status(500).json({ error: "Failed to download file" });
    }
});

/**
 * Helper: Build 2-column caption table for discovery documents
 */
function buildCaptionTable(caption) {
    const { Table, TableRow, TableCell, Paragraph, TextRun, AlignmentType, BorderStyle, WidthType } = require("docx");

    // Parse caption into left (parties) and right (case info) columns
    const lines = caption.split('\n').filter(l => l.trim().length > 0);
    const leftCol = [];
    const rightCol = [];

    lines.forEach(line => {
        const trimmed = line.trim();
        // Heuristic: "Claim No." and "SET" lines go to right column
        if (trimmed.match(/^(SET\s+NUMBER|CLAIM\s+NO|RESPONSES?)/i)) {
            rightCol.push(trimmed);
        } else if (trimmed.match(/^(ASKING|RESPONDING|SET|CLAIM)/i) && trimmed.includes(':')) {
            // Split "ASKING PARTY: value" into separate parts
            const [label, ...values] = trimmed.split(':');
            const value = values.join(':').trim();
            if (label.match(/^(ASKING|RESPONDENT|RESPONDING)/i)) {
                leftCol.push(label.trim() + ':');
                if (value) leftCol.push(value);
            } else {
                rightCol.push(label.trim() + ':');
                if (value) rightCol.push(value);
            }
        } else {
            // Default to left column for party info
            leftCol.push(trimmed);
        }
    });

    // Build table cells with proper formatting
    const leftCellParagraphs = leftCol.map(line => new Paragraph({
        children: [new TextRun({
            text: line,
            bold: !line.includes('vs.'),
            size: 12 * 2,
            font: "Times New Roman"
        })],
        alignment: AlignmentType.LEFT,
        line: 12 * 240,
        spacing: { before: 0, after: 60 }
    }));

    const rightCellParagraphs = rightCol.map(line => new Paragraph({
        children: [new TextRun({
            text: line,
            bold: true,
            size: 12 * 2,
            font: "Times New Roman"
        })],
        alignment: AlignmentType.LEFT,
        line: 12 * 240,
        spacing: { before: 0, after: 60 }
    }));

    // Create 2-column table with no borders
    const table = new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        rows: [
            new TableRow({
                children: [
                    new TableCell({
                        width: { size: 50, type: WidthType.PERCENTAGE },
                        children: leftCellParagraphs.length > 0 ? leftCellParagraphs : [new Paragraph("")],
                        borders: {
                            top: { style: BorderStyle.NONE },
                            bottom: { style: BorderStyle.NONE },
                            left: { style: BorderStyle.NONE },
                            right: { style: BorderStyle.NONE }
                        }
                    }),
                    new TableCell({
                        width: { size: 50, type: WidthType.PERCENTAGE },
                        children: rightCellParagraphs.length > 0 ? rightCellParagraphs : [new Paragraph("")],
                        borders: {
                            top: { style: BorderStyle.NONE },
                            bottom: { style: BorderStyle.NONE },
                            left: { style: BorderStyle.NONE },
                            right: { style: BorderStyle.NONE }
                        }
                    })
                ]
            })
        ]
    });

    return [table];
}

/**
 * Helper: Parse discovery document structure with robust state machine
 */
function parseDiscoveryDocument(text) {
    const lines = text.split('\n');

    const structure = {
        attorneyHeader: [],
        preambleHeader: [],
        caseCaption: [],
        mainSectionTitle: null,
        preambleText: [],
        requests: [],
        signatureBlock: []
    };

    let state = 'ATTORNEY_HEADER';
    let blankCount = 0;
    let capturedFirstCaseMarker = false;
    let currentRequest = null;

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const trimmed = line.trim().toUpperCase();
        const trimmedLower = line.trim();

        // Skip excessive blank lines
        if (trimmed.length === 0) {
            blankCount++;
            continue;
        } else {
            blankCount = 0;
        }

        // STATE MACHINE

        // Transition to PREAMBLE when we see "IN THE MATTER"
        if (trimmed.match(/^IN THE MATTER OF/)) {
            state = 'PREAMBLE_HEADER';
            structure.preambleHeader.push(trimmedLower);
            continue;
        }

        // Continue collecting preamble header
        if (state === 'PREAMBLE_HEADER' && trimmedLower.length > 0) {
            if (!trimmed.match(/^ASKING|^RESPONDENT|^RESPONDING|^SET|^CLAIM|^RESPONSES?/)) {
                structure.preambleHeader.push(trimmedLower);
                continue;
            } else {
                // Check if this line is the main title (has "SET" in it - like "SET ONE")
                if (trimmed.match(/^RESPONSES? TO REQUESTS? FOR.*SET\s+(ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN|\d+)/i)) {
                    structure.mainSectionTitle = trimmedLower;
                    state = 'CASE_CAPTION';  // Case caption comes next
                    continue;  // Skip adding this line elsewhere
                } else {
                    state = 'CASE_CAPTION';
                }
            }
        }

        // Collect case caption lines (ASKING PARTY, RESPONDENT, SET NUMBER, CLAIM NO)
        if (state === 'CASE_CAPTION' &&
            (trimmed.match(/^ASKING PARTY|^RESPONDENT|^RESPONDING PARTY|^SET NUMBER|^CLAIM NO/) ||
                capturedFirstCaseMarker)) {
            capturedFirstCaseMarker = true;
            structure.caseCaption.push(trimmedLower);

            // Look ahead to see if we should transition to preamble text
            if (i + 1 < lines.length) {
                const nextTrimmed = lines[i + 1].trim().toUpperCase();
                if (nextTrimmed.match(/^PURSUANT|^THE PARTIES/)) {
                    state = 'PREAMBLE_TEXT';
                }
            }
            continue;
        }

        // Capture preamble text ("Pursuant to Code of Civil Procedure...", "THE PARTIES...")
        if (state === 'PREAMBLE_TEXT' && trimmedLower.length > 0) {
            if (!trimmed.match(/^REQUEST FOR|^RESPONSES?/)) {
                structure.preambleText.push(trimmedLower);
                continue;
            } else if (trimmed.match(/^REQUEST FOR/)) {
                state = 'REQUESTS';
                // Process this line as a request heading (fall through)
            } else {
                continue;
            }
        }

        // Capture document title if we haven't already (must include "SET")
        if (trimmed.match(/^RESPONSES? TO REQUESTS? FOR.*SET\s+(ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN|\d+)/i) && !structure.mainSectionTitle) {
            structure.mainSectionTitle = trimmedLower;
            state = 'PREAMBLE_TEXT';
            continue;
        }

        // Detect REQUEST headings (REQUEST FOR ADMISSIONS, REQUEST FOR PRODUCTION, etc.)
        if (trimmed.match(/^REQUEST FOR (ADMISSIONS?|PRODUCTION|INTERROGATORIES|DOCUMENTS) NO\.? (\d+|[A-Z]+)/i)) {
            // Save previous request if exists
            if (currentRequest && (currentRequest.heading || currentRequest.text)) {
                structure.requests.push(currentRequest);
            }

            currentRequest = {
                heading: trimmedLower,
                text: null,
                responseHeading: null,
                responseText: null
            };
            state = 'REQUESTS';
            continue;
        }

        // Detect RESPONSE headings (when explicitly stated)
        if (trimmed.match(/^RESPONSE TO REQUESTS? FOR (ADMISSIONS?|PRODUCTION|INTERROGATORIES|DOCUMENTS) NO\.? (\d+|[A-Z]+)/i)) {
            if (currentRequest) {
                currentRequest.responseHeading = trimmedLower;
            }
            continue;
        }

        // Detect response text indicators (Responding Party..., Denied, etc.)
        if (state === 'REQUESTS' && currentRequest && trimmedLower.length > 0) {
            const isResponseIndicator = trimmed.match(/^RESPONDING PARTY|^OBJECTION|^DENIED|^ADMIT|^REFUSE|^WILL COMPLY|^UNABLE TO COMPLY|^NO DOCUMENTS/i);

            if (isResponseIndicator) {
                // If we don't have a responseHeading yet, create implicit one
                if (!currentRequest.responseHeading) {
                    currentRequest.responseHeading = 'RESPONSE:';
                }
            }
        }

        // Signature block detection (at end of document)
        if (state === 'REQUESTS' && i > lines.length - 20 && trimmedLower.length > 5) {
            if (trimmed.match(/^DATED|^RESPECTFULLY|^SIGNATURE|^PROOF OF|^CERTIFICATE|^ATTORNEY FOR/)) {
                state = 'SIGNATURE';
            }
        }

        // Populate current section based on state
        if (state === 'ATTORNEY_HEADER' && trimmedLower.length > 0) {
            if (!trimmed.match(/^IN THE MATTER|^UNINSURED|^UNDERINSURED/)) {
                structure.attorneyHeader.push(trimmedLower);
            }
        } else if (state === 'REQUESTS' && trimmedLower.length > 0 && currentRequest) {
            if (currentRequest.responseHeading && !trimmed.match(/^REQUEST|^RESPONSE|^ADMISSIONS?|^PRODUCTION|^INTERROGATORIES/)) {
                // We're in response text
                currentRequest.responseText = currentRequest.responseText
                    ? currentRequest.responseText + ' ' + trimmedLower
                    : trimmedLower;
            } else if (!currentRequest.responseHeading && !trimmed.match(/^REQUEST|^RESPONSE|^RESPONDING PARTY|^OBJECTION|^DENIED|^ADMIT/i)) {
                // We're in request text
                currentRequest.text = currentRequest.text
                    ? currentRequest.text + ' ' + trimmedLower
                    : trimmedLower;
            } else if (!currentRequest.responseHeading && trimmed.match(/^RESPONDING PARTY|^OBJECTION|^DENIED|^ADMIT/i)) {
                // This is response content without explicit heading
                currentRequest.responseHeading = 'RESPONSE:';
                currentRequest.responseText = trimmedLower;
            }
        } else if (state === 'SIGNATURE' && trimmedLower.length > 0) {
            structure.signatureBlock.push(trimmedLower);
        }
    }

    // Save final request
    if (currentRequest && (currentRequest.heading || currentRequest.text)) {
        structure.requests.push(currentRequest);
    }

    return {
        attorneyHeader: structure.attorneyHeader.join('\n'),
        preambleHeader: structure.preambleHeader.join('\n'),
        caseCaption: structure.caseCaption.join('\n'),
        mainSectionTitle: structure.mainSectionTitle,
        preambleText: structure.preambleText.join('\n'),
        requests: structure.requests,
        signatureBlock: structure.signatureBlock.join('\n')
    };
}

/**
 * Helper: Detect legal headings in text
 */
function detectHeadings(text) {
    const HEADING_PATTERNS = [
        { name: "Interrogatory", regex: /^Interrogatory\s+No\.\s*\d+/im },
        { name: "Special Interrogatory", regex: /^Special\s+Interrogatory\s+No\.\s*\d+/im },
        { name: "Form Interrogatory", regex: /^Form\s+Interrogatory\s+No\.\s*\d+/im },
        { name: "Request for Production", regex: /^Request\s+(?:for\s+)?Production\s+No\.\s*\d+/im },
        { name: "Request for Admission", regex: /^Request\s+for\s+Admission\s+No\.\s*\d+/im },
        { name: "Topic Section", regex: /^Topic\s+\d+[:\.\s]/im },
        { name: "Document Request", regex: /^Document\s+Request\s+No\.\s*\d+/im }
    ];

    const detected = [];
    const lines = text.split('\n');

    lines.forEach((line, idx) => {
        for (const pattern of HEADING_PATTERNS) {
            if (pattern.regex.test(line)) {
                detected.push({ type: pattern.name, text: line.trim() });
                break;
            }
        }
    });

    return detected;
}

/**
 * Helper: Generate recommendations
 */
function generateRecommendations(text) {
    const recommendations = [];
    const headings = detectHeadings(text);

    if (headings.length === 0) {
        recommendations.push("No legal headings detected. Document may need restructuring.");
    } else {
        recommendations.push(`Found ${headings.length} legal headings. Good document structure detected.`);
    }

    if (text.length > 50000) {
        recommendations.push("Document is large (50KB+). Consider breaking into multiple sections.");
    }

    recommendations.push("Try 'California Pleading' template for legal compliance formatting.");

    return recommendations;
}

// Start server
app.listen(PORT, () => {
    console.log(`✨ Darwin Document Pipeline running on http://localhost:${PORT}`);
    console.log(`📤 Upload documents for analysis and reformatting`);
});
