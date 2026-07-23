/**
 * Legal Document Formatting Templates
 * Darwin Style Profile v2 (Finalized)
 * 
 * KEY RULES:
 * - Caption Page (Page 1): 12pt line spacing, no indent, plain text
 * - Body Pages: 24pt line spacing, 0.5" first-line indent
 * - Headings: BOLD + UNDERLINE on both pages
 * - Major titles: Centered
 * - Request/Response: Left-justified
 */

const TEMPLATES = {
    ca_discovery: {
        name: "California Discovery",
        description: "California discovery document formatting (interrogatories, requests, admissions)",

        // Margins
        margins: {
            top: 1152,      // 0.80 inches
            bottom: 1440,   // 1.0 inch
            left: 1440,     // 1.0 inch
            right: 1440     // 1.0 inch
        },

        // CAPTION PAGE (Page 1): 12pt spacing, no indent
        captionPageFormatting: {
            fontSize: 12,
            fontName: "Times New Roman",
            bold: false,
            underline: false,
            lineSpacing: 12 * 240,  // 12pt = 12 * 240 twips
            spacing: { before: 0, after: 0 },
            alignment: "left",
            indent: { firstLine: 0, hanging: 0 }
        },

        // BODY PAGES: 24pt spacing, 0.5" indent
        bodyPageFormatting: {
            fontSize: 12,
            fontName: "Times New Roman",
            bold: false,
            underline: false,
            lineSpacing: 24 * 240,  // 24pt = 24 * 240 twips
            spacing: { before: 0, after: 0 },
            alignment: "left",
            indent: { firstLine: 720, hanging: 0 }  // 720 twips = 0.5 inches
        },

        // MAJOR SECTION HEADINGS (centered, bold, underline)
        majorHeadingFormatting: {
            fontSize: 12,
            fontName: "Times New Roman",
            bold: true,
            underline: true,
            lineSpacing: 12 * 240,  // 12pt on caption page
            spacing: { before: 0, after: 120 },  // 1 blank line
            alignment: "center",
            indent: 0
        },

        // REQUEST/RESPONSE HEADINGS (left-justified, bold, underline)
        requestResponseHeadingFormatting: {
            fontSize: 12,
            fontName: "Times New Roman",
            bold: true,
            underline: true,
            lineSpacing: 24 * 240,  // 24pt on body pages
            spacing: { before: 0, after: 120 },  // 1 blank line
            alignment: "left",
            indent: 0
        },

        // SIGNATURE BLOCK: 12pt spacing, no indent
        signatureBlockFormatting: {
            fontSize: 12,
            fontName: "Times New Roman",
            bold: false,
            underline: false,
            lineSpacing: 12 * 240,  // 12pt
            spacing: { before: 0, after: 0 },
            alignment: "left",
            indent: 0
        },

        rules: [
            "Caption Page (Page 1): 12pt line spacing, no indent",
            "Body Pages: 24pt line spacing, 0.5in first-line indent",
            "Major Section Headings: Bold, Underline, Centered",
            "Request/Response Headings: Bold, Underline, Left-justified",
            "Font: Times New Roman 12pt throughout",
            "Margins: 1.0in all sides",
            "Signature block: 12pt spacing",
            "Proof of Service: 12pt spacing",
            "Objections: 24pt line spacing with 0.5in indent"
        ]
    },

    ca_pleading: {
        name: "California Pleading",
        description: "California pleading paper formatting (complaints, answers, motions)",

        margins: {
            top: 1440,      // 1 inch
            bottom: 1440,
            left: 1440,
            right: 1440
        },

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
            lineSpacing: 2.0,      // Double spacing
            spacing: { before: 0, after: 0 },
            alignment: "left",
            indent: {
                firstLine: 720,     // 0.5 inch first line indent
                hanging: 0
            }
        },

        rules: [
            "Pleading paper with numbered lines required",
            "Double spacing mandatory",
            "0.5 inch first line indent for paragraphs",
            "1 inch all margins",
            "Main headings bold and underlined",
            "Numbered paragraphs required",
            "Times New Roman 12pt font",
            "Page numbering in footer"
        ]
    },

    contract: {
        name: "Generic Contract",
        description: "Professional contract formatting",

        margins: {
            top: 1440,
            bottom: 1440,
            left: 1440,
            right: 1440
        },

        headingFormatting: {
            level1: {
                fontSize: 12,
                bold: true,
                underline: true,
                fontName: "Arial",
                spacing: { before: 120, after: 60 },
                alignment: "left"
            }
        },

        bodyFormatting: {
            fontSize: 11,
            fontName: "Arial",
            lineSpacing: 1.5,
            spacing: { before: 0, after: 0 },
            alignment: "left",
            indent: {
                firstLine: 0,
                hanging: 0
            }
        },

        rules: [
            "Arial 11pt font for modern look",
            "1.5 line spacing",
            "1 inch all margins",
            "Bold and underlined section headers",
            "Capitalized defined terms"
        ]
    }
};

module.exports = TEMPLATES;

