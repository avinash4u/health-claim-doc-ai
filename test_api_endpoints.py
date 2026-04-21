#!/usr/bin/env python3
"""
API Endpoint Testing Script
Tests all API endpoints of the claim adjudication system
"""

import requests
import json
import time
import os
from typing import Dict, Any

class APITester:
    """Test all API endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.test_results = []
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🌐 Starting API Endpoint Tests")
        print("=" * 50)
        
        # Test 1: Health Check
        self._test_health_check()
        
        # Test 2: Agent Status
        self._test_agent_status()
        
        # Test 3: Submit Claim
        self._test_submit_claim()
        
        # Test 4: Upload and Process Claim
        self._test_upload_and_process()
        
        # Test 5: Get Claim Status
        self._test_get_claim_status()
        
        # Test 6: List Claims
        self._test_list_claims()
        
        # Test 7: Analytics Dashboard
        self._test_analytics_dashboard()
        
        # Test 8: Error Handling
        self._test_error_handling()
        
        # Generate Report
        self._generate_api_report()
    
    def _test_health_check(self):
        """Test health check endpoint"""
        print("\n🏥 Testing Health Check")
        print("-" * 30)
        
        try:
            response = requests.get(f"{self.base_url}/")
            success = response.status_code == 200
            data = response.json() if success else {}
            
            self._record_api_test(
                "Health Check",
                success,
                response.status_code,
                data.get("message", ""),
                0
            )
            
            if success:
                print(f"  ✅ Health Check: {data.get('message')}")
            else:
                print(f"  ❌ Health Check failed: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Health Check error: {str(e)}")
            self._record_api_test("Health Check", False, 0, str(e), 0)
    
    def _test_agent_status(self):
        """Test agent status endpoint"""
        print("\n🤖 Testing Agent Status")
        print("-" * 30)
        
        try:
            response = requests.get(f"{self.base_url}/agents/status")
            success = response.status_code == 200
            data = response.json() if success else {}
            
            # Check if all agents are active
            all_active = all(status == "active" for status in data.values())
            
            self._record_api_test(
                "Agent Status",
                success and all_active,
                response.status_code,
                f"Active agents: {len(data)}",
                0
            )
            
            if success and all_active:
                print(f"  ✅ All {len(data)} agents active")
            else:
                print(f"  ❌ Agent status check failed")
                
        except Exception as e:
            print(f"  ❌ Agent status error: {str(e)}")
            self._record_api_test("Agent Status", False, 0, str(e), 0)
    
    def _test_submit_claim(self):
        """Test claim submission endpoint"""
        print("\n📋 Testing Claim Submission")
        print("-" * 30)
        
        claim_data = {
            "claim_id": "API_TEST_001",
            "policy_number": "POL123456",
            "patient_name": "Test Patient",
            "documents": [
                {
                    "file_name": "test_document.pdf",
                    "file_path": "uploads/test.pdf",
                    "file_size": 100000
                }
            ],
            "policy_details": {
                "policy_number": "POL123456",
                "policy_holder_name": "Test Patient",
                "sum_insured": 500000,
                "start_date": "2023-01-01",
                "end_date": "2024-12-31",
                "policy_type": "individual",
                "premium_status": "paid",
                "waiting_periods": {},
                "exclusions": [],
                "room_rent_limit": 5000,
                "co_payment_percentage": 20,
                "deductible_amount": 10000
            }
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/claim/submit",
                json=claim_data,
                headers={"Content-Type": "application/json"}
            )
            processing_time = time.time() - start_time
            
            success = response.status_code == 200
            data = response.json() if success else {}
            
            self._record_api_test(
                "Submit Claim",
                success,
                response.status_code,
                f"Decision: {data.get('decision', 'unknown')}",
                processing_time
            )
            
            if success:
                print(f"  ✅ Claim submitted: {data.get('decision')} (Time: {processing_time:.2f}s)")
            else:
                print(f"  ❌ Claim submission failed: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Claim submission error: {str(e)}")
            self._record_api_test("Submit Claim", False, 0, str(e), 0)
    
    def _test_upload_and_process(self):
        """Test upload and process endpoint"""
        print("\n📤 Testing Upload and Process")
        print("-" * 30)
        
        # Create a test file for upload
        test_file_path = "test_upload.txt"
        with open(test_file_path, "w") as f:
            f.write("Test claim document content")
        
        try:
            with open(test_file_path, "rb") as f:
                files = {
                    "files": ("test_document.txt", f, "text/plain")
                }
                data = {
                    "policy_number": "POL123456",
                    "policy_holder_name": "Test User",
                    "sum_insured": 300000,
                    "start_date": "2023-01-01",
                    "end_date": "2024-12-31",
                    "policy_type": "individual",
                    "premium_status": "paid",
                    "co_payment_percentage": 20,
                    "deductible_amount": 5000
                }
                
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/claim/upload-and-process",
                    files=files,
                    data=data
                )
                processing_time = time.time() - start_time
                
                success = response.status_code == 200
                response_data = response.json() if success else {}
                
                self._record_api_test(
                    "Upload and Process",
                    success,
                    response.status_code,
                    f"Claim ID: {response_data.get('claim_id', 'unknown')}",
                    processing_time
                )
                
                if success:
                    print(f"  ✅ Upload successful: {response_data.get('claim_id')} (Time: {processing_time:.2f}s)")
                else:
                    print(f"  ❌ Upload failed: {response.status_code}")
                    
        except Exception as e:
            print(f"  ❌ Upload error: {str(e)}")
            self._record_api_test("Upload and Process", False, 0, str(e), 0)
        finally:
            # Clean up test file
            if os.path.exists(test_file_path):
                os.remove(test_file_path)
    
    def _test_get_claim_status(self):
        """Test get claim status endpoint"""
        print("\n📊 Testing Get Claim Status")
        print("-" * 30)
        
        try:
            # Try to get status of a test claim
            response = requests.get(f"{self.base_url}/claim/API_TEST_001")
            
            if response.status_code == 200:
                data = response.json()
                self._record_api_test(
                    "Get Claim Status",
                    True,
                    response.status_code,
                    f"Status: {data.get('status', 'unknown')}",
                    0
                )
                print(f"  ✅ Claim status: {data.get('status')}")
            elif response.status_code == 404:
                self._record_api_test(
                    "Get Claim Status",
                    True,  # 404 is expected for non-existent claim
                    response.status_code,
                    "Claim not found (expected)",
                    0
                )
                print(f"  ✅ Claim not found (expected behavior)")
            else:
                self._record_api_test(
                    "Get Claim Status",
                    False,
                    response.status_code,
                    "Unexpected status code",
                    0
                )
                print(f"  ❌ Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Get claim status error: {str(e)}")
            self._record_api_test("Get Claim Status", False, 0, str(e), 0)
    
    def _test_list_claims(self):
        """Test list claims endpoint"""
        print("\n📋 Testing List Claims")
        print("-" * 30)
        
        try:
            response = requests.get(f"{self.base_url}/claims")
            success = response.status_code == 200
            data = response.json() if success else {}
            
            claim_count = data.get("total_claims", 0)
            
            self._record_api_test(
                "List Claims",
                success,
                response.status_code,
                f"Total claims: {claim_count}",
                0
            )
            
            if success:
                print(f"  ✅ Claims listed: {claim_count} claims found")
            else:
                print(f"  ❌ List claims failed: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ List claims error: {str(e)}")
            self._record_api_test("List Claims", False, 0, str(e), 0)
    
    def _test_analytics_dashboard(self):
        """Test analytics dashboard endpoint"""
        print("\n📈 Testing Analytics Dashboard")
        print("-" * 30)
        
        try:
            response = requests.get(f"{self.base_url}/analytics/dashboard")
            success = response.status_code == 200
            data = response.json() if success else {}
            
            total_claims = data.get("total_claims", 0)
            approval_rate = data.get("approval_rate", 0)
            
            self._record_api_test(
                "Analytics Dashboard",
                success,
                response.status_code,
                f"Claims: {total_claims}, Approval rate: {approval_rate:.1f}%",
                0
            )
            
            if success:
                print(f"  ✅ Analytics: {total_claims} claims, {approval_rate:.1f}% approval rate")
            else:
                print(f"  ❌ Analytics failed: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Analytics error: {str(e)}")
            self._record_api_test("Analytics Dashboard", False, 0, str(e), 0)
    
    def _test_error_handling(self):
        """Test error handling"""
        print("\n⚠️ Testing Error Handling")
        print("-" * 30)
        
        # Test invalid claim submission
        invalid_claim = {
            "claim_id": "",  # Invalid empty claim ID
            "policy_number": "POL123456",
            "documents": [],  # Empty documents
            "policy_details": {}  # Empty policy details
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/claim/submit",
                json=invalid_claim,
                headers={"Content-Type": "application/json"}
            )
            
            # Should return error (400 or 500)
            error_handled = response.status_code >= 400
            
            self._record_api_test(
                "Error Handling",
                error_handled,
                response.status_code,
                "Proper error response" if error_handled else "Error not handled",
                0
            )
            
            if error_handled:
                print(f"  ✅ Error handled properly: {response.status_code}")
            else:
                print(f"  ❌ Error not handled: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error handling test failed: {str(e)}")
            self._record_api_test("Error Handling", False, 0, str(e), 0)
    
    def _record_api_test(self, test_name: str, success: bool, status_code: int, details: str, response_time: float):
        """Record API test result"""
        self.test_results.append({
            "test_name": test_name,
            "success": success,
            "status_code": status_code,
            "details": details,
            "response_time": response_time,
            "timestamp": time.time()
        })
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"    {status} {test_name} (Status: {status_code})")
        if details:
            print(f"      {details}")
        if response_time > 0:
            print(f"      Response time: {response_time:.3f}s")
    
    def _generate_api_report(self):
        """Generate API test report"""
        print("\n" + "=" * 50)
        print("🌐 API TEST REPORT")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        avg_response_time = sum(result["response_time"] for result in self.test_results if result["response_time"] > 0) / len([r for r in self.test_results if r["response_time"] > 0]) if self.test_results else 0
        
        print(f"📊 API Test Results:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ({success_rate:.1f}%)")
        print(f"   Failed: {failed_tests} ({100-success_rate:.1f}%)")
        print(f"   Average Response Time: {avg_response_time:.3f}s")
        
        # Endpoint-wise results
        print(f"\n🔗 Endpoint-wise Results:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            response_time = f" ({result['response_time']:.3f}s)" if result["response_time"] > 0 else ""
            print(f"   {status} {result['test_name']}: {result['status_code']}{response_time}")
        
        # Save report
        report_data = {
            "test_summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": success_rate,
                "average_response_time": avg_response_time,
                "test_date": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "detailed_results": self.test_results
        }
        
        with open("api_test_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n💾 API test report saved to: api_test_report.json")
        
        # API readiness assessment
        print(f"\n🚀 API Readiness Assessment:")
        if success_rate >= 90 and avg_response_time < 2.0:
            print("   🟢 API READY FOR PRODUCTION")
        elif success_rate >= 75:
            print("   🟡 API NEEDS MINOR FIXES")
        else:
            print("   🔴 API NEEDS MAJOR IMPROVEMENTS")

if __name__ == "__main__":
    print("🌐 Starting API Endpoint Tests")
    print("Make sure the claim adjudication API is running:")
    print("python claim_adjudication_api.py")
    print()
    
    tester = APITester()
    tester.run_all_tests()
