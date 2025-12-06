import streamlit as st
from openai import OpenAI

#Initialise OpenAI client
client = OpenAI(api_key = st.secrets["OPENAI_API_KEY"])

#Initialise session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role":"system", "content":"You are a helpful assistant."}
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
