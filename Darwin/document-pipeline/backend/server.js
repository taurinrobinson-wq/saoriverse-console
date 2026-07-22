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
        const lines = text.split('\n').filter(l => l.trim().length > 0);

        // Import docx functions at top of file if not already done
        const { Document, Packer, Paragraph, TextRun, UnderlineType, AlignmentType } = require("docx");
        const templateConfig = TEMPLATES[template];

        // Create paragraphs with template formatting
        const paragraphs = lines.map(line => {
            const trimmed = line.trim();
            let isHeading = false;

            // Check if this line is a heading
            for (const pattern of HEADING_PATTERNS) {
                if (pattern.regex.test(trimmed)) {
                    isHeading = true;
                    // Apply heading formatting
                    const headingFormat = templateConfig.headingFormatting.level1;
                    return new Paragraph({
                        children: [
                            new TextRun({
                                text: trimmed,
                                bold: headingFormat.bold,
                                underline: headingFormat.underline ? { type: UnderlineType.SINGLE } : undefined,
                                size: headingFormat.fontSize * 2, // Convert to half-points
                                font: headingFormat.fontName
                            })
                        ],
                        spacing: headingFormat.spacing,
                        line: templateConfig.bodyFormatting.lineSpacing * 240, // Convert to twips
                        alignment: headingFormat.alignment === "center" ? AlignmentType.CENTER :
                            headingFormat.alignment === "right" ? AlignmentType.RIGHT : AlignmentType.LEFT
                    });
                }
            }

            // Apply body text formatting
            if (!isHeading) {
                const bodyFormat = templateConfig.bodyFormatting;
                return new Paragraph({
                    children: [
                        new TextRun({
                            text: trimmed,
                            bold: false,
                            size: bodyFormat.fontSize * 2,
                            font: bodyFormat.fontName
                        })
                    ],
                    spacing: bodyFormat.spacing,
                    line: bodyFormat.lineSpacing * 240, // Convert to twips
                    alignment: bodyFormat.alignment === "center" ? AlignmentType.CENTER :
                        bodyFormat.alignment === "right" ? AlignmentType.RIGHT : AlignmentType.LEFT,
                    indent: {
                        firstLine: bodyFormat.indent.firstLine,
                        hanging: bodyFormat.indent.hanging
                    }
                });
            }
        }).filter(p => p); // Remove undefined paragraphs

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
