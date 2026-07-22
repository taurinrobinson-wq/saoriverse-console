/**
 * Task Pane Script
 * Handles UI interactions for Darwin formatter
 */

import { registerFormatHeadingsCommand, formatLegalHeadings } from "../src/commands/formatHeadings";

// Initialize when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  // Register all commands
  registerFormatHeadingsCommand();

  // Attach event listeners
  const formatHeadingsBtn = document.getElementById("formatHeadings");
  if (formatHeadingsBtn) {
    formatHeadingsBtn.onclick = async () => {
      try {
        formatHeadingsBtn.disabled = true;
        formatHeadingsBtn.textContent = "Formatting...";

        await formatLegalHeadings();

        // Show success feedback
        formatHeadingsBtn.textContent = "✓ Done!";
        setTimeout(() => {
          formatHeadingsBtn.textContent = "Format Legal Headings";
          formatHeadingsBtn.disabled = false;
        }, 2000);
      } catch (error) {
        console.error("Error:", error);
        formatHeadingsBtn.textContent = "Error - Try Again";
        formatHeadingsBtn.disabled = false;
      }
    };
  }
});
