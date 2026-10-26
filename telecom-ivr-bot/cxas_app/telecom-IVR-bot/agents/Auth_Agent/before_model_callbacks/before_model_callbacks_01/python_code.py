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

"""before_model_callback for Auth_Agent: live agent & fraud escalation."""

import re
from typing import Optional


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


def before_model_callback(callback_context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
    state = callback_context.state

    # Recover clid if provided in previous turns
    if not state.get("clid"):
        prior_clid = extract_clid_from_contents(llm_request.contents)
        if prior_clid:
            state["clid"] = prior_clid
            state["auth_state"] = "Identified"
            state["identification_status"] = "Pass"

    user_text = " ".join(
        p.text.lower().strip() for p in callback_context.get_last_user_input() if p.text
    )

    # Universal Live Agent Escalation Handler
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

    # Fraud claims bypass authentication completely (PRD M2 / BR-TV-013)
    fraud = ("fraud", "unauthorized", "unauthorised", "someone used my account", "hacked", "stolen", "scam")
    if any(k in user_text for k in fraud):
        return LlmResponse.from_parts(parts=[
            Part.from_text(text="I'm very sorry to hear that you are facing challenges. I will ensure we handle your request with the utmost care."),
            Part.from_function_call(name="execute_live_agent_handover", args={"reason": "fraud_escalation"}),
            Part.from_function_call(name="end_session", args={"session_escalated": True, "reason": "fraud_escalation"}),
        ])

    return None
