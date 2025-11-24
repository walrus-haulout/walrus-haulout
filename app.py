import streamlit as st
import pandas as pd
import plotly.express as px
from scraper import fetch_all_projects, process_projects

# Set Page Config
st.set_page_config(
    page_title="DeepSurge Intelligence Dashboard",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better visibility
st.markdown("""
<style>
    .reportview-container {
        background: #0e1117;
    }
    .main .block-container {
        padding-top: 2rem;
    }
    h1, h2, h3 {
        color: #f0f2f6;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #0068c9;
        color: white;
    }
    /* Improve metric card visibility */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #ffffff;
        font-weight: 600;
    }
    [data-testid="stMetricLabel"] {
        color: #b0b0b0;
        font-size: 1rem;
    }
    [data-testid="metric-container"] {
        background-color: #1e1e1e;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🌊 DeepSurge Intelligence")
    st.caption("Walrus Haulout Hackathon 2025")
    
    st.markdown("---")
    
    st.subheader("Mining Configuration")
    auto_mine = st.checkbox("Auto Mine All (Until End)", value=False)
    
    if auto_mine:
        page_limit = 1000 # Set a high limit to effectively mine all
        st.info("Mining will continue until no more data is found.")
    else:
        page_limit = st.slider("Max Pages to Scrape", min_value=1, max_value=100, value=50)
    
    start_btn = st.button("🚀 Start Mining")
    
    st.markdown("---")
    st.markdown("### About")
    st.info(
        "This dashboard scrapes and analyzes project data from the DeepSurge Hackathon platform. "
        "It calculates a Quality Score (PQI) to help identify top-tier projects."
    )

# Main Content
st.title("DeepSurge Intelligence Dashboard")

if "data" not in st.session_state:
    st.session_state.data = None

if start_btn:
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    def update_progress(page, total_items):
        progress = min(page / page_limit, 1.0)
        progress_bar.progress(progress)
        status_text.text(f"Scraping Page {page}... Found {total_items} projects so far.")
    
    with st.spinner("Mining data from DeepSurge..."):
        try:
            raw_projects = fetch_all_projects(page_limit=page_limit, progress_callback=update_progress)
            
            if raw_projects:
                status_text.text("Processing data and calculating scores...")
                df = process_projects(raw_projects)
                st.session_state.data = df
                status_text.success(f"Successfully mined {len(df)} projects!")
                progress_bar.empty()
            else:
                status_text.error("No projects found. Please check your network or cookie.")
        except Exception as e:
            status_text.error(f"An error occurred: {e}")
            st.error(f"Detailed Error: {e}")

if st.session_state.data is not None:
    df = st.session_state.data
    
    # Export Button in Sidebar
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.sidebar.download_button(
        "📥 Download CSV",
        csv,
        "walrus_haulout_data.csv",
        "text/csv",
        key='download-csv'
    )

    # Tabs
    tab1, tab2 = st.tabs(["📊 Macro Overview", "🔎 Detail Grid"])
    
    with tab1:
        st.subheader("Market Overview")
        
        # KPI Cards
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Projects", len(df))
        
        open_source_count = df['github_url'].notna().sum()
        open_source_rate = (open_source_count / len(df)) * 100 if len(df) > 0 else 0
        col2.metric("Open Source Rate", f"{open_source_rate:.1f}%")
        
        deployed_count = df['packageId'].notna().sum()
        deployed_rate = (deployed_count / len(df)) * 100 if len(df) > 0 else 0
        col3.metric("On-Chain Deployment", f"{deployed_rate:.1f}%")

        
        st.markdown("---")
        
        # Charts
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("#### Track Distribution")
            if 'track' in df.columns:
                track_counts = df['track'].value_counts().reset_index()
                track_counts.columns = ['track', 'count']
                fig_pie = px.pie(track_counts, values='count', names='track', hole=0.4)
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.warning("Track data not available.")
                
        with c2:
            st.markdown("#### Network Status")
            if 'deployNetwork' in df.columns:
                net_counts = df['deployNetwork'].fillna('Undeployed').value_counts().reset_index()
                net_counts.columns = ['network', 'count']
                fig_bar = px.bar(net_counts, x='network', y='count', color='network')
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.warning("Network data not available.")

    with tab2:
        st.subheader("Project Explorer")
        
        # Filters
        f1, f2, f3 = st.columns([1, 1, 2])
        with f1:
            tracks = ["All"] + list(df['track'].unique()) if 'track' in df.columns else ["All"]
            selected_track = st.selectbox("Filter by Track", tracks)
        with f2:
            statuses = ["All"] + list(df['status'].unique()) if 'status' in df.columns else ["All"]
            selected_status = st.selectbox("Filter by Status", statuses)
        with f3:
            search_term = st.text_input("Search Projects", placeholder="Project Name or Description...")
            
        # Apply Filters
        filtered_df = df.copy()
        if selected_track != "All":
            filtered_df = filtered_df[filtered_df['track'] == selected_track]
        if selected_status != "All":
            filtered_df = filtered_df[filtered_df['status'] == selected_status]
        if search_term:
            filtered_df = filtered_df[
                filtered_df['projectName'].str.contains(search_term, case=False, na=False) |
                filtered_df['description_clean'].str.contains(search_term, case=False, na=False)
            ]
            
        # Display Grid
        st.dataframe(
            filtered_df[[
                'projectName', 'description', 'track', 'status', 'deployNetwork', 
                'packageId', 'github_url', 'website_url', 'youtube_url',
                'likeCount', 'createdAt'
            ]],
            use_container_width=True,
            height=600
        )

else:
    st.info("👈 Click 'Start Mining' in the sidebar to fetch the latest hackathon data.")
