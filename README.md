# Health Claim Document Intelligence System

An AI-powered system for processing medical documents with automatic categorization, field extraction, fraud detection, and readability analysis.

## Features

- 🏥 **Document Upload**: Support for PDF, JPG, PNG files
- 🤖 **AI Classification**: Automatic document type detection using Ollama
- 📝 **Field Extraction**: Extract structured data from medical documents
- 🔍 **Fraud Detection**: Identify potential fraud indicators
- 📊 **Readability Analysis**: Assess document quality and completeness
- 🎨 **Modern Web UI**: Intuitive drag-and-drop interface
- 📱 **Responsive Design**: Works on desktop and mobile devices

## Prerequisites

1. **Ollama** (Local LLM)
   ```bash
   # Install Ollama
   brew install ollama
   
   # Start Ollama service
   ollama serve
   
   # Pull the required model
   ollama pull mistral
   ```

2. **Tesseract OCR**
   ```bash
   # Install Tesseract
   brew install tesseract
   brew install tesseract-lang
   ```

## Installation

1. Clone or download the project
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Quick Start

```bash
python3 run.py
```

This will start the server with:
- **Web UI**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Manual Start

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

| Method | Endpoint | Description |
|---------|-----------|-------------|
| GET | `/` | Web UI |
| GET | `/health` | System health check |
| POST | `/process-medical-document` | Process single document |
| POST | `/batch-process` | Process multiple documents |
| GET | `/documents` | List uploaded documents |
| DELETE | `/documents/{filename}` | Delete document |

## Supported Document Types

- Discharge Summary
- Final Bill
- Pharmacy Bill
- Diagnostic Report
- Radiology Report
- Claim Form
- Pre-Authorization Form
- Cashless Authorization Letter
- OPD Prescription
- ID Proof
- Policy Document
- Death Certificate
- FIR / MLC Report
- ICU Chart / Nursing Notes
- OT Notes / Surgery Notes
- Implant Invoice
- Lab Test Bill

## Processing Pipeline

1. **OCR Extraction**: Extract text from documents using Tesseract
2. **Classification**: Categorize documents using rule-based + AI
3. **Field Extraction**: Extract structured data using Ollama
4. **Quality Checks**: 
   - Readability scoring
   - Fraud detection
   - Data validation

## Web UI Features

### Upload Interface
- Drag & drop file upload
- Multiple file selection
- File size validation (10MB limit)
- File type filtering

### Results Dashboard
- Real-time processing progress
- Document statistics
- Individual document results
- Fraud alerts
- Readability scores
- Extracted field display

### Quality Indicators

- 🟢 **Low Risk**: No issues detected
- 🟡 **Medium Risk**: Minor concerns
- 🔴 **High Risk**: Multiple fraud indicators

## Configuration

### Environment Variables
```bash
# No API keys required - uses local Ollama
# Optional: Configure Ollama model in utils/classifier.py and utils/extractors.py
```

### Model Configuration
Default model: `mistral`
To change model, update in:
- `utils/classifier.py` (line 113)
- `utils/extractors.py` (line 207)

## Troubleshooting

### OCR Issues
- Ensure Tesseract is installed: `tesseract --version`
- Check file permissions in uploads directory
- Verify image quality and resolution

### Ollama Issues
- Verify Ollama is running: `ollama list`
- Check model is downloaded: `ollama pull mistral`
- Confirm service is active: `ollama serve`

### Common Errors
- **404 Model Not Found**: Check Ollama model installation
- **500 Internal Error**: Check logs for specific error details
- **Empty OCR Output**: Verify document quality and format

## Development

### Project Structure
```
health-claim-doc-ai/
├── main.py              # FastAPI application
├── run.py               # Startup script
├── requirements.txt      # Dependencies
├── templates/
│   └── index.html      # Web UI
├── utils/
│   ├── ocr.py         # Text extraction
│   ├── classifier.py    # Document classification
│   └── extractors.py   # Field extraction
└── uploads/            # File storage
```

### Adding New Document Types
1. Update `DOCUMENT_RULES` in `utils/classifier.py`
2. Add extraction prompt in `utils/extractors.py`
3. Test with sample documents

## License

This project is open source and available under the MIT License.
