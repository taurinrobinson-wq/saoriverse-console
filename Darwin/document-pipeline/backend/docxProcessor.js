/**
 * DOCX Document Processor
 * Handles parsing, analyzing, and reformatting Word documents
 */

const { Document, Packer, Paragraph, TextRun, UnderlineType, AlignmentType } = require("docx");
const TEMPLATES = require("./templates");
const HEADING_PATTERNS = require("./headingPatterns");

class DocxProcessor {
    constructor() {
        this.document = null;
        this.analysis = null;
    }

    /**
     * Analyze a Word document and extract formatting information
     */
    analyzeDocument(wordDocument) {
        this.document = wordDocument;

        const analysis = {
            totalParagraphs: wordDocument.body.length,
            headingsDetected: [],
            bodyText: [],
            formattingIssues: [],
            currentFormatting: {}
        };

        wordDocument.body.forEach((element, index) => {
            if (element.children) {
                const text = element.children.map(child => child.text || "").join("");

                // Detect headings using patterns
                for (const pattern of HEADING_PATTERNS) {
                    if (pattern.regex.test(text)) {
                        analysis.headingsDetected.push({
                            index,
                            text: text.trim(),
                            type: pattern.name,
                            originalFormatting: this.getElementFormatting(element)
                        });
                        break;
                    }
                }

                // Track body text
                if (text.trim().length > 0) {
                    analysis.bodyText.push({
                        index,
                        text: text.substring(0, 100),
                        formatting: this.getElementFormatting(element)
                    });
                }
            }
        });

        this.analysis = analysis;
        return analysis;
    }

    /**
     * Extract formatting from a document element
     */
    getElementFormatting(element) {
        const formatting = {
            fontSize: element.properties?.run?.size || 24, // Default 12pt (in half-points)
            bold: element.properties?.run?.bold || false,
            italic: element.properties?.run?.italics || false,
            underline: element.properties?.run?.underline || false,
            fontName: element.properties?.run?.font || "Unknown"
        };
        return formatting;
    }

    /**
     * Reformat document according to template
     */
    reformatDocument(wordDocument, templateName) {
        const template = TEMPLATES[templateName];
        if (!template) {
            throw new Error(`Template not found: ${templateName}`);
        }

        // Create new document with reformatted content
        const reformattedParagraphs = [];

        wordDocument.body.forEach((element) => {
            if (!element.children) return;

            const text = element.children.map(child => child.text || "").join("");
            if (text.trim().length === 0) {
                // Preserve empty paragraphs
                reformattedParagraphs.push(new Paragraph({ text: "" }));
                return;
            }

            // Check if this is a heading
            let isHeading = false;
            for (const pattern of HEADING_PATTERNS) {
                if (pattern.regex.test(text)) {
                    // Apply heading formatting
                    const headingFormat = template.headingFormatting.level1;
                    reformattedParagraphs.push(
                        new Paragraph({
                            text: text.trim(),
                            spacing: headingFormat.spacing,
                            alignment: this.mapAlignment(headingFormat.alignment),
                            children: [
                                new TextRun({
                                    text: text.trim(),
                                    bold: headingFormat.bold,
                                    underline: headingFormat.underline ? { type: UnderlineType.SINGLE } : undefined,
                                    size: headingFormat.fontSize * 2, // Convert to half-points
                                    font: headingFormat.fontName
                                })
                            ]
                        })
                    );
                    isHeading = true;
                    break;
                }
            }

            // If not a heading, apply body text formatting
            if (!isHeading) {
                const bodyFormat = template.bodyFormatting;
                reformattedParagraphs.push(
                    new Paragraph({
                        text: text.trim(),
                        spacing: bodyFormat.spacing,
                        alignment: this.mapAlignment(bodyFormat.alignment),
                        indent: {
                            firstLine: bodyFormat.indent.firstLine,
                            hanging: bodyFormat.indent.hanging
                        },
                        children: [
                            new TextRun({
                                text: text.trim(),
                                bold: false,
                                size: bodyFormat.fontSize * 2,
                                font: bodyFormat.fontName
                            })
                        ]
                    })
                );
            }
        });

        // Create new document with reformatted content
        const newDocument = new Document({
            sections: [
                {
                    properties: {
                        page: {
                            margins: {
                                top: template.margins.top,
                                bottom: template.margins.bottom,
                                left: template.margins.left,
                                right: template.margins.right
                            }
                        }
                    },
                    children: reformattedParagraphs
                }
            ]
        });

        return newDocument;
    }

    /**
     * Map alignment string to docx AlignmentType
     */
    mapAlignment(alignment) {
        const alignmentMap = {
            left: AlignmentType.LEFT,
            center: AlignmentType.CENTER,
            right: AlignmentType.RIGHT,
            justify: AlignmentType.JUSTIFIED
        };
        return alignmentMap[alignment] || AlignmentType.LEFT;
    }

    /**
     * Generate formatting report
     */
    generateReport() {
        if (!this.analysis) {
            return { error: "No document analyzed" };
        }

        const report = {
            documentStats: {
                totalParagraphs: this.analysis.totalParagraphs,
                headingsFound: this.analysis.headingsDetected.length,
                bodyTextParagraphs: this.analysis.bodyText.length
            },
            detectedHeadings: this.analysis.headingsDetected.map(h => ({
                text: h.text,
                type: h.type,
                formatting: h.originalFormatting
            })),
            formattingIssues: this.identifyFormattingIssues(),
            recommendations: this.generateRecommendations()
        };

        return report;
    }

    /**
     * Identify formatting issues
     */
    identifyFormattingIssues() {
        const issues = [];

        this.analysis.bodyText.forEach((para, idx) => {
            // Check for inconsistent font sizes
            if (para.formatting.fontSize < 22) { // Less than 11pt
                issues.push({
                    type: "Small font",
                    paragraph: idx,
                    issue: `Font size ${para.formatting.fontSize / 2}pt is too small. Recommend 12pt minimum.`
                });
            }

            // Check for non-standard fonts
            if (!["Times New Roman", "Arial", "Calibri"].includes(para.formatting.fontName)) {
                issues.push({
                    type: "Non-standard font",
                    paragraph: idx,
                    issue: `Font "${para.formatting.fontName}" is non-standard. Use Times New Roman or Arial.`
                });
            }
        });

        return issues;
    }

    /**
     * Generate recommendations based on analysis
     */
    generateRecommendations() {
        const recommendations = [];

        if (this.analysis.headingsDetected.length === 0) {
            recommendations.push("No structured headings detected. Consider adding section headings for clarity.");
        }

        if (this.analysis.formattingIssues.length > 0) {
            recommendations.push(`Found ${this.analysis.formattingIssues.length} formatting issues that can be corrected.`);
        }

        recommendations.push(
            "Recommend using 'California Pleading' template for legal documents to ensure court compliance."
        );

        return recommendations;
    }
}

module.exports = DocxProcessor;
