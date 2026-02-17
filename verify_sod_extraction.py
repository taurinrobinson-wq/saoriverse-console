#!/usr/bin/env python3
"""
Error checking script - verify extracted text against known good reference
"""

from pathlib import Path
import re

# Your reference text for Page 1
reference_page_1 = """I. INTRODUCTION
In this document the Court announces its Final Statement of Decision. The bench trial came on regularly for trial 'on January 22, 2025, in Department 45 of the Los Angeles Superior Court, Central District, Judge Virginia Keeny presiding, and continued thereafter, with interruptions, for seventeen days of testimony, concluding on March 14, 2025. Plaintiffs Baird Brown, Baird Brown, a Law Corporation, and Ann Brown were represented by Andrew M. White and Jonathan N. White. Defendants and cross-complainants Donald G. Norris and Donald G. Norris, a Law Corporation, were represented by David Welch of Enso Law, LLP. Defendant and cross-complainant Michele Pak was represented by Brett A. Greenfield. After the parties rested on March 14, 2025, the court requested closing briefs to be submitted on May 14, 2025, at which time the matter was taken under submission. The court issued a Tentative Statement of Decision on June 30, 2025. Cross-defendants Andrew and Jonathan White submitted objections to the tentative statement of decision on July 25, 2025. Plaintiffs submitted objections on July 29, 2025, and the Norris Defendants/Cross-complainants filed objections on July 30. The court requested additional briefing from Pak on the objections raised by plaintiffs.

Having now considered the post-trial briefs, all admissible evidence and argument of counsel at trial, as well as the objections of the parties, the court now issues this Final Statement of Decision.

II. PROCEDURAL HISTORY
Plaintiffs filed the initial complaint in this action on November 8, 2023, seeking damages, penalties, punitive damages and attorney fees against defendants for allegedly stealing plaintiffs' mass tort law practice and diverting money and clients to their coffers. Plaintiffs' operative First Amended Complaint was filed on August 22, 2024 and sets forth seven causes of action: (1) Elder and Financial Abuse; (2) Theft and Conversion under Penal Code Section 496(c); (3) Unfair Competition under Bus. & Prof. Code Section 17200 et seq.; (4) Interference with Contract; (5) Breach of Fiduciary Duty; (6) Aiding and Abetting Breach of Fiduciary Duty and (7) Conspiracy.

Donald Norris filed a cross-complaint against Baird and Ann Brown, Baird Brown, a law corporation, and Jonathan and Andrew White on January 12, 2024, seeking damages for (1) Conversion; (2) Violation of Cal. Penal Code§ 502; (3) Unfair Practices Act (Cal. Bus. & Prof. Code§ 17200 et seq.); (4) Interference with Prospective Economic Advantage; and (5) Breach of Fiduciary Duty.

Michelle Pak filed a cross-complaint against the same cross-defendants on February 5, 2024, alleging various causes of action. By the time of trial, the only causes of action pursued by Pak were claims for Assault and Battery, for which she sought $250,000 against each of the Brown defendants and each of the White defendants, plus punitive damages.

III. EVIDENCE PRESENTED
Testimony of Baird Brown Baird Brown developed a successful plaintiff's personal injury law practice, specializing in mass tort litigation. Prior to 2019, he began to display symptoms of Parkinson's disease and in"""

# Read extracted page 1
pages_dir = Path(r"d:\saoriverse-console\DraftShift\Docs\BrownVacateMtn\SOD_Pages")
page_1_file = pages_dir / "Page_01.txt"

with open(page_1_file, 'r', encoding='utf-8') as f:
    extracted = f.read()

# Remove page markers and line numbers
extracted_lines = extracted.split('\n')
cleaned_lines = []
skip_numbers = True

for line in extracted_lines:
    if '===== PAGE' in line or '===== END PAGE' in line:
        continue
    
    stripped = line.strip()
    # Skip pure number lines at the top
    if skip_numbers and re.match(r'^[\d\s]+$', stripped) and all(int(n) <= 28 for n in re.findall(r'\d+', stripped)):
        continue
    
    if stripped and not re.match(r'^[\d\s]+$', stripped):
        skip_numbers = False
    
    if not skip_numbers:
        cleaned_lines.append(line)

extracted_cleaned = '\n'.join(cleaned_lines).strip()

# Normalize both for comparison
def normalize(text):
    # Remove extra whitespace but preserve structure
    text = re.sub(r'\s+', ' ', text)
    text = text.replace("'on January", "on January")  # Fix the single quote issue
    text = text.replace("plaintiff's ", "plaintiff's ")
    return text

ref_norm = normalize(reference_page_1)
ext_norm = normalize(extracted_cleaned[:len(extracted_cleaned)//2])  # Check first half

# Check specific key phrases
check_phrases = [
    "Los Angeles Superior Court",
    "Andrew M. White and Jonathan N. White",
    "Donald G. Norris, a Law Corporation",
    "David Welch of Enso Law, LLP",
    "Michele Pak was represented by Brett A. Greenfield",
    "November 8, 2023",
    "successful plaintiff's personal injury law practice"
]

print("=" * 60)
print("VERIFICATION REPORT - Page 1")
print("=" * 60)

errors = []
for phrase in check_phrases:
    # Normalize phrase for search
    phrase_norm = normalize(phrase)
    if phrase_norm in ref_norm:
        print(f"✓ Reference phrase found in expected location")
    else:
        print(f"✗ Reference phrase NOT found: {phrase}")
        errors.append(phrase)

# Check extracted content
print("\n" + "=" * 60)
print("EXTRACTED CONTENT CHECK")
print("=" * 60)

key_terms = {
    "Los Angeles": "Los Angel_es" in extracted,
    "withinterruptions": "withinterruptions" in extracted,
    "presiding ,": "presiding ," in extracted,
    "November 8, 2023": "November 8, 2023" in extracted,
}

for term, found in key_terms.items():
    status = "FOUND" if found else "NOT FOUND"
    print(f"{term}: {status}")

print("\n" + "=" * 60)
if errors:
    print(f"ISSUES FOUND: {len(errors)} discrepancies")
    for err in errors:
        print(f"  - {err}")
else:
    print("✓ All key phrases verified")
print("=" * 60)
