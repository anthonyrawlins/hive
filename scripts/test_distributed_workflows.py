#!/usr/bin/env python3
"""
Comprehensive Testing Suite for Hive Distributed Workflows
Tests all aspects of the distributed development workflow system
"""

import asyncio
import aiohttp
import json
import time
import sys
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import argparse
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Test result data class"""
    name: str
    success: bool
    duration: float
    message: str
    data: Optional[Dict[str, Any]] = None

class DistributedWorkflowTester:
    """Comprehensive tester for distributed workflow system"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.test_results: List[TestResult] = []
        self.workflow_ids: List[str] = []
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=300)  # 5 minute timeout
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def run_test(self, test_name: str, test_func, *args, **kwargs) -> TestResult:
        """Run a single test with error handling and timing"""
        logger.info(f"🧪 Running test: {test_name}")
        start_time = time.time()
        
        try:
            result = await test_func(*args, **kwargs)
            duration = time.time() - start_time
            
            if isinstance(result, bool):
                success = result
                message = "Test passed" if success else "Test failed"
                data = None
            elif isinstance(result, dict):
                success = result.get('success', True)
                message = result.get('message', 'Test completed')
                data = result.get('data')
            else:
                success = True
                message = str(result)
                data = None
            
            test_result = TestResult(
                name=test_name,
                success=success,
                duration=duration,
                message=message,
                data=data
            )
            
            self.test_results.append(test_result)
            
            if success:
                logger.info(f"✅ {test_name} - {message} ({duration:.2f}s)")
            else:
                logger.error(f"❌ {test_name} - {message} ({duration:.2f}s)")
            
            return test_result
            
        except Exception as e:
            duration = time.time() - start_time
            error_message = f"Exception: {str(e)}"
            logger.error(f"💥 {test_name} - {error_message} ({duration:.2f}s)")
            logger.debug(traceback.format_exc())
            
            test_result = TestResult(
                name=test_name,
                success=False,
                duration=duration,
                message=error_message
            )
            
            self.test_results.append(test_result)
            return test_result
    
    async def test_system_health(self) -> Dict[str, Any]:
        """Test basic system health"""
        async with self.session.get(f"{self.base_url}/health") as response:
            if response.status != 200:
                return {
                    'success': False,
                    'message': f"Health check failed with status {response.status}"
                }
            
            health_data = await response.json()
            
            # Check component health
            components = health_data.get('components', {})
            unhealthy_components = [
                name for name, status in components.items()
                if status not in ['operational', 'healthy']
            ]
            
            if unhealthy_components:
                return {
                    'success': False,
                    'message': f"Unhealthy components: {unhealthy_components}",
                    'data': health_data
                }
            
            return {
                'success': True,
                'message': "All system components healthy",
                'data': health_data
            }
    
    async def test_cluster_status(self) -> Dict[str, Any]:
        """Test cluster status endpoint"""
        async with self.session.get(f"{self.base_url}/api/distributed/cluster/status") as response:
            if response.status != 200:
                return {
                    'success': False,
                    'message': f"Cluster status failed with status {response.status}"
                }
            
            cluster_data = await response.json()
            
            total_agents = cluster_data.get('total_agents', 0)
            healthy_agents = cluster_data.get('healthy_agents', 0)
            
            if total_agents == 0:
                return {
                    'success': False,
                    'message': "No agents found in cluster",
                    'data': cluster_data
                }
            
            if healthy_agents == 0:
                return {
                    'success': False,
                    'message': "No healthy agents in cluster",
                    'data': cluster_data
                }
            
            return {
                'success': True,
                'message': f"{healthy_agents}/{total_agents} agents healthy",
                'data': cluster_data
            }
    
    async def test_workflow_submission(self) -> Dict[str, Any]:
        """Test workflow submission"""
        workflow_data = {
            "name": "Test REST API Development",
            "requirements": "Create a simple REST API with user authentication, CRUD operations for a todo list, and comprehensive error handling.",
            "context": "This is a test workflow to validate the distributed system functionality.",
            "language": "python",
            "priority": "high"
        }
        
        async with self.session.post(
            f"{self.base_url}/api/distributed/workflows",
            json=workflow_data
        ) as response:
            if response.status != 200:
                return {
                    'success': False,
                    'message': f"Workflow submission failed with status {response.status}"
                }
            
            result = await response.json()
            workflow_id = result.get('workflow_id')
            
            if not workflow_id:
                return {
                    'success': False,
                    'message': "No workflow_id returned",
                    'data': result
                }
            
            self.workflow_ids.append(workflow_id)
            
            return {
                'success': True,
                'message': f"Workflow submitted successfully: {workflow_id}",
                'data': result
            }
    
    async def test_workflow_status_tracking(self) -> Dict[str, Any]:
        """Test workflow status tracking"""
        if not self.workflow_ids:
            return {
                'success': False,
                'message': "No workflows available for status tracking"
            }
        
        workflow_id = self.workflow_ids[0]
        
        # Poll workflow status for up to 2 minutes
        max_wait_time = 120  # 2 minutes
        poll_interval = 5    # 5 seconds
        start_time = time.time()
        
        status_changes = []
        
        while time.time() - start_time < max_wait_time:
            async with self.session.get(
                f"{self.base_url}/api/distributed/workflows/{workflow_id}"
            ) as response:
                if response.status != 200:
                    return {
                        'success': False,
                        'message': f"Status check failed with status {response.status}"
                    }
                
                status_data = await response.json()
                current_status = status_data.get('status', 'unknown')
                progress = status_data.get('progress', 0)
                
                status_changes.append({
                    'timestamp': datetime.now().isoformat(),
                    'status': current_status,
                    'progress': progress,
                    'completed_tasks': status_data.get('completed_tasks', 0),
                    'total_tasks': status_data.get('total_tasks', 0)
                })
                
                logger.info(f"Workflow {workflow_id}: {current_status} ({progress:.1f}%)")
                
                if current_status in ['completed', 'failed']:
                    break
                
                await asyncio.sleep(poll_interval)
        
        final_status = status_changes[-1] if status_changes else {}
        
        return {
            'success': True,
            'message': f"Status tracking completed. Final status: {final_status.get('status', 'unknown')}",
            'data': {
                'workflow_id': workflow_id,
                'status_changes': status_changes,
                'final_status': final_status
            }
        }
    
    async def test_multiple_workflow_submission(self) -> Dict[str, Any]:
        """Test concurrent workflow submission"""
        workflows = [
            {
                "name": "Frontend React App",
                "requirements": "Create a React application with TypeScript, routing, and state management.",
                "language": "typescript",
                "priority": "normal"
            },
            {
                "name": "Python Data Analysis",
                "requirements": "Create a data analysis script with pandas, visualization, and reporting.",
                "language": "python",
                "priority": "normal"
            },
            {
                "name": "Microservice Architecture",
                "requirements": "Design a microservices system with API gateway and service discovery.",
                "language": "go",
                "priority": "high"
            }
        ]
        
        submission_tasks = []
        for workflow in workflows:
            task = self.session.post(
                f"{self.base_url}/api/distributed/workflows",
                json=workflow
            )
            submission_tasks.append(task)
        
        try:
            responses = await asyncio.gather(*submission_tasks)
            
            submitted_workflows = []
            for i, response in enumerate(responses):
                if response.status == 200:
                    result = await response.json()
                    workflow_id = result.get('workflow_id')
                    if workflow_id:
                        self.workflow_ids.append(workflow_id)
                        submitted_workflows.append({
                            'name': workflows[i]['name'],
                            'workflow_id': workflow_id
                        })
                response.close()
            
            return {
                'success': len(submitted_workflows) == len(workflows),
                'message': f"Submitted {len(submitted_workflows)}/{len(workflows)} workflows concurrently",
                'data': {'submitted_workflows': submitted_workflows}
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Concurrent submission failed: {str(e)}"
            }
    
    async def test_workflow_cancellation(self) -> Dict[str, Any]:
        """Test workflow cancellation"""
        if not self.workflow_ids:
            return {
                'success': False,
                'message': "No workflows available for cancellation test"
            }
        
        # Submit a new workflow specifically for cancellation
        workflow_data = {
            "name": "Cancellation Test Workflow",
            "requirements": "This workflow will be cancelled during execution to test cancellation functionality.",
            "language": "python",
            "priority": "low"
        }
        
        async with self.session.post(
            f"{self.base_url}/api/distributed/workflows",
            json=workflow_data
        ) as response:
            if response.status != 200:
                return {
                    'success': False,
                    'message': "Failed to submit workflow for cancellation test"
                }
            
            result = await response.json()
            workflow_id = result.get('workflow_id')
            
            if not workflow_id:
                return {
                    'success': False,
                    'message': "No workflow_id returned for cancellation test"
                }
        
        # Wait a bit to let the workflow start
        await asyncio.sleep(2)
        
        # Cancel the workflow
        async with self.session.post(
            f"{self.base_url}/api/distributed/workflows/{workflow_id}/cancel"
        ) as response:
            if response.status != 200:
                return {
                    'success': False,
                    'message': f"Cancellation failed with status {response.status}"
                }
            
            cancel_result = await response.json()
            
            return {
                'success': True,
                'message': f"Workflow cancelled successfully: {workflow_id}",
                'data': cancel_result
            }
    
    async def test_performance_metrics(self) -> Dict[str, Any]:
        """Test performance metrics endpoint"""
        async with self.session.get(f"{self.base_url}/api/distributed/performance/metrics") as response:
            if response.status != 200:
                return {
                    'success': False,
                    'message': f"Performance metrics failed with status {response.status}"
                }
            
            metrics_data = await response.json()
            
            required_fields = ['total_workflows', 'completed_workflows', 'agent_performance']
            missing_fields = [field for field in required_fields if field not in metrics_data]
            
            if missing_fields:
                return {
                    'success': False,
                    'message': f"Missing required metrics fields: {missing_fields}",
                    'data': metrics_data
                }
            
            return {
                'success': True,
                'message': "Performance metrics retrieved successfully",
                'data': metrics_data
            }
    
    async def test_cluster_optimization(self) -> Dict[str, Any]:
        """Test cluster optimization trigger"""
        async with self.session.post(f"{self.base_url}/api/distributed/cluster/optimize") as response:
            if response.status != 200:
                return {
                    'success': False,
                    'message': f"Cluster optimization failed with status {response.status}"
                }
            
            result = await response.json()
            
            return {
                'success': True,
                'message': "Cluster optimization triggered successfully",
                'data': result
            }
    
    async def test_workflow_listing(self) -> Dict[str, Any]:
        """Test workflow listing functionality"""
        async with self.session.get(f"{self.base_url}/api/distributed/workflows") as response:
            if response.status != 200:
                return {
                    'success': False,
                    'message': f"Workflow listing failed with status {response.status}"
                }
            
            workflows = await response.json()
            
            if not isinstance(workflows, list):
                return {
                    'success': False,
                    'message': "Workflow listing should return a list"
                }
            
            return {
                'success': True,
                'message': f"Retrieved {len(workflows)} workflows",
                'data': {'workflow_count': len(workflows), 'workflows': workflows[:5]}  # First 5 for brevity
            }
    
    async def test_agent_health_monitoring(self) -> Dict[str, Any]:
        """Test individual agent health monitoring"""
        # First get cluster status to get agent list
        async with self.session.get(f"{self.base_url}/api/distributed/cluster/status") as response:
            if response.status != 200:
                return {
                    'success': False,
                    'message': "Failed to get cluster status for agent testing"
                }
            
            cluster_data = await response.json()
            agents = cluster_data.get('agents', [])
            
            if not agents:
                return {
                    'success': False,
                    'message': "No agents found for health monitoring test"
                }
        
        # Test individual agent health
        agent_results = []
        for agent in agents[:3]:  # Test first 3 agents
            agent_id = agent.get('id')
            if agent_id:
                async with self.session.get(
                    f"{self.base_url}/api/distributed/agents/{agent_id}/tasks"
                ) as response:
                    agent_results.append({
                        'agent_id': agent_id,
                        'status_code': response.status,
                        'health_status': agent.get('health_status', 'unknown')
                    })
        
        successful_checks = sum(1 for result in agent_results if result['status_code'] == 200)
        
        return {
            'success': successful_checks > 0,
            'message': f"Agent health monitoring: {successful_checks}/{len(agent_results)} agents responding",
            'data': {'agent_results': agent_results}
        }
    
    async def run_comprehensive_test_suite(self) -> Dict[str, Any]:
        """Run the complete test suite"""
        logger.info("🚀 Starting Comprehensive Distributed Workflow Test Suite")
        logger.info("=" * 60)
        
        # Define test sequence
        tests = [
            ("System Health Check", self.test_system_health),
            ("Cluster Status", self.test_cluster_status),
            ("Single Workflow Submission", self.test_workflow_submission),
            ("Multiple Workflow Submission", self.test_multiple_workflow_submission),
            ("Workflow Status Tracking", self.test_workflow_status_tracking),
            ("Workflow Cancellation", self.test_workflow_cancellation),
            ("Performance Metrics", self.test_performance_metrics),
            ("Cluster Optimization", self.test_cluster_optimization),
            ("Workflow Listing", self.test_workflow_listing),
            ("Agent Health Monitoring", self.test_agent_health_monitoring),
        ]
        
        # Run all tests
        for test_name, test_func in tests:
            await self.run_test(test_name, test_func)
            await asyncio.sleep(1)  # Brief pause between tests
        
        # Generate summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result.success)
        failed_tests = total_tests - passed_tests
        total_duration = sum(result.duration for result in self.test_results)
        
        summary = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
            'total_duration': total_duration,
            'workflow_ids_created': self.workflow_ids
        }
        
        logger.info("=" * 60)
        logger.info("📊 Test Suite Summary:")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   Passed: {passed_tests}")
        logger.info(f"   Failed: {failed_tests}")
        logger.info(f"   Success Rate: {summary['success_rate']:.1f}%")
        logger.info(f"   Total Duration: {total_duration:.2f}s")
        logger.info(f"   Workflows Created: {len(self.workflow_ids)}")
        
        if failed_tests > 0:
            logger.error("❌ Failed Tests:")
            for result in self.test_results:
                if not result.success:
                    logger.error(f"   - {result.name}: {result.message}")
        
        return summary
    
    def generate_detailed_report(self) -> str:
        """Generate a detailed test report"""
        report = []
        report.append("# Hive Distributed Workflow System - Test Report")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")
        
        # Summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result.success)
        failed_tests = total_tests - passed_tests
        total_duration = sum(result.duration for result in self.test_results)
        
        report.append("## Test Summary")
        report.append(f"- **Total Tests**: {total_tests}")
        report.append(f"- **Passed**: {passed_tests}")
        report.append(f"- **Failed**: {failed_tests}")
        report.append(f"- **Success Rate**: {(passed_tests/total_tests)*100:.1f}%")
        report.append(f"- **Total Duration**: {total_duration:.2f} seconds")
        report.append(f"- **Workflows Created**: {len(self.workflow_ids)}")
        report.append("")
        
        # Detailed results
        report.append("## Detailed Test Results")
        for result in self.test_results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            report.append(f"### {result.name} - {status}")
            report.append(f"- **Duration**: {result.duration:.2f}s")
            report.append(f"- **Message**: {result.message}")
            if result.data:
                report.append(f"- **Data**: ```json\n{json.dumps(result.data, indent=2)}\n```")
            report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        if failed_tests == 0:
            report.append("🎉 All tests passed! The distributed workflow system is functioning correctly.")
        else:
            report.append("⚠️ Some tests failed. Please review the failed tests and address any issues.")
            report.append("")
            report.append("### Failed Tests:")
            for result in self.test_results:
                if not result.success:
                    report.append(f"- **{result.name}**: {result.message}")
        
        return "\n".join(report)


async def main():
    """Main test execution function"""
    parser = argparse.ArgumentParser(description="Test Hive Distributed Workflow System")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL for the Hive API (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--output",
        help="Output file for detailed test report"
    )
    parser.add_argument(
        "--single-test",
        help="Run a single test by name"
    )
    
    args = parser.parse_args()
    
    try:
        async with DistributedWorkflowTester(args.url) as tester:
            if args.single_test:
                # Run single test
                test_methods = {
                    'health': tester.test_system_health,
                    'cluster': tester.test_cluster_status,
                    'submit': tester.test_workflow_submission,
                    'multiple': tester.test_multiple_workflow_submission,
                    'status': tester.test_workflow_status_tracking,
                    'cancel': tester.test_workflow_cancellation,
                    'metrics': tester.test_performance_metrics,
                    'optimize': tester.test_cluster_optimization,
                    'list': tester.test_workflow_listing,
                    'agents': tester.test_agent_health_monitoring,
                }
                
                if args.single_test in test_methods:
                    await tester.run_test(args.single_test, test_methods[args.single_test])
                else:
                    logger.error(f"Unknown test: {args.single_test}")
                    logger.info(f"Available tests: {', '.join(test_methods.keys())}")
                    return 1
            else:
                # Run full test suite
                summary = await tester.run_comprehensive_test_suite()
            
            # Generate and save report if requested
            if args.output:
                report = tester.generate_detailed_report()
                with open(args.output, 'w') as f:
                    f.write(report)
                logger.info(f"📄 Detailed report saved to: {args.output}")
            
            # Return appropriate exit code
            if args.single_test:
                return 0 if tester.test_results[-1].success else 1
            else:
                return 0 if summary['failed_tests'] == 0 else 1
                
    except KeyboardInterrupt:
        logger.info("❌ Test execution interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"💥 Test execution failed: {str(e)}")
        logger.debug(traceback.format_exc())
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)