/**
 * Legal Heading Detector
 * Identifies all legal headings in a document
 */

import { HEADING_PATTERNS, HeadingMatch } from "./headingPatterns";

/**
 * Find all legal headings in document paragraphs
 * @param paragraphs - Array of Word paragraphs to search
 * @returns Array of paragraphs that match heading patterns
 */
export function findLegalHeadings(paragraphs: any[]): any[] {
  return paragraphs.filter(p => {
    const text = p.text.trim();
    return HEADING_PATTERNS.some(pattern => pattern.test(text));
  });
}

/**
 * Find legal headings with pattern metadata
 * @param paragraphs - Array of Word paragraphs to search
 * @returns Array of heading matches with pattern information
 */
export function findLegalHeadingsWithMetadata(paragraphs: any[]): HeadingMatch[] {
  const matches: HeadingMatch[] = [];

  paragraphs.forEach(p => {
    const text = p.text.trim();
    const matchedPattern = HEADING_PATTERNS.find(pattern => pattern.test(text));

    if (matchedPattern) {
      matches.push({
        paragraph: p,
        pattern: matchedPattern,
        text: text,
      });
    }
  });

  return matches;
}
