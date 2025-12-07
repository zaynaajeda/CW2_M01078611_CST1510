import streamlit as st
from openai import OpenAI
import os
import sys
from my_app.components.sidebar import logout_section
from my_app.components.ai_functions import get_system_prompt

#Adjust path to main project directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_DIR)

#Initialise OpenAI client
client = OpenAI(api_key = st.secrets["OPENAI_API_KEY"])

#Webpage title and icon
st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")

#Ensure session state variables are initialised
if "logged_in" not in st.session_state:
    #Initialise login status
    st.session_state.logged_in = False

# Check if user is logged in
if not st.session_state.logged_in:
    st.error("You must be logged in to view the AI Assistant page.")

    #Button to go back to login/register page
    if st.button("Go to Login/Register page"):
        #Use the official navigation API to switch pages
        st.switch_page("Home.py")
        st.stop()

    #Stop further execution of the script
    st.stop()

#AI Assistant content for logged-in users
st.title("AI Assistant")

#Allow user to choose Specific AI Assistant
assistant_domain = st.selectbox("Choose AI Assistant", ["General", "Cyber Security", "Data Science", "IT Operations"])

st.divider()

#Prompt message for system is retrived from function based on domain selected
system_prompt = get_system_prompt(assistant_domain)

#Initialise session state for messages
if "messages" not in st.session_state:
    #Session state variable is initialised with content for system 
    st.session_state.messages = [
        {"role":"system", "content":system_prompt}
    ]

#Iterate through messages
for message in st.session_state.messages:
    #Skip system messages
    if message["role"] != "system":
        #Goes through user's messages
        with st.chat_message(message["role"]):
            #Display existing messages
            st.write(message["content"])

#Handle user input
user_input = st.chat_input("Type your message...")

#Verify if user entered message
if user_input:
    #Display user message immediately
    with st.chat_message("user"):
        st.write(user_input)

    #Add user message to state session
    st.session_state.messages.append(
        {"role":"user", "content":user_input}
    )

    #Send entire conversation to API
    response = client.chat.completions.create(
        model = "gpt-4o",
        messages = st.session_state.messages,
        stream = True   #Enable streaming
    )
    
    #Create an empty placeholder for AI response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        #Process chunks as they arrive
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                #Extract content from chunk
                content = chunk.choices[0].delta.content

                full_response += content

                #Update display with cursor effect
                message_placeholder.markdown(full_response + " ")
        
        #Finalise message display and store it
        message_placeholder.markdown(full_response)

        #Answer of AI is also added to session state variable
        st.session_state.messages.append(
            {"role":"assistant", "content":full_response}
        )

#Count messages
message_count = len(st.session_state.get("messages", [])) - 1

#Create sidebar after processing input to use latest counts
with st.sidebar:
    st.header("AI Chat Controls")

    #Show message count
    st.metric("Messages", message_count)

    #Clear chat button
    if st.button("Clear AI Chat", use_container_width=True):

        #Reset messages to initial state
        st.session_state.messages = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]

        #Rerun to refresh the interface
        st.rerun()  

    #Add divider and logout section
    st.divider()  
    logout_section()
