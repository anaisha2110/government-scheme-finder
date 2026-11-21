import html
import sqlite3
from urllib.parse import urlparse
from io import BytesIO

import pandas as pd
import streamlit as st

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet


def create_eligibility_pdf(
    name,
    age,
    gender,
    education,
    state,
    occupation,
    category,
    disability,
    income,
    eligible_schemes,
):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(
        Paragraph(
            "Government Scheme Finder",
            styles["Title"],
        )
    )
    story.append(
        Paragraph(
            "Personal Eligibility Report",
            styles["Heading2"],
        )
    )
    story.append(Spacer(1, 12))

    profile = [
        ["Applicant Detail", "Information"],
        ["Name", str(name)],
        ["Age", str(age)],
        ["Gender", str(gender)],
        ["Education", str(education)],
        ["State", str(state)],
        ["Occupation", str(occupation)],
        ["Social Category", str(category)],
        ["Disability", str(disability)],
        ["Annual Family Income", f"Rs. {income:,.0f}"],
    ]

    profile_table = Table(
        profile,
        colWidths=[6 * cm, 10 * cm],
    )

    profile_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#174A7E"),
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white,
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey,
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                7,
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP",
            ),
        ])
    )

    story.append(profile_table)
    story.append(Spacer(1, 18))

    story.append(
        Paragraph(
            f"Matching schemes found: {len(eligible_schemes)}",
            styles["Heading2"],
        )
    )
    story.append(Spacer(1, 8))

    for number, scheme in enumerate(
        eligible_schemes,
        start=1,
    ):
        scheme_name = html.escape(
            str(scheme.get("name") or "Unnamed Scheme")
        )

        story.append(
            Paragraph(
                f"{number}. {scheme_name}",
                styles["Heading3"],
            )
        )

        description = (
            scheme.get("description")
            or "No description available."
        )

        story.append(
            Paragraph(
                "<b>Description:</b> "
                + html.escape(str(description)),
                styles["BodyText"],
            )
        )

        min_age = scheme.get("min_age")
        max_age = scheme.get("max_age")

        age_text = (
            f"{min_age if min_age is not None else 'Not specified'}"
            f" to "
            f"{max_age if max_age is not None else 'Not specified'} years"
        )

        details = [
            f"<b>Age:</b> {html.escape(age_text)}",
            (
                "<b>Gender:</b> "
                + html.escape(
                    str(scheme.get("gender") or "Not specified")
                )
            ),
            (
                "<b>State:</b> "
                + html.escape(
                    str(scheme.get("state") or "Not specified")
                )
            ),
            (
                "<b>Education:</b> "
                + html.escape(
                    str(scheme.get("education") or "Not specified")
                )
            ),
            (
                "<b>Occupation:</b> "
                + html.escape(
                    str(scheme.get("occupation") or "Not specified")
                )
            ),
            (
                "<b>Social category:</b> "
                + html.escape(
                    str(scheme.get("category") or "Not specified")
                )
            ),
            (
                "<b>Disability:</b> "
                + html.escape(
                    str(scheme.get("disability") or "Not specified")
                )
            ),
        ]

        for detail in details:
            story.append(
                Paragraph(
                    detail,
                    styles["BodyText"],
                )
            )

        application_link = scheme.get("application_link")

        if application_link:
            story.append(
                Paragraph(
                    "<b>Application link:</b> "
                    + html.escape(str(application_link)),
                    styles["BodyText"],
                )
            )

        story.append(Spacer(1, 12))

    if not eligible_schemes:
        story.append(
            Paragraph(
                "No matching schemes were found for the "
                "information provided.",
                styles["BodyText"],
            )
        )

    story.append(Spacer(1, 16))

    story.append(
        Paragraph(
            "Disclaimer: This report is an initial eligibility "
            "check only. Eligibility is determined by the relevant "
            "government authority. Verify scheme details and "
            "requirements through official sources before applying.",
            styles["Italic"],
        )
    )

    doc.build(story)
    buffer.seek(0)

    return buffer.getvalue()


# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="Government Scheme Finder",
    page_icon="🏛️",
    layout="wide",
)

DB_NAME = "schemes.db"
ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]


STATES = [
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal",
    "Delhi",
    "Jammu and Kashmir",
    "Ladakh",
    "Puducherry",
    "Chandigarh",
    "Andaman and Nicobar Islands",
    "Dadra and Nagar Haveli and Daman and Diu",
    "Lakshadweep",
]

EDUCATION = [
    "School",
    "High School (10th)",
    "Senior Secondary (12th)",
    "Diploma",
    "Undergraduate",
    "Postgraduate",
    "Doctorate",
    "Other",
]

OCCUPATION = [
    "Student",
    "Farmer",
    "Government Employee",
    "Private Employee",
    "Business Owner",
    "Self-Employed",
    "Homemaker",
    "Retired",
    "Unemployed",
    "Other",
]

GENDERS = [
    "Male",
    "Female",
    "Other",
]

CATEGORIES = [
    "General",
    "OBC",
    "SC",
    "ST",
    "EWS",
]

DISABILITY = [
    "Yes",
    "No",
]

SCHEME_COLUMNS = [
    "id",
    "scheme_name",
    "min_age",
    "max_age",
    "gender",
    "max_income",
    "state",
    "education",
    "occupation",
    "category",
    "disability",
    "description",
    "benefits",
    "required_documents",
    "application_link",
    "official_source",
    "last_verified",
]

CSV_COLUMNS = [
    "scheme_name",
    "min_age",
    "max_age",
    "gender",
    "max_income",
    "state",
    "education",
    "occupation",
    "description",
    "benefits",
    "required_documents",
    "application_link",
    "category",
    "disability",
    "official_source",
    "last_verified",
]


# =========================================================
# DATABASE
# Existing schemes.db is preserved.
# New columns are added without deleting existing schemes.
# =========================================================

def get_connection():
    return sqlite3.connect(DB_NAME)


def setup_database():
    with get_connection() as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS schemes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scheme_name TEXT NOT NULL,
                min_age INTEGER,
                max_age INTEGER,
                gender TEXT DEFAULT 'Any',
                max_income INTEGER,
                state TEXT DEFAULT 'Any',
                education TEXT DEFAULT 'Any',
                occupation TEXT DEFAULT 'Any',
                description TEXT,
                category TEXT DEFAULT 'Any',
                disability TEXT DEFAULT 'Any',
                application_link TEXT,
                benefits TEXT,
                required_documents TEXT,
                official_source TEXT,
                last_verified TEXT
            )
            """
        )

        existing = {
            row[1]
            for row in con.execute(
                "PRAGMA table_info(schemes)"
            )
        }

        additions = {
            "scheme_name": "TEXT",
            "min_age": "INTEGER",
            "max_age": "INTEGER",
            "gender": "TEXT DEFAULT 'Any'",
            "max_income": "INTEGER",
            "state": "TEXT DEFAULT 'Any'",
            "education": "TEXT DEFAULT 'Any'",
            "occupation": "TEXT DEFAULT 'Any'",
            "description": "TEXT",
            "category": "TEXT DEFAULT 'Any'",
            "disability": "TEXT DEFAULT 'Any'",
            "application_link": "TEXT",
            "benefits": "TEXT",
            "required_documents": "TEXT",
            "official_source": "TEXT",
            "last_verified": "TEXT",
        }

        for column, sql_type in additions.items():
            if column not in existing:
                con.execute(
                    f"ALTER TABLE schemes ADD COLUMN "
                    f"{column} {sql_type}"
                )

        con.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL
            )
            """
        )


setup_database()


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def fetch_schemes():
    with get_connection() as con:
        return pd.read_sql_query(
            """
            SELECT *
            FROM schemes
            ORDER BY scheme_name COLLATE NOCASE
            """,
            con,
        )


def clean_text(value, default=""):
    if value is None or pd.isna(value):
        return default

    text = str(value).strip()

    return text if text else default


def norm(value):
    return clean_text(value, "Any").casefold()


def valid_web_url(value):
    value = clean_text(value)
    parsed = urlparse(value)

    return (
        parsed.scheme in ("http", "https")
        and bool(parsed.netloc)
    )


def show_link(label, value):
    value = clean_text(value)

    if valid_web_url(value):
        st.link_button(
            label,
            value,
        )

        # =========================================================
# ELIGIBILITY CHECKING
# =========================================================

def is_eligible(row, profile):
    """
    Return True if a scheme matches the applicant's details.
    Missing or unspecified scheme criteria are treated as Any.
    """

    def get_value(field, default="Any"):
        value = row.get(field, default)

        if value is None or pd.isna(value):
            return default

        return str(value).strip() or default

    def matches_option(scheme_value, applicant_value):
        scheme_value = norm(scheme_value)
        applicant_value = norm(applicant_value)

        any_values = {
            "",
            "any",
            "all",
            "not specified",
            "not applicable",
            "n/a",
        }

        return (
            scheme_value in any_values
            or scheme_value == applicant_value
        )

    try:
        age = int(profile["age"])
        income = float(profile["income"])
    except (TypeError, ValueError, KeyError):
        return False

    min_age = row.get("min_age")
    max_age = row.get("max_age")
    max_income = row.get("max_income")

    if min_age is not None and not pd.isna(min_age):
        if age < float(min_age):
            return False

    if max_age is not None and not pd.isna(max_age):
        if age > float(max_age):
            return False

    if max_income is not None and not pd.isna(max_income):
        if income > float(max_income):
            return False

    fields_to_match = [
        "gender",
        "education",
        "state",
        "occupation",
        "category",
        "disability",
    ]

    for field in fields_to_match:
        scheme_value = get_value(field)
        applicant_value = profile.get(field, "Any")

        if not matches_option(
            scheme_value,
            applicant_value,
        ):
            return False

    return True


# =========================================================
# SCHEME DETAIL DISPLAY
# =========================================================

def render_scheme_detail(row):
    st.markdown("#### Scheme information")

    description = clean_text(
        row.get("description"),
        "No description has been added yet.",
    )
    st.write(description)

    benefits = clean_text(
        row.get("benefits"),
        "Benefits information has not been added yet.",
    )
    st.markdown("**Benefits**")
    st.write(benefits)

    documents = clean_text(
        row.get("required_documents"),
        "Required documents have not been added yet.",
    )
    st.markdown("**Required documents**")
    st.write(documents)

    st.markdown("**Eligibility criteria**")

    min_age = row.get("min_age")
    max_age = row.get("max_age")
    max_income = row.get("max_income")

    min_age_text = (
        "Not specified"
        if min_age is None or pd.isna(min_age)
        else str(int(min_age))
    )

    max_age_text = (
        "Not specified"
        if max_age is None or pd.isna(max_age)
        else str(int(max_age))
    )

    max_income_text = (
        "Not specified"
        if max_income is None or pd.isna(max_income)
        else f"₹{float(max_income):,.0f}"
    )

    criteria = {
        "Minimum age": min_age_text,
        "Maximum age": max_age_text,
        "Maximum annual family income": max_income_text,
        "Gender": clean_text(row.get("gender"), "Any"),
        "State": clean_text(row.get("state"), "Any"),
        "Education": clean_text(row.get("education"), "Any"),
        "Occupation": clean_text(row.get("occupation"), "Any"),
        "Social category": clean_text(row.get("category"), "Any"),
        "Disability criterion": clean_text(
            row.get("disability"),
            "Any",
        ),
    }

    for label, value in criteria.items():
        st.write(f"**{label}:** {value}")

    application_link = clean_text(
        row.get("application_link")
    )

    if valid_web_url(application_link):
        st.link_button(
            "🌐 Visit application website",
            application_link,
        )
    elif application_link:
        st.caption(
            "Application information: "
            + application_link
        )

    official_source = clean_text(
        row.get("official_source")
    )

    if valid_web_url(official_source):
        st.link_button(
            "🔗 Visit official source",
            official_source,
        )
    elif official_source:
        st.write(f"**Official source:** {official_source}")

    last_verified = clean_text(
        row.get("last_verified")
    )

    if last_verified:
        st.caption(f"Last verified: {last_verified}")

    st.caption(
        "Please confirm the latest eligibility criteria and "
        "application requirements with the official authority."
    )


# =========================================================
# SAVE A SCHEME
# =========================================================

def save_scheme(scheme_data, scheme_id=None):
    """
    Insert a new scheme or update an existing scheme.
    Existing database records are not deleted.
    """

    fields = [
        "scheme_name",
        "min_age",
        "max_age",
        "gender",
        "max_income",
        "state",
        "education",
        "occupation",
        "description",
        "category",
        "disability",
        "application_link",
        "benefits",
        "required_documents",
        "official_source",
        "last_verified",
    ]

    values = [
        scheme_data.get(field)
        for field in fields
    ]

    with get_connection() as con:
        if scheme_id is None:
            placeholders = ", ".join(
                ["?"] * len(fields)
            )

            columns = ", ".join(fields)

            con.execute(
                f"""
                INSERT INTO schemes ({columns})
                VALUES ({placeholders})
                """,
                values,
            )
        else:
            assignments = ", ".join(
                f"{field} = ?"
                for field in fields
            )

            con.execute(
                f"""
                UPDATE schemes
                SET {assignments}
                WHERE id = ?
                """,
                values + [scheme_id],
            )

            # =========================================================
# LOAD SCHEMES
# =========================================================

all_schemes = fetch_schemes()


# =========================================================
# SESSION STATE
# =========================================================

if "page" not in st.session_state:
    st.session_state.page = "🏠 Home"

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

st.sidebar.title("🏛️ Scheme Finder")

st.sidebar.write(
    "Find government schemes that may suit your needs."
)

page_options = [
    "🏠 Home",
    "ℹ️ About",
    "📩 Contact / Feedback",
    "🔐 Admin",
]

page = st.sidebar.radio(
    "Navigation",
    page_options,
    key="page",
)

st.sidebar.divider()

st.sidebar.caption(
    "Information is provided for guidance. "
    "Always verify scheme requirements with official sources."
)


# =========================================================
# HOME PAGE
# =========================================================

if page == "🏠 Home":

    st.title("🏛️ Government Scheme Finder")

    st.write(
        "Discover government schemes based on your profile, "
        "or browse the schemes available in the database."
    )

    mode = st.radio(
        "What would you like to do?",
        [
            "✅ Check Eligibility",
            "🔎 Browse Schemes",
        ],
        horizontal=True,
    )

    if all_schemes.empty:

        st.warning(
            "No schemes are currently stored in the database. "
            "An administrator can add schemes from the Admin page."
        )

    elif mode == "🔎 Browse Schemes":

        st.subheader("Browse Government Schemes")

        search_text = st.text_input(
            "Search by scheme name or description",
            placeholder="Enter a scheme name or keyword",
        )

        state_filter = st.selectbox(
            "Filter by state",
            ["All States"] + STATES,
        )

        filtered = all_schemes.copy()

        if search_text.strip():

            search_mask = (
                filtered["scheme_name"]
                .fillna("")
                .astype(str)
                .str.contains(
                    search_text.strip(),
                    case=False,
                    regex=False,
                )
            )

            if "description" in filtered.columns:

                description_mask = (
                    filtered["description"]
                    .fillna("")
                    .astype(str)
                    .str.contains(
                        search_text.strip(),
                        case=False,
                        regex=False,
                    )
                )

                search_mask = (
                    search_mask | description_mask
                )

            filtered = filtered[search_mask]

        if state_filter != "All States":

            filtered = filtered[
                filtered["state"]
                .fillna("Any")
                .astype(str)
                .str.casefold()
                .isin(
                    [
                        "any",
                        "all",
                        state_filter.casefold(),
                    ]
                )
            ]

        st.write(
            f"**{len(filtered)} scheme(s) found**"
        )

        if filtered.empty:

            st.info(
                "No schemes matched your search. "
                "Try another keyword or state."
            )

        else:

            for _, row in filtered.iterrows():

                scheme_name = clean_text(
                    row.get("scheme_name"),
                    "Unnamed scheme",
                )

                with st.container(border=True):

                    st.subheader(scheme_name)

                    st.write(
                        clean_text(
                            row.get("description"),
                            "No description has been added yet.",
                        )
                    )

                    with st.expander(
                        "📄 View scheme details"
                    ):
                        render_scheme_detail(row)

    else:

        # ================================================
        # CHECK ELIGIBILITY
        # ================================================

        st.subheader("Check Eligibility")

        st.info(
            "Enter your details to find schemes that may match "
            "your profile. This is an initial check, not an "
            "official eligibility decision."
        )

        with st.form("eligibility_form"):

            col1, col2 = st.columns(2)

            with col1:

                name = st.text_input("Full name")

                age = st.number_input(
                    "Age",
                    min_value=0,
                    max_value=120,
                    value=18,
                    step=1,
                )

                gender = st.selectbox(
                    "Gender",
                    GENDERS,
                )

                education = st.selectbox(
                    "Highest education",
                    EDUCATION,
                )

                state = st.selectbox(
                    "State / Union Territory",
                    STATES,
                )

            with col2:

                occupation = st.selectbox(
                    "Occupation",
                    OCCUPATION,
                )

                category = st.selectbox(
                    "Social category",
                    CATEGORIES,
                )

                disability = st.selectbox(
                    "Disability",
                    DISABILITY,
                )

                income = st.number_input(
                    "Annual family income (₹)",
                    min_value=0,
                    value=0,
                    step=1000,
                )

            submitted = st.form_submit_button(
                "🔎 Find eligible schemes",
                use_container_width=True,
            )

        if submitted:

            if not name.strip():

                st.error("Please enter your name.")

            else:

                profile = {
                    "age": age,
                    "income": income,
                    "gender": gender,
                    "education": education,
                    "state": state,
                    "occupation": occupation,
                    "category": category,
                    "disability": disability,
                }

                eligible = all_schemes[
                    all_schemes.apply(
                        lambda row: is_eligible(
                            row,
                            profile,
                        ),
                        axis=1,
                    )
                ]

                st.subheader(
                    f"{len(eligible)} possible match(es)"
                )

                if eligible.empty:

                    st.warning(
                        "No schemes matched all the criteria "
                        "stored in the database. You can try "
                        "Browse Schemes or verify the scheme "
                        "eligibility data."
                    )

                else:

                    for _, row in eligible.iterrows():

                        with st.container(border=True):

                            st.markdown(
                                "### "
                                + clean_text(
                                    row.get("scheme_name"),
                                    "Unnamed scheme",
                                )
                            )

                            st.write(
                                clean_text(
                                    row.get("description"),
                                    "No description has been added yet.",
                                )
                            )

                            with st.expander(
                                "📄 View full scheme details"
                            ):
                                render_scheme_detail(row)

                    # ------------------------------------
                    # Prepare matching schemes for the PDF
                    # ------------------------------------

                    pdf_schemes = []

                    for _, row in eligible.iterrows():

                        pdf_schemes.append({
                            "name": clean_text(
                                row.get("scheme_name"),
                                "Unnamed scheme",
                            ),
                            "description": clean_text(
                                row.get("description"),
                                "No description available.",
                            ),
                            "min_age": (
                                None
                                if pd.isna(row.get("min_age"))
                                else row.get("min_age")
                            ),
                            "max_age": (
                                None
                                if pd.isna(row.get("max_age"))
                                else row.get("max_age")
                            ),
                            "gender": clean_text(
                                row.get("gender"),
                                "Any",
                            ),
                            "state": clean_text(
                                row.get("state"),
                                "Any",
                            ),
                            "education": clean_text(
                                row.get("education"),
                                "Any",
                            ),
                            "occupation": clean_text(
                                row.get("occupation"),
                                "Any",
                            ),
                            "category": clean_text(
                                row.get("category"),
                                "Any",
                            ),
                            "disability": clean_text(
                                row.get("disability"),
                                "Any",
                            ),
                            "application_link": clean_text(
                                row.get("application_link"),
                                "",
                            ),
                        })

                    # ------------------------------------
                    # Generate and download the PDF
                    # ------------------------------------

                    try:

                        pdf_bytes = create_eligibility_pdf(
                            name,
                            age,
                            gender,
                            education,
                            state,
                            occupation,
                            category,
                            disability,
                            income,
                            pdf_schemes,
                        )

                        st.download_button(
                            label=(
                                "📥 Download Eligibility "
                                "Report (PDF)"
                            ),
                            data=pdf_bytes,
                            file_name="eligibility_report.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )

                    except Exception as error:

                        st.error(
                            "The eligibility report could not "
                            "be generated. Please check the "
                            "ReportLab installation and the "
                            "PDF function."
                        )

                        st.caption(str(error))

                        # =========================================================
# ABOUT PAGE
# =========================================================

elif page == "ℹ️ About":

    st.title("ℹ️ About Government Scheme Finder")

    st.write(
        """
        Government Scheme Finder helps people explore government
        schemes that may be relevant to their circumstances.
        """
    )

    st.subheader("Our purpose")

    st.write(
        """
        Government schemes can provide support for education,
        agriculture, employment, women, entrepreneurs, and
        other groups. Finding the relevant information can
        sometimes be difficult.

        This application helps users search the schemes stored
        in its database and perform an initial eligibility check.
        """
    )

    st.subheader("How it works")

    st.markdown(
        """
        1. Enter your profile details on the Home page.
        2. Review the schemes that match the stored criteria.
        3. Open a scheme to view its available details.
        4. Follow the official application link, where available.
        5. Verify all requirements before applying.
        """
    )

    st.subheader("Important disclaimer")

    st.warning(
        """
        This application is an informational tool, not a
        government authority. A matching result does not
        guarantee approval or eligibility. Scheme information
        may be incomplete or outdated, so always check the
        official government website.
        """
    )

    st.subheader("Data and privacy")

    st.write(
        """
        Avoid entering unnecessary sensitive personal
        information. Before deploying this application publicly,
        review its data storage, access controls, and privacy
        practices.
        """
    )


# =========================================================
# CONTACT / FEEDBACK PAGE
# =========================================================

elif page == "📩 Contact / Feedback":

    st.title("📩 Contact / Feedback")

    st.write(
        "Share a suggestion, report an issue, or tell us "
        "how the application could be improved."
    )

    with st.form("feedback_form"):

        feedback_name = st.text_input(
            "Your name"
        )

        feedback_email = st.text_input(
            "Email address"
        )

        feedback_message = st.text_area(
            "Your feedback",
            height=150,
        )

        feedback_submitted = st.form_submit_button(
            "Submit feedback",
            use_container_width=True,
        )

    if feedback_submitted:

        if not feedback_name.strip():
            st.error("Please enter your name.")

        elif not feedback_email.strip():
            st.error("Please enter your email address.")

        elif (
            "@" not in feedback_email
            or "." not in feedback_email.split("@")[-1]
        ):
            st.error(
                "Please enter a valid email address."
            )

        elif not feedback_message.strip():
            st.error("Please enter your feedback.")

        else:

            try:

                with get_connection() as con:

                    con.execute(
                        """
                        INSERT INTO feedback
                        (name, email, message)
                        VALUES (?, ?, ?)
                        """,
                        (
                            feedback_name.strip(),
                            feedback_email.strip(),
                            feedback_message.strip(),
                        ),
                    )

                st.success(
                    "Thank you! Your feedback has been saved."
                )

            except sqlite3.Error as error:

                st.error(
                    "Your feedback could not be saved."
                )

                st.caption(str(error))

                # =========================================================
# ADMIN LOGIN AND DASHBOARD
# =========================================================

elif page == "🔐 Admin":

    st.title("🔐 Admin Dashboard")

    if not st.session_state.admin_logged_in:

        st.write(
            "Log in to manage government scheme records."
        )

        with st.form("admin_login_form"):

            password = st.text_input(
                "Admin password",
                type="password",
            )

            login_submitted = st.form_submit_button(
                "Log in",
                use_container_width=True,
            )

        if login_submitted:

            if password == ADMIN_PASSWORD:

                st.session_state.admin_logged_in = True

                st.success("Login successful.")

                st.rerun()

            else:

                st.error("Incorrect password.")

    else:

        st.success("You are logged in as an administrator.")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Total schemes",
                len(fetch_schemes()),
            )

        with col2:

            with get_connection() as con:

                feedback_count = con.execute(
                    "SELECT COUNT(*) FROM feedback"
                ).fetchone()[0]

            st.metric(
                "Feedback submissions",
                feedback_count,
            )

        with col3:

            current_data = fetch_schemes()

            if (
                "last_verified" in current_data.columns
                and not current_data.empty
            ):
                verified_count = int(
                    current_data["last_verified"]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                    .ne("")
                    .sum()
                )
            else:
                verified_count = 0

            st.metric(
                "Records with verification dates",
                verified_count,
            )

        st.divider()

        st.subheader("Manage schemes")

        st.write(
            "Use the options below to add, edit, delete, "
            "or import scheme records."
        )

        if st.button(
            "➕ Add a new scheme",
            use_container_width=True,
        ):
            st.session_state.admin_action = "add"
            st.rerun()

        if st.button(
            "✏️ Edit an existing scheme",
            use_container_width=True,
        ):
            st.session_state.admin_action = "edit"
            st.rerun()

        if st.button(
            "🗑️ Delete a scheme",
            use_container_width=True,
        ):
            st.session_state.admin_action = "delete"
            st.rerun()

        st.divider()

        st.subheader("Current scheme records")

        admin_schemes = fetch_schemes()

        if admin_schemes.empty:

            st.info("No schemes are currently stored.")

        else:

            display_columns = [
                column
                for column in [
                    "id",
                    "scheme_name",
                    "state",
                    "min_age",
                    "max_age",
                    "max_income",
                    "last_verified",
                ]
                if column in admin_schemes.columns
            ]

            st.dataframe(
                admin_schemes[display_columns],
                use_container_width=True,
                hide_index=True,
            )

        st.divider()

        if st.button(
            "🚪 Log out",
            use_container_width=True,
        ):

            st.session_state.admin_logged_in = False

            if "admin_action" in st.session_state:
                del st.session_state.admin_action

            st.rerun()

            # =========================================================
# ADMIN ACTIONS: ADD, EDIT, DELETE
# =========================================================

if (
    page == "🔐 Admin"
    and st.session_state.admin_logged_in
    and st.session_state.get("admin_action")
):
    action = st.session_state.admin_action

    st.divider()

    if action == "add":
        st.subheader("➕ Add a Scheme")

        with st.form("add_scheme_form"):
            scheme_name = st.text_input("Scheme name")
            min_age = st.number_input(
                "Minimum age", min_value=0, max_value=120, value=0
            )
            max_age = st.number_input(
                "Maximum age", min_value=0, max_value=120, value=120
            )
            gender = st.selectbox("Eligible gender", ["Any"] + GENDERS)
            max_income = st.number_input(
                "Maximum annual family income (₹)",
                min_value=0,
                value=0,
                step=1000,
            )
            state = st.selectbox("Applicable state", ["Any"] + STATES)
            education = st.selectbox(
                "Education requirement", ["Any"] + EDUCATION
            )
            occupation = st.selectbox(
                "Occupation", ["Any"] + OCCUPATION
            )
            category = st.selectbox(
                "Social category", ["Any"] + CATEGORIES
            )
            disability = st.selectbox(
                "Disability criterion", ["Any"] + DISABILITY
            )
            description = st.text_area("Description")
            benefits = st.text_area("Benefits")
            required_documents = st.text_area("Required documents")
            application_link = st.text_input("Application URL")
            official_source = st.text_input("Official source URL")
            last_verified = st.text_input(
                "Last verified date (e.g. 2026-10-11)"
            )

            add_submitted = st.form_submit_button(
                "Save scheme",
                use_container_width=True,
            )

        if add_submitted:
            if not scheme_name.strip():
                st.error("Please enter a scheme name.")
            elif max_age < min_age:
                st.error(
                    "Maximum age cannot be lower than minimum age."
                )
            elif application_link.strip() and not valid_web_url(
                application_link
            ):
                st.error(
                    "The application URL must start with http:// or https://."
                )
            elif official_source.strip() and not valid_web_url(
                official_source
            ):
                st.error(
                    "The official source URL must start with http:// or https://."
                )
            else:
                save_scheme({
                    "scheme_name": scheme_name.strip(),
                    "min_age": int(min_age),
                    "max_age": int(max_age),
                    "gender": gender,
                    "max_income": int(max_income),
                    "state": state,
                    "education": education,
                    "occupation": occupation,
                    "description": description.strip(),
                    "category": category,
                    "disability": disability,
                    "application_link": application_link.strip(),
                    "benefits": benefits.strip(),
                    "required_documents": required_documents.strip(),
                    "official_source": official_source.strip(),
                    "last_verified": last_verified.strip(),
                })
                st.success("Scheme added successfully.")
                st.session_state.admin_action = ""
                st.rerun()

    elif action == "edit":
        st.subheader("✏️ Edit a Scheme")

        edit_data = fetch_schemes()

        if edit_data.empty:
            st.info("There are no schemes to edit.")
        else:
            scheme_options = {
                f"{int(row['id'])} — {row['scheme_name']}": int(row["id"])
                for _, row in edit_data.iterrows()
            }

            selected_label = st.selectbox(
                "Choose a scheme",
                list(scheme_options.keys()),
            )
            selected_id = scheme_options[selected_label]
            selected_rows = edit_data[
                edit_data["id"] == selected_id
            ]
            selected = selected_rows.iloc[0]

            def existing_value(field, default=""):
                value = selected.get(field, default)
                if value is None or pd.isna(value):
                    return default
                return value

            with st.form("edit_scheme_form"):
                edit_name = st.text_input(
                    "Scheme name",
                    value=str(existing_value("scheme_name")),
                )
                edit_min_age = st.number_input(
                    "Minimum age",
                    min_value=0,
                    max_value=120,
                    value=int(existing_value("min_age", 0) or 0),
                )
                edit_max_age = st.number_input(
                    "Maximum age",
                    min_value=0,
                    max_value=120,
                    value=int(existing_value("max_age", 120) or 120),
                )
                edit_gender = st.selectbox(
                    "Eligible gender",
                    ["Any"] + GENDERS,
                    index=(
                        ["Any"] + GENDERS
                    ).index(
                        str(existing_value("gender", "Any"))
                        if str(existing_value("gender", "Any"))
                        in ["Any"] + GENDERS
                        else "Any"
                    ),
                )
                edit_income = st.number_input(
                    "Maximum annual family income (₹)",
                    min_value=0,
                    value=int(existing_value("max_income", 0) or 0),
                    step=1000,
                )
                edit_state_options = ["Any"] + STATES
                old_state = str(existing_value("state", "Any"))
                edit_state = st.selectbox(
                    "Applicable state",
                    edit_state_options,
                    index=(
                        edit_state_options.index(old_state)
                        if old_state in edit_state_options
                        else 0
                    ),
                )
                edit_education_options = ["Any"] + EDUCATION
                old_education = str(
                    existing_value("education", "Any")
                )
                edit_education = st.selectbox(
                    "Education requirement",
                    edit_education_options,
                    index=(
                        edit_education_options.index(old_education)
                        if old_education in edit_education_options
                        else 0
                    ),
                )
                edit_occupation_options = ["Any"] + OCCUPATION
                old_occupation = str(
                    existing_value("occupation", "Any")
                )
                edit_occupation = st.selectbox(
                    "Occupation",
                    edit_occupation_options,
                    index=(
                        edit_occupation_options.index(old_occupation)
                        if old_occupation in edit_occupation_options
                        else 0
                    ),
                )
                edit_category_options = ["Any"] + CATEGORIES
                old_category = str(
                    existing_value("category", "Any")
                )
                edit_category = st.selectbox(
                    "Social category",
                    edit_category_options,
                    index=(
                        edit_category_options.index(old_category)
                        if old_category in edit_category_options
                        else 0
                    ),
                )
                edit_disability_options = ["Any"] + DISABILITY
                old_disability = str(
                    existing_value("disability", "Any")
                )
                edit_disability = st.selectbox(
                    "Disability criterion",
                    edit_disability_options,
                    index=(
                        edit_disability_options.index(old_disability)
                        if old_disability in edit_disability_options
                        else 0
                    ),
                )
                edit_description = st.text_area(
                    "Description",
                    value=str(existing_value("description")),
                )
                edit_benefits = st.text_area(
                    "Benefits",
                    value=str(existing_value("benefits")),
                )
                edit_documents = st.text_area(
                    "Required documents",
                    value=str(existing_value("required_documents")),
                )
                edit_link = st.text_input(
                    "Application URL",
                    value=str(existing_value("application_link")),
                )
                edit_source = st.text_input(
                    "Official source URL",
                    value=str(existing_value("official_source")),
                )
                edit_verified = st.text_input(
                    "Last verified date",
                    value=str(existing_value("last_verified")),
                )

                edit_submitted = st.form_submit_button(
                    "Save changes",
                    use_container_width=True,
                )

            if edit_submitted:
                if not edit_name.strip():
                    st.error("Please enter a scheme name.")
                elif edit_max_age < edit_min_age:
                    st.error(
                        "Maximum age cannot be lower than minimum age."
                    )
                elif edit_link.strip() and not valid_web_url(edit_link):
                    st.error(
                        "The application URL must start with http:// or https://."
                    )
                elif edit_source.strip() and not valid_web_url(edit_source):
                    st.error(
                        "The official source URL must start with http:// or https://."
                    )
                else:
                    save_scheme({
                        "scheme_name": edit_name.strip(),
                        "min_age": int(edit_min_age),
                        "max_age": int(edit_max_age),
                        "gender": edit_gender,
                        "max_income": int(edit_income),
                        "state": edit_state,
                        "education": edit_education,
                        "occupation": edit_occupation,
                        "description": edit_description.strip(),
                        "category": edit_category,
                        "disability": edit_disability,
                        "application_link": edit_link.strip(),
                        "benefits": edit_benefits.strip(),
                        "required_documents": edit_documents.strip(),
                        "official_source": edit_source.strip(),
                        "last_verified": edit_verified.strip(),
                    }, scheme_id=selected_id)
                    st.success("Scheme updated successfully.")
                    st.session_state.admin_action = ""
                    st.rerun()

    elif action == "delete":
        st.subheader("🗑️ Delete a Scheme")

        delete_data = fetch_schemes()

        if delete_data.empty:
            st.info("There are no schemes to delete.")
        else:
            delete_options = {
                f"{int(row['id'])} — {row['scheme_name']}": int(row["id"])
                for _, row in delete_data.iterrows()
            }
            delete_label = st.selectbox(
                "Choose a scheme to delete",
                list(delete_options.keys()),
            )
            delete_id = delete_options[delete_label]

            st.warning(
                "Deleting a scheme is permanent. Make sure you selected "
                "the correct record."
            )
            confirm_delete = st.checkbox(
                "I confirm that I want to delete this scheme."
            )

            if st.button("Delete selected scheme", type="primary"):
                if not confirm_delete:
                    st.error("Please confirm before deleting.")
                else:
                    with get_connection() as con:
                        con.execute(
                            "DELETE FROM schemes WHERE id = ?",
                            (delete_id,),
                        )
                    st.success("Scheme deleted.")
                    st.session_state.admin_action = ""
                    st.rerun()

    if st.button("Cancel admin action"):
        st.session_state.admin_action = ""
        st.rerun()

        # =========================================================
# ADMIN: CSV IMPORT AND EXPORT
# =========================================================

if (
    page == "🔐 Admin"
    and st.session_state.admin_logged_in
):

    st.divider()
    st.subheader("📁 Import and Export Schemes")

    st.write(
        "Use CSV files to back up your scheme records or "
        "add multiple schemes in one operation."
    )

    # -----------------------------------------------
    # EXPORT SCHEMES
    # -----------------------------------------------

    export_data = fetch_schemes()

    if not export_data.empty:

        export_columns = [
            column
            for column in CSV_COLUMNS
            if column in export_data.columns
        ]

        export_csv = export_data[
            export_columns
        ].to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            label="📥 Export schemes to CSV",
            data=export_csv,
            file_name="government_schemes.csv",
            mime="text/csv",
            use_container_width=True,
        )

    else:

        st.info(
            "There are no schemes to export yet."
        )

    # -----------------------------------------------
    # IMPORT SCHEMES
    # -----------------------------------------------

    st.markdown("### Import schemes from CSV")

    st.caption(
        "Your CSV should contain a scheme_name column. "
        "Other supported columns include min_age, max_age, "
        "gender, max_income, state, education, occupation, "
        "description, benefits, required_documents, "
        "application_link, category, disability, "
        "official_source and last_verified."
    )

    uploaded_csv = st.file_uploader(
        "Choose a CSV file",
        type=["csv"],
        key="scheme_csv_upload",
    )

    if uploaded_csv is not None:

        try:

            imported_data = pd.read_csv(
                uploaded_csv
            )

            imported_data.columns = (
                imported_data.columns
                .astype(str)
                .str.strip()
            )

            st.write("Preview of uploaded data")

            st.dataframe(
                imported_data.head(10),
                use_container_width=True,
                hide_index=True,
            )

            if "scheme_name" not in imported_data.columns:

                st.error(
                    "The CSV must contain a scheme_name column."
                )

            else:

                st.warning(
                    "Importing creates new records. It does not "
                    "automatically update existing schemes."
                )

                import_confirmed = st.checkbox(
                    "I have checked the CSV preview and want "
                    "to import these schemes.",
                    key="confirm_scheme_import",
                )

                if st.button(
                    "Import schemes",
                    use_container_width=True,
                ):

                    if not import_confirmed:

                        st.error(
                            "Please confirm the import first."
                        )

                    else:

                        allowed_columns = [
                            column
                            for column in CSV_COLUMNS
                            if column in imported_data.columns
                        ]

                        valid_rows = imported_data[
                            imported_data["scheme_name"]
                            .fillna("")
                            .astype(str)
                            .str.strip()
                            .ne("")
                        ]

                        if valid_rows.empty:

                            st.error(
                                "No rows with a valid scheme name "
                                "were found."
                            )

                        else:

                            inserted = 0
                            skipped = 0

                            try:

                                with get_connection() as con:

                                    for _, csv_row in valid_rows.iterrows():

                                        record = {}

                                        for column in allowed_columns:

                                            value = csv_row.get(column)

                                            if (
                                                value is None
                                                or pd.isna(value)
                                            ):
                                                value = None

                                            record[column] = value

                                        name_value = str(
                                            record.get("scheme_name", "")
                                        ).strip()

                                        if not name_value:
                                            skipped += 1
                                            continue

                                        if record.get("min_age") is not None:
                                            record["min_age"] = int(
                                                float(record["min_age"])
                                            )

                                        if record.get("max_age") is not None:
                                            record["max_age"] = int(
                                                float(record["max_age"])
                                            )

                                        if record.get("max_income") is not None:
                                            record["max_income"] = int(
                                                float(record["max_income"])
                                            )

                                        columns = list(record.keys())

                                        placeholders = ", ".join(
                                            ["?"] * len(columns)
                                        )

                                        column_names = ", ".join(
                                            columns
                                        )

                                        con.execute(
                                            f"""
                                            INSERT INTO schemes
                                            ({column_names})
                                            VALUES ({placeholders})
                                            """,
                                            [
                                                record[column]
                                                for column in columns
                                            ],
                                        )

                                        inserted += 1

                                st.success(
                                    f"Imported {inserted} scheme(s). "
                                    f"Skipped {skipped} row(s)."
                                )

                                st.rerun()

                            except (
                                sqlite3.Error,
                                ValueError,
                                TypeError,
                            ) as error:

                                st.error(
                                    "The CSV import failed. Please "
                                    "check the column names and data "
                                    "types before trying again."
                                )

                                st.caption(str(error))

        except (
            pd.errors.ParserError,
            UnicodeDecodeError,
            ValueError,
        ) as error:

            st.error(
                "The uploaded file could not be read as a valid CSV."
            )

            st.caption(str(error))


# =========================================================
# APPLICATION FOOTER
# =========================================================

st.divider()

st.caption(
    "🏛️ Government Scheme Finder | An informational tool "
    "to help users discover potentially relevant government schemes."
)

st.caption(
    "Eligibility results are indicative only. Confirm current "
    "rules, deadlines, benefits and application requirements "
    "with the relevant official government authority."
)




