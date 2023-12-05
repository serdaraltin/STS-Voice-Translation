import streamlit as st

def create_ui(_section):
    with _section:
        st.subheader("Add Voice", divider="rainbow")

        txt_voice_name = st.text_input(
            key="voice_name", label="Name", placeholder="Cloning Voice Name"
        )
        uploaded_voice = st.file_uploader("Audio or Video files, up to 10MB each", type=["mp3","wav"])

        txt_description = st.text_area(
            key="description",
            label="Description",
            placeholder='How would you describe the voice? e.g. "An old American male voice with a slight hoarseness in his throat. Perfect for news."',
        )
        st.header("", divider="rainbow")
        agree = st.checkbox(
            "I hereby confirm that I have all necessary rights or consents to upload and clone these voice samples and that I will not use the platform-generated content for any illegal, fraudulent, or harmful purpose. I reaffirm my obligation to abide by ElevenLabs’ Terms of Service and Privacy Policy."
        )

        btn_add_voice = st.button(
            key="add_voice", label="Add Voice", disabled=True, on_click=""
        )