# AI_assistant_for_finance

This repository depends on Google Gemini API to provide intelligent output. You need to add API key in helper_functions.py file. The program will run even if the key is not provided but the output will be generic


Steps to Run The Code

1. Create Virtual Environment
    - python3 -m venv .venv

2. Activate Virtual Environemnt
    - source .venv/bin/activate

3. Install all the required Library
    - pip install -r requirements.txt

4. Run FastAPI app
    - python -m uvicorn main:app --reload

5. open the local url provided in the cmd eg-
    - http://127.0.0.1:8000

6. you will get the following page on start-
   
<img width="1452" height="784" alt="chat_start_page" src="https://github.com/user-attachments/assets/849d8252-8a24-4aed-a579-4fa175d14d07" />


