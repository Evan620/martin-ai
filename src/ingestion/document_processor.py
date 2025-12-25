"""
Document processing pipeline for various file formats.

Supports PDF, DOCX, TXT, and Markdown with OCR fallback for scanned documents.
"""

from pathlib import Path
from typing import Dict, Optional

from loguru import logger

from src.utils.validators import sanitize_text, validate_file_path


class DocumentProcessor:
    """Base class for document processors."""
    
    def __init__(self):
        """Initialize document processor."""
        self.supported_formats = []
    
    def can_process(self, file_path: Path) -> bool:
        """
        Check if this processor can handle the file.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if processor supports this file type
        """
        return file_path.suffix.lower().lstrip('.') in self.supported_formats
    
    def process(self, file_path: Path) -> Dict[str, str]:
        """
        Process document and extract text.
        
        Args:
            file_path: Path to document
            
        Returns:
            Dictionary with 'content' and 'metadata'
        """
        raise NotImplementedError("Subclasses must implement process()")


class PDFProcessor(DocumentProcessor):
    """PDF document processor."""
    
    def __init__(self, enable_ocr: bool = True):
        """
        Initialize PDF processor.
        
        Args:
            enable_ocr: Enable OCR for scanned PDFs
        """
        super().__init__()
        self.supported_formats = ['pdf']
        self.enable_ocr = enable_ocr
    
    def process(self, file_path: Path) -> Dict[str, str]:
        """Process PDF document."""
        try:
            import PyPDF2
            
            text = ""
            metadata = {}
            
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                # Extract metadata
                if reader.metadata:
                    metadata = {
                        'title': reader.metadata.get('/Title', ''),
                        'author': reader.metadata.get('/Author', ''),
                        'subject': reader.metadata.get('/Subject', ''),
                        'creator': reader.metadata.get('/Creator', ''),
                    }
                
                # Extract text from all pages
                for page_num, page in enumerate(reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n\n"
                    except Exception as e:
                        logger.warning(f"Failed to extract text from page {page_num}: {e}")
            
            # If no text extracted and OCR is enabled, try OCR
            if not text.strip() and self.enable_ocr:
                logger.info(f"No text extracted from {file_path.name}, attempting OCR")
                text = self._ocr_pdf(file_path)
            
            text = sanitize_text(text)
            
            return {
                'content': text,
                'metadata': metadata,
            }
            
        except Exception as e:
            logger.error(f"Failed to process PDF {file_path}: {e}")
            raise
    
    def _ocr_pdf(self, file_path: Path) -> str:
        """
        Perform OCR on PDF.
        
        Args:
            file_path: Path to PDF
            
        Returns:
            Extracted text
        """
        try:
            from pdf2image import convert_from_path
            import pytesseract
            
            text = ""
            images = convert_from_path(file_path)
            
            for i, image in enumerate(images):
                logger.debug(f"OCR processing page {i + 1}/{len(images)}")
                page_text = pytesseract.image_to_string(image, lang='eng+fra')
                text += page_text + "\n\n"
            
            return text
            
        except ImportError:
            logger.warning("OCR dependencies not installed (pdf2image, pytesseract)")
            return ""
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return ""


class DOCXProcessor(DocumentProcessor):
    """DOCX document processor."""
    
    def __init__(self):
        """Initialize DOCX processor."""
        super().__init__()
        self.supported_formats = ['docx']
    
    def process(self, file_path: Path) -> Dict[str, str]:
        """Process DOCX document."""
        try:
            from docx import Document
            
            doc = Document(file_path)
            
            # Extract text from paragraphs
            text = "\n\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            
            # Extract metadata
            metadata = {
                'title': doc.core_properties.title or '',
                'author': doc.core_properties.author or '',
                'subject': doc.core_properties.subject or '',
                'created': str(doc.core_properties.created) if doc.core_properties.created else '',
            }
            
            text = sanitize_text(text)
            
            return {
                'content': text,
                'metadata': metadata,
            }
            
        except Exception as e:
            logger.error(f"Failed to process DOCX {file_path}: {e}")
            raise


class TXTProcessor(DocumentProcessor):
    """Plain text document processor."""
    
    def __init__(self):
        """Initialize TXT processor."""
        super().__init__()
        self.supported_formats = ['txt', 'md', 'markdown']
    
    def process(self, file_path: Path) -> Dict[str, str]:
        """Process text document."""
        try:
            # Try UTF-8 first
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            
            text = None
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        text = file.read()
                    logger.debug(f"Successfully read {file_path.name} with {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue
            
            if text is None:
                raise ValueError(f"Could not decode {file_path} with any supported encoding")
            
            text = sanitize_text(text)
            
            return {
                'content': text,
                'metadata': {},
            }
            
        except Exception as e:
            logger.error(f"Failed to process TXT {file_path}: {e}")
            raise


class DocumentProcessorFactory:
    """Factory for creating appropriate document processors."""
    
    def __init__(self, enable_ocr: bool = True):
        """
        Initialize processor factory.
        
        Args:
            enable_ocr: Enable OCR for scanned documents
        """
        self.processors = [
            PDFProcessor(enable_ocr=enable_ocr),
            DOCXProcessor(),
            TXTProcessor(),
        ]
    
    def get_processor(self, file_path: Path) -> Optional[DocumentProcessor]:
        """
        Get appropriate processor for file.
        
        Args:
            file_path: Path to file
            
        Returns:
            DocumentProcessor instance or None if unsupported
        """
        for processor in self.processors:
            if processor.can_process(file_path):
                return processor
        
        logger.warning(f"No processor found for {file_path.suffix}")
        return None
    
    def process_document(self, file_path: Path) -> Optional[Dict[str, str]]:
        """
        Process document using appropriate processor.
        
        Args:
            file_path: Path to document
            
        Returns:
            Processed document data or None if failed
        """
        if not validate_file_path(file_path):
            logger.error(f"Invalid file path: {file_path}")
            return None
        
        processor = self.get_processor(file_path)
        if not processor:
            return None
        
        try:
            logger.info(f"Processing {file_path.name} with {processor.__class__.__name__}")
            result = processor.process(file_path)
            logger.info(f"Successfully processed {file_path.name} ({len(result['content'])} characters)")
            return result
        except Exception as e:
            logger.error(f"Failed to process {file_path.name}: {e}")
            return None
