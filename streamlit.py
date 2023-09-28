import base64
from pathlib import Path
import streamlit as st

def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded


logo_url = "./images/translation.png"

st.set_page_config(layout="wide")

css = '''
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
    
</style>
'''
st.markdown(css, unsafe_allow_html=True)

tab_panel, tab_cloning, tab_info = st.tabs(["⚙️ Panel", "🎙️ Cloning", "ℹ️ Info"])

#sidebar
with st.sidebar:
   imgSideBar = st.image(logo_url, width=200)
   title = st.markdown("<h1 style='text-align: center; color: #58a5ec; font-size:2rem;'>Transvoice</h1>", unsafe_allow_html=True)
   #st.divider()
   st.header('', divider='rainbow')
   st.header("New Features")
   feature = st.markdown("""<p style='color: #b5b5b5; height:200px;'>
                         - Lorem Ipsum is simply dummy text of the printing and <b>typesetting</b> industry.<br>
                         - Lorem Ipsum has been the industry's <b>standard</b> dummy text ever since the 1500s,<br>
                         - There are many variations of <b>passages</b> of Lorem Ipsum available,<br>
                          </p>""",unsafe_allow_html=True)
   
   social_link = st.markdown("""<div style='color:gray; position:fixed; bottom:0;'><div class='row'>
                             <div class='column'><a href='https://www.digitales.com.tr'><img src='data:image/png;base64,{}' class='img-fluid' width=32></a></div>
                             <div class='column'><a href='https://www.digitales.com.tr'><img src='data:image/png;base64,{}' class='img-fluid' width=32></a></div>
                             <div class='column'><a href='https://www.digitales.com.tr'><img src='data:image/png;base64,{}' class='img-fluid' width=32></a></div>
                             <div class='column'><a href='https://www.digitales.com.tr'><img src='data:image/png;base64,{}' class='img-fluid' width=32></a></div>
                             </div>
                             <p style='margin-top:1rem;'>Copyright © 2023 by <a href='https://www.digitales.com.tr'>Digitales</a></p></div>""".format(img_to_bytes("./images/instagram.png"),img_to_bytes("./images/facebook.png"),img_to_bytes("./images/linkedin.png"),img_to_bytes("./images/youtube.png")), unsafe_allow_html=True)
#panel tab
with tab_panel:
   st.write()

   personal_details = st.markdown("<p style='text-align: left; color: gray;'>Personal Details</p>", unsafe_allow_html=True)
   info_col1, info_col2, info_col3 = st.columns([1,1,1])

   with info_col1:
      st.subheader("English")
      st.caption("Selected Language")
      st.subheader("1.5s")
      st.caption("Delay")

   with info_col2:
      st.subheader("Spanish")
      st.caption("Translated Language")
      st.subheader("2Hr")
      st.caption("Used")

   with info_col3:
      st.subheader("Steve")
      st.caption("Voice")
      st.subheader("80%")
      st.caption("Credits Left")

   #with calender_col:
      #st.caption("Calender")
      
   st.header('', divider='rainbow')

   title_settings = st.markdown("<p style='text-align: left; color: gray;'>Settings</p>", unsafe_allow_html=True)

   settings_input_device, settings_output_device, settings_cloned_voice = st.columns([1,1,1])


   with settings_input_device:
      st.subheader("Input Device")
      input_device = st.selectbox(key="input_device",label="", options=("Read Microphone","Front Microphone"), index=0,
         placeholder="Default Device"
      )


   with settings_output_device:
      st.subheader("Output Device")
      output_device = st.selectbox(key="output_device",label="", options=("Line Out","HDMI/Displayport 3"), index=0,
         placeholder="Default Device"
      )


   with settings_cloned_voice:
      st.subheader("Cloned Voice")
      cloned_voice = st.selectbox(key="cloned_voice",label="", options=("Adam","Eve"), index=0,
         placeholder="Default Voice"
      )

      
   settings_input_language, settings_target_language, settings_voice_quality = st.columns([1,1,1])

   with settings_input_language:
      st.subheader("Input Language")
      input_language = st.selectbox(key="input_language",label="", options=("English","Turkish"), index=0,
         placeholder="Default Voice"
      )

   with settings_target_language:
      st.subheader("Target Language")
      target_language = st.selectbox(key="target_language",label="", options=("Spanish","English","Turkish"), index=0,
         placeholder="Default Voice"
      )

      
   with settings_voice_quality:
      st.subheader("Voice Quality")
      voice_quality = st.selectbox(key="voice_quality",label="", options=("48 KBPS","96 KBPS","128 KBPS","192 KBPS"), index=0,
         placeholder="Default Voice"
      )
#cloning tab
with tab_cloning:
   title_add_voice = st.markdown("<p style='text-align: left; color: gray;'>Add Voice</p>", unsafe_allow_html=True)

   txt_voice_name = st.text_input(key="voice_name",label="Name", placeholder="Cloning Voice Name")
   uploaded_voice = st.file_uploader("Audio or Video files, up to 10MB each")
   
   txt_description = st.text_area(key="description", label="Description", placeholder='How would you describe the voice? e.g. "An old American male voice with a slight hoarseness in his throat. Perfect for news."')
   st.header('', divider='rainbow')
   agree = st.checkbox('I hereby confirm that I have all necessary rights or consents to upload and clone these voice samples and that I will not use the platform-generated content for any illegal, fraudulent, or harmful purpose. I reaffirm my obligation to abide by ElevenLabs’ Terms of Service and Privacy Policy.')
   
   btn_add_voice = st.button(key="add_voice", label='Add Voice', disabled=True, on_click="")
#info tab
with tab_info:
   title_info = st.markdown("<p style='text-align: left; color: gray;'>Info</p>", unsafe_allow_html=True)
   st.image(logo_url, width=200)
   st.header('', divider='rainbow')
   info = st.markdown("""Lorem Ipsum is simply dummy text of the printing and typesetting industry.
                      Lorem Ipsum has been the industry's standard dummy text ever since the 1500s,
                      when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries,
                      but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages,
                      and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.""")
  
   info = st.markdown("""Lorem Ipsum is simply dummy text of the printing and typesetting industry.
                      Lorem Ipsum has been the industry's standard dummy text ever since the 1500s,
                      when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries,
                      but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing.""")
