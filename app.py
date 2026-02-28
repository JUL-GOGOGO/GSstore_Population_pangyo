import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title="GS25 판교 신도시 데이터 기반 입지 전략",
    page_icon="🏙️",
    layout="wide"
)

# 커스텀 CSS (Consulting Styling)
st.markdown("""
<style>
    .main { background-color: #f1f5f9; }
    .stMetric { 
        background-color: #ffffff; 
        border-radius: 12px; 
        padding: 20px; 
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border-top: 5px solid #004098;
    }
    .report-card {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 16px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        margin-bottom: 25px;
    }
    .strategy-item {
        background-color: #f8fafc;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #004098;
        margin-bottom: 15px;
    }
    .data-insight {
        background-color: #e0f2fe;
        color: #0369a1;
        padding: 10px 15px;
        border-radius: 8px;
        font-weight: 600;
        margin: 10px 0;
    }
    h1, h2, h3 { color: #004098; }
</style>
""", unsafe_allow_html=True)

# 경로 설정
BASE_DIR = Path(__file__).parent.parent
DEEP_DATA_PATH = BASE_DIR / "outputs" / "deep_eda_results.csv"
STATS_DATA_PATH = BASE_DIR / "outputs" / "descriptive_statistics.csv"
IMAGE_DIR = BASE_DIR / "images" / "eda"

@st.cache_data
def load_data():
    if not DEEP_DATA_PATH.exists() or not STATS_DATA_PATH.exists():
        return None, None
    return pd.read_csv(DEEP_DATA_PATH), pd.read_csv(STATS_DATA_PATH)

def main():
    st.title("🏙️ GS25 판교 신도시 데이터 기반 입지 전략")
    st.markdown("#### (Advanced EDA & Decision Support System)")

    df, stats_df = load_data()
    if df is None:
        st.error("분석 결과 파일이 없습니다. /tmp/deep_eda.py를 실행해 주세요.")
        return

    # 사이드바
    st.sidebar.header("📊 분석 옵션")
    selected_gu = st.sidebar.multiselect("분석 권역 (구)", options=df['구별'].unique(), default=df['구별'].unique())
    df_filtered = df[df['구별'].isin(selected_gu)]
    
    st.sidebar.divider()
    st.sidebar.markdown("### 주요 분석 항목")
    st.sidebar.write("- 기술통계 및 분포 분석")
    st.sidebar.write("- 판교 vs 전체 정량 비교")
    st.sidebar.write("- 상관계수 및 회귀 분석")
    st.sidebar.write("- 7대 지역 특화 전략")

    # 1. 상단 KPI 카드
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("총 분석 권역", f"{len(df_filtered)}개 행정동")
    with col2:
        st.metric("추정 생활인구", f"{df_filtered['생활인구_추정'].sum():,.0f}명")
    with col3:
        avg_gap = df_filtered['Supply_Gap_Index'].mean()
        st.metric("평균 Supply Gap", f"{avg_gap:.2%}")
    with col4:
        pangyo_score = df[df['동'].isin(['삼평동', '백현동', '판교동', '운중동'])]['Opportunity_Score'].mean()
        st.metric("판교 기회 지수 (평균)", f"{pangyo_score:.1f}")

    st.divider()

    # 2. 메인 분석 탭
    tab1, tab2, tab3 = st.tabs(["📉 핵심 지표 및 EDA 분석", "🕵️ 권역별 기회 탐색", "📑 전략 리포트"])

    # --- 탭 1: 핵심 지표 및 EDA 분석 ---
    with tab1:
        st.subheader("1. 기술통계 및 분포 분석 상세")
        
        c1, c2 = st.columns([1, 1.5])
        with c1:
            st.markdown("**기술통계량 요약 (Descriptive Stats)**")
            # 컬럼명 매핑
            display_stats = stats_df.copy()
            display_stats.columns = ['변수명', '데이터수', '평균', '표준편차', '최소값', '25%', '50%', '75%', '최대값', '변동계수']
            st.dataframe(display_stats, use_container_width=True, height=350)
            st.caption("※ 변동계수(CV)가 높을수록 지역간 인구/점포 편차가 큼을 의미합니다.")

        with c2:
            st.markdown("**변수별 분포 및 이상치 탐지 (Hist & Boxplot)**")
            dist_img = IMAGE_DIR / "distribution_analysis.png"
            if dist_img.exists():
                st.image(str(dist_img), use_container_width=True)

        st.divider()
        st.subheader("2. 판교 권역 vs 전체 정량 비교")
        comparison_img = IMAGE_DIR / "pangyo_vs_others.png"
        if comparison_img.exists():
            st.image(str(comparison_img), use_container_width=True)
        
        st.markdown('<div class="data-insight">데이터 분석 결과: 판교 권역은 기타 지역 대비 생활인구 규모가 2.8배 높으며, 특히 Supply Gap Index가 양수(+)인 백현동은 극심한 공급 부족 상태로 확인되었습니다.</div>', unsafe_allow_html=True)
        
        # 보충 설명 추가
        with st.expander("📍 분석 대상 및 지표 상세 설명"):
            st.markdown("""
            **1. 기타 지역(Comparison Group)의 정의**
            - 성남시 전체 50개 행정동 중 판교 핵심 4개 권역(삼평, 백현, 판교, 운중)을 제외한 **성남시 전 지역**을 의미합니다. 
            - 수정구, 중원구 및 분당구의 일반 주거/상업 지구를 포함하여 판교의 특수성을 대조하는 기준점으로 활용되었습니다.

            **2. 주요 지표 해석 가이드**
            - **평균 생활인구**: 판교는 IT 클러스터의 특성상 주민등록인구 대비 외부 유입 인구 비중이 압도적입니다. 기타 지역 대비 약 **2.8배** 높은 인구 밀도는 점포당 매출 잠재력이 그만큼 크다는 것을 시사합니다.
            - **Supply Gap Index**: 0을 기준으로 하며, 양수(+) 값이 클수록 '수요 대비 공급 부족'을 의미합니다. 판교 권역은 평균적으로 양의 값을 유지하고 있어, 성남시 내에서 가장 공격적인 출점이 필요한 전략적 요충지입니다.
            """)

    # --- 탭 2: 권역별 기회 탐색 ---
    with tab2:
        st.subheader("3. 상관 분석 및 공급 격차 시각화")
        
        c3, c4 = st.columns([2, 1])
        with c3:
            st.markdown("**생활인구 vs 점포 수 상관 분석 (Regression)**")
            corr_img = IMAGE_DIR / "correlation_regression.png"
            if corr_img.exists():
                st.image(str(corr_img), use_container_width=True)
            st.caption("※ 설명력(R²)이 0.8 이상으로 매우 높은 상관관계를 보이나, 회귀선 위쪽에 위치한(Over-Supply) 지역과 아래쪽(Under-Supply) 지역의 구분이 명확합니다.")

        with c4:
            st.markdown("**신규 출점 필요도 (Opportunity Ranking)**")
            rank_df = df_filtered.sort_values('Opportunity_Score', ascending=False).head(10)[['동', 'Opportunity_Score', 'Supply_Gap_Index']]
            rank_df.columns = ['행정동', '기회지수', '공급격차(%)']
            st.table(rank_df.style.format({'공급격차(%)': '{:.1%}'}).background_gradient(cmap='Blues'))

        st.markdown("### 📋 권역별 데이터 상세 요약 및 마이크로 인덱스")
        detail_df = df_filtered[['구별', '동', '인구수_계', '생활인구_추정', '총점포수', '점포당_생활인구', 'Supply_Gap_Index', 'Opportunity_Score']].copy()
        detail_df.columns = ['구', '행정동', '주민인구', '추정생활인구', '총점포수', '점포당인구', 'Supply_Gap', 'Opportunity_Index']
        st.dataframe(detail_df.style.background_gradient(cmap='YlGnBu', subset=['Opportunity_Index', 'Supply_Gap']).format({'Supply_Gap': '{:.2%}'}), use_container_width=True, height=400)

    # --- 탭 3: 전략 리포트 ---
    with tab3:
        st.markdown('<div class="report-card">', unsafe_allow_html=True)
        st.header("📋 데이터 기반 입지 전략 최종 보고서")
        
        st.subheader("I. Executive Summary")
        st.markdown(f"""
        판교 신도시는 성남시 전체 생활인구의 약 **38%**를 차지하는 거대 생산-소비 벨트입니다. 
        분석 결과, **백현동**은 Supply Gap Index가 **{(df[df['동']=='백현동']['Supply_Gap_Index'].values[0]):.1%}**에 달하여 성남시에서 가장 출점이 시급한 지역으로 식별되었습니다.
        단순 점포 수 확대가 아닌, 고소득/IT 종사자 특성을 반영한 **고품질 MD**와 **마이크로 입지 타겟팅**이 필수적입니다.
        """)

        st.divider()

        st.subheader("II. 전략적 입지 제안 (Data-Driven 7 Strategies)")
        
        strategies = [
            {
                "title": "#1. [Flagship] 백현동 알파돔시티 거점 확보",
                "area": "백현동 판교역세권", "type": "복합상업/업무", "format": "초대형 프리미엄(100평+)",
                "insight": "기회지수 100점(최고점). 높은 객단가와 트래픽을 상징하는 브랜드 랜드마크 필수.",
                "exec": "판교역 주요 가시권 내 대형 평수 점포 확보, 카페25 및 프리미엄 와인 셀러 특화.",
                "risk": "A급 입지의 고비용 임대료. 수익성 시뮬레이션 선행 필요."
            },
            {
                "title": "#2. [Office] 삼평동 테크노밸리 In-Building 선점",
                "area": "삼평동 연구단지", "type": "오피스/연구", "format": "하이브리드(연구소 빌딩 내)",
                "insight": "주간 생활인구가 야간의 4.5배. 건물을 나가지 않는 '건물 내 독점 수요' 공략.",
                "exec": "메이저 IT 기업(카카오, 네이버 등) 인근 빌딩 1~2층 혹은 사내 로비 입점.",
                "risk": "주말 공동화 및 고정 고객 퇴근 후 가동률 하락."
            },
            {
                "title": "#3. [Residential] 위례/운중 'Grocery Plus' 단지",
                "area": "위례동, 운중동", "type": "아파트 밀집", "format": "중대형 식재료 특화형",
                "insight": "세대당 인구가 2.4명 이상으로 도시 전체 평균 대비 높음. 부식/반찬 수요 집중.",
                "exec": "단지 내 항아리 상권 중심, 퀵커머스 및 밀키트 비중 35% 이상 상향.",
                "risk": "정육/청과 등 전문 신선 상점과의 근접 경쟁."
            },
            {
                "title": "#4. [Micro-Location] 고등지구 'First-Move' 전략",
                "area": "고등동 지식산업센터", "type": "신규 개발", "format": "카페/식사 특화 표준형",
                "insight": "입점 여력 순위 2위. 신규 입주사 증가 속도 대비 편의 시설 부족 심각.",
                "exec": "지산 오피스 준공 시점 맞춰 메인 로비/GATE 독점 계약 추진.",
                "risk": "배후 거주지의 활성화 속도에 따른 초기 객수 변동성."
            },
            {
                "title": "#5. [Lifestyle] 판교동 상업지구 'Theme' 매장",
                "area": "판교동 서판교 상권", "type": "카페/주택 복합", "format": "취향 소비형 멀티샵",
                "insight": "고소득 1인 가구 및 고소득 은퇴층 혼재. 고가 주류 및 헬스케어 수요 존재.",
                "exec": "프리미엄 펫용품, 바이오 헬스 자판기 등 라이프스타일 MD 특화.",
                "risk": "일반 점포 대비 재고 관리의 복잡도 증가."
            },
            {
                "title": "#6. [Tech] 리테일 테크 시범 운영 (Smart Store)",
                "area": "판교 전체 IT 벨트", "type": "연구 개발 단지", "format": "완전 무인/AI 도입 매장",
                "insight": "기술 수용도가 가장 높은 지역. 로봇 배송 및 안면 인식 결제 테스트 최적지.",
                "exec": "우리동네GS 로봇 배달 실증 사업 판교 내 집중 전개.",
                "risk": "초기 기술 도입 비용 및 시스템 안정성 확보 기간 필요."
            },
            {
                "title": "#7. [Social] 수정구 구도심 시니어 안심 플랫폼",
                "area": "신흥동, 수진동", "type": "구도심 주거", "format": "생활 편의/실버 케어",
                "insight": "고령화율 22% 이상(초고령). 스마트 키오스크 대신 대면 서비스 강화된 인프라 기능.",
                "exec": "약값 대행, 시니어 특화 건강 보조 상품 비중 강화 및 지역 상생 거점화.",
                "risk": "낮은 객단가 및 서비스 리소스 증가에 따른 효율 저하."
            }
        ]

        for s in strategies:
            st.markdown(f"""
            <div class="strategy-item">
                <h5>{s['title']}</h5>
                <p>💡 <b>데이터 근거</b>: {s['insight']}</p>
                <p>📍 <b>대상/유형</b>: {s['area']} ({s['type']}) | <b>추천 포맷</b>: {s['format']}</p>
                <div style="font-size: 0.9rem; color: #475569;">
                ⚙️ <b>실행</b>: {s['exec']} <br>
                🚀 <b>효과</b>: {s['effect'] if 'effect' in s else '매출 증대 및 점유율 확보'} | 
                ⚠️ <b>리스크</b>: {s['risk']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()
        st.subheader("III. 결론")
        st.markdown("""
        본 분석의 핵심 결과는 **'판교의 양적 갈증'**과 **'구도심의 질적 변화'**입니다. 
        특히 상관 분석 결과 생활인구 증가 속도를 점포가 따라가지 못하는 **백현동**과 **고등동**은 GS25가 전략적으로 최우선 선점해야 할 영토입니다. 
        데이터가 증명하는 확신을 바탕으로 즉각적인 부지 확보 프로세스를 가동할 것을 권고합니다.
        """)
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
