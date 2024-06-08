About
=====
Patient education plays a crucial role in the healthcare profession, offering numerous benefits to both patients and healthcare providers alike. 
By empowering patients with comprehensive knowledge about their health conditions, treatment options, and preventive measures, patient education 
fosters informed decision-making and encourages active participation in healthcare management. This leads to improved treatment adherence, better 
health outcomes, and reduced healthcare costs. Additionally, patient education promotes patient autonomy and self-care, ultimately enhancing 
overall patient satisfaction and quality of life. Moreover, healthcare providers benefit from reduced patient visits, enhanced communication, 
and strengthened patient-provider relationships, resulting in more efficient healthcare delivery and improved patient care experiences.

#################
Problem Statement
#################

Low health literacy among patients poses a significant challenge, as it impedes their ability to comprehend medical information, follow instructions, 
and recognize the importance of their treatments. This difficulty in understanding can severely limit their capacity to manage their health effectively. 
Additionally, healthcare professionals often face time constraints during appointments, preventing them from delivering thorough patient education, 
which results in many patients receiving inadequate information about their health.

#########################
Project Goals & Non-goals
#########################

Inclusions
----------
* **Develop an AI Chatbot:** Create an AI-driven chatbot to deliver high-quality health education materials.
* **Enhance Health Literacy:** Improve patient understanding of health information to promote better health management.
* **Improve Treatment Adherence:** Increase compliance with treatment plans by providing clear and accessible health information.

Exclusions
----------
* Not Focused on Reducing Healthcare Costs: Although well-informed patients who effectively manage their conditions are less likely to need emergency care or frequent hospitalizations, the primary aim of this project is not to reduce healthcare costs.
* Not Intended to Alleviate Provider Workload: This project does not seek to replace healthcare providers or diminish their workload. Instead, it is designed to serve as an educational resource to supplement patient knowledge.

#################
Technical Details
#################
A.M.Y.T.H.E.S.T. stands for **Artificial Messaging Yielding Thoughtful Human-like Engagement Systems Technology**.

.. figure:: img/ai_chatbot_data_architecture.png
   :width: 800   
   :alt: This is an image

   ETL architecture for ingesting health-related data, performing transformations, and storing it in a vector database for reference by an AI 
   chatbot utilizing Retrieval-Augmented Generation (RAG).

Data Extraction
---------------
Health-related data was extracted from `MedlinePlus <https://medlineplus.gov/>`_ using Python. Utilizing 
`Boto3 <https://boto3.amazonaws.com/v1/documentation/api/latest/index.html>`_, a Python library for interfacing 
with Amazon S3, the raw data was subsequently stored in an Amazon S3 bucket as a text file (.txt) for 
preprocessing purposes.

Data Transformation
-------------------
An Amazon Lambda function was used to preprocess the raw data in S3 into smaller chunks, ensuring it met the token 
constraints for vector embedding. The processed data was then staged in another S3 bucket.

Data Loading
------------
Another Amazon Lambda function was utilized to process the staged data in S3 into vector embeddings using the 
`Voyage AI API <https://docs.voyageai.com/docs/introduction>`_ (voyage-large-2 model). These embeddings were then 
stored in `Pinecone <https://docs.pinecone.io/home>`_, a vector database.

Data Privacy & Security
-----------------------
To ensure data privacy and security, a process was implemented to eliminate highly confidential (C4) data. This 
category includes the most sensitive information, whose unauthorized disclosure could result in severe legal, financial, 
or security repercussions.

Prior to storing the chatbot history in an S3 bucket, names, dates of birth, locations, and phone numbers were removed 
through a process called desensitization using an Amazon Lambda function.
