import streamlit as st

from tools.escalation_tool import get_open_escalations

st.set_page_config(
    page_title="Krishi Mitra Human Help",
    page_icon="🌾",
    layout="wide",
)

st.title("🌾 Krishi Mitra - Human Help Dashboard")

try:
    escalations = get_open_escalations()

    if not escalations:
        st.info("No open human-help requests.")
    else:
        st.success(f"{len(escalations)} open request(s)")

        for row in escalations:
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
            ) = row

            with st.container():
                st.subheader(f"🆔 {reference_id}")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.write(f"**Farmer:** {farmer_name}")
                    st.write(f"**District:** {district}")
                    st.write(f"**Crop:** {crop}")

                with col2:
                    st.write(f"**Urgency:** {urgency}")
                    st.write(f"**Language:** {language}")
                    st.write(f"**Follow-up:** {preferred_follow_up}")

                with col3:
                    st.write(f"**Status:** {status}")
                    st.write(f"**Created:** {created_at}")

                st.write(f"**Reason:** {reason}")
                st.write(f"**What happened:** {what_happened}")

                st.divider()

except Exception as e:
    st.error(f"Dashboard error: {e}")
