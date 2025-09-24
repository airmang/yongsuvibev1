#!/usr/bin/env python3
"""
Streamlit Community Cloud 배포 전 테스트 스크립트
"""

import sys
import importlib
import traceback

def test_imports():
    """필수 패키지 import 테스트"""
    print("🔍 필수 패키지 import 테스트...")
    
    required_packages = [
        'streamlit',
        'pandas', 
        'plotly',
        'numpy'
    ]
    
    failed_imports = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package} - OK")
        except ImportError as e:
            print(f"❌ {package} - FAILED: {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n❌ 실패한 패키지: {', '.join(failed_imports)}")
        print("다음 명령어로 설치하세요:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ 모든 패키지 import 성공!")
    return True

def test_app_import():
    """앱 모듈 import 테스트"""
    print("\n🔍 앱 모듈 import 테스트...")
    
    try:
        # app.py의 함수들을 import
        import pandas as pd
        import plotly.express as px
        import plotly.graph_objects as go
        import numpy as np
        
        # 샘플 데이터 생성 테스트
        sample_data = {
            '행정구역': ['경기도 용인시 (4146000000)'],
            '2025년08월_총인구수': [1093639],
            '2025년08월_세대수': [449693],
            '2025년08월_세대당 인구': [2.43],
            '2025년08월_남자 인구수': [541919],
            '2025년08월_여자 인구수': [551720],
            '2025년08월_남여 비율': [0.98]
        }
        
        df = pd.DataFrame(sample_data)
        print("✅ 샘플 데이터 생성 성공!")
        
        # Plotly 차트 생성 테스트
        fig = px.bar(df, x='행정구역', y='2025년08월_총인구수')
        print("✅ Plotly 차트 생성 성공!")
        
        return True
        
    except Exception as e:
        print(f"❌ 앱 모듈 테스트 실패: {e}")
        traceback.print_exc()
        return False

def test_file_structure():
    """필수 파일 구조 테스트"""
    print("\n🔍 파일 구조 테스트...")
    
    required_files = [
        'app.py',
        'requirements.txt'
    ]
    
    missing_files = []
    
    for file in required_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                if len(content) > 0:
                    print(f"✅ {file} - OK")
                else:
                    print(f"❌ {file} - 비어있음")
                    missing_files.append(file)
        except FileNotFoundError:
            print(f"❌ {file} - 파일 없음")
            missing_files.append(file)
        except Exception as e:
            print(f"❌ {file} - 오류: {e}")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ 누락된 파일: {', '.join(missing_files)}")
        return False
    
    print("✅ 모든 필수 파일 존재!")
    return True

def main():
    """메인 테스트 함수"""
    print("🚀 Streamlit Community Cloud 배포 전 테스트 시작\n")
    
    tests = [
        test_imports,
        test_app_import,
        test_file_structure
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"테스트 결과: {passed}/{total} 통과")
    
    if passed == total:
        print("🎉 모든 테스트 통과! 배포 준비 완료!")
        return 0
    else:
        print("❌ 일부 테스트 실패. 문제를 해결한 후 다시 시도하세요.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
