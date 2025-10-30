import streamlit as st
from openai import OpenAI
from streamlit_js_eval import streamlit_js_eval
client = OpenAI(api_key = st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Streamlit Chat")
st.title("Chatbot")

if "setup_complete" not in st.session_state:
    st.session_state.setup_complete = False
if "message_count" not in st.session_state:
    st.session_state.message_count = 0
if "feedback_shown" not in st.session_state:
    st.session_state.feedback_shown = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_complete" not in st.session_state:
    st.session_state.chat_complete = False

def show_feedback():
    st.session_state.feedback_shown = True
def complete_Setup():
    st.session_state.setup_complete = True

if not st.session_state.setup_complete:

    st.subheader("Personal Information", divider="rainbow")

    if "name" not in st.session_state:
        st.session_state["name"] = ""
    if "experience" not in st.session_state:
        st.session_state["experience"] = ""
    if "skills" not in st.session_state:
        st.session_state["skills"] = ""


    st.session_state["name"] = st.text_input(label="Name", max_chars=30,value = st.session_state["name"], placeholder="Enter Your Name")

    st.session_state["experience"] = st.text_area(label="Experience",height=None, value=st.session_state["experience"],max_chars=150, placeholder="Describe Your Experience")

    st.session_state["skills"] = st.text_area(label="skills", height=None,value = st.session_state["skills"],max_chars=150, placeholder="List Your Skills")

    st.subheader("Company & Position", divider="rainbow")

    if "company" not in st.session_state:
        st.session_state["company"] = "Meta"
    if "position" not in st.session_state:
        st.session_state["position"] = "Data Scientist"
    if "level" not in st.session_state:
        st.session_state["level"] = "junior"

    col1,col2 = st.columns(2)

    with col1:
        st.session_state["level"] = st.radio(
            "Choose level",
            key="visibility",
            options=["junior","mid-level","senior"]
        )

    with col2:
        st.session_state["position"] = st.selectbox(
            "Choose Position",
            ("Data Scientist","Data Engineer","ML Engineer","BI Analyst","Financial Analyst")
        )
        st.session_state["company"] = st.selectbox(
            "Choose Company",
            ("Meta","Amazon","Company 365","LinkedIn","Nestle","Spotify","Udemy")
        )
    if st.button("Start Interview", on_click=complete_Setup):
        st.write("Setup Complete. Starting Interview....")

if st.session_state.setup_complete and not st.session_state.chat_complete and not st.session_state.feedback_shown:

    st.info("""
    start by introducing youself.
        """)
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4o"

    if not st.session_state.messages:
        st.session_state.messages = [{"role":"system","content":f"Your are an HR executive that interviews an interviewee called {st.session_state["name"]} with experience {st.session_state["experience"]} and skills {st.session_state["skills"]}. You should interview them for {st.session_state["level"]} {st.session_state["position"]} at {st.session_state["company"]}" }]

    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if st.session_state.message_count < 5:
        if prompt:= st.chat_input("Your answer. ",max_chars=600):
            st.session_state.messages.append({"role":"user","content":prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            if st.session_state.message_count < 5:
                with st.chat_message("assistant"):
                    stream = client.chat.completions.create(
                        model=st.session_state["openai_model"],
                        messages = [
                            {"role": m["role"], "content":m["content"]} for m in st.session_state.messages
                        ],
                        stream=True
                    )
                    response = st.write_stream(stream)
                st.session_state.messages.append({"role":"assistant","content":response})
            st.session_state.message_count += 1
    if st.session_state.message_count >= 5:
        st.session_state.chat_complete = True

if st.session_state.chat_complete and not st.session_state.feedback_shown:
    if st.button("Get Feedback",on_click=show_feedback):
        st.write("Fetching Feedback...")

if st.session_state.feedback_shown:
    st.subheader("Feedback")

    conversation_history = "\n".join([f"{msg["role"]} : {msg["content"]}" for msg in st.session_state.messages])

    feedback_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    feedback_completion = feedback_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role":"system",
             "content":"""
                You are a helpful tool that provide feedback on interviewee performance.
                Before the feedback give the score of 1 to 10.
                Follow this format:
                Overall score: //Your score
                feedback: //Here you put your feedback
                Give only the feedback donot ask any additional questions.
            """},
            {
                "role":"user",
                "content":f"""
                    This is the interview you need to evaluate.Keep in mind that you are only a tool and should not engage in conversation:
                    {conversation_history}
                    """
            }
        ]
    )

    st.write(feedback_completion.choices[0].message.content)

    if st.button("Restart Interview", type="primary"):
        streamlit_js_eval(js_expressions="parent.window.location.reload()")