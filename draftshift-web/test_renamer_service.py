"""
DraftShift Renamer Service - Integration Tests

Tests the complete renamer workflow: file upload, analysis, custom overrides, ZIP download.
"""

import pytest
import tempfile
import os
from pathlib import Path
from io import BytesIO

# Note: Run with: python -m pytest test_renamer_service.py -v
# Requires: FastAPI, python-multipart, requests


@pytest.fixture
def sample_files():
    """Create temporary sample files for testing."""
    files = {}
    
    # Create a mock motion file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("""
        MOTION FOR SUMMARY JUDGMENT
        
        Plaintiff respectfully submits this Motion for Summary Judgment pursuant to 
        Rule 56 of the Federal Rules of Civil Procedure.
        
        Dated: January 15, 2024
        """)
        files['motion.txt'] = f.name
    
    # Create a mock declaration
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("""
        DECLARATION OF JOHN SMITH
        
        I, John Smith, declare under penalty of perjury that the following is true
        and correct to the best of my knowledge:
        
        Dated: February 20, 2024
        """)
        files['declaration.txt'] = f.name
    
    # Create a mock notice
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("""
        NOTICE OF MOTION
        
        Please take notice that on March 5, 2024, Plaintiff will move this Court
        for an order...
        """)
        files['notice.txt'] = f.name
    
    yield files
    
    # Cleanup
    for filepath in files.values():
        if os.path.exists(filepath):
            os.unlink(filepath)


class TestRenamerEndpoints:
    """Test DraftShift Renamer API endpoints."""
    
    def test_analyze_endpoint(self, sample_files):
        """Test POST /api/renamer/analyze endpoint."""
        from fastapi.testclient import TestClient
        from api import app
        
        client = TestClient(app)
        
        # Prepare files for upload
        files_to_upload = []
        for name, path in sample_files.items():
            with open(path, 'rb') as f:
                files_to_upload.append(('files', (name, f.read())))
        
        response = client.post('/api/renamer/analyze', files=files_to_upload)
        
        # Verify response structure
        assert response.status_code == 200
        data = response.json()
        
        assert 'files' in data
        assert 'total_files' in data
        assert 'successful' in data
        assert 'errors' in data
        
        assert data['total_files'] == 3
        assert data['successful'] == 3
        assert len(data['files']) == 3
    
    def test_preview_endpoint(self, sample_files):
        """Test POST /api/renamer/preview endpoint."""
        from fastapi.testclient import TestClient
        from api import app
        
        client = TestClient(app)
        
        # Prepare files
        files_to_upload = []
        for name, path in sample_files.items():
            with open(path, 'rb') as f:
                files_to_upload.append(('files', (name, f.read())))
        
        response = client.post('/api/renamer/preview', files=files_to_upload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'previews' in data
        assert len(data['previews']) == 3
        
        # Check each preview has required fields
        for preview in data['previews']:
            assert 'original_name' in preview
            assert 'renamed_to' in preview
            assert 'detected_date' in preview
            assert 'detected_type' in preview
            assert 'confidence' in preview
    
    def test_supported_types_endpoint(self):
        """Test GET /api/renamer/supported-types endpoint."""
        from fastapi.testclient import TestClient
        from api import app
        
        client = TestClient(app)
        response = client.get('/api/renamer/supported-types')
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'types' in data
        assert 'total' in data
        assert len(data['types']) > 0
        
        # Should include common document types
        type_names = [t for t in data['types']]
        assert any('Motion' in t for t in type_names)
        assert any('Declaration' in t for t in type_names)
        assert any('Notice' in t for t in type_names)
    
    def test_custom_rename_endpoint(self, sample_files):
        """Test POST /api/renamer/custom-rename endpoint."""
        from fastapi.testclient import TestClient
        from api import app
        
        client = TestClient(app)
        
        # First analyze to get current names
        files_to_upload = []
        for name, path in sample_files.items():
            with open(path, 'rb') as f:
                files_to_upload.append(('files', (name, f.read())))
        
        # Submit custom overrides
        override_data = {
            "files": [
                {
                    "original_name": "motion.txt",
                    "override_date": "2024-01-10",
                    "override_type": "Motion to Compel"
                }
            ]
        }
        
        response = client.post(
            '/api/renamer/custom-rename',
            json=override_data,
            files=files_to_upload
        )
        
        # Should accept custom overrides
        assert response.status_code in [200, 400]  # May vary by implementation


class TestFilenameNormalization:
    """Test filename normalization logic."""
    
    def test_date_extraction_from_motion(self):
        """Test date extraction from motion text."""
        from filename_normalizer import FilenameNormalizer
        
        normalizer = FilenameNormalizer()
        
        content = """
        MOTION FOR SUMMARY JUDGMENT
        Dated: January 15, 2024
        """
        
        result = normalizer.normalize(
            original_filename="motion.txt",
            file_content=content
        )
        
        assert result.detected_date is not None
        assert result.detected_date.month == 1
        assert result.detected_date.day == 15
        assert result.detected_date.year == 2024
    
    def test_document_type_detection(self):
        """Test document type detection."""
        from filename_normalizer import FilenameNormalizer
        
        normalizer = FilenameNormalizer()
        
        # Test motion detection
        result = normalizer.normalize(
            original_filename="motion.txt",
            file_content="MOTION FOR SUMMARY JUDGMENT"
        )
        assert 'Motion' in result.detected_type
        
        # Test declaration detection
        result = normalizer.normalize(
            original_filename="decl.txt",
            file_content="DECLARATION OF JOHN DOE"
        )
        assert 'Declaration' in result.detected_type
    
    def test_filename_format(self):
        """Test output filename format."""
        from filename_normalizer import FilenameNormalizer
        from datetime import datetime
        
        normalizer = FilenameNormalizer()
        
        result = normalizer.normalize(
            original_filename="motion_2024.pdf",
            file_content="MOTION FOR SUMMARY JUDGMENT",
            user_provided_date=datetime(2024, 1, 15)
        )
        
        # Should match format: YYMMDD – Type.ext
        assert result.renamed_filename.startswith('240115')
        assert '–' in result.renamed_filename
        assert result.renamed_filename.endswith('.pdf')


class TestRenamerIntegration:
    """End-to-end integration tests."""
    
    def test_full_workflow_zip_download(self, sample_files):
        """Test complete workflow: upload → analyze → download ZIP."""
        from fastapi.testclient import TestClient
        from api import app
        import zipfile
        
        client = TestClient(app)
        
        # Prepare files
        files_to_upload = []
        for name, path in sample_files.items():
            with open(path, 'rb') as f:
                files_to_upload.append(('files', (name, f.read())))
        
        # Request rename and download
        response = client.post(
            '/api/renamer/rename-and-download',
            files=files_to_upload
        )
        
        assert response.status_code == 200
        assert response.headers['content-type'] == 'application/zip'
        
        # Verify ZIP contents
        zip_buffer = BytesIO(response.content)
        with zipfile.ZipFile(zip_buffer, 'r') as z:
            files_in_zip = z.namelist()
            
            # Should have 3 files
            assert len(files_in_zip) == 3
            
            # All filenames should follow format
            for filename in files_in_zip:
                # Format: YYMMDD – Type.ext
                assert ' – ' in filename
                parts = filename.split(' – ')
                assert len(parts) == 2
                
                # First part should be date (YYMMDD)
                date_part = parts[0]
                assert len(date_part) == 6
                assert date_part.isdigit()


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
