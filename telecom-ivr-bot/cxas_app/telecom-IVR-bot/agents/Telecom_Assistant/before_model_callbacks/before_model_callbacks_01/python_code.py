# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""before_model_callback for Telecom_Assistant."""

import re
from typing import Iterator, Optional


def count_consecutive_no_input(contents: list, user_text: str = "") -> int:
    """Count consecutive trailing silence / no-input events in conversation history."""
    silence_pattern = r"no user activity detected for \d+ seconds"
    count = 0
    for content in reversed(contents):
        role = getattr(content, "role", "")
        if role == "user":
            texts = [getattr(p, "text", "") for p in getattr(content, "parts", []) if getattr(p, "text", None)]
            full_text = " ".join(texts)
            if re.search(silence_pattern, full_text, re.IGNORECASE):
                count += 1
            else:
                break
    if count == 0 and user_text and re.search(silence_pattern, user_text, re.IGNORECASE):
        count = 1
    return count


def get_disambig_strike(contents: list) -> int:
    """Determine the current disambiguation strike count from previous agent messages."""
    for content in reversed(contents):
        role = getattr(content, "role", "")
        if role == "model":
            texts = [getattr(p, "text", "") for p in getattr(content, "parts", []) if getattr(p, "text", None)]
            full_text = " ".join(texts)
            if "still didn't understand" in full_text:
                return 3
            elif "didn't quite understand" in full_text:
                return 2
            else:
                return 1
    return 1


def get_reversed_agent_messages(contents: list) -> Iterator[str]:
    """Yield previous agent messages in reverse chronological order."""
    for content in reversed(contents):
        texts = []
        for part in getattr(content, "parts", []):
            if getattr(content, "role", "") == "model" and getattr(part, "text", None) is not None:
                texts.append(part.text)
        if texts:
            yield "".join(texts)


def extract_clid_from_contents(contents: list) -> Optional[str]:
    """Scan previous user messages in conversation history for phone number or account number."""
    for content in contents:
        if getattr(content, "role", "") == "user":
            for part in getattr(content, "parts", []):
                t = getattr(part, "text", "") or ""
                if t:
                    m = re.search(r'\b\d{10}\b|\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b', t)
                    if m:
                        return m.group(0).replace("-", "").replace(".", "").replace(" ", "")
                    a = re.search(r'\bacc-\d+\b|\bcrn-\d+\b', t, re.IGNORECASE)
                    if a:
                        return a.group(0)
    return None


def classify_target_agent(text: str) -> Optional[str]:
    """Helper to classify utterance into target specialist agent."""
    # Tech Support & Virtual Repair (M4)
    if any(k in text for k in ("internet is down", "down", "wifi", "outage", "no service", "tv says no signal", "signal", "repair", "troubleshoot", "slow", "modem", "router")):
        return "Tech_Support_Agent"
    # Billing & Payment (M3)
    if any(k in text for k in ("autopay", "bill", "billing", "payment", "pay", "charge", "dispute", "refund", "credit back", "deposit")):
        return "Billing_Agent"
    # Appointments (M6)
    if any(k in text for k in ("appointment", "technician", "schedule", "reschedule", "book a technician", "ticket")):
        return "Appointment_Agent"
    # Account & Security (M7)
    if any(k in text for k in ("mfa", "two-factor", "2fa", "suspend", "restore service", "cancel service", "port out")):
        return "Account_Agent"
    # Sales (M5)
    if any(k in text for k in ("warranty", "defective", "transfer my number", "port in", "new plan", "plan", "plans", "add tv", "upgrade", "buy phone", "shopping", "catalog", "new service", "packages", "package", "offer", "offers", "pricing")):
        return "Sales_Agent"
    return None


def before_model_callback(callback_context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
    state = callback_context.state

    # 0. Restricted caller check (BR-TV-002)
    if state.get("clid") == "0000000000" or state.get("_action_trigger") == "restricted_caller_deflect":
        state["_action_trigger"] = ""
        return LlmResponse.from_parts(parts=[
            Part.from_text(text="We are unable to process calls from this number at this time. Goodbye."),
            Part.from_function_call(name="end_session", args={"session_escalated": False, "reason": "restricted_caller"}),
        ])

    # 1. Deterministic opening greeting + verbatim recording notice (BR-TV-001)
    for part in callback_context.get_last_user_input():
        if part.text in ("<event>session start</event>", "<event>welcome</event>", "<event>welcome</event>\n"):
            opening = (
                "Welcome to Telco. I can help with billing, technical support, or managing your account. "
                "To get started, could you tell me the phone number or account number associated with your service? "
                "This call may be recorded for quality and training purposes."
            )
            return LlmResponse.from_parts(parts=[
                Part.from_text(text=opening),
            ])

    # Extract user input string
    user_text = " ".join(
        p.text.lower().strip() for p in callback_context.get_last_user_input() if p.text
    )

    # 2. Silence / No-input accounting (BR-TV-006)
    no_input_count = count_consecutive_no_input(llm_request.contents, user_text)
    if no_input_count > 0:
        state["local_noinput_counter"] = no_input_count

        if no_input_count < 3:
            reversed_msgs = get_reversed_agent_messages(llm_request.contents)
            last_msg = next(reversed_msgs, "How can I help you today?")
            while last_msg.startswith("I didn't hear anything. "):
                last_msg = last_msg[len("I didn't hear anything. "):]
            return LlmResponse.from_parts(parts=[
                Part.from_text(text=f"I didn't hear anything. {last_msg}"),
            ])
        else:
            return LlmResponse.from_parts(parts=[
                Part.from_text(text="I'll connect you to a representative who can help. Please hold."),
                Part.from_function_call(name="execute_live_agent_handover", args={"reason": "no_input_escalation"}),
                Part.from_function_call(name="end_session", args={"session_escalated": True, "reason": "no_input_escalation"}),
            ])
    else:
        state["local_noinput_counter"] = 0

    # 1b. Deterministic auth routing: a specialist bounced an unauthenticated caller back to us.
    if state.get("_needs_auth") == "true":
        state["_needs_auth"] = ""
        if state.get("auth_status") != "Pass":
            return LlmResponse.from_parts(parts=[
                Part.from_text(text="Before I can help with that, I need to verify your identity."),
                Part.from_agent_transfer(agent="Auth_Agent"),
            ])

    # 1c. Deterministic handoff upon returning from Auth_Agent
    if state.get("auth_status") == "Pass" or state.get("auth_state") == "Authenticated":
        target = state.get("_target_agent", "")
        if target:
            state["_target_agent"] = ""
            return LlmResponse.from_parts(parts=[
                Part.from_agent_transfer(agent=target),
            ])
        if state.get("_just_authenticated") == "true":
            state["_just_authenticated"] = ""
            return LlmResponse.from_parts(parts=[
                Part.from_text(text="Thank you, your identity has been verified. What can I help you with today?"),
            ])

    # --- Module M2: Authentication & Identity State Machine ---
    # Recover clid and Identified state if previously provided in conversation history
    if not state.get("clid"):
        prior_clid = extract_clid_from_contents(llm_request.contents)
        if prior_clid:
            state["clid"] = prior_clid
            state["auth_state"] = "Identified"
            state["identification_status"] = "Pass"

    # BR-TV-001 turn 2: Verbatim recording notice repetition when asked
    if any(q in user_text for q in ("recording", "recorded")):
        return LlmResponse.from_parts(parts=[
            Part.from_text(text="This call may be recorded for quality and training purposes."),
        ])

    # Transition: Explicit live agent request (no auth required, escalate immediately)
    live_agent = (
        "live agent", "representative", "human", "person", "talk to an agent",
        "speak to an agent", "speak with an agent", "talk to a person", "talk to a human",
        "speak to a person", "speak to a human", "connect me to an agent", "operator",
        "customer service rep", "real person"
    )
    if any(k in user_text for k in live_agent) or state.get("_action_trigger") == "user_requested_agent":
        state["_action_trigger"] = ""
        return LlmResponse.from_parts(parts=[
            Part.from_text(text="I'll connect you to a representative who can help. Please hold."),
            Part.from_function_call(name="execute_live_agent_handover", args={"reason": "user_requested_agent"}),
            Part.from_function_call(name="end_session", args={"session_escalated": True, "reason": "user_requested_agent"}),
        ])

    # BR-TV-012: Business account handoff
    if state.get("business_flag") == "true" or any(k in user_text for k in ("business phone", "business line", "business account", "business")):
        return LlmResponse.from_parts(parts=[
            Part.from_text(text="To get you the best support for your business account, I'll transfer you to an agent. You'll need to use your phone keypad instead of talking to the virtual assistant. Just a moment while I connect you."),
            Part.from_function_call(name="execute_live_agent_handover", args={"reason": "business_handoff"}),
            Part.from_function_call(name="end_session", args={"session_escalated": True}),
        ])

    # Transition: Explicit fraud claim -> Escalate fraud_escalation (NO auth attempt) with verbatim empathy line
    fraud = ("fraud", "unauthorized", "unauthorised", "someone used my account", "hacked", "stolen", "scam")
    if any(k in user_text for k in fraud):
        return LlmResponse.from_parts(parts=[
            Part.from_text(text="I'm very sorry to hear that you are facing challenges. I will ensure we handle your request with the utmost care."),
            Part.from_function_call(name="execute_live_agent_handover", args={"reason": "fraud_escalation"}),
            Part.from_function_call(name="end_session", args={"session_escalated": True}),
        ])

    # Transition: Caller provides phone number or account# in utterance -> Resolve to Identified
    phone_match = re.search(r'\b\d{10}\b|\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b', user_text)
    acct_match = re.search(r'\bacc-\d+\b|\bcrn-\d+\b', user_text)
    identified_in_this_turn = False
    if phone_match or acct_match:
        state["no_match_confirmation_count"] = 0
        extracted = phone_match.group(0).replace("-", "").replace(".", "").replace(" ", "") if phone_match else acct_match.group(0)
        try:
            profile = tools.fetch_customer_profile(clid=extracted)
            state["auth_state"] = "Identified"
            state["identification_status"] = "Pass"
            state["clid"] = extracted
            identified_in_this_turn = True
        except Exception:
            state["auth_state"] = "Identified"
            state["identification_status"] = "Pass"
            state["clid"] = extracted
            identified_in_this_turn = True

    # If caller ONLY provided phone number or account# to identify themselves without an intent:
    if identified_in_this_turn:
        cleaned = user_text
        if phone_match:
            cleaned = cleaned.replace(phone_match.group(0), "")
        if acct_match:
            cleaned = cleaned.replace(acct_match.group(0), "")
        filler_words = {
            "my", "phone", "number", "is", "it's", "its", "it", "account",
            "here", "hello", "hi", "hey", "the", "num", "no", "yes", "and", "a", "service"
        }
        remaining_words = [w for w in re.findall(r'[a-zA-Z0-9]+', cleaned) if w not in filler_words]
        if not remaining_words:
            return LlmResponse.from_parts(parts=[
                Part.from_text(text="Thank you. How can I help you today?"),
            ])

    auth_state = state.get("auth_state", "Guest")
    auth_status = state.get("auth_status", "")

    # Transition: Forgot password / reset login proceeds at Identified (see M2), route to Account_Agent
    forgot_password = ("forgot my password", "forgot password", "forgot my login",
                       "reset my password", "reset password", "reset login",
                       "reset my login", "can't log in", "cannot log in")
    if any(k in user_text for k in forgot_password):
        state["no_match_confirmation_count"] = 0
        return LlmResponse.from_parts(parts=[
            Part.from_text(text="I can help you reset your password. Let me connect you with account services."),
            Part.from_agent_transfer(agent="Account_Agent"),
        ])

    # Transition: Sales and general questions may proceed at Identified (M5)
    sales = ("plan", "plans", "new plan", "add tv", "upgrade", "buy phone", "shopping", "catalog", "new service", "packages", "package", "offer", "offers", "pricing")
    tech_billing_keywords = ("down", "outage", "slow", "broken", "repair", "bill", "pay", "charge", "dispute", "autopay")
    if any(k in user_text for k in sales) and not any(k in user_text for k in tech_billing_keywords):
        state["no_match_confirmation_count"] = 0
        return LlmResponse.from_parts(parts=[
            Part.from_agent_transfer(agent="Sales_Agent"),
        ])

    # Transition: If caller is Authenticated, route immediately
    if auth_status == "Pass" or auth_state == "Authenticated":
        target = classify_target_agent(user_text)
        if target:
            state["no_match_confirmation_count"] = 0
            return LlmResponse.from_parts(parts=[
                Part.from_agent_transfer(agent=target),
            ])

    # Transition: Caller needs authentication or intent disambiguation
    greeting_words = {"hi", "hello", "hey", "good", "morning", "afternoon", "evening",
                      "there", "yes", "yeah", "ok", "okay", "thanks", "thank", "you"}
    stripped = "".join(c if c.isalnum() or c == " " else " " for c in user_text).split()
    is_greeting_only = bool(stripped) and all(w in greeting_words for w in stripped)
    is_system_text = user_text.startswith("<")

    if user_text and not is_system_text and not is_greeting_only:
        # Check if caller matches a known specialist intent
        target = classify_target_agent(user_text)

        if auth_state == "Guest" and not state.get("clid"):
            if target:
                state["no_match_confirmation_count"] = 0
                return LlmResponse.from_parts(parts=[
                    Part.from_text(text="I can certainly help with that. To get started, could you tell me the phone number or account number associated with your service?"),
                ])
            else:
                # Disambiguation / No-match strike on Guest state (BR-TV-006)
                strike = get_disambig_strike(llm_request.contents)
                state["no_match_confirmation_count"] = strike
                if strike < 3:
                    if strike == 1:
                        reprompt = "I didn't quite understand that. To get started, could you tell me the phone number or account number associated with your service?"
                    else:
                        reprompt = "I'm sorry, I still didn't understand. Could you please tell me your 10-digit phone number or account number?"
                    return LlmResponse.from_parts(parts=[
                        Part.from_text(text=reprompt),
                    ])
                else:
                    return LlmResponse.from_parts(parts=[
                        Part.from_text(text="I'll connect you to a representative who can help. Please hold."),
                        Part.from_function_call(name="execute_live_agent_handover", args={"reason": "disambig_max_attempts"}),
                        Part.from_function_call(name="end_session", args={"session_escalated": True, "reason": "disambig_max_attempts"}),
                    ])

        # If Identified:
        if target:
            state["no_match_confirmation_count"] = 0
            state["_target_agent"] = target
            return LlmResponse.from_parts(parts=[
                Part.from_text(text="Before I can help with that, I need to verify your identity."),
                Part.from_agent_transfer(agent="Auth_Agent"),
            ])
        else:
            # Disambiguation / No-match strike on Identified state (BR-TV-006)
            strike = get_disambig_strike(llm_request.contents)
            state["no_match_confirmation_count"] = strike
            if strike < 3:
                if strike == 1:
                    reprompt = "I didn't quite understand that. I can help with billing, technical support, or managing your account. How can I help you today?"
                else:
                    reprompt = "I'm sorry, I still didn't understand. Could you please specify whether you need help with billing, technical support, or managing your account?"
                return LlmResponse.from_parts(parts=[
                    Part.from_text(text=reprompt),
                ])
            else:
                return LlmResponse.from_parts(parts=[
                    Part.from_text(text="I'll connect you to a representative who can help. Please hold."),
                    Part.from_function_call(name="execute_live_agent_handover", args={"reason": "disambig_max_attempts"}),
                    Part.from_function_call(name="end_session", args={"session_escalated": True, "reason": "disambig_max_attempts"}),
                ])

    # 4. Trigger pattern for deterministic live agent escalation
    trigger = state.get("_action_trigger", "")
    if trigger == "user_requested_agent":
        state["_action_trigger"] = ""
        return LlmResponse.from_parts(parts=[
            Part.from_text(text="I'll connect you to a representative who can help. Please hold."),
            Part.from_function_call(name="execute_live_agent_handover", args={"reason": "user_requested_agent"}),
            Part.from_function_call(name="end_session", args={"session_escalated": True, "reason": "user_requested_agent"}),
        ])
    elif trigger == "malicious_input":
        state["_action_trigger"] = ""
        return LlmResponse.from_parts(parts=[
            Part.from_text(text="Thank you for calling Telco. Have a pleasant day. Goodbye."),
            Part.from_function_call(name="end_session", args={"session_escalated": False, "reason": "malicious_input"}),
        ])

    return None
