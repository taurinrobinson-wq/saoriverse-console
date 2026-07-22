/**
 * Legal Document Formatting Templates
 * Defines formatting rules for different document types
 */

const TEMPLATES = {
    ca_discovery: {
        name: "California Discovery",
        description: "California discovery document formatting (interrogatories, requests, admissions)",
        headingFormatting: {
            level1: {
                fontSize: 12,
                bold: true,
                fontName: "Times New Roman",
                spacing: { before: 240, after: 120 },
                alignment: "left"
            },
            level2: {
                fontSize: 12,
                bold: true,
                fontName: "Times New Roman",
                spacing: { before: 120, after: 120 },
                alignment: "left"
            }
        },
        bodyFormatting: {
            fontSize: 12,
            fontName: "Times New Roman",
            lineSpacing: 2, // Double spacing for discovery
            spacing: { before: 0, after: 0 },
            alignment: "left",
            indent: {
                firstLine: 0,
                hanging: 0
            }
        },
        margins: {
            top: 1440,    // 1 inch
            bottom: 1440,
            left: 1440,
            right: 1440
        },
        rules: [
            "Interrogatories must be numbered sequentially",
            "Responses should be double-spaced",
            "Headings should be bold, 12pt Times New Roman",
            "All margins must be 1 inch",
            "Font size must not be smaller than 12pt"
        ]
    },

    ca_pleading: {
        name: "California Pleading",
        description: "California pleading paper formatting (complaints, answers, motions)",
        headingFormatting: {
            level1: {
                fontSize: 12,
                bold: true,
                underline: true,
                fontName: "Times New Roman",
                spacing: { before: 240, after: 120 },
                alignment: "left"
            },
            level2: {
                fontSize: 12,
                bold: true,
                fontName: "Times New Roman",
                spacing: { before: 120, after: 120 },
                alignment: "left"
            }
        },
        bodyFormatting: {
            fontSize: 12,
            fontName: "Times New Roman",
            lineSpacing: 2, // Double spacing
            spacing: { before: 0, after: 0 },
            alignment: "left",
            indent: {
                firstLine: 720, // 0.5 inch first line indent
                hanging: 0
            }
        },
        margins: {
            top: 1440,    // 1 inch top
            bottom: 1440,
            left: 1440,
            right: 1440
        },
        rules: [
            "Main section headings must be underlined",
            "All text must be double-spaced",
            "First line of paragraphs must be indented 0.5 inch",
            "Font size must be 12pt Times New Roman",
            "Margins must be 1 inch on all sides",
            "Numbered paragraphs required for complaints/answers"
        ]
    },

    contract: {
        name: "Generic Contract",
        description: "Professional contract formatting",
        headingFormatting: {
            level1: {
                fontSize: 12,
                bold: true,
                underline: true,
                fontName: "Arial",
                spacing: { before: 240, after: 120 },
                alignment: "left"
            },
            level2: {
                fontSize: 11,
                bold: true,
                fontName: "Arial",
                spacing: { before: 120, after: 80 },
                alignment: "left"
            }
        },
        bodyFormatting: {
            fontSize: 11,
            fontName: "Arial",
            lineSpacing: 1.5, // 1.5 spacing for contracts
            spacing: { before: 0, after: 80 },
            alignment: "left",
            indent: {
                firstLine: 0,
                hanging: 0
            }
        },
        margins: {
            top: 1440,    // 1 inch
            bottom: 1440,
            left: 1440,
            right: 1440
        },
        rules: [
            "Section headings must be bold and underlined",
            "Subsections should be bold but not underlined",
            "Standard font is Arial 11pt",
            "Line spacing should be 1.5",
            "Margins must be 1 inch on all sides",
            "Key terms should be capitalized throughout"
        ]
    }
};

module.exports = TEMPLATES;
