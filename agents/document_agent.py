"""
Document Processing Agent - Agent 1
Handles document identification, classification, and field extraction
"""

from typing import Dict, Any
import logging
from .base_agent import BaseAgent, AgentResult
from utils.ocr import extract_text
from utils.classifier import classify_document
from utils.extractors import extract_fields

class DocumentProcessingAgent(BaseAgent):
    """Agent for processing medical documents and extracting structured data"""
    
    def __init__(self):
        super().__init__("Document Processing Agent")
    
    def validate_input(self, claim_data: Dict[str, Any]) -> bool:
        """Validate input contains required document information"""
        required_fields = ["documents", "claim_id"]
        return all(field in claim_data for field in required_fields)
    
    def process(self, claim_data: Dict[str, Any]) -> AgentResult:
        """Process all documents in a claim and extract structured data"""
        try:
            documents = claim_data.get("documents", [])
            claim_id = claim_data.get("claim_id", "unknown")
            
            extracted_data = {
                "claim_id": claim_id,
                "documents": [],
                "summary": {},
                "errors": []
            }
            
            for doc in documents:
                doc_result = self._process_single_document(doc)
                extracted_data["documents"].append(doc_result)
                
                # Update summary
                doc_type = doc_result.get("document_type", "Unknown")
                if doc_type not in extracted_data["summary"]:
                    extracted_data["summary"][doc_type] = 0
                extracted_data["summary"][doc_type] += 1
            
            # Check for required documents
            missing_docs = self._check_required_documents(extracted_data["summary"])
            if missing_docs:
                extracted_data["errors"].append(f"Missing required documents: {missing_docs}")
            
            # Calculate overall confidence
            confidence = self._calculate_confidence(extracted_data["documents"])
            
            return AgentResult(
                agent_name=self.name,
                status="completed" if not extracted_data["errors"] else "needs_review",
                data=extracted_data,
                confidence=confidence,
                reasoning=f"Processed {len(documents)} documents with {len(extracted_data['errors'])} errors"
            )
            
        except Exception as e:
            self.logger.error(f"Document processing failed: {e}")
            return AgentResult(
                agent_name=self.name,
                status="error",
                data={"error": str(e)},
                confidence=0.0,
                reasoning=f"Processing failed: {str(e)}"
            )
    
    def _process_single_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single document and extract information"""
        try:
            file_path = document.get("file_path")
            file_name = document.get("file_name", "unknown")
            
            self.logger.info(f"Processing document: {file_name}, path: {file_path}")
            
            # Extract text - handle both text and PDF files
            if file_path and file_path.lower().endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            else:
                text = extract_text(file_path or '')
            
            self.logger.info(f"Extracted text length: {len(text)} characters")
            self.logger.info(f"First 200 chars of text: {text[:200]}")
            
            # Classify document
            doc_type = classify_document(text)
            self.logger.info(f"Document classified as: {doc_type}")
            
            # Extract fields
            extracted_fields = extract_fields(text, doc_type)
            self.logger.info(f"Extracted fields: {extracted_fields}")
            
            return {
                "file_name": file_name,
                "file_path": file_path,
                "document_type": doc_type,
                "text_length": len(text),
                "extracted_fields": extracted_fields,
                "processing_status": "success"
            }
            
        except Exception as e:
            return {
                "file_name": document.get("file_name", "unknown"),
                "file_path": document.get("file_path", ""),
                "document_type": "Unknown",
                "text_length": 0,
                "extracted_fields": {},
                "processing_status": "error",
                "error": str(e)
            }
    
    def _check_required_documents(self, doc_summary: Dict[str, int]) -> list:
        """Check if required documents are present"""
        required_types = ["Claim Form", "Discharge Summary", "Final Bill"]
        missing = []
        
        for doc_type in required_types:
            if doc_summary.get(doc_type, 0) == 0:
                missing.append(doc_type)
        
        return missing
    
    def _calculate_confidence(self, documents: list) -> float:
        """Calculate overall confidence score for document processing"""
        if not documents:
            return 0.0
        
        total_confidence = 0.0
        successful_docs = 0
        
        for doc in documents:
            if doc.get("processing_status") == "success":
                successful_docs += 1
                # Simple confidence based on text length and field extraction
                text_length = doc.get("text_length", 0)
                fields = doc.get("extracted_fields", {})
                
                if text_length > 100 and len(fields) > 3:
                    total_confidence += 0.9
                elif text_length > 50 and len(fields) > 1:
                    total_confidence += 0.7
                else:
                    total_confidence += 0.5
        
        return total_confidence / len(documents) if documents else 0.0
