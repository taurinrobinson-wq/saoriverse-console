/**
 * Legal Heading Detection Patterns
 * Reused from Darwin v1 formatter
 */

const HEADING_PATTERNS = [
    {
        name: "Interrogatory",
        regex: /^Interrogatory\s+No\.\s*\d+/i
    },
    {
        name: "Special Interrogatory",
        regex: /^Special\s+Interrogatory\s+No\.\s*\d+/i
    },
    {
        name: "Form Interrogatory",
        regex: /^Form\s+Interrogatory\s+No\.\s*\d+/i
    },
    {
        name: "Request for Production",
        regex: /^Request\s+(?:for\s+)?Production\s+(?:of\s+)?(?:Documents\s+)?No\.\s*\d+/i
    },
    {
        name: "Request for Admission",
        regex: /^Request\s+for\s+Admission\s+No\.\s*\d+/i
    },
    {
        name: "Topic Section",
        regex: /^Topic\s+\d+[:\.\s]/i
    },
    {
        name: "Document Request",
        regex: /^Document\s+Request\s+No\.\s*\d+/i
    },
    {
        name: "ALL CAPS Section",
        regex: /^[A-Z][A-Z\s]{5,}[A-Z]$/
    }
];

module.exports = HEADING_PATTERNS;
