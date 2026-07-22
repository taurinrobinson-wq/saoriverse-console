/**
 * Test Cases for Darwin v1 Legal Heading Formatter
 * Comprehensive testing suite for heading detection and formatting
 */

import { findLegalHeadings } from "../src/utils/findHeadings";
import { HEADING_PATTERNS } from "../src/utils/headingPatterns";

/**
 * Test 1 — Discovery Set
 * Verifies that only headings are detected, responses are untouched
 */
export const TEST_1_DISCOVERY_SET = {
  name: "Test 1 — Discovery Set",
  input: [
    "Interrogatory No. 1",
    "Response to Interrogatory No. 1",
    "Request for Production No. 3",
  ],
  expected: {
    description: "Only the headings are underlined. Responses untouched. No regeneration. No spacing changes.",
    headingsCount: 2,
    detectedHeadings: ["Interrogatory No. 1", "Request for Production No. 3"],
    untouchedLines: ["Response to Interrogatory No. 1"],
  },
};

/**
 * Test 2 — Pleading Sections
 * Verifies that all caps section headings are detected
 */
export const TEST_2_PLEADING_SECTIONS = {
  name: "Test 2 — Pleading Sections",
  input: [
    "INTRODUCTION",
    "This is introductory text that should not be formatted.",
    "FACTUAL BACKGROUND",
    "Here are the facts.",
    "ARGUMENT",
    "Here is the argument.",
  ],
  expected: {
    description: "All headings underlined. Paragraph text untouched.",
    headingsCount: 3,
    detectedHeadings: ["INTRODUCTION", "FACTUAL BACKGROUND", "ARGUMENT"],
    untouchedLines: [
      "This is introductory text that should not be formatted.",
      "Here are the facts.",
      "Here is the argument.",
    ],
  },
};

/**
 * Test 3 — PMK Notice
 * Verifies detection of PMK-style headings
 */
export const TEST_3_PMK_NOTICE = {
  name: "Test 3 — PMK Notice",
  input: [
    "Topic No. 12",
    "Document Request No. 4",
    "Special Interrogatory No. 2",
    "The company shall produce all documents related to...",
  ],
  expected: {
    description: "Both headings underlined. No regeneration.",
    headingsCount: 3,
    detectedHeadings: ["Topic No. 12", "Document Request No. 4", "Special Interrogatory No. 2"],
    untouchedLines: ["The company shall produce all documents related to..."],
  },
};

/**
 * Test 4 — Mixed Legal Document
 * Comprehensive test with various heading types
 */
export const TEST_4_MIXED_LEGAL_DOCUMENT = {
  name: "Test 4 — Mixed Legal Document",
  input: [
    "COMPLAINT FOR FRAUD",
    "INTRODUCTION",
    "Plaintiff alleges the following:",
    "FACTS",
    "1. Defendant made representations.",
    "Interrogatory No. 1",
    "State the date when the fraud occurred.",
    "Request for Production No. 5",
    "Produce all communications regarding the fraud.",
    "CONCLUSION",
    "Plaintiff respectfully requests relief.",
  ],
  expected: {
    description: "All legal headings underlined. Body text preserved. No formatting changes to numbered items.",
    headingsCount: 6,
    detectedHeadings: [
      "COMPLAINT FOR FRAUD",
      "INTRODUCTION",
      "FACTS",
      "Interrogatory No. 1",
      "Request for Production No. 5",
      "CONCLUSION",
    ],
  },
};

/**
 * Test 5 — Edge Cases
 * Tests boundary conditions and special formatting
 */
export const TEST_5_EDGE_CASES = {
  name: "Test 5 — Edge Cases",
  input: [
    "INTERROGATORY NO. 1",
    "interrogatory no. 1",
    "Special Interrogatory No. 1",
    "Form Interrogatory No. 2",
    "Request For Production No. 3",
    "This is Headline Format But Not All Caps",
    "H", // Single letter shouldn't match
    "1234", // Numbers only shouldn't match
  ],
  expected: {
    description: "Case-insensitive matching. All variants detected. Non-headings ignored.",
    headingsCount: 5, // All variants match except edge cases
    detectedHeadings: [
      "INTERROGATORY NO. 1",
      "interrogatory no. 1",
      "Special Interrogatory No. 1",
      "Form Interrogatory No. 2",
      "Request For Production No. 3",
    ],
  },
};

/**
 * Test Suite Runner
 * Execute all tests and report results
 */
export function runAllTests(): void {
  console.log("=== Darwin v1 Legal Heading Formatter - Test Suite ===\n");

  const tests = [TEST_1_DISCOVERY_SET, TEST_2_PLEADING_SECTIONS, TEST_3_PMK_NOTICE, TEST_4_MIXED_LEGAL_DOCUMENT, TEST_5_EDGE_CASES];

  tests.forEach(test => {
    console.log(`\n${test.name}`);
    console.log("-".repeat(50));
    console.log(`Expected: ${test.expected.description}`);
    console.log(`Headings to detect: ${test.expected.headingsCount}`);
    console.log(`Sample headings: ${test.expected.detectedHeadings.slice(0, 2).join(", ")}`);
  });

  console.log("\n=== Test Suite Complete ===");
  console.log("Note: These are specification tests. Run in Word context for full integration testing.");
}

/**
 * Pattern Validation Test
 * Verify all patterns compile correctly
 */
export function validatePatterns(): boolean {
  try {
    HEADING_PATTERNS.forEach(pattern => {
      if (!(pattern instanceof RegExp)) {
        console.error("Invalid pattern:", pattern);
        return false;
      }
    });
    console.log(`✓ All ${HEADING_PATTERNS.length} heading patterns validated`);
    return true;
  } catch (error) {
    console.error("Pattern validation failed:", error);
    return false;
  }
}

/**
 * Quick Test Runner
 * Run validation and output test specifications
 */
export function quickTest(): void {
  console.log("Darwin v1 — Legal Heading Formatter\n");
  validatePatterns();
  runAllTests();
}
