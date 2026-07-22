/**
 * Legal Heading Pattern Library
 * Detects all common legal document heading formats
 */

export const HEADING_PATTERNS: RegExp[] = [
  // Discovery headings
  /^Interrogatory\s+No\.\s*\d+/i,
  /^Special\s+Interrogatory\s+No\.\s*\d+/i,
  /^Form\s+Interrogatory\s+No\.\s*\d+/i,
  /^Request\s+for\s+Production\s+No\.\s*\d+/i,
  /^Request\s+for\s+Admission\s+No\.\s*\d+/i,
  /^Topic\s+No\.\s*\d+/i,
  /^Document\s+Request\s+No\.\s*\d+/i,

  // Pleading sections (all caps headings with optional colon)
  /^[A-Z][A-Za-z\s]+:$/,
  /^[A-Z][A-Za-z\s]+$/,
];

/**
 * Identifier for heading detection strategy
 */
export interface HeadingMatch {
  paragraph: any; // Word.Paragraph
  pattern: RegExp;
  text: string;
}
