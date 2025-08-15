# Resume Parser

A comprehensive Flask-based web application for parsing and analyzing resumes using AI/ML techniques. This application helps HR professionals and recruiters efficiently screen and match candidates with job requirements.

## Features

- **Resume Upload & Parsing**: Support for PDF and DOCX resume formats
- **AI-Powered Analysis**: Uses BERT-based models for intelligent resume analysis
- **Job Matching**: Automatically matches resumes with job requirements
- **Candidate Scoring**: Provides detailed scoring and ranking of candidates
- **User Management**: Separate dashboards for HR professionals and candidates
- **Job Posting**: Create and manage job postings
- **Database Storage**: SQLite database for storing parsed data and user information

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Database**: SQLite with SQLAlchemy ORM
- **AI/ML**: BERT models for text analysis
- **File Processing**: PyPDF2, python-docx
- **Authentication**: Flask-Login

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Mokshith-Byreddy/resume-parser.git
   cd resume-parser
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## Project Structure

```
resume-parser/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── .gitignore           # Git ignore rules
├── templates/           # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   ├── hr_dashboard.html
│   └── create_job.html
├── utils/               # Utility modules
│   ├── bert_analyzer.py
│   ├── job_recommendations.py
│   └── __init__.py
├── uploads/            # Uploaded resume files
└── instance/          # Database files (not in version control)
```

## Usage

### For HR Professionals
1. Register/Login to access the HR dashboard
2. Create job postings with specific requirements
3. Upload candidate resumes
4. View AI-generated analysis and matching scores
5. Review candidate rankings and detailed insights

### For Candidates
1. Register/Login to access the candidate dashboard
2. Upload your resume
3. View job recommendations based on your profile
4. Track application status

## API Endpoints

- `GET /` - Home page
- `GET /login` - Login page
- `POST /login` - User authentication
- `GET /register` - Registration page
- `POST /register` - User registration
- `GET /dashboard` - Candidate dashboard
- `GET /hr_dashboard` - HR dashboard
- `POST /upload_resume` - Resume upload
- `GET /create_job` - Job creation page
- `POST /create_job` - Create new job posting

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

**Mokshith Byreddy**
- GitHub: [@Mokshith-Byreddy](https://github.com/Mokshith-Byreddy)

## Acknowledgments

- Flask framework and its ecosystem
- BERT models for natural language processing
- Bootstrap for responsive UI design
- All contributors and open-source libraries used in this project
