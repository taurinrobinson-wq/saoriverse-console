/**
 * Legal Document Formatting Templates
 * Based on ACTUAL court-filed documents (Cho v. Mobilitas RFA Response)
 */

const TEMPLATES = {
    ca_discovery: {
        name: "California Discovery",
        description: "California discovery document formatting (interrogatories, requests, admissions)",

        // Margins from properly formatted Cho v. Mobilitas document
        margins: {
            top: 1152,      // 0.80 inches in twips
            bottom: 1440,   // 1.0 inch
            left: 1620,     // 1.12 inches
            right: 1440     // 1.0 inch
        },
        
        // Attorney header formatting (name, firm, contact info)
        headerFormatting: {
            fontSize: 12,
            fontName: "Times New Roman",
            bold: false,
            spacing: { before: 0, after: 0 }
        },
        
        // Case caption formatting (ASKING PARTY, RESPONDING PARTY, SET NUMBER)
        captionFormatting: {
            fontSize: 12,
            fontName: "Times New Roman",
            bold: true,
            underline: false,
            lineSpacing: 2.54,      // 304800 twips - nearly triple spacing
            spacing: { before: 0, after: 0 }
        },
        
        // Request/Response heading formatting (REQUEST FOR ADMISSIONS NO. X)
        headingFormatting: {
            level1: {
                fontSize: 12,
                bold: true,
                underline: true,    // ALL HEADINGS UNDERLINED in formatted doc
                fontName: "Times New Roman",
                lineSpacing: 2.54,  // 304800 twips
                spacing: { before: 120, after: 60 },
                alignment: "left"
            },
            level2: {
                fontSize: 12,
                bold: true,
                underline: true,    // Response headings also underlined
                fontName: "Times New Roman",
                lineSpacing: 2.54,
                spacing: { before: 60, after: 60 },
                alignment: "left"
            }
        },
        
        // Request/Response body text formatting
        bodyFormatting: {
            fontSize: 12,
            fontName: "Times New Roman",
            lineSpacing: 2.54,     // 304800 twips - nearly triple-spaced
            spacing: { before: 0, after: 0 },
            alignment: "left",
            indent: {
                firstLine: 457200,   // 3.825 inches - LARGE indent on questions
                hanging: 0
            }
        },
        
        // Introductory text (preamble, "Pursuant to Code of Civil Procedure...")
        preambleFormatting: {
            fontSize: 12,
            fontName: "Times New Roman",
            lineSpacing: 2.54,
            spacing: { before: 0, after: 0 },
            alignment: "left",
            indent: {
                firstLine: 457200,   // Same large indent as body text
                hanging: 0
            }
        },
        
        rules: [
            "Line spacing: 2.54x (304800 twips) - nearly triple-spaced",
            "All REQUEST and RESPONSE headings: BOLD + UNDERLINED",
            "First-line indent on questions/responses: 3.825 inches (457200 twips)",
            "Margins: 0.80\" top, 1.12\" left, 1.0\" right",
            "Font: Times New Roman 12pt throughout",
            "Request/Response pairs properly formatted",
            "Bold labels in caption (ASKING PARTY, RESPONDING PARTY, SET NUMBER)",
            "Include objections and legal grounds as applicable",
            "Preamble text uses same large first-line indent"
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

