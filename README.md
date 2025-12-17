# ⚖️ Court Case Timeline Extraction

A powerful NLP-powered web application that automatically extracts chronological timelines and key information from court case PDF documents. Built with Streamlit and spaCy, this tool helps legal professionals and researchers quickly analyze case documents and understand case progression.

## 🌟 Features

### Core Functionality
- **📄 PDF Processing**: Automatically extracts text from court case PDF documents
- **📅 Date Extraction**: Identifies and extracts dates from various formats (e.g., "15 Jan 2024", "January 15, 2024")
- **🏷️ Event Classification**: Automatically categorizes legal events into:
  - Filing
  - Hearing
  - Interim Order
  - Transfer
  - Judgment
  - Appeal
  - Other
- **👥 Person Name Extraction**: Uses Named Entity Recognition (NER) to identify parties and persons involved in the case
- **📊 Timeline Visualization**: Displays chronological timeline of all events

### User Interface
- **🎨 Modern UI**: Beautiful gradient design with custom CSS styling
- **📈 Statistics Dashboard**: 
  - Total events count
  - Event types distribution
  - Case duration in days
  - Most common event type
- **📊 Event Distribution Chart**: Visual bar chart showing event frequency
- **🗓️ Detailed Timeline View**: Expandable sections for each event with full descriptions
- **💾 Export Options**: Download timeline data as CSV or JSON

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Step 1: Clone or Download the Project
```bash
cd NLP_project
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Download spaCy Language Model
The application requires the English spaCy model. Install it using:
```bash
python -m spacy download en_core_web_sm
```

## 📁 Project Structure

```
NLP_project/
│
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
└── NLP_cases/            # Folder containing PDF case files
    ├── case1.pdf
    ├── case2.pdf
    └── ...
```

## 🎯 Usage

### 1. Prepare Your PDF Files
Place your court case PDF files in the `NLP_cases` folder.

### 2. Run the Application
```bash
streamlit run app.py
```

The application will automatically open in your default web browser at `http://localhost:8501`

### 3. Extract Timeline
1. **Select a PDF**: Choose a court case PDF from the dropdown menu
2. **Generate Timeline**: Click the "🚀 Generate Timeline" button
3. **View Results**: 
   - See parties involved at the top
   - Review statistics and event distribution
   - Browse the timeline table
   - Expand individual events for detailed descriptions
4. **Export Data**: Download the timeline as CSV or JSON

## 📋 Requirements

The project uses the following Python packages:

- **streamlit** - Web application framework
- **pdfplumber** - PDF text extraction
- **spacy** - Natural Language Processing and NER
- **dateparser** - Flexible date parsing
- **pandas** - Data manipulation and analysis

## 🔧 Technologies Used

- **Frontend**: Streamlit (Python web framework)
- **NLP**: spaCy (Named Entity Recognition, sentence segmentation)
- **PDF Processing**: pdfplumber
- **Data Processing**: pandas
- **Date Parsing**: dateparser
- **Styling**: Custom CSS

## 🎨 Features in Detail

### Event Detection
The application uses keyword-based detection to classify events:
- **Filing**: "filed", "instituted"
- **Hearing**: "heard", "arguments"
- **Interim Order**: "interim", "ex-parte", "stay"
- **Transfer**: "transferred"
- **Judgment**: "judgment", "decision", "held"
- **Appeal**: "appeal"

### Person Name Extraction
Uses two methods:
1. **Named Entity Recognition (NER)**: spaCy's built-in PERSON entity recognition
2. **Pattern Matching**: Detects case parties using patterns like:
   - "Plaintiff vs Defendant"
   - "Party A and Party B"

### Date Recognition
Supports multiple date formats:
- `DD MMM YYYY` (e.g., "15 Jan 2024")
- `DD MMMM YYYY` (e.g., "15 January 2024")
- `MMMM DD, YYYY` (e.g., "January 15, 2024")

## 📊 Output Format

The timeline is exported with the following columns:
- **Date**: Event date (YYYY-MM-DD format)
- **Event**: Event type/category
- **Persons**: Names of persons involved (comma-separated)
- **Description**: Full sentence/context from the document

## 🛠️ Customization

### Adding More Event Types
Edit the `EVENT_KEYWORDS` dictionary in `app.py`:
```python
EVENT_KEYWORDS = {
    "Your Event": ["keyword1", "keyword2"],
    # ... existing events
}
```

### Changing Data Folder
Modify the `DATA_FOLDER` variable in `app.py`:
```python
DATA_FOLDER = "your_folder_name"
```

### Styling
Customize the CSS in the `st.markdown()` section at the top of `app.py` to change colors, fonts, and layout.

## ⚠️ Limitations

- Date extraction works best with standard date formats
- Person name extraction may miss names in non-standard formats
- PDF quality affects text extraction accuracy
- Event classification is keyword-based and may require manual review

## 🔮 Future Enhancements

Potential improvements:
- Support for multiple date formats
- Machine learning-based event classification
- Court name and location extraction
- Case number extraction
- Multi-language support
- Batch processing of multiple PDFs
- Timeline visualization with interactive charts

## 📝 License

This project is open source and available for educational and research purposes.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## 📧 Support

For issues or questions, please open an issue in the project repository.

---

**Built with ❤️ using Streamlit and spaCy**

