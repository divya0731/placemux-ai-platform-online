import os
import sys
from fpdf import FPDF

class PlaceMuxDocPDF(FPDF):
    def header(self):
        # We don't display header on page 1 (cover page)
        if self.page_no() > 1:
            self.set_font("helvetica", "B", 8)
            self.set_text_color(100, 116, 139)  # Slate-500
            self.cell(0, 10, "PlaceMux AI - Technical Documentation & Developer Guide", align="R")
            self.ln(8)
            self.set_draw_color(226, 232, 240)  # Slate-200
            self.set_line_width(0.4)
            self.line(10, 18, 200, 18)
            self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(148, 163, 184)  # Slate-400
        # Left side: Confidential, Right side: Page X
        self.cell(100, 10, "Confidential - Internal Developer Reference", align="L")
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="R")

    def heading1(self, text):
        self.ln(6)
        self.set_font("helvetica", "B", 16)
        self.set_text_color(30, 41, 59)  # Slate-900 (primary)
        self.cell(0, 10, text)
        self.ln(10)
        self.set_draw_color(13, 148, 136)  # Teal-600 (secondary)
        self.set_line_width(0.8)
        # Draw line under heading
        y = self.get_y() - 1
        self.line(10, y, 200, y)
        self.set_line_width(0.2) # reset
        self.ln(4)

    def heading2(self, text):
        self.ln(4)
        self.set_font("helvetica", "B", 12)
        self.set_text_color(13, 148, 136)  # Teal-600
        self.cell(0, 8, text)
        self.ln(8)

    def heading3(self, text):
        self.ln(2)
        self.set_font("helvetica", "B", 10)
        self.set_text_color(71, 85, 105)  # Slate-600
        self.cell(0, 6, text)
        self.ln(6)

    def body_text(self, text):
        self.set_font("helvetica", "", 10)
        self.set_text_color(51, 65, 85)  # Slate-700
        self.multi_cell(0, 5, text)
        self.ln(3)

    def bullet_point(self, text, bold_prefix=""):
        self.set_font("helvetica", "", 10)
        self.set_text_color(51, 65, 85)
        self.cell(6, 5, "-", align="R")
        self.cell(2)
        if bold_prefix:
            self.set_font("helvetica", "B", 10)
            self.cell(self.get_string_width(bold_prefix) + 1, 5, bold_prefix)
            self.set_font("helvetica", "", 10)
        self.multi_cell(0, 5, text)
        self.ln(1)

    def code_block(self, code_lines):
        self.set_fill_color(248, 250, 252)  # Slate-50
        self.set_text_color(30, 41, 59)
        self.set_draw_color(226, 232, 240)
        self.set_font("courier", "", 9)
        code_text = "\n".join(code_lines)
        self.multi_cell(0, 4.5, code_text, border=1, fill=True)
        self.ln(3)

    def callout_box(self, title, text, severity="info"):
        # Set colors based on severity
        if severity == "warning":
            bg_color = (255, 251, 235)  # Amber-50
            border_color = (245, 158, 11)  # Amber-500
            text_color = (120, 53, 4)  # Amber-900
        elif severity == "danger":
            bg_color = (254, 242, 242)  # Red-50
            border_color = (239, 68, 68)  # Red-500
            text_color = (153, 27, 27)  # Red-900
        else: # info/success
            bg_color = (240, 253, 250)  # Teal-50
            border_color = (13, 148, 136)  # Teal-600
            text_color = (17, 94, 89)  # Teal-900

        self.set_fill_color(*bg_color)
        self.set_draw_color(*border_color)
        self.set_text_color(*text_color)
        self.set_font("helvetica", "B", 10)
        
        # Calculate current height needed
        self.set_line_width(0.6)
        # Create block using cell and multi_cell
        self.cell(0, 6, f" {title.upper()}", border="TLR", fill=True)
        self.ln(6)
        self.set_font("helvetica", "", 9.5)
        self.multi_cell(0, 5, f" {text}", border="BLR", fill=True)
        self.set_line_width(0.2)  # reset
        self.ln(3)

    def cover_page(self):
        self.add_page()
        # Top banner background (dark slate)
        self.set_fill_color(15, 23, 42)
        self.rect(0, 0, 210, 80, "F")
        
        # Logo Icon
        self.set_y(22)
        self.set_fill_color(13, 148, 136)
        self.rect(15, 22, 16, 16, "F")
        self.set_xy(15, 22)
        self.set_font("helvetica", "B", 20)
        self.set_text_color(255, 255, 255)
        self.cell(16, 16, "PM", align="C")
        self.ln(16)
        
        # Title
        self.set_y(44)
        self.set_font("helvetica", "B", 22)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, "PlaceMux AI Assessment Platform")
        self.ln(10)
        
        self.set_font("helvetica", "", 12)
        self.set_text_color(148, 163, 184)
        self.cell(0, 6, "Adaptive Cognitive Assessments with Real-Time Proctoring & Analytics")
        self.ln(6)
        
        # Metadata Card
        self.set_y(90)
        self.set_fill_color(248, 250, 252)
        self.set_draw_color(226, 232, 240)
        self.rect(15, 90, 180, 95, "DF")
        
        self.set_xy(20, 95)
        self.set_font("helvetica", "B", 11)
        self.set_text_color(30, 41, 59)
        self.cell(0, 8, "SYSTEM MANUAL & OPERATOR WORKBOOK")
        self.ln(8)
        self.ln(2)
        
        metadata = [
            ("Technical Focus", "AI/ML Developer Roles, Core IRT Platform, & Verification Tools"),
            ("Psychometric Engine", "3-Parameter Logistic (3PL) Item Response Theory (IRT)"),
            ("Parameter Calibration", "Joint Maximum Likelihood Estimation (JMLE) with Cold-Start Policies"),
            ("Stopping Rules", "Standard Error of Measurement (SEM) < 0.30 Threshold / Max 10 Items Limit"),
            ("AI Proctoring Engine", "Face-api.js Live Face Verification & Defocus Event Detection"),
            ("Decision Framework", "Severity-Weighted Cumulative Risk Scoring & Human-Review Routing"),
            ("Backend Architecture", "FastAPI (Python 3.12) + SQLite/PostgreSQL with SQLAlchemy ORM"),
            ("Frontend Client", "Single-Page Application (SPA) with Dark Glassmorphism Design System"),
            ("Fairness Auditing", "Cohen's d Effect Size Statistics & EEOC Four-Fifths Adverse Impact Rule"),
        ]
        
        for label, val in metadata:
            self.set_x(20)
            self.set_font("helvetica", "B", 8.5)
            self.set_text_color(71, 85, 105)
            self.cell(42, 5.5, label + ":")
            self.set_font("helvetica", "", 8.5)
            self.set_text_color(51, 65, 85)
            self.cell(0, 5.5, val)
            self.ln(5.5)
            
        self.set_xy(20, 172)
        self.set_font("helvetica", "I", 8.5)
        self.set_text_color(100, 116, 139)
        self.cell(0, 6, "Platform Build Status: Phase 1 (Production Complete) - June 2026")
        self.ln(6)
        
        # Graphic representation of components
        self.set_y(195)
        self.set_fill_color(241, 245, 249)
        self.set_draw_color(203, 213, 225)
        self.rect(15, 195, 180, 45, "DF")
        
        self.set_xy(20, 198)
        self.set_font("helvetica", "B", 9)
        self.set_text_color(13, 148, 136)
        self.cell(0, 5, "CORE PIPELINE OVERVIEW")
        self.ln(5)
        
        self.set_x(20)
        self.set_font("helvetica", "", 8.5)
        self.set_text_color(71, 85, 105)
        pipeline_desc = (
            "Registration (Saves profile, initializes video camera) -> "
            "Adaptive CAT Loop (Estimates ability, checks SEM threshold, selects max Fisher-Info item) -> "
            "Real-time Proctoring (Tracks face presence, defocus, and switch alerts) -> "
            "Final Score & Recommendations (Computes final EAP theta and matches candidates to career pathways)"
        )
        self.multi_cell(170, 4.5, pipeline_desc)
        
        # Bottom text
        self.set_y(255)
        self.set_font("helvetica", "B", 10)
        self.set_text_color(13, 148, 136)
        self.cell(0, 6, "Designed & Maintained by AI/ML Core Systems Team", align="C")
        self.ln(6)
        self.set_font("helvetica", "", 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 4, "PlaceMux Systems Inc. / Open Source Developer Guide", align="C")


def build_placemux_pdf(output_path="docs/placemux_documentation.pdf"):
    # Ensure directory exists
    dir_name = os.path.dirname(output_path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)

    pdf = PlaceMuxDocPDF()
    pdf.alias_nb_pages()
    
    # 1. Render Cover Page
    pdf.cover_page()
    
    # 2. Section 1: Introduction & Architecture
    pdf.add_page()
    pdf.heading1("1. Platform Overview & Architecture")
    pdf.body_text(
        "PlaceMux is a high-performance, AI-driven candidate assessment and placement platform designed "
        "to evaluate engineering students' cognitive capacity. Unlike standardized exams that force every "
        "candidate to answer the same fixed question list, PlaceMux leverages a Computerized Adaptive Testing "
        "(CAT) framework built upon 3-Parameter Logistic (3PL) Item Response Theory (IRT)."
    )
    
    pdf.heading2("System Topology")
    pdf.body_text(
        "The system follows a lightweight decoupled architecture utilizing a FastAPI backend and a Single-Page "
        "Application (SPA) frontend. A relational SQLite or PostgreSQL database handles candidate registration, "
        "item parameter structures, response tables, and session-based logs."
    )
    
    # Architecture chart in text (ASCII format using only safe characters)
    arch_lines = [
        " +-------------------------------------------------------------+",
        " |                      FRONTEND CLIENT                        |",
        " |    SPA Client (HTML5, Vanilla JS, Canvas Gauges, Charts)    |",
        " |    Real-time face tracking webcam overlay (face-api.js)    |",
        " +------------------------------+------------------------------+",
        "                                | HTTP REST APIs",
        " +------------------------------v------------------------------+",
        " |                      FASTAPI BACKEND                        |",
        " |  +-------------------------------------------------------+  |",
        " |  |                   AI/ML MATHEMATICS                   |  |",
        " |  | irt.py  ,  calibration.py  ,  recommendations.py     |  |",
        " |  | eval_harness.py  ,  fairness_check.py                 |  |",
        " |  +-------------------------------------------------------+  |",
        " |  SQLAlchemy ORM Data Mappers                                |",
        " +------------------------------+------------------------------+",
        "                                | SQLite / PostgreSQL",
        " +------------------------------v------------------------------+",
        " |                      DATABASE SCHEMA                        |",
        " |  questions , candidates , responses , proctoring_logs        |",
        " +-------------------------------------------------------------+"
    ]
    pdf.code_block(arch_lines)

    pdf.heading2("Technical Stack Overview")
    
    with pdf.table(col_widths=(45, 145), text_align="L") as table:
        row = table.row()
        row.cell("Layer")
        row.cell("Technologies & Modules")
        
        row = table.row()
        row.cell("Backend Server")
        row.cell("FastAPI (Python 3.12), Uvicorn ASGI Web Server")
        
        row = table.row()
        row.cell("Database Mapper")
        row.cell("SQLAlchemy ORM + SQLite/PostgreSQL Engine")
        
        row = table.row()
        row.cell("AI Math Pipeline")
        row.cell("Pure Python mathematical implementation (Math, NumPy, SciPy-free logic for extreme portability)")
        
        row = table.row()
        row.cell("Frontend Engine")
        row.cell("Vanilla JS (ES6), HTML5 Canvas-based telemetry gauges, Chart.js integrations")
        
        row = table.row()
        row.cell("Computer Vision")
        row.cell("face-api.js browser-level model execution (TensorFlow.js backend for zero-latency face tracking)")

    # 3. Section 2: Mathematical Engine (IRT)
    pdf.add_page()
    pdf.heading1("2. Mathematics of Adaptive Testing (IRT)")
    pdf.body_text(
        "At the core of the PlaceMux evaluation pipeline is the 3-Parameter Logistic (3PL) model. "
        "Standard testing counts the raw number of correct answers to generate a score. PlaceMux calculates "
        "a candidate's latent ability (represented as theta) by examining the specific properties of the items "
        "the student answered correctly or incorrectly."
    )
    
    pdf.heading2("The 3PL Model Formula")
    pdf.body_text(
        "For a candidate with latent ability theta, the probability of answering item i correctly is given by:"
    )
    
    formula_lines = [
        "                c_i + (1 - c_i)",
        " P(correct | theta) = ----------------------------------",
        "                      1 + exp(-a_i * (theta - b_i))"
    ]
    pdf.code_block(formula_lines)
    
    pdf.body_text("Where the parameters are defined as:")
    pdf.bullet_point("Discrimination parameter. Dictates how sharply the item distinguishes between candidates below or above the difficulty threshold. Higher value means a steeper slope.", bold_prefix="a_param: ")
    pdf.bullet_point("Difficulty parameter. Represents the point on the theta scale where a student with no guessing probability has a 50% chance of answering correctly.", bold_prefix="b_param: ")
    pdf.bullet_point("Guessing parameter (pseudo-chance). The floor probability that a student with extremely low ability will answer the item correctly by pure chance (e.g. 0.25 for 4 choices).", bold_prefix="c_param: ")
    
    pdf.heading2("Ability Estimation: EAP (Expected A Posteriori)")
    pdf.body_text(
        "Because maximum likelihood estimators (MLE) fail to compute when a candidate answers all items "
        "correctly or incorrectly, PlaceMux implements an Expected A Posteriori (EAP) algorithm. "
        "EAP estimates theta by integrating the likelihood function over a normal prior distribution:"
    )
    
    eap_math = [
        "                     Integrate [ theta * L(theta) * g(theta) d_theta ]",
        " Theta_EAP Estimate = -----------------------------------------------",
        "                       Integrate [ L(theta) * g(theta) d_theta ]"
    ]
    pdf.code_block(eap_math)
    
    pdf.body_text(
        "This integration is calculated numerically using standard Gauss-Hermite quadrature across a grid "
        "extending from -3.0 to +3.0 with 61 points. After estimating theta, the Standard Error of Measurement (SEM) "
        "is updated. The SEM indicates the standard deviation of our estimate's uncertainty."
    )
    
    pdf.heading2("Item Selection via Fisher Information")
    pdf.body_text(
        "To maximize testing efficiency, the item bank is scanned after each answered question. The system "
        "calculates the Fisher Information of each remaining question at the current estimated theta level, "
        "and selects the item that provides the maximum information:"
    )
    
    fisher_math = [
        "                   [ a_i * (1 - c_i) ]^2 * P_i(theta)",
        " Info_i(theta) = ----------------------------------------------",
        "                  (1 - P_i(theta)) * [ c_i + (1 - c_i) ]^2"
    ]
    pdf.code_block(fisher_math)
    
    pdf.body_text(
        "By delivering questions that supply the highest information at the candidate's exact estimated ability, "
        "the engine narrows the confidence interval of theta as rapidly as possible."
    )
    
    # 4. Section 3: Calibration & Recommendations
    pdf.add_page()
    pdf.heading1("3. Calibration & Recalibration (JMLE)")
    pdf.body_text(
        "While questions are initially created with difficulty tags (Easy, Medium, Hard) and seeded with "
        "SME-specified difficulties (e.g. -1.5, 0.0, 1.5), real candidate responses allow us to empirically "
        "calibrate the item bank parameters. This is achieved using Joint Maximum Likelihood Estimation (JMLE)."
    )
    
    pdf.heading2("The Calibration Pipeline")
    pdf.body_text(
        "When a administrator triggers recalibration, the pipeline follows this logic:"
    )
    pdf.bullet_point("Filters out items with fewer than 10 total responses to ensure stability.", "Min Response Filter: ")
    pdf.bullet_point("Constructs a candidate-by-item response matrix from the responses logged in the database.", "Matrix Setup: ")
    pdf.bullet_point("Runs alternating iterations: first estimating candidate abilities based on current item parameters, then refining item difficulties based on estimated candidate abilities using Newton-Raphson optimization.", "Iterative Refinement: ")
    pdf.bullet_point("Standardizes difficulties so the mean item difficulty remains centered around 0.0.", "Scaling Constraint: ")
    pdf.bullet_point("Persists the updated b_param parameters back to the question bank.", "DB Persistence: ")
    
    pdf.callout_box(
        "Cold-Start Mitigation Policy",
        "To avoid unstable updates, items with fewer than 10 responses are locked from JMLE recalibration, "
        "retaining their original expert-seeded values. This ensures that new questions are not distorted "
        "by anomalous early response vectors.",
        "warning"
    )

    pdf.heading1("4. Career Recommendation Engine")
    pdf.body_text(
        "Once a test completes, the candidate's performance profile is converted into a structured vector. "
        "We compute competency scores based on the candidate's responses within specific cognitive topics "
        "(e.g., Python OOP, Data Structures). The resulting skills vector is compared against job profiles."
    )
    
    pdf.heading2("Ranking Formulation")
    pdf.body_text(
        "The matching engine scores each job role in the ontology. The math incorporates the candidate's scaled "
        "ability score and the percentage overlap between the candidate's strong competencies and the job's "
        "required competencies. The recommendations are returned to the user sorted by this score, "
        "accompanied by dynamic, natural explainability descriptions (e.g. 'Your high ability in Backend Architecture "
        "aligns perfectly with the requirements for a Senior Python Developer...')."
    )

    # 5. Section 4: Proctoring & Integrity Risk Fusion
    pdf.add_page()
    pdf.heading1("5. Real-Time Proctoring & Integrity Risk")
    pdf.body_text(
        "To ensure the credibility of assessments taken remotely, PlaceMux integrates browser-side "
        "computer vision (face-api.js) and event telemetry (focus tracking) to assess integrity risks "
        "without violating candidate privacy."
    )
    
    pdf.heading2("Detection Telemetry & Event Logging")
    pdf.body_text(
        "During the assessment, the frontend executes live facial detection. If a violation is found, "
        "an event is instantly posted to the backend API. Telemetry logs record three primary risk profiles:"
    )
    
    with pdf.table(col_widths=(40, 20, 130), text_align="L") as table:
        row = table.row()
        row.cell("Event Type")
        row.cell("Severity")
        row.cell("Telemetry / Detection Logic")
        
        row = table.row()
        row.cell("TAB_SWITCH")
        row.cell("HIGH")
        row.cell("Triggered when candidate switches browser tabs or minimizes the window.")
        
        row = table.row()
        row.cell("NO_FACE")
        row.cell("HIGH")
        row.cell("Triggered when no face is detected in the video frame for > 0.75 seconds.")
        
        row = table.row()
        row.cell("MULTIPLE_FACES")
        row.cell("HIGH")
        row.cell("Triggered when 2 or more faces are detected in the webcam view.")
        
        row = table.row()
        row.cell("WINDOW_DEFOCUS")
        row.cell("MEDIUM")
        row.cell("Triggered when the exam viewport loses focus, suggesting external application interaction.")
        
        row = table.row()
        row.cell("AUDIO_SPIKE")
        row.cell("LOW")
        row.cell("Triggered if surrounding audio levels cross ambient thresholds (ambient + 25dB).")

    pdf.heading2("Cumulative Risk Fusion & Scoring")
    pdf.body_text(
        "Instead of immediately failing a candidate upon a single minor violation (which creates high false-positive rates), "
        "PlaceMux uses a weighted fusion algorithm. Each event has a severity point value:"
    )
    pdf.bullet_point("30 points (e.g., TAB_SWITCH, MULTIPLE_FACES, NO_FACE)", "HIGH Severity: ")
    pdf.bullet_point("20 points (e.g., WINDOW_DEFOCUS)", "MEDIUM Severity: ")
    pdf.bullet_point("10 points (e.g., AUDIO_SPIKE)", "LOW Severity: ")
    
    pdf.body_text(
        "The total risk score is the sum of these values, capped at 100%. Based on this score, the candidate "
        "is categorised into a risk level and routed accordingly:"
    )
    pdf.bullet_point("Risk score 0 - 29. The session is considered secure. Automated clearance is granted.", "LOW RISK: ")
    pdf.bullet_point("Risk score 30 - 59. The session is flagged. The results are recorded, but marked as warning.", "MEDIUM RISK: ")
    pdf.bullet_point("Risk score 60 or above. The session is flagged for manual audit. Results are locked pending supervisor review.", "HIGH RISK: ")

    pdf.callout_box(
        "Critical Decision Policy",
        "PlaceMux does not auto-fail high-risk students during the test to prevent candidate panic or disruptions "
        "caused by false-positive hardware issues. Instead, the session is completed and routed to a supervisor queue.",
        "danger"
    )

    # 6. Section 5: Offline Evaluation & Fairness
    pdf.add_page()
    pdf.heading1("6. System Auditing: Evaluation & Fairness")
    pdf.body_text(
        "To ensure the adaptive engine remains scientifically valid and free from systematic bias, two "
        "auditing utilities are built directly into the AI/ML suite: `eval_harness.py` and `fairness_check.py`."
    )
    
    pdf.heading2("Offline Evaluation Harness (eval_harness.py)")
    pdf.body_text(
        "The evaluation harness simulates a distribution of synthetic candidates (e.g., 500 simulated test-takers) "
        "whose true abilities (true theta) are drawn from a standard normal distribution. The harness runs "
        "them through the adaptive CAT pipeline and evaluates the following key metrics:"
    )
    pdf.bullet_point("Bias = Mean(estimated_theta - true_theta). Measures systematic over- or under-estimation. Ideal: ~0.0.", "Theta Bias: ")
    pdf.bullet_point("RMSE = Root Mean Squared Error. Measures deviation. Must remain below 0.35.", "Root Mean Square Error: ")
    pdf.bullet_point("Checks if the candidate's true theta lies within the 95% confidence interval of the EAP estimate (theta +- 1.96 * SEM). Must be >= 90%.", "Confidence Interval Coverage: ")
    pdf.bullet_point("Measures the number of questions required before stopping. Typically ranges between 6 and 10 questions.", "Average Item Load: ")

    pdf.heading2("Fairness & Disparate Impact Auditing (fairness_check.py)")
    pdf.body_text(
        "PlaceMux enforces fairness standard tests across engineering branches (e.g. CSE vs ECE) to check "
        "if questions bias against specific groups. It applies two industry-standard statistics:"
    )
    
    pdf.heading3("1. Cohen's d Effect Size")
    pdf.body_text(
        "Cohen's d measures the standardized difference in mean scores between two groups. "
        "A difference of less than 0.2 is small, while greater than 0.8 is large. PlaceMux triggers "
        "a warning if the absolute value of Cohen's d exceeds 0.5:"
    )
    pdf.code_block([
        "            Mean_Group1 - Mean_Group2",
        " Cohen's d = -------------------------",
        "                Pooled_StdDev"
    ])
    
    pdf.heading3("2. EEOC 4/5ths Rule (Adverse Impact)")
    pdf.body_text(
        "Adapted from the US Equal Employment Opportunity Commission, this rule states that the passing (or high-scoring) "
        "rate of the lower-performing group must be at least 80% (four-fifths) of the higher-performing group's rate. "
        "If the ratio is below 0.80, the system flags a potential disparate impact in the question pool, prompting "
        "item audit."
    )

    # 7. Section 6: Database & API Catalog
    pdf.add_page()
    pdf.heading1("7. Database Schema & Data Models")
    pdf.body_text(
        "The relational database contains five core tables. The ORM models are declared in `backend/models/`."
    )
    
    pdf.heading2("1. `questions` Table (Item Bank)")
    with pdf.table(col_widths=(35, 30, 125), text_align="L") as table:
        row = table.row()
        row.cell("Column")
        row.cell("Type")
        row.cell("Description")
        
        row = table.row()
        row.cell("question_id")
        row.cell("VARCHAR (PK)")
        row.cell("Unique identifier (e.g. 'CSE-Q01').")
        
        row = table.row()
        row.cell("competency_id")
        row.cell("VARCHAR")
        row.cell("Links to skill ontology (e.g. 'CSE001').")
        
        row = table.row()
        row.cell("question")
        row.cell("TEXT")
        row.cell("The text of the question.")
        
        row = table.row()
        row.cell("a_param")
        row.cell("FLOAT")
        row.cell("IRT Discrimination parameter (seeded default: 1.0).")
        
        row = table.row()
        row.cell("b_param")
        row.cell("FLOAT")
        row.cell("IRT Difficulty parameter (recalibrated by JMLE).")
        
        row = table.row()
        row.cell("c_param")
        row.cell("FLOAT")
        row.cell("IRT Guessing parameter (seeded default: 0.25).")

    pdf.heading2("2. `proctoring_logs` Table (Violations Log)")
    with pdf.table(col_widths=(35, 30, 125), text_align="L") as table:
        row = table.row()
        row.cell("Column")
        row.cell("Type")
        row.cell("Description")
        
        row = table.row()
        row.cell("id")
        row.cell("INTEGER (PK)")
        row.cell("Auto-increment primary key.")
        
        row = table.row()
        row.cell("candidate_id")
        row.cell("INTEGER (FK)")
        row.cell("Links to candidates table.")
        
        row = table.row()
        row.cell("event_type")
        row.cell("VARCHAR")
        row.cell("TAB_SWITCH, NO_FACE, MULTIPLE_FACES, Defocus.")
        
        row = table.row()
        row.cell("severity")
        row.cell("VARCHAR")
        row.cell("LOW, MEDIUM, or HIGH.")
        
        row = table.row()
        row.cell("timestamp")
        row.cell("DATETIME")
        row.cell("UTC timestamp of the violation.")

    pdf.heading1("8. API Endpoint Reference")
    pdf.body_text(
        "All API endpoints are registered on the FastAPI app under the `/api` prefix."
    )
    pdf.bullet_point("POST /candidate - Register a new candidate. Body: name, email.", "Candidate Setup: ")
    pdf.bullet_point("POST /api/next-question - Returns the next adaptive question based on current response history. Body: candidate_id, answers list. Returns finished=true when SEM < 0.30.", "Next Question: ")
    pdf.bullet_point("POST /api/submit-answer - Submits a candidate response. Body: candidate_id, question_id, response (A/B/C/D), time_taken.", "Submit Answer: ")
    pdf.bullet_point("POST /api/final-score - Computes final theta, scaled score (300-900), percentile and SEM. Saves to scores table. Body: candidate_id.", "Final Score: ")
    pdf.bullet_point("GET /api/recommendations/{candidate_id} - Fetches career recommendations and explainability descriptions.", "Get Recommendations: ")
    pdf.bullet_point("POST /api/proctoring-verdict - Submits a violation. Body: candidate_id, event_type, severity. Returns updated cumulative risk score.", "Log Proctoring Event: ")
    pdf.bullet_point("GET /api/proctoring-report/{candidate_id} - Fetches the complete integrity log and human audit routing verdict.", "Proctoring Report: ")
    pdf.bullet_point("POST /api/recalibrate - Runs JMLE parameter recalibration. Returns a list of updated difficulty parameters.", "Recalibrate Item Bank: ")

    # 8. Section 7: How to Run
    pdf.add_page()
    pdf.heading1("9. Developer Operations (How to Run & Test)")
    pdf.body_text(
        "Follow these steps to spin up the local environment, run tests, and execute evaluation harness tasks."
    )
    
    pdf.heading2("1. Environment Prerequisites")
    pdf.body_text(
        "The project requires Python 3.12+ and pip. A virtual environment is highly recommended. "
        "No heavy machine learning frameworks (like TensorFlow or PyTorch) are required on the backend, "
        "keeping dependencies lightweight and memory usage low."
    )
    
    pdf.heading2("2. Database Setup & Seeding")
    pdf.body_text(
        "Before starting the application for the first time, initialize and seed the database with "
        "pre-calibrated questions (15 items covering Python OOP and advanced syntax):"
    )
    pdf.code_block([
        "cd backend",
        "python seed.py"
    ])
    
    pdf.heading2("3. Start Backend Application Server")
    pdf.body_text(
        "Run the FastAPI server using Uvicorn with auto-reload enabled for development:"
    )
    pdf.code_block([
        "cd backend",
        "python -m uvicorn main:app --reload --port 8000"
    ])
    
    pdf.heading2("4. Start Frontend Assessment App")
    pdf.body_text(
        "The frontend is served directly as static files by FastAPI at http://localhost:8000. "
        "Open your web browser, navigate to http://localhost:8000, and register a candidate. "
        "Grant webcam access when prompted to enable real-time face verification."
    )
    
    pdf.heading2("5. Executing AI/ML Verification Scripts")
    pdf.body_text(
        "You can run the offline simulation harness and the fairness auditing suite from your terminal:"
    )
    pdf.code_block([
        "# Run simulation and output metrics (RMSE, Bias, SEM coverage)",
        "python backend/ai_engine/eval_harness.py",
        "",
        "# Run Cohen's d and 4/5ths fairness checks",
        "python backend/ai_engine/fairness_check.py"
    ])
    
    pdf.heading2("6. Triggering Item Recalibration")
    pdf.body_text(
        "Once candidates have completed several assessment sessions, trigger the Joint Maximum Likelihood Estimation "
        "pipeline to update item difficulties based on empirical response data:"
    )
    pdf.code_block([
        "curl -X POST http://localhost:8000/api/recalibrate"
    ])

    # Save to path
    pdf.output(output_path)
    print(f"PDF successfully generated at: {output_path}")

if __name__ == "__main__":
    path = "docs/placemux_documentation.pdf"
    if len(sys.argv) > 1:
        path = sys.argv[1]
    build_placemux_pdf(path)
