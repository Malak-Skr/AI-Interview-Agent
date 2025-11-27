# rag_engine.py
import os
from dotenv import load_dotenv # لاستدعاء مفتاح API
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

# تحميل مفتاح API من ملف .env
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

def get_pdf_text(pdf_docs):
    text = ""
    # يُتوقع أن تكون pdf_docs قائمة بملفات UplodedFile
    for pdf in pdf_docs:
        # يجب تمرير الملف كـ binary/bytes
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            if page.extract_text():
                text += page.extract_text()
    return text

def create_vector_db(text_content):
    # تقسيم النص إلى أجزاء صغيرة
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_text(text_content)
    
    # تحويل النصوص إلى أرقام (Embeddings) باستخدام Gemini
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # إنشاء قاعدة البيانات المتجهية
    vector_store = FAISS.from_texts(chunks, embedding=embeddings)
    return vector_store

def get_relevant_context(vector_store, query):
    # استرجاع النصوص الأكثر صلة بالاستفسار
    docs = vector_store.similarity_search(query)
    return " ".join([d.page_content for d in docs])