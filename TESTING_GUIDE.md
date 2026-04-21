# Complete System Testing Guide

## 🧪 Testing Overview

This guide provides comprehensive testing strategies for the Agentic AI Claim Adjudication System.

## 🎯 Testing Objectives

1. **Functional Testing**: Verify all agents work correctly
2. **Integration Testing**: Ensure agents coordinate properly
3. **Performance Testing**: Validate system speed and scalability
4. **API Testing**: Test all REST endpoints
5. **Edge Case Testing**: Handle unusual scenarios
6. **End-to-End Testing**: Complete claim processing workflow

## 🚀 Quick Start Testing

### **Prerequisites**
```bash
# 1. Start Ollama (required for LLM agents)
ollama serve

# 2. Start the API server
python claim_adjudication_api.py

# 3. Run comprehensive tests
python test_complete_system.py

# 4. Test API endpoints
python test_api_endpoints.py
```

### **Basic Health Check**
```bash
# Check if API is running
curl http://localhost:8001/

# Check agent status
curl http://localhost:8001/agents/status
```

## 📋 Detailed Testing Scenarios

### **1. Individual Agent Testing**

#### **Document Processing Agent**
```python
from agents.document_agent import DocumentProcessingAgent

agent = DocumentProcessingAgent()
claim_data = {
    "claim_id": "TEST_001",
    "documents": [
        {
            "file_name": "discharge_summary.pdf",
            "file_path": "uploads/test_document.pdf"
        }
    ]
}
result = agent.process(claim_data)
print(f"Status: {result.status}, Confidence: {result.confidence}")
```

**Expected Results:**
- ✅ Status: "completed"
- ✅ Confidence: > 0.7
- ✅ Document classification working
- ✅ Field extraction successful

#### **Policy Validation Agent**
```python
from agents.policy_agent import PolicyValidationAgent

agent = PolicyValidationAgent()
claim_data = {
    "policy_details": {
        "status": "active",
        "premium_status": "paid",
        "start_date": "2023-01-01",
        "end_date": "2024-12-31"
    },
    "claim_details": {
        "admission_date": "2024-03-15",
        "diagnosis": "Medical condition"
    }
}
result = agent.process(claim_data)
print(f"Policy Valid: {result.status}")
```

**Expected Results:**
- ✅ Status: "approved" or "needs_review"
- ✅ Policy validation checks working
- ✅ Coverage period validation
- ✅ Waiting period checks

### **2. End-to-End Claim Testing**

#### **Valid Claim Scenario**
```bash
# Test with valid claim data
python -c "
from agents.orchestrator_agent import ClaimOrchestratorAgent

orchestrator = ClaimOrchestratorAgent()
claim_data = {
    'claim_id': 'VALID_TEST_001',
    'documents': [{'file_name': 'discharge.pdf', 'file_path': 'uploads/test.pdf'}],
    'policy_details': {
        'status': 'active',
        'sum_insured': 500000,
        'premium_status': 'paid'
    },
    'claim_details': {
        'patient_name': 'John Doe',
        'claimed_amount': 100000,
        'diagnosis': 'Appendicitis'
    }
}
result = orchestrator.process(claim_data)
print(f'Decision: {result.data.get(\"final_decision\", {}).get(\"decision\")}')
print(f'Confidence: {result.confidence}')
print(f'Payable Amount: {result.data.get(\"financial_calculation\", {}).get(\"payable_amount\", 0)}')
"
```

#### **High Fraud Risk Scenario**
```bash
# Test with suspicious claim patterns
python -c "
from agents.orchestrator_agent import ClaimOrchestratorAgent

orchestrator = ClaimOrchestratorAgent()
claim_data = {
    'claim_id': 'FRAUD_TEST_001',
    'documents': [{'file_name': 'suspicious.pdf', 'file_path': 'uploads/test.pdf'}],
    'policy_details': {
        'claim_history': [
            {'months_ago': 1, 'claimed_amount': 200000},
            {'months_ago': 2, 'claimed_amount': 150000}
        ]
    },
    'claim_details': {
        'claimed_amount': 500000,
        'number_of_days': 1  # Suspicious: high amount for 1 day
    }
}
result = orchestrator.process(claim_data)
print(f'Fraud Risk: {result.data.get(\"validation_results\", {}).get(\"fraud_agent\", {}).get(\"status\")}')
print(f'Decision: {result.data.get(\"final_decision\", {}).get(\"decision\")}')
"
```

### **3. API Endpoint Testing**

#### **Health Check**
```bash
curl -X GET http://localhost:8001/ \
  -H "Content-Type: application/json"
```

#### **Submit Claim**
```bash
curl -X POST http://localhost:8001/claim/submit \
  -H "Content-Type: application/json" \
  -d '{
    "claim_id": "API_TEST_001",
    "policy_number": "POL123456",
    "patient_name": "Test Patient",
    "documents": [
      {
        "file_name": "discharge_summary.pdf",
        "file_path": "uploads/test.pdf"
      }
    ],
    "policy_details": {
      "policy_number": "POL123456",
      "sum_insured": 500000,
      "premium_status": "paid"
    }
  }'
```

#### **Upload and Process**
```bash
curl -X POST http://localhost:8001/claim/upload-and-process \
  -F "files=@test_document.pdf" \
  -F "policy_number=POL123456" \
  -F "policy_holder_name=Test User" \
  -F "sum_insured=500000" \
  -F "premium_status=paid"
```

### **4. Performance Testing**

#### **Load Testing**
```bash
# Test multiple concurrent claims
python -c "
import asyncio
import aiohttp
import time

async def test_concurrent_claims():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(10):
            claim_data = {
                'claim_id': f'CONCURRENT_TEST_{i}',
                'policy_number': f'POL{i:06d}',
                'patient_name': f'Patient {i}',
                'documents': [],
                'policy_details': {'sum_insured': 500000, 'premium_status': 'paid'}
            }
            task = session.post('http://localhost:8001/claim/submit', json=claim_data)
            tasks.append(task)
        
        start_time = time.time()
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        successful = sum(1 for r in responses if not isinstance(r, Exception) and r.status == 200)
        print(f'Successful: {successful}/10')
        print(f'Total time: {end_time - start_time:.2f}s')
        print(f'Average per claim: {(end_time - start_time)/10:.2f}s')

asyncio.run(test_concurrent_claims())
"
```

#### **Memory Usage Testing**
```bash
# Monitor memory during processing
python -c "
import psutil
import os
from agents.orchestrator_agent import ClaimOrchestratorAgent

def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # MB

orchestrator = ClaimOrchestratorAgent()

# Test memory before
mem_before = get_memory_usage()
print(f'Memory before: {mem_before:.2f} MB')

# Process multiple claims
for i in range(50):
    claim_data = {
        'claim_id': f'MEM_TEST_{i}',
        'documents': [],
        'policy_details': {'sum_insured': 500000},
        'claim_details': {'claimed_amount': 100000}
    }
    result = orchestrator.process(claim_data)

# Test memory after
mem_after = get_memory_usage()
print(f'Memory after: {mem_after:.2f} MB')
print(f'Memory increase: {mem_after - mem_before:.2f} MB')
print(f'Memory per claim: {(mem_after - mem_before)/50:.2f} MB')
"
```

### **5. Edge Case Testing**

#### **Missing Documents**
```bash
curl -X POST http://localhost:8001/claim/submit \
  -H "Content-Type: application/json" \
  -d '{
    "claim_id": "EDGE_TEST_001",
    "documents": [],
    "policy_details": {"sum_insured": 500000}
  }'
```

#### **Expired Policy**
```bash
curl -X POST http://localhost:8001/claim/submit \
  -H "Content-Type: application/json" \
  -d '{
    "claim_id": "EDGE_TEST_002",
    "policy_details": {
      "end_date": "2023-12-31",
      "status": "expired"
    }
  }'
```

#### **Extremely High Amount**
```bash
curl -X POST http://localhost:8001/claim/submit \
  -H "Content-Type: application/json" \
  -d '{
    "claim_id": "EDGE_TEST_003",
    "claim_details": {
      "claimed_amount": 10000000
    }
  }'
```

## 📊 Test Result Analysis

### **Success Criteria**

| Test Category | Success Rate Target | Confidence Target | Response Time Target |
|---------------|-------------------|-------------------|-------------------|
| Individual Agents | 95% | > 0.8 | < 5s |
| End-to-End | 90% | > 0.7 | < 30s |
| API Endpoints | 95% | N/A | < 2s |
| Performance | 90% | N/A | < 30s per claim |
| Edge Cases | 85% | N/A | N/A |

### **Expected Test Results**

#### **Valid Claim**
- ✅ Decision: "approved"
- ✅ Confidence: > 0.8
- ✅ Payable amount: Calculated correctly
- ✅ Processing time: < 30s

#### **Fraud Risk Claim**
- ✅ Decision: "rejected" or "needs_review"
- ✅ Fraud risk: "medium_risk" or "high_risk"
- ✅ Reasoning: Clear fraud indicators

#### **Policy Violation**
- ✅ Decision: "rejected"
- ✅ Policy validation: Failed
- ✅ Reasoning: Clear policy violation

## 🔧 Troubleshooting

### **Common Issues**

#### **Ollama Not Running**
```bash
# Check if Ollama is running
ollama list

# Start Ollama
ollama serve

# Pull required model
ollama pull mistral
```

#### **API Server Not Starting**
```bash
# Check port availability
lsof -i :8001

# Start with different port
python claim_adjudication_api.py  # Uses default port
# Or modify to use port 8002
```

#### **Memory Issues**
```bash
# Monitor system memory
top -p $(pgrep -f python)

# Increase swap if needed
sudo swapon /swapfile
```

#### **Slow Processing**
```bash
# Check LLM response time
python -c "
import ollama
import time
start = time.time()
response = ollama.chat(model='mistral', messages=[{'role': 'user', 'content': 'Test'}])
end = time.time()
print(f'LLM response time: {end - start:.2f}s')
"
```

### **Debug Mode**

#### **Enable Debug Logging**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or set for specific agents
logging.getLogger('agent.policy_agent').setLevel(logging.DEBUG)
```

#### **Test Single Agent**
```bash
# Test only document agent
python -c "
from agents.document_agent import DocumentProcessingAgent
agent = DocumentProcessingAgent()
result = agent.process({'claim_id': 'DEBUG', 'documents': []})
print(result.to_dict())
"
```

## 📈 Continuous Testing

### **Automated Testing Pipeline**
```bash
# Create test script
cat > run_tests.sh << 'EOF'
#!/bin/bash
echo "Starting automated tests..."

# Start services
ollama serve &
OLLAMA_PID=$!
sleep 5

python claim_adjudication_api.py &
API_PID=$!
sleep 10

# Run tests
python test_complete_system.py
python test_api_endpoints.py

# Cleanup
kill $OLLAMA_PID $API_PID
echo "Tests completed"
EOF

chmod +x run_tests.sh
./run_tests.sh
```

### **Performance Monitoring**
```bash
# Monitor during tests
watch -n 1 '
echo "=== System Resources ==="
echo "CPU: $(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)% id.*/\1/" | cut -d. -f1)"
echo "Memory: $(free -m | awk '"'"'"'/Mem/{printf "%.1f%%", $3/$2*100}'"'"')"
echo "=== API Status ==="
curl -s http://localhost:8001/agents/status | python -m json.tool
'
```

## 🎯 Production Readiness Checklist

### **Functional Requirements**
- [ ] All 7 agents working correctly
- [ ] End-to-end claim processing successful
- [ ] All API endpoints responding
- [ ] Error handling working
- [ ] Data consistency maintained

### **Performance Requirements**
- [ ] Single claim processing < 30 seconds
- [ ] API response time < 2 seconds
- [ ] Memory usage < 500MB per claim
- [ ] Concurrent processing supported

### **Quality Requirements**
- [ ] Decision confidence > 0.8 for valid claims
- [ ] Clear reasoning for all decisions
- [ ] Comprehensive audit trail
- [ ] Consistent results across runs

### **Security Requirements**
- [ ] Input validation working
- [ ] Error messages don't leak sensitive info
- [ ] Rate limiting implemented
- [ ] Audit logging enabled

## 🚀 Next Steps

1. **Run All Tests**: Execute complete test suite
2. **Analyze Results**: Review test reports
3. **Fix Issues**: Address any failing tests
4. **Performance Tuning**: Optimize slow components
5. **Load Testing**: Test with higher volumes
6. **Production Deployment**: Deploy to production environment

This comprehensive testing approach ensures your agentic AI claim adjudication system is production-ready and reliable!
