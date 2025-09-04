# 🌍 Smart Places Finder (AI Multi-Agent System)

An AI-powered location-based search app that demonstrates the use of **multi-agent collaboration** to solve real-world problems like finding nearby restaurants, cafes, or landmarks.  

Deployed App: [Streamlit Demo Link](https://nearmeai.streamlit.app/)  


---

## 📌 Problem Statement
Finding nearby places often requires manual searching on maps, switching between apps, and interpreting messy results.  
This project solves the problem by using **AI multi-agent systems** that collaborate to:
- Understand user queries (e.g., *"cafes near me"* or *"restaurants in Delhi"*).  
- Detect location (live GPS or mentioned city).  
- Search for relevant places using APIs.  
- Summarize results into clear, human-friendly responses.  

---

## 🤖 Why Multi-Agent AI?
Instead of a single AI doing everything, we break down the task into **specialized agents**:
1. **Location Extractor Agent** → Understands and extracts location from user query.  
2. **Geocoding Agent** → Converts city names into latitude/longitude.  
3. **Places Search Agent** → Calls Google Places API to fetch results.  
4. **Summarizer Agent** → Uses LLM to generate clear, bulleted summaries.  
5. **Orchestrator (Main Agent)** → Coordinates all agents to produce the final answer.  

This modular approach shows how agents can **operate independently** yet **collaborate effectively**.  

---

## 🛠️ Tools & Frameworks
- **Python, Streamlit** → UI & deployment  
- **LangChain** → Multi-agent orchestration (ReAct framework)  
- **Google Gemini (via LangChain)** → LLM for reasoning & summarization  
- **Google Places API** → Real-world place search  
- **Open-Meteo Geocoding API** → City → coordinates  
- **python-dotenv** → Secure API key handling  

---

## 🧠 LLM Selection
- **Ideal Choice**: Google Gemini 1.5 Pro (best reasoning + summarization).  
- **Free-tier Used**: Google Gemini 1.5 Flash (fast, efficient, free API).  
- **Alternative Options Considered**: GPT-3.5 (OpenAI), open-source models (Mistral, HuggingFace).  

Gemini Flash was chosen for **speed, zero-cost, and good integration with LangChain**.  

---

## 🚀 How It Works
1. User enters query → *“cafes near Jalandhar”*.  
2. Location Extractor Agent → Detects `"Jalandhar"`.  
3. Geocoding Agent → Finds `(31.3260, 75.5762)`.  
4. Places Search Agent → Fetches nearby cafes via Google Places API.  
5. Summarizer Agent → Converts JSON into a neat bulleted list.  
6. Orchestrator Agent → Combines everything into final user response.  

---

## 📷 Screenshots
![Demo Image 1](assets/demo1.png)

---

## ⚙️ Setup Instructions
1. Clone this repo  
   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd your-repo
Create a .env file

env
Copy code
GOOGLE_API_KEY=your_api_key_here
Install dependencies

bash
Copy code
pip install -r requirements.txt
Run locally

bash
Copy code
streamlit run app.py
