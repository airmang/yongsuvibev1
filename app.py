import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# 페이지 설정
st.set_page_config(
    page_title="용인시 인구 데이터 시각화",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 한글 폰트 설정
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """데이터 로딩 및 전처리"""
    try:
        # CP-949 인코딩으로 데이터 로드
        df = pd.read_csv('data.csv', encoding='cp949')
        
        # 숫자 데이터 정리 (쉼표 제거 및 숫자 변환)
        numeric_columns = ['2025년08월_총인구수', '2025년08월_세대수', '2025년08월_남자 인구수', '2025년08월_여자 인구수']
        for col in numeric_columns:
            df[col] = df[col].str.replace(',', '').astype(int)
        
        # 비율 데이터 정리
        ratio_columns = ['2025년08월_세대당 인구', '2025년08월_남여 비율']
        for col in ratio_columns:
            df[col] = df[col].str.replace(',', '').astype(float)
        
        # 행정구역 정보 추출
        df['시도'] = df['행정구역'].str.extract(r'(\w+시)')
        df['구군'] = df['행정구역'].str.extract(r'(\w+구|\w+군)')
        df['읍면동'] = df['행정구역'].str.extract(r'(\w+읍|\w+면|\w+동)')
        
        return df
    except Exception as e:
        st.error(f"데이터 로딩 중 오류가 발생했습니다: {e}")
        return None

def create_population_pyramid(df_filtered):
    """인구 피라미드 생성"""
    if df_filtered.empty:
        return None
    
    # 남녀 인구 데이터 준비
    male_data = df_filtered['2025년08월_남자 인구수'].sum()
    female_data = df_filtered['2025년08월_여자 인구수'].sum()
    
    # 연령대별 데이터가 없으므로 전체 인구로 단순화
    fig = go.Figure()
    
    # 남성 데이터 (음수로 표시하여 왼쪽에 배치)
    fig.add_trace(go.Bar(
        y=['전체'],
        x=[-male_data],
        orientation='h',
        name='남성',
        marker_color='#3498db',
        text=[f"{male_data:,}"],
        textposition='inside'
    ))
    
    # 여성 데이터 (양수로 표시하여 오른쪽에 배치)
    fig.add_trace(go.Bar(
        y=['전체'],
        x=[female_data],
        orientation='h',
        name='여성',
        marker_color='#e74c3c',
        text=[f"{female_data:,}"],
        textposition='inside'
    ))
    
    fig.update_layout(
        title="인구 구성 (남성 vs 여성)",
        xaxis_title="인구수",
        yaxis_title="",
        barmode='relative',
        height=300,
        font=dict(family="Noto Sans KR", size=12),
        xaxis=dict(tickformat=','),
        showlegend=True
    )
    
    return fig

def create_region_comparison(df):
    """지역별 비교 차트"""
    # 구/군별 데이터만 필터링
    region_data = df[df['구군'].notna()].copy()
    
    if region_data.empty:
        return None
    
    fig = px.bar(
        region_data,
        x='구군',
        y='2025년08월_총인구수',
        title="구/군별 총 인구수",
        color='2025년08월_총인구수',
        color_continuous_scale='Blues',
        text_auto=True
    )
    
    fig.update_layout(
        font=dict(family="Noto Sans KR", size=12),
        xaxis_tickangle=-45,
        height=500
    )
    
    fig.update_traces(texttemplate='%{text:,}', textposition='outside')
    
    return fig

def create_household_analysis(df_filtered):
    """세대 분석 차트"""
    if df_filtered.empty:
        return None
    
    # 세대당 인구수 분포
    fig = px.histogram(
        df_filtered,
        x='2025년08월_세대당 인구',
        nbins=20,
        title="세대당 인구수 분포",
        labels={'2025년08월_세대당 인구': '세대당 인구수', 'count': '지역 수'}
    )
    
    fig.update_layout(
        font=dict(family="Noto Sans KR", size=12),
        height=400
    )
    
    return fig

def create_gender_ratio_analysis(df_filtered):
    """성비 분석 차트"""
    if df_filtered.empty:
        return None
    
    # 남여 비율이 1.0에 가까운 순으로 정렬
    df_sorted = df_filtered.sort_values('2025년08월_남여 비율')
    
    fig = px.bar(
        df_sorted,
        x='행정구역',
        y='2025년08월_남여 비율',
        title="지역별 남여 비율 (1.0 = 남녀 균등)",
        color='2025년08월_남여 비율',
        color_continuous_scale='RdYlBu_r',
        text_auto=True
    )
    
    # 기준선 추가 (1.0)
    fig.add_hline(y=1.0, line_dash="dash", line_color="red", 
                  annotation_text="균등선 (1.0)", annotation_position="top right")
    
    fig.update_layout(
        font=dict(family="Noto Sans KR", size=12),
        xaxis_tickangle=-45,
        height=500
    )
    
    return fig

def main():
    st.title("🏘️ 용인시 인구 데이터 시각화 대시보드")
    st.markdown("---")
    
    # 데이터 로딩
    df = load_data()
    if df is None:
        st.stop()
    
    # 사이드바 필터
    st.sidebar.header("🔍 필터 옵션")
    
    # 시도 선택
    sido_options = ['전체'] + sorted(df['시도'].dropna().unique().tolist())
    selected_sido = st.sidebar.selectbox("시도 선택", sido_options)
    
    # 구/군 선택
    if selected_sido != '전체':
        gu_options = ['전체'] + sorted(df[df['시도'] == selected_sido]['구군'].dropna().unique().tolist())
    else:
        gu_options = ['전체'] + sorted(df['구군'].dropna().unique().tolist())
    
    selected_gu = st.sidebar.selectbox("구/군 선택", gu_options)
    
    # 읍/면/동 선택
    if selected_gu != '전체':
        dong_options = ['전체'] + sorted(df[df['구군'] == selected_gu]['읍면동'].dropna().unique().tolist())
    else:
        dong_options = ['전체'] + sorted(df['읍면동'].dropna().unique().tolist())
    
    selected_dong = st.sidebar.selectbox("읍/면/동 선택", dong_options)
    
    # 데이터 필터링
    df_filtered = df.copy()
    
    if selected_sido != '전체':
        df_filtered = df_filtered[df_filtered['시도'] == selected_sido]
    
    if selected_gu != '전체':
        df_filtered = df_filtered[df_filtered['구군'] == selected_gu]
    
    if selected_dong != '전체':
        df_filtered = df_filtered[df_filtered['읍면동'] == selected_dong]
    
    # 필터링된 데이터 정보 표시
    st.sidebar.markdown("---")
    st.sidebar.metric("선택된 지역 수", len(df_filtered))
    if not df_filtered.empty:
        st.sidebar.metric("총 인구수", f"{df_filtered['2025년08월_총인구수'].sum():,}")
        st.sidebar.metric("총 세대수", f"{df_filtered['2025년08월_세대수'].sum():,}")
    
    # 메인 콘텐츠
    if df_filtered.empty:
        st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
        return
    
    # 요약 통계
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 인구수", f"{df_filtered['2025년08월_총인구수'].sum():,}")
    
    with col2:
        st.metric("총 세대수", f"{df_filtered['2025년08월_세대수'].sum():,}")
    
    with col3:
        avg_household = df_filtered['2025년08월_세대당 인구'].mean()
        st.metric("평균 세대당 인구", f"{avg_household:.2f}")
    
    with col4:
        male_ratio = df_filtered['2025년08월_남자 인구수'].sum() / df_filtered['2025년08월_여자 인구수'].sum()
        st.metric("남여 비율", f"{male_ratio:.2f}")
    
    st.markdown("---")
    
    # 차트 섹션
    tab1, tab2, tab3, tab4 = st.tabs(["인구 피라미드", "지역별 비교", "세대 분석", "성비 분석"])
    
    with tab1:
        st.subheader("인구 구성 분석")
        pyramid_fig = create_population_pyramid(df_filtered)
        if pyramid_fig:
            st.plotly_chart(pyramid_fig, use_container_width=True)
        
        # 상세 데이터 테이블
        st.subheader("상세 데이터")
        display_cols = ['행정구역', '2025년08월_총인구수', '2025년08월_세대수', 
                       '2025년08월_세대당 인구', '2025년08월_남자 인구수', 
                       '2025년08월_여자 인구수', '2025년08월_남여 비율']
        st.dataframe(df_filtered[display_cols], use_container_width=True)
    
    with tab2:
        st.subheader("지역별 인구 비교")
        region_fig = create_region_comparison(df_filtered)
        if region_fig:
            st.plotly_chart(region_fig, use_container_width=True)
    
    with tab3:
        st.subheader("세대 분석")
        household_fig = create_household_analysis(df_filtered)
        if household_fig:
            st.plotly_chart(household_fig, use_container_width=True)
    
    with tab4:
        st.subheader("성비 분석")
        gender_fig = create_gender_ratio_analysis(df_filtered)
        if gender_fig:
            st.plotly_chart(gender_fig, use_container_width=True)
    
    # 푸터
    st.markdown("---")
    st.markdown("📊 **용인시 인구 데이터 시각화 대시보드** | 데이터 출처: 용인시 통계")
    st.markdown("💡 **사용법**: 왼쪽 사이드바에서 원하는 지역을 선택하여 데이터를 필터링할 수 있습니다.")

if __name__ == "__main__":
    main()
