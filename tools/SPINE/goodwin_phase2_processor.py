#!/usr/bin/env python3
"""
Phase 2: Comprehensive Case Document Processor
Extracts settlement statements AND medical records for complete case profiles
"""

import pdfplumber
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime

class GoodwinCaseProcessor:
    """Process Penney Goodwin's complete case including settlement statement and medical records"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.full_text = ""
        self.pages = []
        
    def extract_all_text(self) -> str:
        """Extract all text from PDF"""
        with pdfplumber.open(self.pdf_path) as pdf:
            self.pages = pdf.pages
            self.full_text = "\n\n".join([page.extract_text() for page in pdf.pages])
        return self.full_text
    
    def get_settlement_statement(self) -> str:
        """Get just the settlement statement section (before EXHIBIT A)"""
        exhibit_idx = self.full_text.find("EXHIBIT A")
        if exhibit_idx < 0:
            return self.full_text
        return self.full_text[:exhibit_idx]
    
    def get_medical_records(self) -> str:
        """Get medical records section (after EXHIBIT A)"""
        exhibit_idx = self.full_text.find("EXHIBIT A")
        if exhibit_idx < 0:
            return ""
        return self.full_text[exhibit_idx:]
    
    def extract_case_info(self) -> Dict[str, Any]:
        """Extract basic case information from settlement statement"""
        stmt = self.get_settlement_statement()
        
        info = {
            "plaintiff_name": None,
            "case_number": None,
            "age": None,
            "location": None,
            "implant_date": None,
            "implant_type": None,
            "injury_summary": None,
            "total_demanded": None,
        }
        
        # Extract plaintiff name
        name_match = re.search(r"This Document Relates to Plaintiff:\s*([^\n]+)", stmt)
        if name_match:
            info["plaintiff_name"] = name_match.group(1).strip()
        
        # Extract case number
        case_match = re.search(r"Case No:\s*([^\n]+)", stmt)
        if case_match:
            info["case_number"] = case_match.group(1).strip()
        
        # Extract age
        age_match = re.search(r"(\d+)-year-old\s+woman", stmt, re.IGNORECASE)
        if age_match:
            info["age"] = int(age_match.group(1))
        
        # Extract location
        location_match = re.search(r"living in\s+([^,]+),\s+([A-Z]{2})", stmt)
        if location_match:
            info["location"] = f"{location_match.group(1)}, {location_match.group(2)}"
        
        # Extract implant date
        implant_match = re.search(r"received a\s+Cook\s+(\w+)\s+filter\s+on\s+([A-Za-z]+\s+\d+,\s+\d{4})", stmt)
        if implant_match:
            info["implant_type"] = implant_match.group(1)
            info["implant_date"] = implant_match.group(2)
        
        # Extract injury summary (first paragraph after filing)
        injury_match = re.search(r"Since the filter implantation, Plaintiff has experienced\s+([^.]+\.[^.]+\.)", stmt)
        if injury_match:
            info["injury_summary"] = injury_match.group(1).strip()
        
        # Extract total settlement
        total_match = re.search(r"Total[:\s]+\$\s*([\d,]+)", stmt)
        if total_match:
            info["total_demanded"] = int(total_match.group(1).replace(",", ""))
        
        return info
    
    def extract_damages_breakdown(self) -> List[Dict[str, Any]]:
        """Extract itemized damages from settlement statement"""
        stmt = self.get_settlement_statement()
        
        damages = []
        
        # Find damages section
        damages_idx = stmt.find("following values represent")
        if damages_idx < 0:
            return damages
        
        damages_section = stmt[damages_idx:damages_idx+2000]
        
        # Extract each line item (Injury/Defect Amount pairs)
        # Pattern: line item description followed by $ amount
        lines = damages_section.split("\n")
        
        current_item = ""
        for line in lines:
            line = line.strip()
            if not line or "Total" in line or "following" in line:
                continue
            
            # Check if line ends with a dollar amount
            amount_match = re.search(r"\$\s*([\d,]+)", line)
            if amount_match:
                # Extract the description (everything before the $)
                description = re.sub(r"\$.*", "", line).strip()
                amount = int(amount_match.group(1).replace(",", ""))
                
                damages.append({
                    "description": description,
                    "amount": amount
                })
        
        return damages
    
    def extract_medical_history(self) -> Dict[str, Any]:
        """Extract patient demographics and admission info from medical records"""
        med_records = self.get_medical_records()
        
        history = {
            "patient_name": None,
            "dob": None,
            "age_at_admission": None,
            "sex": None,
            "mrn": None,
            "account_number": None,
            "facility_name": None,
            "facility_phone": None,
            "admit_date": None,
            "discharge_date": None,
            "physician": None,
            "diagnoses": [],
            "procedures": [],
        }
        
        # Extract patient name
        name_match = re.search(r"NAME:\s*([^\n]+?)(?:\s+DOB|\n)", med_records)
        if name_match:
            history["patient_name"] = name_match.group(1).strip()
        
        # Extract DOB
        dob_match = re.search(r"DOB:\s*(\d+/\d+/\d+)", med_records)
        if dob_match:
            history["dob"] = dob_match.group(1)
        
        # Extract age at admission
        age_match = re.search(r"Age:\s*(\d+)\s*years", med_records)
        if age_match:
            history["age_at_admission"] = int(age_match.group(1))
        
        # Extract sex
        sex_match = re.search(r"Sex:\s*([MFmf])", med_records)
        if sex_match:
            history["sex"] = sex_match.group(1).upper()
        
        # Extract MRN
        mrn_match = re.search(r"MRN:\s*([^\n]+)", med_records)
        if mrn_match:
            history["mrn"] = mrn_match.group(1).strip()
        
        # Extract facility name
        facility_match = re.search(r"([A-Z][^\n]*Medical Center)[^\n]*\n.*?(\d+)", med_records)
        if facility_match:
            history["facility_name"] = facility_match.group(1).strip()
        
        # Extract admit/discharge dates
        admit_match = re.search(r"Admit Date:\s*(\d+/\d+/\d+)", med_records)
        if admit_match:
            history["admit_date"] = admit_match.group(1)
        
        disch_match = re.search(r"Disch Date:\s*(\d+/\d+/\d+)", med_records)
        if disch_match:
            history["discharge_date"] = disch_match.group(1)
        
        # Extract attending physician
        physician_match = re.search(r"Physician:\s*([^\n]+)", med_records)
        if physician_match:
            history["physician"] = physician_match.group(1).strip()
        
        return history
    
    def generate_comprehensive_summary(self) -> str:
        """Generate complete case summary combining settlement and medical info"""
        case_info = self.extract_case_info()
        damages = self.extract_damages_breakdown()
        med_history = self.extract_medical_history()
        
        settlement_amt = f"${case_info['total_demanded']:,}" if case_info['total_demanded'] else "Not found"
        injury_desc = case_info['injury_summary'] or "Not found"
        
        summary = f"""
COMPREHENSIVE CASE SUMMARY: {case_info['plaintiff_name']}
{'='*80}

CASE INFORMATION:
  Case Number: {case_info['case_number']}
  Age: {case_info['age']} years old
  Location: {case_info['location']}
  Filter Type: {case_info['implant_type']}
  Implant Date: {case_info['implant_date']}
  Settlement Amount: {settlement_amt}

INJURIES ALLEGED:
  {injury_desc}

DAMAGES BREAKDOWN:
"""
        for item in damages:
            summary += f"  - {item['description']}: ${item['amount']:,}\n"
        
        summary += f"""
MEDICAL RECORDS INFORMATION:
  Patient Name: {med_history['patient_name']}
  DOB: {med_history['dob']}
  Sex: {med_history['sex']}
  MRN: {med_history['mrn']}
  
  Admission Details:
    Facility: {med_history['facility_name']}
    Admit Date: {med_history['admit_date']}
    Discharge Date: {med_history['discharge_date']}
    Attending Physician: {med_history['physician']}

NEXT STEPS FOR PHASE 2:
  - Extract detailed treatment timeline
  - Identify all procedures performed
  - Extract imaging findings and test results
  - Cross-validate settlement claims against medical records
  - OCR and process any scanned documents
"""
        
        return summary


if __name__ == "__main__":
    processor = GoodwinCaseProcessor("Raw_Data_Docs/17-cv-02775 - GoodwinConfSettlementStmt.pdf")
    processor.extract_all_text()
    
    print(processor.generate_comprehensive_summary())
    
    # Also save structured data
    print("\n\nSTRUCTURED DATA:")
    print("Case Info:", processor.extract_case_info())
    print("\nDamages:")
    for item in processor.extract_damages_breakdown():
        print(f"  {item}")
    print("\nMedical History:", processor.extract_medical_history())
