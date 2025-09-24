# 용인시 인구 데이터 시각화 대시보드

Streamlit을 이용한 용인시 인구 데이터 시각화 웹 애플리케이션입니다.

## 주요 기능

- 📊 **인구 피라미드**: 남녀 인구 구성 시각화
- 🏘️ **지역별 비교**: 구/군별 인구수 비교
- 👨‍👩‍👧‍👦 **세대 분석**: 세대당 인구수 분포 분석
- ⚖️ **성비 분석**: 지역별 남녀 비율 분석
- 🔍 **필터링**: 시도, 구/군, 읍/면/동별 데이터 필터링

## 설치 및 실행

### 로컬 실행

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. 애플리케이션 실행:
```bash
streamlit run app.py
```

### Streamlit Community Cloud 배포

1. GitHub 저장소에 코드 업로드
2. [Streamlit Community Cloud](https://share.streamlit.io/)에서 새 앱 생성
3. 저장소 연결 및 배포

## 데이터 형식

- CSV 파일은 CP-949 인코딩으로 저장되어 있습니다
- 컬럼: 행정구역, 총인구수, 세대수, 세대당 인구, 남자 인구수, 여자 인구수, 남여 비율

## 기술 스택

- **Frontend**: Streamlit
- **Visualization**: Plotly Express
- **Data Processing**: Pandas, NumPy
- **Font**: Noto Sans KR (한글 지원)

## 라이선스

MIT License
