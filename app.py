import re
from pathlib import Path
from datetime import datetime

import joblib
import streamlit as st


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="AI Job Scam Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

MODEL_PATH = next(
    (
        p for p in [
            Path("scam_model.joblib"),
            Path("job_scam_model.joblib"),
        ]
        if p.exists()
    ),
    Path("scam_model.joblib"),
)


# --------------------------------------------------
# SESSION STATE
# Keeping the result here prevents it disappearing
# when a checkbox is clicked and Streamlit reruns.
# --------------------------------------------------
if "posting_text" not in st.session_state:
    st.session_state.posting_text = ""

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "scan_history" not in st.session_state:
    st.session_state.scan_history = []

# --------------------------------------------------
# COLOURS
# --------------------------------------------------
NAVY = "#0B1F3A"
BLUE = "#2563EB"
TEAL = "#0F766E"
RED = "#DC2626"
AMBER = "#D97706"
GREEN = "#15803D"
BG = "#F4F7FB"
CARD = "#FFFFFF"
TEXT = "#172033"
MUTED = "#64748B"
BORDER = "#E2E8F0"


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------
st.markdown(
    f"""
<style>
.stApp {{
    background:
        radial-gradient(
            circle at 0% 0%,
            rgba(37,99,235,.08),
            transparent 24%
        ),
        radial-gradient(
            circle at 100% 5%,
            rgba(15,118,110,.07),
            transparent 20%
        ),
        {BG};
    color: {TEXT};
}}

.block-container {{
    max-width: 1220px;
    padding-top: 1.4rem;
    padding-bottom: 3rem;
}}

.hero {{
    background: linear-gradient(
        135deg,
        {NAVY} 0%,
        {BLUE} 55%,
        {TEAL} 100%
    );
    padding: 2rem 2.3rem 2.1rem;
    border-radius: 26px;
    color: white;
    box-shadow: 0 18px 42px rgba(11,31,58,.17);
    margin-bottom: 1.1rem;
    position: relative;
    overflow: hidden;
}}

.hero-title {{
    font-size: 2.35rem;
    line-height: 1.15;
    font-weight: 850;
    margin: 0;
    letter-spacing: -.02em;
}}

.hero-subtitle {{
    font-size: 1rem;
    opacity: .92;
    line-height: 1.6;
    max-width: 900px;
    margin-top: .65rem;
}}

.hero-tag {{
    display: inline-block;
    padding: .35rem .7rem;
    border-radius: 999px;
    background: rgba(255,255,255,.15);
    border: 1px solid rgba(255,255,255,.2);
    font-size: .78rem;
    font-weight: 700;
    margin-bottom: .9rem;
}}

.stat-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: .9rem;
    margin: 1rem 0 1.35rem;
}}

.stat-card {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 18px;
    padding: 1rem 1.1rem;
    box-shadow: 0 8px 22px rgba(15,23,42,.05);
}}

.stat-icon {{
    font-size: 1.25rem;
}}

.stat-title {{
    color: {MUTED};
    font-size: .8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .06em;
    margin-top: .35rem;
}}

.stat-value {{
    color: {NAVY};
    font-size: 1.05rem;
    font-weight: 800;
    margin-top: .2rem;
}}

.section-title {{
    font-size: 1.15rem;
    font-weight: 850;
    color: {NAVY};
    margin: .15rem 0 .3rem;
}}

.section-title span {{
    color: {BLUE};
}}

.section-text {{
    color: {MUTED};
    font-size: .9rem;
    line-height: 1.5;
    margin-bottom: .85rem;
}}

.feature {{
    display: flex;
    gap: .65rem;
    align-items: flex-start;
    padding: .7rem .75rem;
    border: 1px solid {BORDER};
    border-radius: 14px;
    margin: .5rem 0;
    background: #FAFCFF;
}}

.feature-icon {{
    font-size: 1.05rem;
    margin-top: .05rem;
}}

.feature-title {{
    font-weight: 750;
    color: {TEXT};
    font-size: .88rem;
}}

.feature-sub {{
    color: {MUTED};
    font-size: .78rem;
    margin-top: .1rem;
    line-height: 1.45;
}}

.example-box {{
    border-radius: 15px;
    border: 1px dashed #BFDBFE;
    background: #EFF6FF;
    padding: .8rem .9rem;
    margin-top: .7rem;
}}

.example-title {{
    font-size: .82rem;
    font-weight: 800;
    color: #1D4ED8;
}}

.example-text {{
    font-size: .76rem;
    color: #475569;
    margin-top: .2rem;
    line-height: 1.45;
}}

.result {{
    border-radius: 20px;
    padding: 1.3rem 1.35rem;
    color: white;
    box-shadow: 0 12px 30px rgba(15,23,42,.13);
}}

.result-safe {{
    background: linear-gradient(135deg, {GREEN}, #22C55E);
}}

.result-risk {{
    background: linear-gradient(135deg, {RED}, #F97316);
}}

.result-label {{
    font-size: .82rem;
    font-weight: 800;
    letter-spacing: .06em;
}}

.score {{
    font-size: 2.75rem;
    line-height: 1;
    font-weight: 900;
    margin: .45rem 0 .35rem;
}}

.result-copy {{
    font-size: .88rem;
    opacity: .94;
    line-height: 1.5;
}}

.mini-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: .75rem;
    margin-top: .8rem;
}}

.mini {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: .9rem;
    text-align: center;
}}

.mini-value {{
    font-size: 1.25rem;
    font-weight: 850;
    color: {NAVY};
}}

.mini-label {{
    color: {MUTED};
    font-size: .75rem;
    margin-top: .1rem;
}}

.warn {{
    background: #FFF7ED;
    border: 1px solid #FED7AA;
    border-left: 4px solid {AMBER};
    padding: .8rem 1rem;
    border-radius: 12px;
    margin: .5rem 0;
    color: #7C2D12;
    font-size: .86rem;
    line-height: 1.45;
}}

.safe {{
    background: #F0FDF4;
    border: 1px solid #BBF7D0;
    border-left: 4px solid {GREEN};
    padding: .8rem 1rem;
    border-radius: 12px;
    color: #14532D;
    font-size: .86rem;
    line-height: 1.45;
}}

/* VERIFICATION CHECKLIST */
[data-testid="stCheckbox"] {{
    margin: .42rem 0 !important;
}}

[data-testid="stCheckbox"] > label {{
    display: flex !important;
    align-items: center !important;
    gap: .75rem !important;
    width: 100% !important;
    min-height: 58px !important;
    box-sizing: border-box !important;
    padding: .78rem .9rem !important;
    background: #FFFFFF !important;
    border: 1px solid #D9E2EF !important;
    border-radius: 14px !important;
    box-shadow: 0 3px 10px rgba(11,31,58,.035) !important;
    transition: background .16s ease,
                border-color .16s ease,
                box-shadow .16s ease !important;
}}

[data-testid="stCheckbox"] > label:hover {{
    border-color: #7EA5E8 !important;
    box-shadow: 0 4px 13px rgba(37,99,235,.08) !important;
}}

[data-testid="stCheckbox"] > label:has(input:checked) {{
    background: #ECF7F0 !important;
    border-color: #75B78A !important;
    box-shadow: inset 4px 0 0 #15803D !important;
}}

[data-testid="stCheckbox"] input[type="checkbox"] {{
    accent-color: #15803D !important;
    width: 18px !important;
    height: 18px !important;
    cursor: pointer !important;
}}

[data-testid="stCheckbox"] label p {{
    color: #172033 !important;
    font-size: .88rem !important;
    line-height: 1.4 !important;
    margin: 0 !important;
}}

.verify-progress-card {{
    background: #F1F5F9;
    border: 1px solid #DCE5EF;
    border-radius: 14px;
    padding: .9rem;
    margin: .8rem 0 .4rem;
}}

.verify-heading {{
    font-size: .76rem;
    font-weight: 800;
    letter-spacing: .07em;
    color: #64748B;
    text-transform: uppercase;
}}

.verify-progress-number {{
    font-size: 1.35rem;
    font-weight: 850;
    color: #0B1F3A;
    margin-top: .2rem;
}}

.verify-progress-copy {{
    font-size: .78rem;
    color: #64748B;
    margin-top: .1rem;
}}

div.stButton > button {{
    border-radius: 12px;
    font-weight: 750;
    min-height: 2.7rem;
}}

button[kind="primary"] {{
    box-shadow: 0 8px 18px rgba(37,99,235,.18);
}}

textarea {{
    border-radius: 14px !important;
}}

.footer {{
    color: {MUTED};
    text-align: center;
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid {BORDER};
    font-size: .75rem;
}}

@media (max-width: 820px) {{
    .stat-grid, .mini-grid {{
        grid-template-columns: 1fr;
    }}

    .hero-title {{
        font-size: 1.8rem;
    }}
}}
</style>
""",
    unsafe_allow_html=True,
)


# --------------------------------------------------
# WARNING-SIGN DETECTION
# --------------------------------------------------
def detect_flags(text: str) -> list[str]:
    rules = [
        (
            r"registration|processing fee|application fee|security deposit|verification fee|pay .* fee|transfer .* fee",
            "Requests a payment, fee or deposit",
        ),
        (
            r"guaranteed|instant joining|no interview|no qualification|no experience.*huge salary|unlimited income",
            "Promises unrealistic or unusually easy employment",
        ),
        (
            r"whatsapp|telegram",
            "Uses informal messaging as the main contact channel",
        ),
        (
            r"aadhaar|aadhar|pan card|bank details|otp|one-time password",
            "Requests sensitive personal or financial information",
        ),
        (
            r"urgent|today|within 30 minutes|limited seats|act now|immediately",
            "Uses pressure or urgency to force a quick decision",
        ),
        (
            r"refund.*fee|refundable.*deposit",
            "Uses a refundable-fee claim as an incentive to pay",
        ),
    ]

    flags = []

    for pattern, message in rules:
        if re.search(pattern, text, flags=re.IGNORECASE):
            flags.append(message)

    return flags


# --------------------------------------------------
# SAMPLE POSTINGS
# --------------------------------------------------
SUSPICIOUS_SAMPLE = """URGENT WORK FROM HOME JOB!

Earn ₹50,000 per week with no experience required.
You are already selected for the position.
Pay ₹999 registration fee immediately to receive your joining letter.
Contact us only on WhatsApp.
Send your Aadhaar card, PAN card and bank details for verification.
Limited seats available. Apply today!"""

GENUINE_SAMPLE = """We are hiring a Data Analyst Intern for our analytics team.

Candidates should have basic knowledge of Excel, SQL and Power BI.
The internship includes a monthly stipend and a structured learning program.
Applicants can submit their resume through the company's official careers page.
Shortlisted candidates will attend an online technical assessment followed by an interview with the hiring team."""


# --------------------------------------------------
# INITIAL SESSION STATE
# --------------------------------------------------
if "verification_checks" not in st.session_state:
    st.session_state.verification_checks = {}

for i in range(5):
    key = f"job_verification_check_{i}"

    if key not in st.session_state:
        st.session_state[key] = False


# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown(
    """
<div class="hero">
    <div class="hero-tag">AI-POWERED EMPLOYMENT SAFETY</div>
    <div class="hero-title">🛡️ AI Job Scam Detection & Verification Agent</div>
    <div class="hero-subtitle">
        Check a job or internship posting before you trust it.
        The prototype combines machine-learning text classification
        with rule-based warning signals to highlight potentially
        suspicious employment offers.
    </div>
</div>
""",
    unsafe_allow_html=True,
)


# --------------------------------------------------
# TOP FEATURE CARDS
# --------------------------------------------------
st.markdown(
    """
<div class="stat-grid">
    <div class="stat-card">
        <div class="stat-icon">🤖</div>
        <div class="stat-title">AI Screening</div>
        <div class="stat-value">TF-IDF + Logistic Regression</div>
    </div>
    <div class="stat-card">
        <div class="stat-icon">🚩</div>
        <div class="stat-title">Risk Signals</div>
        <div class="stat-value">Payment, urgency, data & contact checks</div>
    </div>
    <div class="stat-card">
        <div class="stat-icon">⚡</div>
        <div class="stat-title">Decision Support</div>
        <div class="stat-value">Risk score + reasons + next action</div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)


# --------------------------------------------------
# MODEL CHECK
# --------------------------------------------------
if not MODEL_PATH.exists():
    st.warning(
        "Model not found. Run train_model.py once before using the analyzer."
    )


# --------------------------------------------------
# MAIN INPUT AREA
# --------------------------------------------------
left, right = st.columns([1.5, 0.9], gap="large")

with left:
    st.markdown(
        '<div class="section-title">📄 Analyze a <span>Job Posting</span></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-text">Paste the complete job or internship description. Include salary, contact method, fees and application instructions whenever available.</div>',
        unsafe_allow_html=True,
    )

    b1, b2, b3 = st.columns(3)

    with b1:
        if st.button("🚨 Try suspicious sample", use_container_width=True):
            st.session_state.posting_text = SUSPICIOUS_SAMPLE

    with b2:
        if st.button("✅ Try genuine sample", use_container_width=True):
            st.session_state.posting_text = GENUINE_SAMPLE

    with b3:
        if st.button("🧹 Clear", use_container_width=True):
            st.session_state.posting_text = ""
            st.session_state.analysis_result = None

            for i in range(5):
                st.session_state[f"job_verification_check_{i}"] = False

    text_input = st.text_area(
        "Job or internship description",
        height=265,
        key="posting_text",
        placeholder="Example: We are hiring a data analyst intern...",
        label_visibility="collapsed",
    )

    st.caption(
        f"{len(text_input)} characters • More complete postings usually give the analyzer more context."
    )

    analyze = st.button(
        "🔍 Analyze Job Posting",
        type="primary",
        use_container_width=True,
    )


# --------------------------------------------------
# RIGHT-SIDE INFORMATION
# --------------------------------------------------
with right:
    st.markdown(
        '<div class="section-title">🔎 What the <span>Agent Checks</span></div>',
        unsafe_allow_html=True,
    )

    features = [
        (
            "💳",
            "Payment requests",
            "Registration, processing or security fees",
        ),
        (
            "💰",
            "Unrealistic offers",
            "Very high pay with little or no qualification",
        ),
        (
            "⏱️",
            "Pressure language",
            "Urgency designed to force a quick decision",
        ),
        (
            "📱",
            "Contact patterns",
            "WhatsApp/Telegram-only or informal communication",
        ),
        (
            "🔐",
            "Sensitive data",
            "Aadhaar, PAN, bank details or OTP requests",
        ),
    ]

    for icon, title, desc in features:
        st.markdown(
            f"""
<div class="feature">
    <div class="feature-icon">{icon}</div>
    <div>
        <div class="feature-title">{title}</div>
        <div class="feature-sub">{desc}</div>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

    st.markdown(
        """
<div class="example-box">
    <div class="example-title">💡 Tip</div>
    <div class="example-text">
        For stronger screening, paste the entire posting rather than
        only the job title. The model uses the text itself and the
        agent checks common warning signals.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# ANALYSIS BUTTON
# Store the entire result in session_state.
# It stays available when a checklist item is clicked.
# --------------------------------------------------
if analyze:
    if not text_input.strip():
        st.session_state.analysis_result = None
        st.error("Please paste a job or internship description first.")

    elif not MODEL_PATH.exists():
        st.session_state.analysis_result = None
        st.error("Please train the model first with train_model.py.")

    else:
        try:
            model = joblib.load(MODEL_PATH)

            probabilities = model.predict_proba([text_input])[0]
            classes = list(model.classes_)
            prob_map = dict(zip(classes, probabilities))

            ml_risk = float(prob_map.get("suspicious", 0.0))

            flags = detect_flags(text_input)
            rule_risk = min(1.0, 0.16 * len(flags))

            risk = min(
                1.0,
                0.75 * ml_risk + 0.25 * rule_risk,
            )

            suspicious = risk >= 0.50
            confidence = risk if suspicious else 1 - risk

            if suspicious:
                label = "POTENTIALLY SUSPICIOUS"
                summary = (
                    "The posting contains patterns that deserve "
                    "additional verification before you proceed."
                )
                result_class = "result-risk"
                icon = "🚨"
                score_text = f"{risk * 100:.0f}% risk"

            else:
                label = "LIKELY GENUINE"
                summary = (
                    "No strong suspicious pattern was detected by "
                    "the prototype, but normal employer verification "
                    "is still recommended."
                )
                result_class = "result-safe"
                icon = "✅"
                score_text = f"{(1 - risk) * 100:.0f}% safety signal"

            # IMPORTANT:
            # Store results so checkbox reruns do not remove them.
            st.session_state.analysis_result = {
                "text": text_input,
                "ml_risk": ml_risk,
                "rule_risk": rule_risk,
                "risk": risk,
                "flags": flags,
                "suspicious": suspicious,
                "confidence": confidence,
                "label": label,
                "summary": summary,
                "result_class": result_class,
                "icon": icon,
                "score_text": score_text,
            }
            st.session_state.scan_history.insert(0, {
                "time": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                "result": label,
                "score": score_text,
                "warnings": len(flags),
                "posting": " ".join(text_input.split())[:180],
            })

            # Keep the latest 10 scans
            st.session_state.scan_history = (
                st.session_state.scan_history[:10]
            )
        except Exception as exc:
            st.error(
                f"The posting could not be analyzed. "
                f"Check that the trained model matches this app. Details: {exc}"
            )


# --------------------------------------------------
# DISPLAY SAVED RESULT
# This section runs on every rerun while a result exists.
# So checkbox clicks won't hide the results.
# --------------------------------------------------
result = st.session_state.analysis_result

if result is not None:
    text_input = result["text"]
    ml_risk = result["ml_risk"]
    rule_risk = result["rule_risk"]
    risk = result["risk"]
    flags = result["flags"]
    suspicious = result["suspicious"]
    confidence = result["confidence"]

    st.markdown(
        "<div style='margin-top:1.2rem'></div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-title">📊 Safety <span>Assessment</span></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
<div class="result {result["result_class"]}">
    <div class="result-label">
        {result["icon"]} {result["label"]}
    </div>
    <div class="score">{result["score_text"]}</div>
    <div class="result-copy">{result["summary"]}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
<div class="mini-grid">
    <div class="mini">
        <div class="mini-value">{len(flags)}</div>
        <div class="mini-label">Warning signals</div>
    </div>
    <div class="mini">
        <div class="mini-value">{confidence * 100:.0f}%</div>
        <div class="mini-label">Screening indicator</div>
    </div>
    <div class="mini">
        <div class="mini-value">{len(text_input.split())}</div>
        <div class="mini-label">Words analyzed</div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown(
            '<div class="section-title" style="margin-top:1.1rem">🚩 Warning <span>Signs</span></div>',
            unsafe_allow_html=True,
        )

        if flags:
            for flag in flags:
                st.markdown(
                    f"<div class='warn'>⚠️ {flag}</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<div class="safe">✅ No major warning signal detected by the rule-based checks.</div>',
                unsafe_allow_html=True,
            )

    with col2:
        st.markdown(
            '<div class="section-title" style="margin-top:1.1rem">🛡️ Recommended <span>Action</span></div>',
            unsafe_allow_html=True,
        )

        if suspicious:
            action = (
                "Do not pay registration, verification or security fees. "
                "Verify the employer through its official website and "
                "avoid sharing sensitive documents or OTPs until the "
                "vacancy is independently confirmed."
            )
            action_class = "warn"

        else:
            action = (
                "Verify the employer website, company email domain, "
                "interview process and role details before sharing "
                "sensitive information or accepting the offer."
            )
            action_class = "safe"

        st.markdown(
            f'<div class="{action_class}">{action}</div>',
            unsafe_allow_html=True,
        )

    # --------------------------------------------------
    # FIXED CHECKLIST
    # Real Streamlit checkboxes with persistent analysis.
    # --------------------------------------------------
        # AUTOMATED VERIFICATION SUMMARY
    st.markdown(
        '<div class="section-title" style="margin-top:1.1rem">'
        '✅ Quick <span>Verification Summary</span></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-text">'
        'The following checks are based on the text you entered.'
        '</div>',
        unsafe_allow_html=True,
    )

    import re

    post_text = text_input
    post_lower = post_text.lower()

    # Check for website mention or URL
    website_found = bool(
        re.search(
            r"https?://\S+|www\.\S+|"
            r"\b[\w-]+\.(com|in|org|net|co|io)\b|"
            r"official website|careers page",
            post_text,
            re.IGNORECASE,
        )
    )

    # Check for recruiter email
    email_match = re.search(
        r"\b[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}\b",
        post_text,
    )

    # Check whether hiring steps are mentioned
    interview_found = bool(
        re.search(
            r"\b(interview|assessment|shortlist|"
            r"selection process|screening round)\b",
            post_lower,
        )
    )

    # Check for payment requests
    fee_found = bool(
        re.search(
            r"registration fee|processing fee|application fee|"
            r"security deposit|verification fee|training fee|"
            r"refundable deposit|pay.{0,30}fee|"
            r"deposit.{0,30}(job|joining|work)",
            post_lower,
        )
    )

    # Check for sensitive information requests
    data_found = bool(
        re.search(
            r"aadhaar|aadhar|pan card|bank details|"
            r"bank account|otp|one-time password",
            post_lower,
        )
    )

    checks = [
        (
            "🏢 Company Website",
            "Website reference found in the posting"
            if website_found
            else "No website reference found in the posting",
            website_found,
            False,
        ),
        (
            "📧 Recruiter Email",
            f"Email found: {email_match.group(0)}"
            if email_match
            else "No recruiter email found in the posting",
            bool(email_match),
            False,
        ),
        (
            "🗣️ Interview Process",
            "Interview or assessment mentioned"
            if interview_found
            else "No interview process mentioned",
            interview_found,
            False,
        ),
        (
            "💳 Payment Request",
            "Potential payment warning detected"
            if fee_found
            else "No payment request detected in the text",
            not fee_found,
            fee_found,
        ),
        (
            "🔐 Sensitive Information",
            "Sensitive information terms detected"
            if data_found
            else "No sensitive-information request detected",
            not data_found,
            data_found,
        ),
    ]

    for title, detail, positive, warning in checks:
        if warning:
            css_class = "warn"
            icon = "⚠️"
        elif positive:
            css_class = "safe"
            icon = "✓"
        else:
            css_class = "check"
            icon = "ℹ️"

        st.markdown(
            f"""
            <div class="{css_class}">
                <strong>{icon} {title}</strong><br>
                {detail}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="warn">
            <strong>🔎 Independent verification still required</strong><br>
            These checks analyze the text only. Visit the company's
            official website and verify the recruiter independently
            before sharing money or sensitive information.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------
    # TECHNICAL DETAILS
    # --------------------------------------------------
    with st.expander("🔬 View technical screening details"):
        st.write(f"**ML suspicious probability:** {ml_risk:.2%}")
        st.write(f"**Rule-based signal score:** {rule_risk:.2%}")
        st.write(f"**Combined prototype risk score:** {risk:.2%}")

        st.write(
            "The final score combines the text classifier with "
            "simple warning-signal rules. It is a screening aid, "
            "not proof that a posting is fraudulent or genuine."
        )

    # --------------------------------------------------
    # DOWNLOAD REPORT
    # --------------------------------------------------
    report_lines = [
        "AI JOB SCAM DETECTION & VERIFICATION AGENT",
        "=" * 45,
        "",
        f"Result: {result['label']}",
        f"Risk score: {risk:.1%}",
        f"Words analyzed: {len(text_input.split())}",
        "",
        "WARNING SIGNS",
        "-" * 20,
    ]

    if flags:
        report_lines.extend(f"- {flag}" for flag in flags)
    else:
        report_lines.append(
            "- No major rule-based warning sign detected."
        )

    report_lines.extend(
        [
            "",
            "RECOMMENDED ACTION",
            "-" * 20,
            action,
            "",
            "DISCLAIMER",
            (
                "This prototype is a screening aid. A likely genuine "
                "result does not prove an employer is legitimate. "
                "Verify job offers independently."
            ),
        ]
    )

    report_text = "\n".join(report_lines)

    st.download_button(
        "⬇️ Download Analysis Report",
        data=report_text,
        file_name="job_scam_analysis_report.txt",
        mime="text/plain",
        use_container_width=True,
    )

# --------------------------------------------------
# RECENT SCAN HISTORY
# --------------------------------------------------
st.markdown(
    '<div class="section-title">🕘 Recent <span>Scan History</span></div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-text">'
    'Your latest analyzed job postings in this session.'
    '</div>',
    unsafe_allow_html=True,
)

if st.session_state.scan_history:
    for index, item in enumerate(st.session_state.scan_history):
        with st.expander(
            f"{item['result']} · {item['time']}",
            expanded=False,
        ):
            st.write(f"**Risk result:** {item['score']}")
            st.write(f"**Warning signals:** {item['warnings']}")
            st.caption("Analyzed posting:")
            st.text(item["posting"])

    if st.button("🗑️ Clear Scan History"):
        st.session_state.scan_history = []
        st.rerun()
else:
    st.info("No scans yet. Analyze a job posting to start your history.")

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown(
    """
<div class="footer">
    AI Job Scam Detection & Verification Agent
    • Python • Streamlit • TF-IDF • Logistic Regression
</div>
""",
    unsafe_allow_html=True,
)