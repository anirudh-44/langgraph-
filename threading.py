import streamlit as st
from chatbot_backend import chatbot
from langchain_core.messages import HumanMessage
import uuid

#*************************** utility functions*****************************
def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    st.session_state['message_history'] = []
    add_thread_id(st.session_state['thread_id'])

def add_thread_id(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    return chatbot.get_state(config={'configurable':{'thread_id':thread_id}}).values['messages']


#***************************SESSION_SETUP**************************************

# displaying previous messages
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id() 

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []

add_thread_id(st.session_state['thread_id'])

CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

#*******************************SIDEBAR_UI*****************************************
st.sidebar.title('LangGraph Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header('My conversations')

for thread_id in st.session_state['chat_threads'][::-1]:
    if st.sidebar.button(str(thread_id)):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id) 

        temp_messages = [] # for storing the message history received by load_conversation() in the format accepted by session_state['message_state']

        for msg in messages:
            if isinstance(msg,HumanMessage):
                role = 'user'
            else:
                role='assistant'
            temp_messages.append({'role':role, 'content':msg.content})

        st.session_state['message_history'] = temp_messages

    


        

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])



user_input = st.chat_input('Type here')




#displaying current user message

if user_input:

    st.session_state['message_history'].append({'role':'user', 'content':user_input})
    with st.chat_message('user'):
        st.text(user_input)

    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk,metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]}, 
                config=CONFIG,
                stream_mode = 'messages'
            )
        )

    st.session_state['message_history'].append({'role':'assistant', 'content':ai_message})
