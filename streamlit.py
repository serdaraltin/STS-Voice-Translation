import base64
from pathlib import Path
import streamlit as st
from ctypes import *
from config import config
from api import api


def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

def set_png_as_page_bg(png_file):
    bin_str = img_to_bytes(png_file)
    page_bg_img = (
        """
   <style>
   body {
   background-image: url("data:image/png;base64,%s");
   background-size: cover;
   }
   </style>
   """
        % bin_str
    )

    st.markdown(page_bg_img, unsafe_allow_html=True)
    return

def save_settings():
    config.save()

def reset_settings():
    pass

def reload_settings():
    config.load()

# set_png_as_page_bg("images/background.jpg")

# st.markdown(
#     f"""
#      <style>
#      .stApp {{
#          background: url(data:image/bacground.jpg;base64,{base64.b64encode(open("./images/background.jpg", "rb").read()).decode()});
#          background-repeat: no-repeat;
#          background-position: center;
#          width: 100%;
#          height: 100%;
#          background-color: black;
#          background-size: cover;
#      }}
#      </style>
#      """,
#     unsafe_allow_html=True,
# )

# --------------------------------------------------------------
# personal_details = st.markdown(
#    "<p style='text-align: left; color: gray;'>Personal Details</p>",
#    unsafe_allow_html=True,
# )
# --------------------------------------------------------------
# title_settings = st.markdown(
#    "<p style='text-align: left; color: gray;'>Settings</p>", unsafe_allow_html=True
# )

logo_url = "./images/translation.png"

# st.set_page_config(layout="wide")

css = """
   <style>
      .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
      font-size:1.2rem;
      margin-right:1rem;    
      }
      .column {
      float: left;
      width: 25%;
      }
      .row:after {
      content: "";
      display: table;
      clear: both;
      }
      div[data-baseweb="select"] > div {
      background-color: rgba(255,255,255,0.4);
      }
      div[role="listbox"] ul {
      background-color: red;
      }
   </style>
"""

# st.markdown(css, unsafe_allow_html=True)

tab_debug,tab_panel, tab_cloning, tab_info = st.tabs(
    [ "🪲Debug", "⚙️ Panel", "🎙️ Cloning", "ℹ️ Info"])

# sidebar ---------------------------------------------------------------
with st.sidebar:
    imgSideBar = st.image(logo_url, width=200)
    title = st.markdown(
        "<h1 style='text-align: center; color: #58a5ec; font-size:2rem;'>Transvoice</h1>",
        unsafe_allow_html=True,
    )
    # st.divider()
    st.header("", divider="rainbow")
    st.header("New Features")
    feature = st.markdown(
        """<p style='color: #b5b5b5; height:200px;'>
                         - Lorem Ipsum is simply dummy text of the printing and <b>typesetting</b> industry.<br>
                         - Lorem Ipsum has been the industry's <b>standard</b> dummy text ever since the 1500s,<br>
                         - There are many variations of <b>passages</b> of Lorem Ipsum available,<br>
                          </p>""",
        unsafe_allow_html=True,
    )

# tab panel -------------------------------------------------------------
with tab_panel:
    st.write()

    st.subheader("Personal Details", divider="rainbow")
    info_col1, info_col2, info_col3 = st.columns([1, 1, 1])

    with info_col1:
        st.caption("Selected Language")
        st.subheader(config.setting.source_language)

        st.caption("Delay")
        st.subheader("1.5s")

    with info_col2:
        st.caption("Translated Language")
        st.subheader(config.setting.target_language)

        st.caption("Used")
        st.subheader("2Hr")

    with info_col3:
        st.caption("Voice")
        st.subheader(config.setting.voice)

        st.caption("Credits Left")
        st.subheader("80%")

    st.subheader("Devices", divider="gray")
    (
        input_device,
        output_device,
        record_quality,
    ) = st.columns([1, 1, 1])
    with input_device:
        input_device = st.selectbox(
            key="input_device",
            label="Input Device",
            options=([config.setting.input_device]),
            index=0,
            disabled=st.session_state.get("disabled", True),
        )
    with output_device:
        output_device = st.selectbox(
            key="output_device",
            label="Output Device",
            options=([config.setting.output_device]),
            index=0,
            disabled=st.session_state.get("disabled", True),
        )
    with record_quality:
        output_device = st.selectbox(
            key="record_quality",
            label="Record Quality ",
            options=([config.setting.record_quality]),
            index=0,
            disabled=st.session_state.get("disabled", True),
        )

    # --------------------------------------------------------------
    st.subheader("Source Voice", divider="gray")
    (input_language, Null) = st.columns([3, 1])

    with input_language:
        input_language = st.selectbox(
            key="input_language",
            label="Input Language",
            options=(api.aws_translate.languages),
            index=0,
        )

    # --------------------------------------------------------------
    st.subheader("Target Voice", divider="gray")

    (ai_model, target_language, voice) = st.columns([1, 1, 1])
    with ai_model:
        ai_model = st.selectbox(
            key="ai_model",
            label="AI Model",
            options=(api.elevenlabs.models_names),
            index=0,
        )
    with target_language:
        target_language = st.selectbox(
            key="target_language",
            label="Target Language",
            options=(api.aws_translate.languages),
            index=0,
        )
    with voice:
        # st.subheader("Cloned Voice")
        cloned_voice = st.selectbox(
            key="cloned_voice",
            label="Voice",
            options=(api.elevenlabs.voice_names),
            index=0,
        )

    (
        col_voice_quality,
        col_voice_optimizing,
        col_speaker_boost,
    ) = st.columns([1, 1, 1])
    with col_voice_quality:
        voice_quality = st.selectbox(
            key="voice_quality",
            label="Quality",
            options=(api.elevenlabs.output_format.keys()),
            index=0,
        )
    with col_voice_optimizing:
        voice_stability = st.slider("Optimizing", 0, 4, 0)
    with col_speaker_boost:
        st.text("Speaker Boost")
        speaker_boost = st.toggle(key="speaker_boost", label="Disable")
        if speaker_boost:
            st.write(label="Active", key="speaker_boost")

    (
        voice_stability,
        voice_similarty,
        voice_style,
    ) = st.columns([1, 1, 1])
    with voice_stability:
        voice_stability = st.slider("Stability", 0, 100, 30)
    with voice_similarty:
        voice_similarty = st.slider("Clarity + Similarity", 0, 100, 29)
    with voice_style:
        voice_quality = st.slider("Style", 0, 100, 0)

    # --------------------------------------------------------------
    st.subheader("Options", divider="rainbow")

    (options_save, options_reload, options_reset) = st.columns((1, 1, 1))
    with options_save:
        btn_save = st.button(
            key="save", label="SAVE SETTINGS", on_click=save_settings, type="primary"
        )
    with options_reset:
        btn_reset = st.button(
            key="reset", label="RESET SETTINGS", on_click=reset_settings
        )
    with options_reload:
        btn_reset = st.button(
            key="reload", label="RELOAD SETTINGS", on_click=reload_settings
        )

# cloning tab -----------------------------------------------------------
with tab_cloning:
    # title_add_voice = st.markdown(
    #    "<p style='text-align: left; color: gray;'>Add Voice</p>",
    #    unsafe_allow_html=True,
    # )
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

# info tab --------------------------------------------------------------
with tab_info:
    title_info = st.markdown(
        "<p style='text-align: left; color: gray;'>Info</p>", unsafe_allow_html=True
    )
    st.image(logo_url, width=200)
    st.header("", divider="rainbow")
    info = st.markdown(
        """Lorem Ipsum is simply dummy text of the printing and typesetting industry.
      Lorem Ipsum has been the industry's standard dummy text ever since the 1500s,
      when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries,
      but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages,
      and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum."""
    )

    info = st.markdown(
        """Lorem Ipsum is simply dummy text of the printing and typesetting industry.
      Lorem Ipsum has been the industry's standard dummy text ever since the 1500s,
      when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries,
      but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing."""
    )

# info debug --------------------------------------------------------------
with tab_debug:
    col1_info, col2_info, col3_info  = st.columns([1,1,1])
    with col1_info:
        st.caption("Source Language: :green[{}] (:blue[{}])".format(config.setting.source_language,config.setting.source_language_code))
        st.caption("Target Language: :green[{}] (:blue[{}])".format(config.setting.target_language,config.setting.target_language_code))
        st.caption("Voice Model: :green[{}](:blue[{}...])".format(config.setting.voice,config.elevenlabs.voice_id[:12]))
    
    with col2_info:
        st.caption("Input Device: :green[{}]".format(config.setting.input_device))
        st.caption("Output Device: :green[{}]".format(config.setting.output_device))
        st.caption("Virtual Device Id: :green[{}]".format(config.setting.device_id))
    
    with col3_info:
        st.caption("Recoid Quality: :green[{}]".format(config.setting.record_quality))
        st.caption("Voice Quality: :green[{}]".format(config.setting.voice_quality))
        st.caption("Optimizing: :green[{}]".format("..."))
    
   
    col_input_text, col_target_text = st.columns([1,1])
    
    with col_input_text:
        txt_input_text = st.text_area(value=st.session_state["recognize_text"],key="txt_input_text", label="Source Text", height=300, disabled= True)
    with col_target_text:
        txt_target_text = st.text_area(key="txt_target_text", label="Target Text", height=300, disabled= True)

    col_speech_voice, col_process = st.columns([1,1])
    
    with col_speech_voice:
        txt_speech = st.text_area(key="txt_speech", label="Speech", height=300, disabled= True)

    with col_process:
        txt_process = st.text_area(key="txt_process", label="Process", height=300, disabled= True)
