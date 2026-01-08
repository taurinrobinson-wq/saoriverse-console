"""
ARX Data Anonymization Integration

Implements k-anonymity verification for stored conversation data.
Ensures no group of users can be uniquely identified by quasi-identifiers.

ARX API: https://api.arx.deidentifier.org/v1
"""

import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class ARXAnonymityVerifier:
    """
    Verifies k-anonymity of conversation data using ARX API.
    
    K-anonymity principle: No group of users can be uniquely identified
    by the combination of quasi-identifiers (hashable characteristics).
    """
    
    def __init__(
        self,
        arx_api_endpoint: str = "https://api.arx.deidentifier.org/v1",
        k_threshold: int = 5,
        config_path: str = "emotional_os/privacy/anonymization_config.json"
    ):
        """Initialize ARX verifier.
        
        Args:
            arx_api_endpoint: ARX API base URL
            k_threshold: Minimum k value required for compliance (default 5 = no group smaller than 5)
            config_path: Path to anonymization configuration
        """
        self.api_endpoint = arx_api_endpoint
        self.k_threshold = k_threshold
        self.config = self._load_config(config_path)
    
    def _load_config(self, config_path: str) -> Dict:
        """Load anonymization configuration."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load anonymization config: {e}")
            return {}
    
    def prepare_dataset_for_arx(
        self,
        records: List[Dict],
        include_fields: Optional[List[str]] = None
    ) -> Dict:
        """
        Prepare conversation data for ARX analysis.
        
        Extracts only quasi-identifiers and transforms them appropriately.
        
        Args:
            records: List of conversation log records from Supabase
            include_fields: Which fields to include (None = use config defaults)
        
        Returns:
            Dataset formatted for ARX API
        """
        if not records:
            logger.warning("No records provided for ARX analysis")
            return {}
        
        quasi_identifiers = include_fields or [
            "user_id_hashed",
            "timestamp_week",  # Generalized to week-level
            "encoded_signals_category",  # Generalized from specific signals
            "message_length_bucket",
            "response_length_bucket",
            "conversation_turn_bucket",
        ]
        
        # Extract and transform data
        dataset = {
            "data": [],
            "column_definitions": [],
        }
        
        for field in quasi_identifiers:
            dataset["column_definitions"].append({
                "name": field,
                "type": "QUASI_IDENTIFYING_ATTRIBUTE",
                "datatype": "STRING"
            })
        
        # Build data rows
        for record in records:
            row = {}
            for field in quasi_identifiers:
                row[field] = record.get(field, "UNKNOWN")
            dataset["data"].append(row)
        
        return dataset
    
    def send_to_arx_for_analysis(self, dataset: Dict) -> Dict:
        """
        Send dataset to ARX API for k-anonymity analysis.
        
        Args:
            dataset: Prepared dataset with quasi-identifiers
        
        Returns:
            ARX analysis result (k-value, risk assessment, etc.)
        """
        if not dataset or not dataset.get("data"):
            logger.error("Cannot analyze empty dataset")
            return {"error": "empty_dataset", "compliant": False}
        
        try:
            # Prepare ARX request
            payload = {
                "dataset": dataset,
                "privacy_models": [
                    {
                        "type": "K_ANONYMITY",
                        "k": self.k_threshold
                    }
                ]
            }
            
            # Call ARX API
            response = requests.post(
                f"{self.api_endpoint}/analyze",
                json=payload,
                timeout=30,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"ARX analysis complete: k={result.get('k_value')}")
                return result
            else:
                logger.error(f"ARX API error: {response.status_code}")
                return {"error": f"arx_api_error_{response.status_code}"}
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to call ARX API: {e}")
            return {"error": "arx_api_unreachable"}
    
    def verify_compliance(self, analysis_result: Dict) -> Tuple[bool, Dict]:
        """
        Check if analysis result meets k-anonymity threshold.
        
        Args:
            analysis_result: Result from ARX API
        
        Returns:
            (is_compliant, details_dict)
        """
        k_value = analysis_result.get("k_value", 0)
        is_compliant = k_value >= self.k_threshold
        
        details = {
            "k_value": k_value,
            "threshold": self.k_threshold,
            "compliant": is_compliant,
            "timestamp": datetime.now().isoformat(),
            "risk_level": self._assess_risk(k_value),
            "recommendations": self._generate_recommendations(k_value, analysis_result)
        }
        
        if not is_compliant:
            logger.warning(
                f"Data does not meet k-anonymity threshold. "
                f"k={k_value}, required k={self.k_threshold}"
            )
        else:
            logger.info(f"Data meets k-anonymity compliance. k={k_value}")
        
        return is_compliant, details
    
    def _assess_risk(self, k_value: int) -> str:
        """Assess re-identification risk based on k-value."""
        if k_value < 3:
            return "CRITICAL"
        elif k_value < 5:
            return "HIGH"
        elif k_value < 10:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _generate_recommendations(self, k_value: int, result: Dict) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        if k_value < self.k_threshold:
            recommendations.append(
                f"Apply further generalization to quasi-identifiers. "
                f"Current k={k_value}, need k={self.k_threshold}"
            )
            recommendations.append(
                "Consider generalizing timestamp to month-level or broader"
            )
            recommendations.append(
                "Consider merging small signal categories"
            )
        
        suppression_percent = result.get("suppression_needed_percent", 0)
        if suppression_percent > 10:
            recommendations.append(
                f"{suppression_percent}% of records need further generalization"
            )
        
        if not recommendations:
            recommendations.append("Data meets compliance requirements. No changes needed.")
        
        return recommendations
    
    def run_monthly_compliance_check(
        self,
        db_connection,
        sample_size: int = 10000
    ) -> Tuple[bool, Dict]:
        """
        Run monthly k-anonymity compliance check on sampled data.
        
        Args:
            db_connection: Supabase connection
            sample_size: Number of records to sample (10k default)
        
        Returns:
            (is_compliant, report_dict)
        """
        logger.info(f"Starting monthly compliance check (sample size: {sample_size})")
        
        # Sample recent records from last 30 days
        try:
            records = db_connection.table("conversation_logs_anonymized")\
                .select("*")\
                .gte("timestamp", (datetime.now() - timedelta(days=30)).isoformat())\
                .limit(sample_size)\
                .execute()
            
            records_data = records.data if hasattr(records, 'data') else []
            
            if not records_data:
                logger.warning("No records found for compliance check")
                return False, {"error": "no_records", "compliant": False}
            
            # Prepare and analyze
            dataset = self.prepare_dataset_for_arx(records_data)
            analysis = self.send_to_arx_for_analysis(dataset)
            is_compliant, report = self.verify_compliance(analysis)
            
            # Log report
            report["sample_size"] = len(records_data)
            report["check_date"] = datetime.now().isoformat()
            report["next_check_date"] = (datetime.now() + timedelta(days=30)).isoformat()
            
            self._log_compliance_report(report)
            
            return is_compliant, report
        
        except Exception as e:
            logger.error(f"Compliance check failed: {e}")
            return False, {"error": str(e), "compliant": False}
    
    def _log_compliance_report(self, report: Dict) -> None:
        """Store compliance report for audit trail."""
        try:
            log_path = Path("emotional_os/privacy/compliance_reports")
            log_path.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = log_path / f"arx_compliance_{timestamp}.json"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Compliance report saved: {report_file}")
        
        except Exception as e:
            logger.error(f"Failed to save compliance report: {e}")
    
    def get_generalization_hierarchy(self, quasi_identifier: str) -> Dict:
        """
        Get recommended generalization hierarchy for a quasi-identifier.
        
        Example: timestamp can generalize from day → week → month → year
        
        Args:
            quasi_identifier: Name of quasi-identifier field
        
        Returns:
            Hierarchy levels and mapping
        """
        hierarchies = {
            "timestamp": {
                "levels": ["day", "week", "month", "quarter", "year"],
                "current": "day",
                "recommendation": "week"  # Balance between privacy and utility
            },
            "encoded_signals": {
                "levels": ["specific_signal", "signal_category", "signal_domain"],
                "current": "specific_signal",
                "recommendation": "signal_category"
            },
            "message_length": {
                "levels": ["exact", "10_char_bucket", "50_char_bucket", "100_char_bucket"],
                "current": "exact",
                "recommendation": "50_char_bucket"
            },
            "conversation_turn": {
                "levels": ["exact", "pair_bucket", "session_bucket"],
                "current": "exact",
                "recommendation": "pair_bucket"
            }
        }
        
        return hierarchies.get(quasi_identifier, {"error": "unknown_identifier"})


class DataMinimizationEnforcer:
    """
    Enforces data minimization principle.
    Ensures only necessary data is collected and stored.
    """
    
    def __init__(self, config_path: str = "emotional_os/privacy/anonymization_config.json"):
        self.config = self._load_config(config_path)
    
    def _load_config(self, config_path: str) -> Dict:
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
    
    def filter_for_storage(self, raw_data: Dict, context: str) -> Dict:
        """
        Filter data to store only what's necessary for given context.
        
        Args:
            raw_data: Complete data object
            context: "conversation" | "affirmation" | "session" | "audit"
        
        Returns:
            Filtered data (PII removed, only necessary fields)
        """
        allowed_fields = self.config.get("data_collection", {}).get(context, {}).get("fields", {})
        
        filtered = {}
        for field in allowed_fields:
            if field in raw_data:
                filtered[field] = raw_data[field]
        
        return filtered
    
    def has_pii(self, data: Dict) -> Tuple[bool, List[str]]:
        """
        Check if data contains personally identifiable information.
        
        Returns:
            (has_pii, list_of_pii_fields_found)
        """
        pii_patterns = {
            "name": r"^[a-zA-Z]+ [a-zA-Z]+$",  # Firstname Lastname pattern
            "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "phone": r"^\+?1?\d{9,15}$",
            "ssn": r"^\d{3}-\d{2}-\d{4}$",
            "address": r"^\d+ [a-zA-Z]+ (St|Ave|Dr|Rd|Ln)",
        }
        
        pii_found = []
        for field, pattern in pii_patterns.items():
            import re
            for key, value in data.items():
                if isinstance(value, str) and re.match(pattern, value):
                    pii_found.append(f"{key}:{field}")
        
        return len(pii_found) > 0, pii_found


def get_anonymization_verifier() -> ARXAnonymityVerifier:
    """Factory function to get ARX verifier instance."""
    return ARXAnonymityVerifier()
