#!/usr/bin/env python3
"""
Bulk Text Processor for Saoriverse Learning System

Process large text files (books, poetry collections, documents) through the
calibrated signal extraction and lexicon learning system to bulk-expand
glyphs and lexicons.

Usage:
    python bulk_text_processor.py --file /path/to/book.txt
    python bulk_text_processor.py --file /path/to/book.txt --chunk-size 500
    python bulk_text_processor.py --dir /path/to/texts/
"""

import sys
import json
import argparse
import re
from pathlib import Path
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent))

from emotional_os.learning.hybrid_learner_v2 import HybridLearnerWithUserOverrides
from emotional_os.learning.poetry_signal_extractor import get_poetry_extractor


class BulkTextProcessor:
    """Process large texts through the learning system."""
    
    def __init__(
        self,
        shared_lexicon_path: str = "emotional_os/parser/signal_lexicon.json",
        db_path: str = "emotional_os/glyphs/glyphs.db",
        learning_log_path: str = "learning/hybrid_learning_log.jsonl",
        user_overrides_dir: str = "learning/user_overrides",
    ):
        """Initialize the bulk processor."""
        self.learner = HybridLearnerWithUserOverrides(
            shared_lexicon_path=shared_lexicon_path,
            db_path=db_path,
            learning_log_path=learning_log_path,
            user_overrides_dir=user_overrides_dir,
        )
        self.extractor = get_poetry_extractor()
        
    def split_into_chunks(self, text: str, chunk_size: int = 500) -> List[str]:
        """Split text into chunks by word count, respecting sentence boundaries."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = []
        current_word_count = 0
        
        for sentence in sentences:
            word_count = len(sentence.split())
            
            if current_word_count + word_count > chunk_size and current_chunk:
                # Save current chunk and start new one
                chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_word_count = word_count
            else:
                current_chunk.append(sentence)
                current_word_count += word_count
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def process_text(
        self,
        text: str,
        user_id: str = "bulk_processor",
        chunk_size: int = 500,
    ) -> Dict:
        """Process text through learning pipeline."""
        chunks = self.split_into_chunks(text, chunk_size)
        
        stats = {
            "chunks_processed": 0,
            "total_signals": 0,
            "total_new_lexicon_entries": 0,
            "chunks_with_signals": 0,
            "quality_contributions": 0,
        }
        
        initial_lexicon_size = len(self.learner.shared_lexicon)
        
        for idx, chunk in enumerate(chunks, 1):
            if len(chunk.strip()) < 20:
                continue
            
            # Extract signals
            signals = self.extractor.extract_signals(chunk)
            
            if signals:
                stats["chunks_with_signals"] += 1
            
            stats["total_signals"] += len(signals)
            
            # Learn from chunk
            result = self.learner.learn_from_exchange(
                user_id=user_id,
                user_input=chunk,
                ai_response=f"Processing literary content with {len(signals)} detected signals",
                emotional_signals=signals,
                glyphs=[]
            )
            
            stats["chunks_processed"] += 1
            if result.get("learned_to_shared"):
                stats["quality_contributions"] += 1
            
            if idx % 10 == 0:
                logger.info(f"  Processed {idx} chunks...")
        
        # Calculate new entries added
        final_lexicon_size = len(self.learner.shared_lexicon)
        stats["total_new_lexicon_entries"] = final_lexicon_size - initial_lexicon_size
        
        return stats
    
    def process_file(
        self,
        filepath: str,
        user_id: str = "bulk_processor",
        chunk_size: int = 500,
    ) -> Dict:
        """Process a single text file."""
        filepath = Path(filepath)
        
        if not filepath.exists():
            logger.error(f"File not found: {filepath}")
            return {}
        
        logger.info(f"Processing file: {filepath.name}")
        
        # Read file
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(filepath, 'r', encoding='latin-1') as f:
                text = f.read()
        
        logger.info(f"File size: {len(text)} characters, {len(text.split())} words")
        
        # Process
        stats = self.process_text(text, user_id, chunk_size)
        stats["filename"] = filepath.name
        stats["total_characters"] = len(text)
        stats["total_words"] = len(text.split())
        
        return stats
    
    def process_directory(
        self,
        dirpath: str,
        user_id: str = "bulk_processor",
        chunk_size: int = 500,
        pattern: str = "*.txt",
    ) -> Dict:
        """Process all text files in a directory."""
        dirpath = Path(dirpath)
        
        if not dirpath.exists():
            logger.error(f"Directory not found: {dirpath}")
            return {}
        
        files = sorted(dirpath.glob(pattern))
        logger.info(f"Found {len(files)} files matching pattern: {pattern}")
        
        all_stats = {
            "files_processed": 0,
            "total_chunks": 0,
            "total_signals": 0,
            "total_new_lexicon_entries": 0,
            "total_quality_contributions": 0,
            "files": [],
        }
        
        for filepath in files:
            logger.info(f"\nProcessing: {filepath.name}")
            stats = self.process_file(str(filepath), user_id, chunk_size)
            
            all_stats["files_processed"] += 1
            all_stats["total_chunks"] += stats.get("chunks_processed", 0)
            all_stats["total_signals"] += stats.get("total_signals", 0)
            all_stats["total_new_lexicon_entries"] += stats.get("total_new_lexicon_entries", 0)
            all_stats["total_quality_contributions"] += stats.get("quality_contributions", 0)
            all_stats["files"].append(stats)
        
        return all_stats
    
    def save_results(self, stats: Dict, output_file: str = "bulk_processing_results.json"):
        """Save processing results to JSON."""
        with open(output_file, 'w') as f:
            json.dump(stats, f, indent=2)
        logger.info(f"Results saved to: {output_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Bulk process text files through Saoriverse learning system"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Path to single text file to process"
    )
    parser.add_argument(
        "--dir",
        type=str,
        help="Path to directory containing text files"
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="*.txt",
        help="File pattern for directory processing (default: *.txt)"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=500,
        help="Word count per chunk (default: 500)"
    )
    parser.add_argument(
        "--user-id",
        type=str,
        default="bulk_processor",
        help="User ID for learning attribution"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="bulk_processing_results.json",
        help="Output file for results"
    )
    
    args = parser.parse_args()
    
    processor = BulkTextProcessor()
    
    print("\n" + "=" * 80)
    print("BULK TEXT PROCESSOR - Saoriverse Learning System")
    print("=" * 80 + "\n")
    
    if args.file:
        logger.info(f"Processing single file: {args.file}")
        stats = processor.process_file(args.file, args.user_id, args.chunk_size)
        
        print("\n" + "=" * 80)
        print("PROCESSING RESULTS")
        print("=" * 80)
        print(f"File: {stats.get('filename', 'N/A')}")
        print(f"Size: {stats.get('total_words', 0)} words")
        print(f"Chunks processed: {stats.get('chunks_processed', 0)}")
        print(f"Signals extracted: {stats.get('total_signals', 0)}")
        print(f"New lexicon entries: {stats.get('total_new_lexicon_entries', 0)}")
        print(f"Quality contributions: {stats.get('quality_contributions', 0)}")
        print("=" * 80 + "\n")
        
        processor.save_results(stats, args.output)
    
    elif args.dir:
        logger.info(f"Processing directory: {args.dir}")
        stats = processor.process_directory(args.dir, args.user_id, args.chunk_size, args.pattern)
        
        print("\n" + "=" * 80)
        print("BATCH PROCESSING RESULTS")
        print("=" * 80)
        print(f"Files processed: {stats.get('files_processed', 0)}")
        print(f"Total chunks: {stats.get('total_chunks', 0)}")
        print(f"Total signals: {stats.get('total_signals', 0)}")
        print(f"New lexicon entries: {stats.get('total_new_lexicon_entries', 0)}")
        print(f"Quality contributions: {stats.get('total_quality_contributions', 0)}")
        print("=" * 80 + "\n")
        
        processor.save_results(stats, args.output)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
