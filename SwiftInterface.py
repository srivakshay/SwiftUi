import asyncio
import time

import httpx
import requests
import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from datetime import datetime


async def generate_code():
    async with httpx.AsyncClient(timeout=50000) as client:
        try:
            res = await client.get("http://127.0.0.1:5000/generate")
            return res.json()["message"]
        except httpx.HTTPStatusError as e:
            return {"error": str(e)}


def upload_plsql_file():
    res = requests.post('http://127.0.0.1:5000/upload',
                        files={"store_proc.txt": uploaded_file.getvalue()})
    if res.status_code == 200:
        return True


def typewriter(text):
    tokens = text.split()
    container = st.empty()
    curr_full_text = ""
    for token in tokens:
        for element in token:
            curr_full_text = curr_full_text + str(element)
            # curr_full_text = " ".join(tokens[1])
            container.markdown(curr_full_text)
            time.sleep(1 / 50)
        curr_full_text += " "


m = st.markdown("""
<style>
div.stButton > button:first-child {
    background-color: rgb(38, 39, 48);
    width: 350px;
    align: left
}
</style>""", unsafe_allow_html=True)

if 'ask_anything' not in st.session_state:
    st.session_state.ask_anything = False

if 'download' not in st.session_state:
    st.session_state.download = False


def click_ask_anything():
    st.session_state.ask_anything = True
    st.session_state.download = False


def click_download():
    st.session_state.download = True


def download_file_from_api():
    url = f"http://127.0.0.1:5000/download"
    filename = "files.zip"
    st.code(st.session_state.code)
    st.markdown(f"[Download {filename}]({url})", unsafe_allow_html=True)


uploaded_file = st.file_uploader("Select a file")
col1, col2 = st.columns(2)
with col1:
    covert_to_java = st.button("Convert code to Java")
with col2:
    ask_anything = st.button("Converse with your code", on_click=click_ask_anything)
col3, col4 = st.columns(2)
with col3:
    generate_business_doc = st.button("Generate business documentation")
with col4:
    generate_tech_doc = st.button("Generate technical documentation")
if uploaded_file is not None:
    st.code(uploaded_file.read().decode("utf-8"), language='plsql')

if covert_to_java:
    st.session_state.ask_anything = False
    st.session_state.download = False
    if uploaded_file is not None:
        upload_plsql_file()
        typewriter("Analysing PLSQL Code ")
        response = requests.get(
            'http://127.0.0.1:5000/getdomaintables')

        if response.status_code == 200:
            json_response = response.json()
            typewriter(json_response["message"])
        with st.spinner("Generating code"):
            # Run the async function in an asyncio event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            task = loop.create_task(generate_code())
            response = loop.run_until_complete(task)
            st.session_state.code = response
            # Display response after spinner
            st.code(response)
            download_file = st.button("Download Code", on_click=click_download)
            if download_file:
                st.session_state.download = True

    else:
        st.write("Please select file to convert")
if st.session_state.download:
    download_file_from_api()
if st.session_state.ask_anything:
    st.session_state.download = False
    if uploaded_file is not None:
        if prompt := st.chat_input("Ask anything"):
            typewriter("Sure - Here is the answer to your query " + '"' + prompt + '"')
            with st.spinner("Fetching answer"):
                response = requests.get("http://127.0.0.1:5000/ask?query=" + prompt)
                st.write(response.json()["message"])

if generate_business_doc:
    st.empty()
    st.session_state.download = False
    typewriter("Sure - Generating business documentation for the above code")
    with st.spinner("Generating business documentation"):
        response = requests.get("http://127.0.0.1:5000/generate_business_doc")
        st.write(response.json()["message"])

if generate_tech_doc:
    st.empty()
    st.session_state.download = False
    typewriter("Sure - Generating business documentation for the above code")
    with st.spinner("Generating technical documentation"):
        response = requests.get("http://127.0.0.1:5000/generate_tech_doc")
        st.write(response.json()["message"])
