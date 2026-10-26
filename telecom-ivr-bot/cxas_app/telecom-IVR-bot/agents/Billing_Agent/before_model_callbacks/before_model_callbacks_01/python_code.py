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

"""before_model_callback for Billing_Agent: deterministic authentication gate."""

from typing import Optional


def before_model_callback(callback_context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
    state = callback_context.state
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

    # Deterministic AUTH GATE: billing/payment/autopay requires a verified caller.
    if state.get("auth_status") != "Pass":
        state["_needs_auth"] = "true"
        return LlmResponse.from_parts(parts=[
            Part.from_agent_transfer(agent="Telecom_Assistant"),
        ])

    return None
