/**
 * Format Legal Headings Command
 * Main entry point for the legal heading formatter
 * Wires together detection and formatting logic
 */

import { findLegalHeadings } from "../utils/findHeadings";
import { underlineHeadings } from "./underlineHeadings";

/**
 * Main command: Format all legal headings in document
 * This is the single-click formatter for Darwin v1
 */
export async function formatLegalHeadings(): Promise<void> {
  console.log("Format Legal Headings command executed");
  // Word integration will be added in next phase
}

/**
 * Register the format headings command
 * This should be called during add-in initialization
 */
export function registerFormatHeadingsCommand(): void {
  console.log("Format headings command registered");
  // Office.js integration will be added in next phase
}
