/**
 * Underline Formatter
 * Applies underline formatting to legal headings
 */

/**
 * Apply single underline to all heading paragraphs
 * Preserves all other formatting and text content
 * @param headings - Array of heading paragraphs to underline
 */
export function underlineHeadings(headings: any[]): void {
  headings.forEach(heading => {
    heading.font.underline = "Single";
  });
}

/**
 * Apply underline with additional formatting
 * @param headings - Array of heading paragraphs
 * @param options - Optional formatting options
 */
export interface UnderlineOptions {
  bold?: boolean;
  italic?: boolean;
  fontSize?: number;
  color?: string;
}

export function underlineHeadingsWithOptions(
  headings: any[],
  options?: UnderlineOptions
): void {
  headings.forEach(heading => {
    // Always apply underline
    heading.font.underline = "Single";

    // Apply optional formatting if specified
    if (options?.bold) {
      heading.font.bold = true;
    }
    if (options?.italic) {
      heading.font.italic = true;
    }
    if (options?.fontSize) {
      heading.font.size = options.fontSize;
    }
    if (options?.color) {
      heading.font.color = options.color;
    }
  });
}

/**
 * Remove underline from headings
 * @param headings - Array of heading paragraphs to remove underline from
 */
export function removeUnderlineFromHeadings(headings: any[]): void {
  headings.forEach(heading => {
    heading.font.underline = "None";
  });
}
