import streamlit as st
import os
import re
import pdfplumber
import dateparser
import pandas as pd

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Court Case Timeline Extraction",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="⚖️"
)

DATA_FOLDER = "NLP_cases"   # folder containing PDFs

# ---------------- CUSTOM CSS ----------------
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
    }
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        margin-top: 0.5rem;
        font-size: 1.1rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
    }
    .event-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    .event-filing { background-color: #e3f2fd; color: #1976d2; }
    .event-hearing { background-color: #fff3e0; color: #f57c00; }
    .event-interim { background-color: #f3e5f5; color: #7b1fa2; }
    .event-transfer { background-color: #e8f5e9; color: #388e3c; }
    .event-judgment { background-color: #fff9c4; color: #f9a825; }
    .event-appeal { background-color: #fce4ec; color: #c2185b; }
    .event-other { background-color: #f5f5f5; color: #616161; }
    .timeline-item {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.4);
    }
    .stSelectbox>div>div {
        border-radius: 8px;
    }
    .dataframe-container {
        overflow-x: auto;
        width: 100%;
    }
    div[data-testid="stDataFrame"] {
        overflow-x: auto;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------- LOAD NLP ----------------
# spaCy has been removed; using regex-based text processing instead.

# ---------------- FUNCTIONS ----------------
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + " "
    return text


def split_sentences(text):
    """Split text into sentences using regex, keeping only reasonably long sentences."""
    sentences = re.split(r'(?<=[\.!\?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 20]


def extract_date(sentence):
    patterns = [
        r'\d{1,2}\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s\d{4}',
        r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{1,2},\s\d{4}'
    ]
    for pattern in patterns:
        match = re.search(pattern, sentence)
        if match:
            return dateparser.parse(match.group())
    return None


EVENT_KEYWORDS = {
    "Filing": ["filed", "instituted"],
    "Hearing": ["heard", "arguments"],
    "Interim Order": ["interim", "ex-parte", "stay"],
    "Transfer": ["transferred"],
    "Judgment": ["judgment", "decision", "held"],
    "Appeal": ["appeal"]
}


def detect_event(sentence):
    sentence = sentence.lower()
    for event, keywords in EVENT_KEYWORDS.items():
        for word in keywords:
            if word in sentence:
                return event
    return "Other"


def extract_person_names(text):
    """Heuristically extract person names from text using regex patterns (no spaCy required)."""
    person_names = set()

    # Look for common patterns like "vs", "v.", "versus" for case parties
    vs_patterns = [
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:vs|v\.|versus|VS|V\.)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+and\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
    ]
    
    for pattern in vs_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            for group in match.groups():
                if group and len(group.strip()) > 2:
                    person_names.add(group.strip())
    
    # Generic heuristic: sequences of capitalized words (likely names)
    name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,4})\b'
    for match in re.finditer(name_pattern, text):
        name = match.group(1).strip()
        if len(name) > 2:
            person_names.add(name)

    return sorted(list(person_names))


def extract_persons_from_sentence(sentence):
    """Heuristically extract person names from a single sentence (no spaCy required)."""
    persons = set()

    name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,4})\b'
    for match in re.finditer(name_pattern, sentence):
        name = match.group(1).strip()
        if len(name) > 2:
            persons.add(name)

    return list(persons)


def build_timeline(pdf_name):
    pdf_path = os.path.join(DATA_FOLDER, pdf_name)
    text = extract_text_from_pdf(pdf_path)

    # Simple sentence splitting without spaCy
    sentences = split_sentences(text)

    timeline = []
    for sent in sentences:
        date = extract_date(sent)
        if date:
            persons_in_sent = extract_persons_from_sentence(sent)
            timeline.append({
                "Date": date.strftime("%Y-%m-%d"),
                "Event": detect_event(sent),
                "Description": sent,
                "Persons": ", ".join(persons_in_sent) if persons_in_sent else "N/A"
            })

    return pd.DataFrame(sorted(timeline, key=lambda x: x["Date"]))


def get_event_badge_class(event):
    """Return CSS class for event badge styling"""
    event_lower = event.lower().replace(" ", "-")
    return f"event-{event_lower}"


def format_event_badge(event):
    """Format event as HTML badge"""
    badge_class = get_event_badge_class(event)
    return f'<span class="event-badge {badge_class}">{event}</span>'

# ---------------- UI ----------------
# Custom Header
st.markdown("""
    <div class="main-header">
        <h1>⚖️ Court Case Timeline Extraction</h1>
        <p>Extract chronological legal timelines from court case documents with AI-powered NLP</p>
    </div>
""", unsafe_allow_html=True)

# Load available PDFs
pdf_files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".pdf")]

if not pdf_files:
    st.error("❌ No PDF files found in the dataset folder.")
    st.info(f"Please add PDF files to the '{DATA_FOLDER}' folder.")
else:
    # File Selection Section
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_pdf = st.selectbox(
            "📂 Select Case PDF",
            pdf_files,
            help="Choose a court case PDF file to analyze"
        )
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        generate_btn = st.button("🚀 Generate Timeline", use_container_width=True)

    if generate_btn:
        with st.spinner("🔍 Processing document and extracting timeline events..."):
            df = build_timeline(selected_pdf)

        if df.empty:
            st.warning("⚠️ No dates/events detected in this document.")
            st.info("💡 Tip: Make sure the document contains date information in recognizable formats.")
        else:
            # Success message
            st.success(f"✅ Timeline extracted successfully for **{selected_pdf}**")
            
            # Statistics Cards
            st.markdown("### 📊 Timeline Statistics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Events", len(df))
            with col2:
                event_types = df['Event'].nunique()
                st.metric("Event Types", event_types)
            with col3:
                date_range = (pd.to_datetime(df['Date'].max()) - pd.to_datetime(df['Date'].min())).days
                st.metric("Duration (Days)", date_range)
            with col4:
                most_common = df['Event'].mode()[0] if not df['Event'].mode().empty else "N/A"
                st.metric("Most Common Event", most_common)
            
            st.divider()
            
            # Event Distribution
            st.markdown("### 📈 Event Distribution")
            event_counts = df['Event'].value_counts()
            col1, col2 = st.columns([2, 1])
            with col1:
                st.bar_chart(event_counts)
            with col2:
                st.markdown("**Event Breakdown:**")
                for event, count in event_counts.items():
                    badge_class = get_event_badge_class(event)
                    st.markdown(f'<span class="event-badge {badge_class}">{event}</span> <strong>{count}</strong>', unsafe_allow_html=True)
            
            st.divider()
            
            # Timeline Table
            st.markdown("### 📋 Timeline Overview")
            # Configure column display for better readability with horizontal scroll
            column_config = {
                "Date": st.column_config.DateColumn("Date", width="small", format="YYYY-MM-DD"),
                "Event": st.column_config.TextColumn("Event", width="medium"),
                "Persons": st.column_config.TextColumn("Persons Involved", width="medium"),
                "Description": st.column_config.TextColumn("Description", width="large")
            }
            st.dataframe(df, use_container_width=True, column_config=column_config, hide_index=True, height=400)
            
            st.divider()
            
            # Detailed Timeline with Enhanced UI
            st.markdown("### 🗓️ Detailed Timeline View")
            st.markdown("Click on any event to view full details")
            
            for idx, row in df.iterrows():
                # Use plain text for expander title, badge will be shown inside
                event_display = row['Event']
                persons_display = row['Persons'] if row['Persons'] != "N/A" else "Not specified"
                with st.expander(f"📅 **{row['Date']}** - {event_display}", expanded=False):
                    event_badge_html = format_event_badge(row['Event'])
                    st.markdown(f"""
                    <div class="timeline-item">
                        <p><strong>Date:</strong> {row['Date']}</p>
                        <p><strong>Event Type:</strong> {event_badge_html}</p>
                        <p><strong>Persons Involved:</strong> {persons_display}</p>
                        <p><strong>Description:</strong></p>
                        <p style="text-align: justify; line-height: 1.6;">{row['Description']}</p>
                    </div>
                    """, unsafe_allow_html=True)

            st.divider()
            
            # Download Section
            st.markdown("### 💾 Export Timeline")
            col1, col2 = st.columns([1, 1])
            with col1:
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="⬇️ Download as CSV",
                    data=csv,
                    file_name=f"{selected_pdf.replace('.pdf', '')}_timeline.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with col2:
                # JSON export option
                json_data = df.to_json(orient='records', indent=2, date_format='iso')
                st.download_button(
                    label="⬇️ Download as JSON",
                    data=json_data.encode("utf-8"),
                    file_name=f"{selected_pdf.replace('.pdf', '')}_timeline.json",
                    mime="application/json",
                    use_container_width=True
                )
