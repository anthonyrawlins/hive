#!/usr/bin/env python3
"""
Direct coordination script for ROSEWOOD UI/UX QA testing
Since the main Hive coordination service is having issues, this script 
directly coordinates with ROSEWOOD for comprehensive UI/UX testing
"""

import json
import requests
import time
from pathlib import Path
import os

# ROSEWOOD Configuration
ROSEWOOD_ENDPOINT = "http://192.168.1.132:11434"
ROSEWOOD_MODEL = "deepseek-r1:8b"

# Project paths
PROJECT_ROOT = Path("/home/tony/AI/projects/hive")
FRONTEND_DIR = PROJECT_ROOT / "frontend"

def test_rosewood_connection():
    """Test if ROSEWOOD is accessible"""
    try:
        response = requests.get(f"{ROSEWOOD_ENDPOINT}/api/tags", timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Cannot connect to ROSEWOOD: {e}")
        return False

def get_file_content(file_path):
    """Get file content safely"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"⚠️  Could not read {file_path}: {e}")
        return None

def collect_frontend_files():
    """Collect all relevant frontend files for analysis"""
    files_to_analyze = []
    
    # Key files to examine
    key_files = [
        "src/App.tsx",
        "src/main.tsx", 
        "src/types/workflow.ts",
        "index.html",
        "src/index.css",
        "package.json",
        "tailwind.config.js",
        "vite.config.ts"
    ]
    
    for file_path in key_files:
        full_path = FRONTEND_DIR / file_path
        if full_path.exists():
            content = get_file_content(full_path)
            if content:
                files_to_analyze.append({
                    "path": str(full_path),
                    "relative_path": file_path,
                    "content": content,
                    "size": len(content)
                })
    
    # Collect additional React components
    src_dir = FRONTEND_DIR / "src"
    if src_dir.exists():
        for ext in ['*.tsx', '*.ts', '*.jsx', '*.js']:
            for file_path in src_dir.rglob(ext):
                if file_path.is_file() and file_path.stat().st_size < 50000:  # Skip very large files
                    content = get_file_content(file_path)
                    if content:
                        rel_path = file_path.relative_to(FRONTEND_DIR)
                        files_to_analyze.append({
                            "path": str(file_path),
                            "relative_path": str(rel_path),
                            "content": content,
                            "size": len(content)
                        })
    
    return files_to_analyze

def send_qa_request_to_rosewood(files_data):
    """Send comprehensive QA testing request to ROSEWOOD"""
    
    # Prepare the comprehensive QA testing prompt
    qa_prompt = f"""
🐝 HIVE UI/UX COMPREHENSIVE QA TESTING TASK

You are ROSEWOOD, a specialized Quality Assurance and Testing agent with expertise in:
- UI/UX Quality Assurance
- Accessibility Testing
- Visual Design Analysis
- User Experience Evaluation
- Frontend Code Review
- React/TypeScript Testing

**MISSION**: Perform comprehensive UI/UX QA testing on the Hive distributed AI orchestration platform frontend.

**FRONTEND CODEBASE ANALYSIS**:
{len(files_data)} files provided for analysis:

"""
    
    # Add file contents to prompt
    for file_info in files_data:
        qa_prompt += f"\n{'='*80}\n"
        qa_prompt += f"FILE: {file_info['relative_path']}\n"
        qa_prompt += f"SIZE: {file_info['size']} characters\n"
        qa_prompt += f"{'='*80}\n"
        qa_prompt += file_info['content']
        qa_prompt += f"\n{'='*80}\n"
    
    qa_prompt += """

**COMPREHENSIVE QA TESTING REQUIREMENTS**:

1. **Frontend Code Analysis**:
   - Review React/TypeScript code structure and quality
   - Identify coding best practices and anti-patterns
   - Check component architecture and reusability
   - Analyze state management and data flow
   - Review type definitions and interfaces

2. **User Interface Testing**:
   - Evaluate visual design consistency
   - Check responsive design implementation
   - Assess component rendering and layout
   - Verify color scheme and typography
   - Test navigation and user workflows

3. **Accessibility Testing**:
   - Screen reader compatibility assessment
   - Keyboard navigation evaluation
   - Color contrast and readability analysis
   - WCAG compliance review
   - Semantic HTML structure evaluation

4. **User Experience Evaluation**:
   - Workflow efficiency assessment
   - Error handling and user feedback analysis
   - Information architecture review
   - Performance optimization opportunities
   - Mobile responsiveness evaluation

5. **Technical Quality Assessment**:
   - Code maintainability and scalability
   - Security considerations
   - Performance optimization
   - Bundle size and loading efficiency
   - Browser compatibility

**DELIVERABLES REQUIRED**:

1. **Detailed QA Testing Report** with:
   - Executive summary of findings
   - Categorized issues by severity (Critical, High, Medium, Low)
   - Specific recommendations for each issue
   - Code examples and proposed fixes

2. **UI/UX Issues List** with:
   - Visual design inconsistencies
   - Layout and responsiveness problems
   - User interaction issues
   - Navigation problems

3. **Accessibility Compliance Assessment** with:
   - WCAG compliance level evaluation
   - Specific accessibility violations found
   - Recommendations for improvement
   - Priority accessibility fixes

4. **User Experience Recommendations** with:
   - Workflow optimization suggestions
   - User interface improvements
   - Performance enhancement opportunities
   - Mobile experience recommendations

5. **Priority Matrix** with:
   - Critical issues requiring immediate attention
   - High-priority improvements for next release
   - Medium-priority enhancements
   - Low-priority nice-to-have improvements

**RESPONSE FORMAT**:
Structure your response as a comprehensive QA report with clear sections, bullet points, and specific actionable recommendations. Include code snippets where relevant and prioritize issues by impact on user experience.

Begin your comprehensive QA analysis now!
"""
    
    # Send request to ROSEWOOD
    print("📡 Sending QA testing request to ROSEWOOD...")
    
    try:
        response = requests.post(
            f"{ROSEWOOD_ENDPOINT}/api/generate",
            json={
                "model": ROSEWOOD_MODEL,
                "prompt": qa_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "max_tokens": 8192
                }
            },
            timeout=300  # 5 minute timeout for comprehensive analysis
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', '')
        else:
            print(f"❌ Error from ROSEWOOD: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error communicating with ROSEWOOD: {e}")
        return None

def save_qa_report(qa_report):
    """Save the QA report to file"""
    timestamp = int(time.time())
    report_file = PROJECT_ROOT / f"results/rosewood_qa_report_{timestamp}.md"
    
    # Ensure results directory exists
    os.makedirs(PROJECT_ROOT / "results", exist_ok=True)
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 🐝 HIVE UI/UX Comprehensive QA Testing Report\n")
            f.write("**Generated by ROSEWOOD QA Agent**\n\n")
            f.write(f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Agent:** ROSEWOOD (deepseek-r1:8b)\n")
            f.write(f"**Endpoint:** {ROSEWOOD_ENDPOINT}\n\n")
            f.write("---\n\n")
            f.write(qa_report)
        
        print(f"✅ QA report saved to: {report_file}")
        return str(report_file)
        
    except Exception as e:
        print(f"❌ Error saving QA report: {e}")
        return None

def main():
    """Main coordination function"""
    print("🐝 HIVE UI/UX QA Testing Coordination")
    print("=" * 60)
    print(f"🎯 Target: ROSEWOOD ({ROSEWOOD_ENDPOINT})")
    print(f"📁 Frontend: {FRONTEND_DIR}")
    print()
    
    # Test ROSEWOOD connection
    if not test_rosewood_connection():
        print("❌ Cannot connect to ROSEWOOD. Ensure it's running and accessible.")
        return
    
    print("✅ ROSEWOOD is accessible")
    
    # Collect frontend files
    print("📁 Collecting frontend files for analysis...")
    files_data = collect_frontend_files()
    
    if not files_data:
        print("❌ No frontend files found for analysis")
        return
    
    print(f"✅ Collected {len(files_data)} files for analysis")
    
    total_size = sum(f['size'] for f in files_data)
    print(f"📊 Total content size: {total_size:,} characters")
    
    # Send QA request to ROSEWOOD
    print("\n🔄 Initiating comprehensive QA testing...")
    qa_report = send_qa_request_to_rosewood(files_data)
    
    if qa_report:
        print("✅ QA testing completed successfully!")
        print(f"📄 Report length: {len(qa_report):,} characters")
        
        # Save the report
        report_file = save_qa_report(qa_report)
        
        if report_file:
            print(f"\n🎉 QA testing coordination completed successfully!")
            print(f"📋 Report saved to: {report_file}")
            
            # Display summary
            print("\n" + "=" * 60)
            print("📊 QA TESTING SUMMARY")
            print("=" * 60)
            print(f"✅ Agent: ROSEWOOD (deepseek-r1:8b)")
            print(f"✅ Files analyzed: {len(files_data)}")
            print(f"✅ Report generated: {report_file}")
            print(f"✅ Content analyzed: {total_size:,} characters")
            print()
            
            # Show first part of the report
            print("📋 QA REPORT PREVIEW:")
            print("-" * 40)
            preview = qa_report[:1000] + "..." if len(qa_report) > 1000 else qa_report
            print(preview)
            print("-" * 40)
            
        else:
            print("❌ Failed to save QA report")
    else:
        print("❌ QA testing failed")

if __name__ == "__main__":
    main()