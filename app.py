'''
-------------------------------------------------------------------------------
Developed by:  Ty Rawls
Email:         tyrell.rawls@gmail.com
LinkedIn:      https://www.linkedin.com/in/tyrellrawls/
-------------------------------------------------------------------------------
'''

import os
import io
import re
import uuid
import boto3
import warnings
import streamlit as st
from pinecone import Pinecone
from datetime import datetime
from urllib.parse import urlparse
from streamlit_chat import message
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.chains import ConversationChain
from langchain_voyageai import VoyageAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.memory import ConversationBufferMemory


# Ignore specific warnings by category
warnings.filterwarnings('ignore', category=DeprecationWarning)

# Setup - Streamlit secrets
OPENAI_API_KEY        = st.secrets['api_keys']['OPENAI_API_KEY']
GROQ_API_KEY          = st.secrets['api_keys']['GROQ_API_KEY']
VOYAGE_AI_API_KEY     = st.secrets['api_keys']['VOYAGE_AI_API_KEY']
PINECONE_API_KEY      = st.secrets['api_keys']['PINECONE_API_KEY']
AWS_ACCESS_KEY_ID     = st.secrets['aws_keys']['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = st.secrets['aws_keys']['AWS_SECRET_ACCESS_KEY']
AWS_REGION            = st.secrets['aws_keys']['AWS_REGION']

# Set up page icons
amythest_icon     = 'https://i.ibb.co/G7wbB8N/amythest.png'
amythest_banner   = 'https://i.ibb.co/qCdJ97g/amythest-banner.png'
user_cyan_icon    = 'https://i.ibb.co/LPtzryF/human-cyan.png'
user_fuchsia_icon = 'https://i.ibb.co/64vZHsv/human-fuchsia.png'

# Set the page title, layout, and icon for the browser tab 
st.set_page_config(page_title='AMYTHEST | Healthcare AI Patient Education Chatbot', 
                   layout='wide', 
                   page_icon=amythest_icon)

# Set page icon and logo banner for sidebar
st.logo(amythest_banner, icon_image=amythest_icon)

# Set title of application
st.markdown(
    '<h1 style="text-align: center;">AMYTHEST | Healthcare AI Patient Education Chatbot</h1>',
    unsafe_allow_html=True
)

# Display app logo with centered alignment using HTML and CSS
st.markdown(
    f"""
    <div style='display: flex; justify-content: center;'>
        <img width='250' height='250' src='{amythest_icon}' alt='AMYTHEST Logo'>
    </div>
    """,
    unsafe_allow_html=True
)
st.header('', divider='violet')  # Add horizontal page divider

# Setup sidebar options and captions
st.sidebar.header('Settings')
color_options = ['Cyan', 'Fuchsia']
llm_options = ['gpt-4o', 'llama3-8b-8192', 'gemma-7b-it']
user_icon_color = st.sidebar.selectbox('Icon Color:', color_options)
user_message_bubble_color = st.sidebar.selectbox('Message Bubble Color:', color_options)
llm_choice = st.sidebar.selectbox('LLM:', llm_options)

st.sidebar.caption(
    'Developed by [Ty Rawls](https://www.linkedin.com/in/tyrellrawls/)\n\n'
    'Want to know more about AMYTHEST? See [documentation](https://tyrawls.github.io/healthcare-ai-patient-education-chatbot/_build/html/index.html) for more info.'
)

linkedin = 'https://i.ibb.co/5MKFS57/linkedin.gif'
email    = 'https://i.ibb.co/FKQqBHr/email.gif'
medium   = 'https://i.ibb.co/rdDqjnX/medium.png'

st.sidebar.caption(
    f"""
        <div style='display: flex; align-items: center;'>
            <a href = 'https://www.linkedin.com/in/tyrellrawls/'><img src='{linkedin}' style='width: 35px; height: 35px; margin-right: 25px;'></a>
            <a href = 'mailto:tyrell.rawls@gmail.com'><img src='{email}' style='width: 35px; height: 35px; margin-right: 25px;'></a>
            <a href = 'https://tyrawls.medium.com/'><img src='{medium}' style='width: 35px; height: 35px; margin-right: 25px;'></a>            
        </div>       
        """,
    unsafe_allow_html=True,
)

# Choose LLM
if llm_choice == 'gpt-4o':
    # Initialize OpenAI ChatGPT-4o model
    llm = ChatOpenAI(
        model=llm_choice, 
        openai_api_key=OPENAI_API_KEY
    )
elif llm_choice == 'llama3-8b-8192':
    # Initialize Meta LLaMA3 8b model
    llm = ChatGroq(
        model_name=llm_choice, 
        groq_api_key=GROQ_API_KEY
    )
else:
    # Initialize Google Gemma 7b model
    llm = ChatGroq(
        model_name='gemma-7b-it', 
        groq_api_key=GROQ_API_KEY
    )

if user_message_bubble_color == 'Cyan':
    # Custom HTML and CSS for chat message styling
    chat_message_config = '''
    <style>
    .chat-message {
        display: flex;
        align-items: center;
        margin: 5px 0;
    }
    .user-message .message-content {
        background-color: #00FFF8;
        color: #000000;
        border-radius: 15px;
        padding: 10px;
        margin-left: 10px;
        max-width: 70%;
        font-size: 18px;
    }
    .bot-message .message-content {
        background-color: #7B17E4;
        color: #FFFFFF;
        border-radius: 15px;
        padding: 10px;
        margin-right: 10px;
        max-width: 70%;
        font-size: 18px;
    }
    .avatar {
        width: 60px;
        height: 60px;
        border-radius: 50%;
    }
    </style>
    '''
else: 
    chat_message_config = '''
    <style>
    .chat-message {
        display: flex;
        align-items: center;
        margin: 5px 0;
    }
    .user-message .message-content {
        background-color: #E740F7;
        color: #FFFFFF;
        border-radius: 15px;
        padding: 10px;
        margin-left: 10px;
        max-width: 70%;
    }
    .bot-message .message-content {
        background-color: #7B17E4;
        color: #FFFFFF;
        border-radius: 15px;
        padding: 10px;
        margin-right: 10px;
        max-width: 70%;
    }
    .avatar {
        width: 60px;
        height: 60px;
        border-radius: 50%;
    }
    </style>
    '''

st.markdown(chat_message_config, unsafe_allow_html=True)

# Initiate a random session ID for chat history key (filename)
current_date     = datetime.now().date()
session_id       = str(uuid.uuid4())
bucket_name      = 'ai-chat-history'
chat_history_key = f'raw/{current_date}/chat_history_{session_id}.txt'

print(f'chat_history_key: {chat_history_key}')

# Initialize Voyage AI vector embedding model
embeddings = VoyageAIEmbeddings(
    model='voyage-large-2' , 
    voyage_api_key=VOYAGE_AI_API_KEY
)

# Initialize Pinecone database and retriever
os.environ['PINECONE_API_KEY'] = PINECONE_API_KEY
pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = 'healthcare-ai-patient-education-data'
vector_store = PineconeVectorStore.from_existing_index(  # Retriever
    index_name=index_name,
    embedding=embeddings
)
retriever = vector_store.as_retriever()

# Initialize the memory and create the conversation chain with memory
memory = ConversationBufferMemory()
conversation_chain = ConversationChain(llm=llm, memory=memory)

# Initialize AWS S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)


# Function to generate pre-signed URL
def generate_presigned_url(s3_uri):
    # Parse the S3 URI
    parsed_url  = urlparse(s3_uri)
    bucket_name = parsed_url.netloc
    object_key  = parsed_url.path.lstrip('/')
    
    # Generate a pre-signed URL for the S3 object
    presigned_url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': object_key},
        ExpiresIn=3600  # URL expiration time in seconds
    )
    return presigned_url


# Function to retrieve documents, generate URLs, and format the response
def retrieve_and_format_response(query, retriever, llm):
    docs = retriever.get_relevant_documents(query)

    formatted_docs = []
    for doc in docs:
        content_data  = doc.page_content
        s3_uri        = doc.metadata['id']
        s3_gen_url    = generate_presigned_url(s3_uri)
        formatted_doc = f'{content_data}\n\n[More Info]({s3_gen_url})'
        formatted_docs.append(formatted_doc)
        
    combined_content = '\n\n'.join(formatted_docs)
    # print(combined_content)
    
    # Create a prompt for the LLM to generate an explanation based on the retrieved content
    prompt = f"Instruction: You are a helpful and polite healthcare assistant named 'Amythest'. \
        If a user asks what their name is, you will reply with their name {st.session_state.name}. \
        You only answer health-related questions providing a summarized & concise explanation using a couple of sentences. \
        Only respond with the information relevant to the user query {query}, if there are none, make sure you say 'I don't know. \
        I did not find the relevant data in the knowledge base.'. In the event that there's relevant info, make sure to attach \
        the download button at the very end: \n\nClick here ---> [More Info]({s3_gen_url}) Context: {combined_content}"
    
    # Create a HumanMessage object using the promppt
    messages = [HumanMessage(content=prompt)]
    
    # Pass the message to the conversation chain
    response = conversation_chain.run(messages)
    
    return {'answer': response}


def push_to_s3(content, bucket, key):
    '''
    Saves file contents to an Amazon S3 bucket.

    Parameters
    ----------
    content : str or BytesIO
        The contents of the disease article.
   
    bucket : str
        The name of the Amazon S3 bucket.
        
    key : str
        The location and name under which to save the file.

    Returns
    -------
    None

    '''    
    # Upload the file to an AWS S3 bucket
    try:
        s3.put_object(Body=content, Bucket=bucket, Key=key)
        print(f'Upload successful: Successfully pushed data to {bucket}.\n'
              f'File saved as: {key}.\n')
    except Exception as e:
        print(f'Upload failed: {e}\n')


# Function to render chat messages
def render_message(message, role):
    if role == 'user':
        if user_icon_color == 'Cyan':
            avatar_url = user_cyan_icon
        else: 
            avatar_url = user_fuchsia_icon
    else:
        avatar_url = 'https://i.ibb.co/G7wbB8N/amythest.png'  # Replace with actual bot avatar URL
    
    message_html = f"""
    <div class="chat-message {role}-message">
        <img src="{avatar_url}" alt="{role} avatar" class="avatar">
        <div class="message-content">{message}</div>
    </div>
    """
    st.markdown(message_html, unsafe_allow_html=True)

    return message_html


def detect_name(text):
    # Try to match patterns like "My name is John" or "I'm John"
    patterns = [
        r"my name is ([A-Z][a-z]+)",  # Pattern for "My name is X"
        r"i am ([A-Z][a-z]+)",        # Pattern for "I am X"
        r"i'm ([A-Z][a-z]+)"          # Pattern for "I'm X"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None

# Initialize session state variable for storing name
if 'name' not in st.session_state:
    st.session_state.name = ''

# Function to update the name in session state
def save_name(user_input):
    user_name = detect_name(user_input)
    if user_name != None:
        st.session_state.name = user_name

# Initialize chat history
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# Display chat messages from history
for message in st.session_state['messages']:
    st.markdown(message['content'], unsafe_allow_html=True)

# Get user input
user_input = st.chat_input('You: ')

if user_input:
    chat_history = f'Session ID: {session_id}\n-------------------------------------------------\n'
    user_content = render_message(user_input, 'user')
    save_name(user_input)

    # Display current name value
    st.write(f"Hello, {st.session_state.name}!")

    # Add user message to chat history
    st.session_state['messages'].append({'role': 'user', 'content': user_content})
    
    # Generate and display bot response
    with st.spinner('Thinking...'):
        bot_response = retrieve_and_format_response(user_input, retriever, llm)['answer']

    bot_content = render_message(bot_response, 'bot')

    st.session_state['messages'].append({'role': 'assistant', 'content': bot_content})

    # Append interaction to chat history
    chat_history += f"You: {user_input}\n\nAmythest: {bot_response}\n\n"

    # Convert the chat history to a bytes-like object
    file_obj = io.BytesIO(chat_history.encode('utf-8'))

    # Upload the file to S3 bucket
    push_to_s3(file_obj, bucket_name, chat_history_key)