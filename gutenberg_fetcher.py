#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Gutenberg Poetry Fetcher & Bulk Processor
Downloads poetry collections from Project Gutenberg and processes them
through the signal extraction and learning pipeline.
"""

import os
import json
import logging
import requests
from pathlib import Path
from typing import List, Dict, Optional
from bulk_text_processor import BulkTextProcessor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GutenbergPoetryFetcher:
    """Fetches poetry collections from Project Gutenberg."""
    
    # Popular poetry collections on Project Gutenberg
    POETRY_BOOKS = {
        # Emily Dickinson
        'dickinson_complete': 12242,
        'dickinson_single_hail': 30412,
        
        # Walt Whitman
        'whitman_leaves': 1322,
        'whitman_drum_taps': 8736,
        
        # Lord Byron
        'byron_collected': 6785,
        
        # John Keats
        'keats_complete': 2350,
        
        # Samuel Taylor Coleridge
        'coleridge_complete': 16800,
        
        # William Wordsworth
        'wordsworth_complete': 8905,
        
        # Percy Bysshe Shelley
        'shelley_complete': 4280,
        
        # Poems of various authors
        'poems_of_passion': 8801,
        'poems_of_nature': 9662,
        'love_poems': 47096,
    }
    
    BASE_URL = "https://www.gutenberg.org/files"
    
    def __init__(self):
        self.downloaded_poems = []
        # Save to external drive
        self.poetry_dir = Path("/Volumes/My Passport for Mac/saoriverse_data/gutenberg_poetry")
        self.poetry_dir.mkdir(parents=True, exist_ok=True)
        
    def get_book_text(self, book_id):
        """Download a book from Project Gutenberg."""
        try:
            # URL for plain text version
            url = "{}/{}/{}-0.txt".format(self.BASE_URL, book_id, book_id)
            
            logger.info("Downloading book {} from {}".format(book_id, url))
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            text = response.text
            # Remove Project Gutenberg header/footer
            text = self._remove_gutenberg_metadata(text)
            
            return text
        except requests.RequestException as e:
            logger.error("Failed to download book {}: {}".format(book_id, e))
            return None
    
    def _remove_gutenberg_metadata(self, text):
        """Remove Project Gutenberg header and footer."""
        # Remove header
        if "*** START" in text:
            start_idx = text.find("*** START")
            text = text[start_idx:]
            # Find the actual content start (after the *** line)
            text = text[text.find('\n'):].lstrip()
        
        # Remove footer
        if "*** END" in text:
            end_idx = text.find("*** END")
            text = text[:end_idx]
        
        return text.strip()
    
    def download_poetry_collection(self, name, book_id):
        """Download a specific poetry collection."""
        logger.info("Starting download of {} (ID: {})".format(name, book_id))
        
        text = self.get_book_text(book_id)
        if not text:
            return False
        
        # Save to file
        file_path = self.poetry_dir / "{}".format(name + ".txt")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        self.downloaded_poems.append({
            'name': name,
            'path': str(file_path),
            'book_id': book_id,
            'size': len(text),
            'words': len(text.split())
        })
        
        logger.info("✓ Downloaded {}: {} chars, {} words".format(name, len(text), len(text.split())))
        return True
    
    def download_all_collections(self):
        """Download all available poetry collections."""
        logger.info("Downloading {} poetry collections...".format(len(self.POETRY_BOOKS)))
        
        for name, book_id in self.POETRY_BOOKS.items():
            self.download_poetry_collection(name, book_id)
        
        return self.downloaded_poems
    
    def get_downloaded_files(self):
        """Get list of downloaded poetry files."""
        return [str(f) for f in self.poetry_dir.glob("*.txt")]


def process_all_poetry():
    """Main function: Download all poetry and process through learning pipeline."""
    
    logger.info("=" * 70)
    logger.info("PROJECT GUTENBERG POETRY DOWNLOAD & LEARNING")
    logger.info("=" * 70)
    
    # Step 1: Download poetry collections
    logger.info("\n[STEP 1] Downloading Poetry Collections")
    logger.info("-" * 70)
    
    fetcher = GutenbergPoetryFetcher()
    downloaded = fetcher.download_all_collections()
    
    logger.info("\n✓ Downloaded {} collections".format(len(downloaded)))
    for item in downloaded:
        logger.info("  - {}: {} words".format(item['name'], item['words']))
    
    # Step 2: Process all poetry through learning pipeline
    logger.info("\n[STEP 2] Processing Poetry Through Learning Pipeline")
    logger.info("-" * 70)
    
    processor = BulkTextProcessor()
    all_stats = {
        'total_files': len(downloaded),
        'total_chunks_processed': 0,
        'total_signals_extracted': 0,
        'total_lexicon_entries': 0,
        'total_quality_contributions': 0,
        'files_processed': []
    }
    
    for poetry_file in fetcher.get_downloaded_files():
        logger.info("\nProcessing: {}".format(Path(poetry_file).name))
        
        try:
            stats = processor.process_file(
                poetry_file,
                user_id="gutenberg_bulk",
                chunk_size=500
            )
            
            all_stats['total_chunks_processed'] += stats.get('chunks_processed', 0)
            all_stats['total_signals_extracted'] += stats.get('total_signals', 0)
            all_stats['total_lexicon_entries'] += stats.get('total_new_lexicon_entries', 0)
            all_stats['total_quality_contributions'] += stats.get('quality_contributions', 0)
            
            all_stats['files_processed'].append({
                'name': Path(poetry_file).name,
                'chunks': stats.get('chunks_processed', 0),
                'signals': stats.get('total_signals', 0),
                'lexicon_entries': stats.get('total_new_lexicon_entries', 0)
            })
            
            logger.info("  ✓ Processed: {} new entries, {} signals".format(
                stats.get('total_new_lexicon_entries', 0),
                stats.get('total_signals', 0)
            ))
            
        except Exception as e:
            logger.error("  ✗ Error processing {}: {}".format(poetry_file, e))
    
    # Step 3: Report results
    logger.info("\n[RESULTS] SUMMARY")
    logger.info("=" * 70)
    logger.info("Files processed: {}".format(all_stats['total_files']))
    logger.info("Total chunks: {}".format(all_stats['total_chunks_processed']))
    logger.info("Total signals extracted: {}".format(all_stats['total_signals_extracted']))
    logger.info("Total new lexicon entries: {}".format(all_stats['total_lexicon_entries']))
    logger.info("Quality contributions: {}".format(all_stats['total_quality_contributions']))
    
    # Save detailed results to external drive
    results_file = Path("/Volumes/My Passport for Mac/saoriverse_data/gutenberg_processing_results.json")
    results_file.parent.mkdir(parents=True, exist_ok=True)
    with open(results_file, 'w') as f:
        json.dump(all_stats, f, indent=2)
    
    logger.info("\n[OK] Detailed results saved to: {}".format(results_file))
    
    return all_stats


if __name__ == "__main__":
    try:
        results = process_all_poetry()
        logger.info("\n[COMPLETE] PROJECT GUTENBERG POETRY PROCESSING COMPLETE")
    except Exception as e:
        logger.error("Fatal error: {}".format(e))
        raise
