# AI_assistant_for_finance

This repository depends on Google Gemini API to provide intelligent output. You need to add API key in helper_functions.py file. The program will run even if the key is not provided but the output will be generic


Steps to Run The Code(python3 should be installed on the system)

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
   <img width="1448" height="756" alt="First_page" src="https://github.com/user-attachments/assets/d3d5cc10-7bef-4efd-925f-22365a192e8b" />





7. After entering the name it will redirect to below main page-
    <img width="1452" height="784" alt="chat_start_page" src="https://github.com/user-attachments/assets/849d8252-8a24-4aed-a579-4fa175d14d07" />



8. You can chat with the assistant or send voice message to get responses 
    <img width="954" height="748" alt="Screenshot 2025-08-28 at 11 11 27 AM" src="https://github.com/user-attachments/assets/e1b3559b-79e5-49eb-936d-a8127e29cd6e" />
    <img width="1296" height="711" alt="Screenshot 2025-08-28 at 11 13 56 AM" src="https://github.com/user-attachments/assets/ba064479-48c2-43df-bd6e-7b54c70138dd" />




9. If your message or voice contains gold keyword, it will provides nudge and button to buy digital gold
    <img width="1277" height="764" alt="Screenshot 2025-08-28 at 11 11 47 AM" src="https://github.com/user-attachments/assets/743315ca-2eae-4df0-b1c3-a884ffca397a" />



10. When you click on Buy-digital-gold, it will redirect to new page to buy digital gold-
    <img width="1367" height="683" alt="Screenshot 2025-08-28 at 12 39 31 PM" src="https://github.com/user-attachments/assets/22408e30-6b22-4e4a-a679-f34a9a5c9cfe" />




# Future Updates-

1. Multiple user can chat at same time. Tracking the user using userid and saving the chat history in SQL database.
   
2. Redis caching for providing fast answers to repeated question.
   
3. Logging of  user purchase in SQL database.
4. updating current price of gold using API call to yahoo finance.
5. streaming of voice output to reduce the wait time for voice input.
6. Saving the voice_input in backend so that it can be streamed later.





