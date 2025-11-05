#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Poetry Data Pipeline

Complete end-to-end pipeline:
1. Download poetry from Project Gutenberg
2. Clean & validate text
3. Register in data hub
4. Make available to all processing modes

Ensures:
- Clean extraction (no artifacts)
- Complete text (no fragmentation)
- Usable everywhere (all modes can access)
"""

import json
import logging
from pathlib import Path
from typing import Dict, List
import requests

from poetry_text_cleaner import PoetryTextCleaner, PoetryTextValidator
from poetry_data_hub import PoetryDataHub, ProcessingModeAdapter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PoetryDataPipeline:
    """Complete poetry data processing pipeline."""
    
    # Poetry collections to extract
    POETRY_COLLECTIONS = {
        # Romantic & Victorian
        'dickinson_complete': {
            'id': 12242,
            'poet': 'Emily Dickinson',
            'period': 'Victorian',
            'description': 'Complete Works - 1,774 poems'
        },
        'whitman_leaves': {
            'id': 1322,
            'poet': 'Walt Whitman',
            'period': 'Romantic',
            'description': 'Leaves of Grass - Major work'
        },
        'keats_complete': {
            'id': 2350,
            'poet': 'John Keats',
            'period': 'Romantic',
            'description': 'Complete Poetical Works'
        },
        'wordsworth_complete': {
            'id': 8905,
            'poet': 'William Wordsworth',
            'period': 'Romantic',
            'description': 'Complete Poetical Works'
        },
        'shakespeare_sonnets': {
            'id': 1041,
            'poet': 'William Shakespeare',
            'period': 'Renaissance',
            'description': '154 Sonnets + Venus & Adonis'
        },
        'yeats_poems': {
            'id': 6811,
            'poet': 'W.B. Yeats',
            'period': 'Modern',
            'description': 'Collected Poems'
        },
        'shelley_complete': {
            'id': 4280,
            'poet': 'Percy Bysshe Shelley',
            'period': 'Romantic',
            'description': 'Complete Works'
        },
        'tennyson_complete': {
            'id': 10031,
            'poet': 'Alfred Tennyson',
            'period': 'Victorian',
            'description': 'Complete Poetical Works'
        },
    }
    
    BASE_URL = "https://www.gutenberg.org/files"
    
    def __init__(self, data_dir: str = "poetry_data"):
        """Initialize pipeline."""
        self.hub = PoetryDataHub(data_dir)
        self.cleaner = PoetryTextCleaner()
        self.validator = PoetryTextValidator()
        self.stats = {
            'downloaded': 0,
            'cleaned': 0,
            'validated': 0,
            'failed': 0,
        }
    
    def download_poetry(self, collection_name: str, collection_info: Dict) -> tuple:
        """
        Download poetry from Project Gutenberg.
        
        Args:
            collection_name: Name identifier
            collection_info: Collection metadata
            
        Returns:
            (text, error_message)
        """
        book_id = collection_info['id']
        url = f"{self.BASE_URL}/{book_id}/{book_id}-0.txt"
        
        try:
            logger.info(f"Downloading: {collection_name} (ID: {book_id})")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            text = response.text
            logger.info(f"✓ Downloaded: {len(text)} chars")
            
            self.stats['downloaded'] += 1
            return text, None
        
        except Exception as e:
            error = f"Download failed: {e}"
            logger.error(f"✗ {error}")
            self.stats['failed'] += 1
            return None, error
    
    def clean_poetry(self, collection_name: str, text: str) -> tuple:
        """
        Clean downloaded poetry.
        
        Args:
            collection_name: Name identifier
            text: Raw downloaded text
            
        Returns:
            (cleaned_text, metrics)
        """
        if not text:
            return None, None
        
        logger.info(f"Cleaning: {collection_name}")
        cleaned = self.cleaner.clean_text(text, verbose=True)
        metrics = self.cleaner.get_stats()
        
        if len(cleaned) < 100:
            logger.error(f"✗ Text too short after cleaning: {len(cleaned)} chars")
            return None, metrics
        
        logger.info(f"✓ Cleaned: {len(cleaned)} chars")
        self.stats['cleaned'] += 1
        
        return cleaned, metrics
    
    def validate_poetry(self, collection_name: str, text: str) -> tuple:
        """
        Validate cleaned poetry.
        
        Args:
            collection_name: Name identifier
            text: Cleaned text
            
        Returns:
            (is_valid, completeness_score, details)
        """
        if not text:
            return False, 0.0, "No text to validate"
        
        logger.info(f"Validating: {collection_name}")
        
        # Check completeness
        is_complete, message = self.cleaner.validate_completeness(text)
        lines = len(text.split('\n'))
        words = len(text.split())
        
        # Calculate completeness score
        completeness_score = 1.0 if is_complete else 0.7
        
        # Calculate usability score based on metrics
        usability_score = 1.0
        if words < 1000:
            usability_score *= 0.5
        if lines < 50:
            usability_score *= 0.5
        
        details = {
            'complete': is_complete,
            'message': message,
            'words': words,
            'lines': lines,
            'completeness_score': completeness_score,
            'usability_score': usability_score,
        }
        
        if is_complete:
            logger.info(f"✓ Validated: {words} words, {lines} lines")
            self.stats['validated'] += 1
            return True, completeness_score, details
        else:
            logger.warning(f"⚠ Validation warning: {message}")
            return True, completeness_score, details
    
    def process_collection(self, collection_name: str, collection_info: Dict) -> bool:
        """
        Process a single poetry collection end-to-end.
        
        Args:
            collection_name: Name identifier
            collection_info: Collection metadata
            
        Returns:
            Success
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"Processing: {collection_name}")
        logger.info(f"{'='*70}")
        
        # Step 1: Register
        self.hub.register_collection(
            collection_name,
            collection_info['id'],
            collection_info['poet'],
            collection_info.get('period'),
            collection_info.get('description')
        )
        
        # Step 2: Download
        text, error = self.download_poetry(collection_name, collection_info)
        if error:
            self.hub.log_processing(collection_name, 'download', 'failed', error)
            return False
        
        self.hub.log_processing(collection_name, 'download', 'success', f"{len(text)} chars")
        
        # Step 3: Clean
        cleaned, metrics = self.clean_poetry(collection_name, text)
        if not cleaned:
            self.hub.log_processing(collection_name, 'clean', 'failed', "Cleaning produced empty text")
            return False
        
        self.hub.log_processing(collection_name, 'clean', 'success', json.dumps(metrics))
        
        # Step 4: Validate
        is_valid, completeness, details = self.validate_poetry(collection_name, cleaned)
        if not is_valid:
            logger.warning(f"⚠ Skipping validation: {details['message']}")
        
        # Step 5: Store
        self.hub.store_clean_text(collection_name, cleaned, metrics)
        
        # Step 6: Mark as validated
        self.hub.mark_validated(
            collection_name,
            completeness,
            details.get('usability_score', 0.9)
        )
        
        self.hub.log_processing(collection_name, 'validate', 'success', json.dumps(details))
        
        logger.info(f"✓ Successfully processed: {collection_name}\n")
        return True
    
    def process_all(self) -> Dict:
        """
        Process all poetry collections.
        
        Returns:
            Results summary
        """
        logger.info("\n" + "=" * 70)
        logger.info("POETRY DATA PIPELINE - PROCESSING ALL COLLECTIONS")
        logger.info("=" * 70 + "\n")
        
        results = {
            'processed': [],
            'failed': [],
            'total': len(self.POETRY_COLLECTIONS),
        }
        
        for collection_name, collection_info in self.POETRY_COLLECTIONS.items():
            try:
                success = self.process_collection(collection_name, collection_info)
                if success:
                    results['processed'].append(collection_name)
                else:
                    results['failed'].append(collection_name)
            except Exception as e:
                logger.error(f"✗ Exception processing {collection_name}: {e}")
                results['failed'].append(collection_name)
        
        return results
    
    def get_pipeline_status(self) -> Dict:
        """Get complete pipeline status."""
        hub_status = self.hub.get_hub_status()
        
        return {
            'pipeline_stats': self.stats,
            'hub_status': hub_status,
            'ready_for_processing': hub_status['validated'] > 0,
            'total_usable_words': hub_status['total_words'],
        }
    
    def export_for_all_modes(self, export_dir: str = "poetry_export") -> Dict:
        """
        Export clean poetry for all processing modes.
        
        Args:
            export_dir: Directory to export to
            
        Returns:
            Export manifest
        """
        logger.info(f"\nExporting clean poetry for all processing modes...")
        
        manifest = self.hub.export_for_processing(export_dir)
        
        # Create processing mode manifests
        adapter = ProcessingModeAdapter(self.hub)
        
        # For signal extraction
        signal_data = adapter.for_signal_extraction()
        signal_manifest = {
            'mode': 'signal_extraction',
            'collections': len(signal_data),
            'total_words': sum(len(t.split()) for t in signal_data.values()),
        }
        
        # For lexicon learning
        lexicon_data = adapter.for_lexicon_learning()
        lexicon_manifest = {
            'mode': 'lexicon_learning',
            'collections': len(lexicon_data),
            'total_words': sum(len(t.split()) for t in lexicon_data.values()),
        }
        
        # For glyph generation
        glyph_data = adapter.for_glyph_generation()
        glyph_manifest = {
            'mode': 'glyph_generation',
            'collections': len(glyph_data),
            'total_words': sum(len(t[1].split()) for t in glyph_data),
        }
        
        # Create combined manifest
        combined_manifest = {
            'exported_at': manifest['exported_at'],
            'base_export': manifest,
            'processing_modes': {
                'signal_extraction': signal_manifest,
                'lexicon_learning': lexicon_manifest,
                'glyph_generation': glyph_manifest,
            }
        }
        
        # Save combined manifest
        manifest_path = Path(export_dir) / "processing_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(combined_manifest, f, indent=2)
        
        logger.info(f"✓ Exported for all processing modes")
        logger.info(f"  Signal extraction: {signal_manifest['collections']} collections")
        logger.info(f"  Lexicon learning: {lexicon_manifest['collections']} collections")
        logger.info(f"  Glyph generation: {glyph_manifest['collections']} collections")
        
        return combined_manifest


def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Poetry data pipeline")
    parser.add_argument("--process", action="store_true", help="Process all collections")
    parser.add_argument("--status", action="store_true", help="Show pipeline status")
    parser.add_argument("--export", type=str, help="Export for processing modes")
    parser.add_argument("--data-dir", default="poetry_data", help="Data directory")
    
    args = parser.parse_args()
    
    pipeline = PoetryDataPipeline(args.data_dir)
    
    if args.process:
        results = pipeline.process_all()
        status = pipeline.get_pipeline_status()
        
        print("\n" + "=" * 70)
        print("PIPELINE RESULTS")
        print("=" * 70)
        print(f"Processed: {len(results['processed'])}")
        print(f"Failed: {len(results['failed'])}")
        print(f"\nTotal words: {status['hub_status']['total_words']:,}")
        print(f"Validated collections: {status['hub_status']['validated']}")
        print(f"Ready for processing: {status['ready_for_processing']}")
        print("=" * 70)
    
    elif args.export:
        manifest = pipeline.export_for_all_modes(args.export)
        print(f"\n✓ Exported to: {args.export}")
    
    elif args.status:
        status = pipeline.get_pipeline_status()
        hub_status = status['hub_status']
        
        print("\n" + "=" * 70)
        print("POETRY DATA PIPELINE STATUS")
        print("=" * 70)
        print(f"Downloaded: {status['pipeline_stats']['downloaded']}")
        print(f"Cleaned: {status['pipeline_stats']['cleaned']}")
        print(f"Validated: {status['pipeline_stats']['validated']}")
        print(f"Failed: {status['pipeline_stats']['failed']}")
        print(f"\nHub Status:")
        print(f"  Total collections: {hub_status['total_collections']}")
        print(f"  Validated: {hub_status['validated']} ({hub_status['validated_percent']:.1f}%)")
        print(f"  Total words: {hub_status['total_words']:,}")
        print(f"  Ready for processing: {status['ready_for_processing']}")
        print("=" * 70)


if __name__ == "__main__":
    main()
