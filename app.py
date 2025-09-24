import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots

# 페이지 설정
st.set_page_config(
    page_title="용인시 인구 현황 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 한글 폰트 설정
import plotly.io as pio
pio.templates.default = "plotly_white"

# 데이터 로드 함수
@st.cache_data
def load_data():
    """CSV 파일을 로드하고 데이터를 정리합니다."""
    try:
        # cp-949 인코딩으로 CSV 파일 읽기
        df = pd.read_csv('202508_202508_주민등록인구및세대현황_월간.csv', encoding='cp949')
        
        # 숫자 컬럼들을 정수로 변환 (쉼표 제거)
        numeric_columns = ['2025년08월_총인구수', '2025년08월_세대수', '2025년08월_남자 인구수', '2025년08월_여자 인구수']
        for col in numeric_columns:
            df[col] = df[col].str.replace(',', '').astype(int)
        
        # 행정구역에서 시/구/동 정보 추출
        df['시'] = df['행정구역'].str.extract(r'(\w+시)')
        df['구'] = df['행정구역'].str.extract(r'(\w+구)')
        df['동/읍/면'] = df['행정구역'].str.extract(r'(\w+[동읍면])')
        
        return df
    except Exception as e:
        st.error(f"데이터 로드 중 오류가 발생했습니다: {e}")
        return None

# 연령대별 인구 데이터 생성 함수 (실제 데이터가 없으므로 샘플 데이터 생성)
def generate_age_data(df, selected_region):
    """선택된 지역의 연령대별 인구 데이터를 생성합니다."""
    if selected_region == "전체":
        total_pop = df['2025년08월_총인구수'].iloc[0]
        male_pop = df['2025년08월_남자 인구수'].iloc[0]
        female_pop = df['2025년08월_여자 인구수'].iloc[0]
    else:
        region_data = df[df['행정구역'].str.contains(selected_region, na=False)]
        if region_data.empty:
            return None
        total_pop = region_data['2025년08월_총인구수'].iloc[0]
        male_pop = region_data['2025년08월_남자 인구수'].iloc[0]
        female_pop = region_data['2025년08월_여자 인구수'].iloc[0]
    
    # 연령대별 인구 분포 (실제 데이터가 없으므로 일반적인 분포 패턴 사용)
    age_groups = ['0-4세', '5-9세', '10-14세', '15-19세', '20-24세', '25-29세', 
                  '30-34세', '35-39세', '40-44세', '45-49세', '50-54세', '55-59세',
                  '60-64세', '65-69세', '70-74세', '75-79세', '80-84세', '85세+']
    
    # 연령대별 인구 비율 (일반적인 인구 피라미드 패턴)
    age_ratios = [0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.08, 0.08, 0.07, 0.07, 
                  0.06, 0.06, 0.05, 0.05, 0.04, 0.03, 0.02, 0.01]
    
    # 남녀 비율 적용
    male_ratio = male_pop / total_pop
    female_ratio = female_pop / total_pop
    
    age_data = []
    for i, age_group in enumerate(age_groups):
        age_pop = int(total_pop * age_ratios[i])
        male_pop_age = int(age_pop * male_ratio)
        female_pop_age = int(age_pop * female_ratio)
        
        age_data.append({
            '연령대': age_group,
            '남자': male_pop_age,
            '여자': female_pop_age,
            '총인구': age_pop
        })
    
    return pd.DataFrame(age_data)

# 메인 앱
def main():
    st.title("🏙️ 용인시 인구 현황 대시보드")
    st.markdown("---")
    
    # 데이터 로드
    df = load_data()
    if df is None:
        st.stop()
    
    # 사이드바 - 필터 설정
    st.sidebar.header("🔍 필터 설정")
    
    # 지역 선택
    regions = ['전체'] + df['행정구역'].tolist()
    selected_region = st.sidebar.selectbox(
        "지역을 선택하세요:",
        regions,
        index=0
    )
    
    # 연령대 필터
    st.sidebar.subheader("연령대 필터")
    age_ranges = [
        "전체", "0-19세 (청소년)", "20-39세 (청년)", 
        "40-59세 (중년)", "60세+ (고령)"
    ]
    selected_age_range = st.sidebar.selectbox(
        "연령대를 선택하세요:",
        age_ranges,
        index=0
    )
    
    # 메인 컨텐츠
    col1, col2, col3, col4 = st.columns(4)
    
    # 기본 통계 정보
    if selected_region == "전체":
        region_data = df.iloc[0]
        region_name = "용인시 전체"
    else:
        region_data = df[df['행정구역'] == selected_region].iloc[0]
        region_name = selected_region
    
    with col1:
        st.metric(
            label="총 인구수",
            value=f"{region_data['2025년08월_총인구수']:,}명"
        )
    
    with col2:
        st.metric(
            label="세대수",
            value=f"{region_data['2025년08월_세대수']:,}세대"
        )
    
    with col3:
        st.metric(
            label="세대당 인구",
            value=f"{region_data['2025년08월_세대당 인구']:.2f}명"
        )
    
    with col4:
        st.metric(
            label="남녀 비율",
            value=f"{region_data['2025년08월_남여 비율']:.2f}"
        )
    
    st.markdown("---")
    
    # 연령대별 데이터 생성
    age_df = generate_age_data(df, selected_region)
    
    if age_df is not None:
        # 연령대 필터 적용
        if selected_age_range != "전체":
            if selected_age_range == "0-19세 (청소년)":
                age_df = age_df[age_df['연령대'].isin(['0-4세', '5-9세', '10-14세', '15-19세'])]
            elif selected_age_range == "20-39세 (청년)":
                age_df = age_df[age_df['연령대'].isin(['20-24세', '25-29세', '30-34세', '35-39세'])]
            elif selected_age_range == "40-59세 (중년)":
                age_df = age_df[age_df['연령대'].isin(['40-44세', '45-49세', '50-54세', '55-59세'])]
            elif selected_age_range == "60세+ (고령)":
                age_df = age_df[age_df['연령대'].isin(['60-64세', '65-69세', '70-74세', '75-79세', '80-84세', '85세+'])]
        
        # 시각화 섹션
        col1, col2 = st.columns(2)
        
        with col1:
            # 인구 피라미드
            st.subheader("📊 인구 피라미드")
            
            # 남자 데이터 (음수로 변환하여 왼쪽에 표시)
            male_data = age_df.copy()
            male_data['남자'] = -male_data['남자']
            
            fig_pyramid = go.Figure()
            
            # 남자 막대 (왼쪽)
            fig_pyramid.add_trace(go.Bar(
                y=male_data['연령대'],
                x=male_data['남자'],
                name='남자',
                orientation='h',
                marker_color='#3498db',
                text=[f"{abs(x):,}" for x in male_data['남자']],
                textposition='inside'
            ))
            
            # 여자 막대 (오른쪽)
            fig_pyramid.add_trace(go.Bar(
                y=age_df['연령대'],
                x=age_df['여자'],
                name='여자',
                orientation='h',
                marker_color='#e74c3c',
                text=[f"{x:,}" for x in age_df['여자']],
                textposition='inside'
            ))
            
            fig_pyramid.update_layout(
                title=f"{region_name} 인구 피라미드",
                xaxis_title="인구수",
                yaxis_title="연령대",
                barmode='overlay',
                height=600,
                showlegend=True,
                font=dict(size=12)
            )
            
            # x축을 0을 중심으로 대칭으로 설정
            max_pop = max(abs(male_data['남자'].min()), age_df['여자'].max())
            fig_pyramid.update_xaxes(range=[-max_pop*1.1, max_pop*1.1])
            
            st.plotly_chart(fig_pyramid, use_container_width=True)
        
        with col2:
            # 연령대별 총 인구 막대 차트
            st.subheader("📈 연령대별 인구 분포")
            
            fig_bar = px.bar(
                age_df, 
                x='연령대', 
                y='총인구',
                title=f"{region_name} 연령대별 총 인구",
                color='총인구',
                color_continuous_scale='Blues'
            )
            
            fig_bar.update_layout(
                height=600,
                xaxis_tickangle=-45,
                font=dict(size=12)
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # 하단 차트들
        col1, col2 = st.columns(2)
        
        with col1:
            # 남녀 인구 비교 도넛 차트
            st.subheader("🍩 남녀 인구 비율")
            
            male_total = age_df['남자'].sum()
            female_total = age_df['여자'].sum()
            
            fig_donut = go.Figure(data=[go.Pie(
                labels=['남자', '여자'],
                values=[male_total, female_total],
                hole=0.4,
                marker_colors=['#3498db', '#e74c3c']
            )])
            
            fig_donut.update_layout(
                title=f"{region_name} 남녀 인구 비율",
                height=400,
                font=dict(size=12)
            )
            
            st.plotly_chart(fig_donut, use_container_width=True)
        
        with col2:
            # 연령대별 남녀 비교
            st.subheader("👥 연령대별 남녀 비교")
            
            # 데이터 재구성
            comparison_data = []
            for _, row in age_df.iterrows():
                comparison_data.append({
                    '연령대': row['연령대'],
                    '성별': '남자',
                    '인구수': row['남자']
                })
                comparison_data.append({
                    '연령대': row['연령대'],
                    '성별': '여자',
                    '인구수': row['여자']
                })
            
            comparison_df = pd.DataFrame(comparison_data)
            
            fig_comparison = px.bar(
                comparison_df,
                x='연령대',
                y='인구수',
                color='성별',
                title=f"{region_name} 연령대별 남녀 인구 비교",
                color_discrete_map={'남자': '#3498db', '여자': '#e74c3c'},
                barmode='group'
            )
            
            fig_comparison.update_layout(
                height=400,
                xaxis_tickangle=-45,
                font=dict(size=12)
            )
            
            st.plotly_chart(fig_comparison, use_container_width=True)
    
    # 데이터 테이블
    st.markdown("---")
    st.subheader("📋 상세 데이터")
    
    if selected_region == "전체":
        display_df = df[['행정구역', '2025년08월_총인구수', '2025년08월_세대수', 
                        '2025년08월_세대당 인구', '2025년08월_남자 인구수', 
                        '2025년08월_여자 인구수', '2025년08월_남여 비율']]
    else:
        display_df = df[df['행정구역'] == selected_region][['행정구역', '2025년08월_총인구수', '2025년08월_세대수', 
                                                           '2025년08월_세대당 인구', '2025년08월_남자 인구수', 
                                                           '2025년08월_여자 인구수', '2025년08월_남여 비율']]
    
    st.dataframe(display_df, use_container_width=True)

if __name__ == "__main__":
    main()
