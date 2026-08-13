import streamlit as st

from tools.escalation_tool import get_open_escalations
from analytics.call_analytics import (
    get_call_metrics,
    get_channel_metrics,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Krishi Mitra - Call Analytics",
    page_icon="🌾",
    layout="wide",
)


# ============================================================
# HEADER
# ============================================================

st.title("🌾 Krishi Mitra — Call Analytics Dashboard")

st.caption(
    "Voice agent performance and human-help escalation monitoring"
)


# ============================================================
# REFRESH
# ============================================================

refresh_col, info_col = st.columns([1, 5])

with refresh_col:

    if st.button("🔄 Refresh"):

        st.rerun()


with info_col:

    st.caption(
        "Call analytics are loaded from the live call analytics database."
    )


# ============================================================
# DAY 8 — CALL ANALYTICS
# ============================================================

st.header("📊 Call Analytics")


try:

    call_metrics = get_call_metrics()

    channel_metrics = get_channel_metrics()

except Exception as e:

    st.error(
        f"Unable to load call analytics: {e}"
    )

    call_metrics = {
        "total_calls": 0,
        "successful_calls": 0,
        "failed_calls": 0,
    }

    channel_metrics = {
        "browser": {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
        },
        "sip": {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
        },
    }


# ============================================================
# OVERALL METRICS
# ============================================================

total_calls = call_metrics["total_calls"]

successful_calls = call_metrics[
    "successful_calls"
]

failed_calls = call_metrics[
    "failed_calls"
]


# ============================================================
# SUCCESS RATE
# ============================================================

if total_calls > 0:

    success_rate = (
        successful_calls / total_calls
    ) * 100

else:

    success_rate = 0


# ============================================================
# REQUIRED DAY 8 METRICS
# ============================================================

st.subheader("All Calls")

col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Total Calls",
        total_calls,
    )


with col2:

    st.metric(
        "Successful Calls",
        successful_calls,
    )


with col3:

    st.metric(
        "Failed Calls",
        failed_calls,
    )


# ============================================================
# SUCCESS RATE
# ============================================================

st.metric(
    "Success Rate",
    f"{success_rate:.1f}%",
)


st.divider()


# ============================================================
# CHANNEL BREAKDOWN
# ============================================================

st.subheader("📡 Calls by Channel")


browser = channel_metrics["browser"]

sip = channel_metrics["sip"]


browser_col, sip_col = st.columns(2)


# ============================================================
# BROWSER CALLS
# ============================================================

with browser_col:

    with st.container(border=True):

        st.markdown(
            "### 🌐 Browser Calls"
        )

        b1, b2, b3 = st.columns(3)


        with b1:

            st.metric(
                "Total",
                browser["total_calls"],
            )


        with b2:

            st.metric(
                "Successful",
                browser["successful_calls"],
            )


        with b3:

            st.metric(
                "Failed",
                browser["failed_calls"],
            )


# ============================================================
# SIP OUTBOUND CALLS
# ============================================================

with sip_col:

    with st.container(border=True):

        st.markdown(
            "### 📞 SIP Outbound Calls"
        )

        s1, s2, s3 = st.columns(3)


        with s1:

            st.metric(
                "Total",
                sip["total_calls"],
            )


        with s2:

            st.metric(
                "Successful",
                sip["successful_calls"],
            )


        with s3:

            st.metric(
                "Failed",
                sip["failed_calls"],
            )


st.divider()


# ============================================================
# HUMAN HELP SECTION
# ============================================================

st.header("🧑‍🌾 Human Help")


# ============================================================
# LOAD REQUESTS
# ============================================================

try:

    requests = get_open_escalations()

except Exception as e:

    st.error(
        f"Unable to load escalation requests: {e}"
    )

    requests = []


# ============================================================
# HUMAN HELP SUMMARY
# ============================================================

total_requests = len(requests)


high_priority = sum(
    1
    for request in requests
    if str(request[7]).upper() == "HIGH"
)


medium_priority = sum(
    1
    for request in requests
    if str(request[7]).upper() == "MEDIUM"
)


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Open Requests",
        total_requests,
    )


with col2:

    st.metric(
        "High Priority",
        high_priority,
    )


with col3:

    st.metric(
        "Medium Priority",
        medium_priority,
    )


st.divider()


# ============================================================
# NO REQUESTS
# ============================================================

if not requests:

    st.success(
        "No open human-help requests."
    )

else:

    # ========================================================
    # REQUEST CARDS
    # ========================================================

    st.subheader(
        "Open Human-Help Requests"
    )


    for request in requests:

        (
            reference_id,
            farmer_name,
            district,
            crop,
            reason,
            what_happened,
            agent_checked,
            urgency,
            language,
            preferred_follow_up,
            status,
            created_at,
        ) = request


        urgency_upper = str(
            urgency or "LOW"
        ).upper()


        if urgency_upper == "HIGH":

            urgency_icon = "🔴"

        elif urgency_upper == "MEDIUM":

            urgency_icon = "🟠"

        else:

            urgency_icon = "🟢"


        with st.container(border=True):

            # ------------------------------------------------
            # TOP ROW
            # ------------------------------------------------

            left, right = st.columns(
                [3, 1]
            )


            with left:

                st.markdown(
                    f"### 🎫 {reference_id}"
                )


                st.write(
                    f"**Farmer:** "
                    f"{farmer_name or 'Unknown'}"
                )


                st.write(
                    f"**District:** "
                    f"{district or 'Unknown'}"
                )


                st.write(
                    f"**Crop:** "
                    f"{crop or 'Unknown'}"
                )


            with right:

                st.metric(
                    "Status",
                    status or "OPEN",
                )


                st.write(
                    f"{urgency_icon} "
                    f"**{urgency_upper}**"
                )


            st.divider()


            # ------------------------------------------------
            # PROBLEM
            # ------------------------------------------------

            st.markdown(
                f"**Reason:** {reason}"
            )


            st.markdown(
                "**What happened:**"
            )


            st.write(
                what_happened
                or "Not provided"
            )


            # ------------------------------------------------
            # AGENT CHECKED
            # ------------------------------------------------

            st.markdown(
                "**What Krishi Mitra already checked:**"
            )


            st.write(
                agent_checked
                or "Not provided"
            )


            # ------------------------------------------------
            # FOLLOW-UP
            # ------------------------------------------------

            col_a, col_b, col_c = st.columns(3)


            with col_a:

                st.write(
                    f"**Language:** "
                    f"{language or 'Not specified'}"
                )


            with col_b:

                st.write(
                    f"**Preferred follow-up:** "
                    f"{preferred_follow_up or 'Not specified'}"
                )


            with col_c:

                st.write(
                    f"**Created:** "
                    f"{created_at or 'Unknown'}"
                )


            st.divider()


            st.info(
                "Human agriculture expert should review "
                "this request."
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()


st.caption(
    "Krishi Mitra • Call Analytics & Human Help"
)
