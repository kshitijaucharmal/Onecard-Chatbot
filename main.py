import google.generativeai as genai
import json

# --- CONFIGURATION ---
# Replace with your actual API key
API_KEY = "AIzaSyBZ5Y1q67VztrSFtvlsExLQXUZxZUEIEeg"
genai.configure(api_key=API_KEY)

# Select the model (Gemini Pro is great for reasoning)
model = genai.GenerativeModel('gemini-2.5-pro')

# --- 1. THE KNOWLEDGE BASE (Simplified for Prototype) ---
# In a real app, this comes from your PostgreSQL database [cite: 17]
knowledge_base = {
    "late_fee": "For outstanding balance between ₹501 - ₹5,000, the Late Fee is ₹500. Above ₹5,000, it is ₹750.",
    "forex_markup": "International transactions attract a markup fee of 1% + GST.",
    "card_replacement": "Replacement of a lost metal card costs ₹3,000 + GST. Plastic card replacement is free.",
    "billing_cycle": "Your statement is generated on the 1st of every month. Payment is due by the 18th.",
}

# --- 2. MOCK APIs (The "Action" Layer) ---
# These simulate the backend systems "doing things" [cite: 18]

def api_get_balance(user_id):
    return {"status": "success", "balance": "₹14,500", "available_limit": "₹85,500"}


def api_block_card(user_id):
    return {"status": "success", "message": "Your card ending in 4455 has been temporarily blocked."}


def api_check_application_status(user_id):
    return {"status": "success", "stage": "KYC Verification", "est_completion": "24 hours"}


# --- 3. THE SYSTEM PROMPT (The "Brain") ---
# This instructs Gemini on how to behave, use the KB, and when to trigger JSON actions.
system_instruction = """
You are the 'OneCard GenAI Assistant'. You speak directly to the Cardholder (User).
Your goal is to be helpful, concise, and accurate.

CONTEXT (Use this to answer informational queries):
- Late Fees: {late_fee}
- Forex Fees: {forex_markup}
- Card Replacement Cost: {card_replacement}
- Billing Cycle: {billing_cycle}

INSTRUCTIONS:
1. If the user asks for information found in CONTEXT, answer naturally.
2. If the user wants to perform an ACTION (check balance, block card, check status), 
   return a JSON object with the 'intent'. Do not output conversational text for actions.
   
   Supported Intents: 
   - "GET_BALANCE"
   - "BLOCK_CARD" 
   - "CHECK_APP_STATUS"

EXAMPLES:
User: "How much does a new metal card cost?"
AI: "A replacement metal card costs ₹3,000 plus GST."

User: "Block my card."
AI: {{"intent": "BLOCK_CARD"}}
"""

# Inject the dynamic knowledge base into the prompt string
formatted_prompt = system_instruction.format(**knowledge_base)

# --- 4. THE CORE LOGIC ENGINE ---


def chat_with_assistant(user_input, user_id="user_123"):
    # Create the chat session
    chat = model.start_chat(history=[])

    # Send the System Instruction + User Input combined
    # (Note: In production, system instructions are handled differently, but this works for prototypes)
    full_prompt = f"{formatted_prompt}\n\nUser: {user_input}\nAI:"

    response = chat.send_message(full_prompt)
    response_text = response.text.strip()

    # --- DECISION TREE (Architecture Flow) ---

    # Check if the response is a JSON Action Trigger
    if "{" in response_text and "intent" in response_text:
        try:
            # Parse the JSON
            action_data = json.loads(response_text)
            intent = action_data.get("intent")

            # Route to the correct Mock API
            if intent == "GET_BALANCE":
                result = api_get_balance(user_id)
                return f"Current Balance: {result['balance']}. Available Limit: {result['available_limit']}"

            elif intent == "BLOCK_CARD":
                result = api_block_card(user_id)
                return f"Done. {result['message']}"

            elif intent == "CHECK_APP_STATUS":
                result = api_check_application_status(user_id)
                return f"Your application is currently in {result['stage']}. Estimated completion: {result['est_completion']}"

            else:
                return "I understood you want to take an action, but I'm not connected to that specific system yet."

        except json.JSONDecodeError:
            # Fallback if Gemini generated malformed JSON
            return "I tried to process your request but encountered a system error."

    else:
        # It's a normal informational answer
        return response_text


# --- 5. RUNNING THE DEMO ---
if __name__ == "__main__":
    print("--- OneCard GenAI Assistant Prototype ---")
    print("(Type 'quit' to exit)\n")

    while True:
        user_query = input("You: ")
        if user_query.lower() in ['quit', 'exit']:
            break

        bot_response = chat_with_assistant(user_query)
        print(f"Bot: {bot_response}\n")
