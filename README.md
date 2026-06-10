# AI-Chat-Application-with-OCR-and-Image-Text-Analysis-using-Streamlit-and-Ollama-
AI Chat Application built with Streamlit and Ollama that supports both text and image inputs. Integrated with OCR to extract and analyze text from images, enabling real-time intelligent conversations and multimodal interaction through a simple, user-friendly interface.


# 🧠 About the Project

This is an AI-powered Chat Application built with Streamlit and Ollama, designed to handle both text and image inputs.
It integrates OCR (Optical Character Recognition) to extract and analyze text from uploaded images, allowing users to interact with an AI chatbot that understands both written and image-based content.

The application provides a user-friendly interface and delivers real-time intelligent responses, making it suitable for learning, automation, content extraction, and research tasks.

# ⚙️ Features

💬 Real-time AI chat powered by Ollama

🖼️ OCR integration to extract text from images

⚡ Handles both text and image inputs

🧠 Intelligent, context-aware responses

🧩 Streamlit-based interactive web interface

# 🧰 Technologies Used

Python

Streamlit (UI)

Ollama LLaMA2 (AI model for intelligent responses)

Tesseract OCR / pytesseract (image text extraction)

Pillow (PIL)

# 🚀 Setup Instructions
1️⃣ Clone the Repository

git clone https://github.com/SaiKeerthiGade/AI-Chat-App-with-OCR-using-Streamlit-and-Ollama

cd AI-Chat-App-with-OCR-using-Streamlit-and-Ollama

2️⃣ Create and Activate Virtual Environment

python -m venv venv

 Windows

venv\Scripts\activate

4️⃣ Configure Tesseract Path (for OCR)

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

5️⃣ Run the Application

streamlit run OCR_AIapp.py


Open your browser and visit:
👉 http://localhost:8501

<img width="1913" height="879" alt="Screenshot 2025-10-02 164441" src="https://github.com/user-attachments/assets/3e0350f8-dbfc-41bb-aab0-bc5e040d3440" />


Image Analysis

<img width="1906" height="940" alt="Screenshot 2025-10-15 220450" src="https://github.com/user-attachments/assets/4966867c-7867-4e61-a365-e9ba7dc8d9ac" />



# 📌 Use Cases

Chat with AI for learning, coding assistance, or generating content

Extract and analyze text from images using OCR

Summarize or analyze content from PDF, CSV, or Text files

Debug or explain uploaded code snippets

Perform deep research queries using LLMs

# 🔮 Future Enhancements

Multi-language OCR support

Voice and speech integration

Cloud deployment with persistent chat sessions

# 👨 Author

Sai Keerthi Gade
