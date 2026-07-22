/**
 * Legal Document Formatting Templates
 * Based on California pleading standards and actual court-filed documents
 */

const TEMPLATES = {
    ca_discovery: {
        name: "California Discovery",
        description: "California discovery document formatting (interrogatories, requests, admissions)",

        // Margins from Cho v. Mobilitas document
        margins: {
            top: 1152,      // 0.80 inches in twips
            bottom: 1440,   // 1.0 inch (set negative to -1360 for special formatting)
            left: 1620,     // 1.12 inches
            right: 1440     // 1.0 inch
        },

        // Attorney header formatting
        headerFormatting: {
            fontSize: 12,
            fontName: "Times New Roman",
            bold: false,
            spacing: { before: 0, after: 0 }
        },

        // Case caption formatting
        captionFormatting: {
            fontSize: 12,
            fontName: "Times New Roman",
            bold: false,
            lineSpacing: 1.5,
            spacing: { before: 240, after: 120 }
        },

        // Request/Question heading formatting
        headingFormatting: {
            level1: {
                fontSize: 12,
                bold: true,
                fontName: "Times New Roman",
                underline: false,
                spacing: { before: 120, after: 60 },
                alignment: "left"
            },
            level2: {
                fontSize: 12,
                bold: false,
                fontName: "Times New Roman",
                spacing: { before: 60, after: 60 },
                alignment: "left"
            }
        },

        // Response text formatting
        bodyFormatting: {
            fontSize: 12,
            fontName: "Times New Roman",
            lineSpacing: 1.0,
            spacing: { before: 0, after: 0 },
            alignment: "left",
            indent: {
                firstLine: 0,
                hanging: 0
            }
        },

        // Table formatting for case caption
        tableFormatting: {
            borders: true,
            cellSpacing: 0,
            fontSize: 12,
            fontName: "Times New Roman"
        },

        rules: [
            "Discovery set number must be clearly identified",
            "Each request followed by specific response",
            "Margins: 0.8\" top, 1.12\" left, 1.0\" right",
            "Font must be Times New Roman 12pt",
            "Single spacing for body text",
            "Use REQUEST FOR [TYPE] NO. [#] format",
            "Use RESPONSE TO REQUEST format",
            "Include objections and grounds if applicable"
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

