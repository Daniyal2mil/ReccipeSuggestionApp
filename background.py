import streamlit as st
import base64

@st.cache(allow_output_mutation=True)
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_gif_as_page_bg(gif_file):
    bin_str = get_base64_of_bin_file(gif_file)
    page_bg_img = '''
    <style>
    .stApp {
        background-image: url("data:image/gif;base64,%s");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
    }
    </style>
    ''' % bin_str
    
    st.markdown(page_bg_img, unsafe_allow_html=True)
