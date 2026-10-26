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

"""execute_live_agent_handover tool implementation."""


def execute_live_agent_handover(reason: str = "user_requested_agent", session_context: str = "") -> dict:
    """Dispatches call session to human escalation queue.

    Args:
        reason: Escalation reason code.
        session_context: Serialized session context or parameters.

    Returns:
        dict: Escalation routing ID and designated queue.
    """
    queue = "General_Support"
    action = "Emit verbatim live_agent_handoff: I'll connect you to a representative who can help. Please hold."

    if reason == "fraud_escalation":
        queue = "Fraud_Specialists_24_7"
        action = "Emit verbatim empathy_protocol: I'm very sorry to hear that you are facing challenges. I will ensure we handle your request with the utmost care."
    elif reason == "business_handoff":
        queue = "Commercial_Business_Queue"
        action = "Emit verbatim business_handoff: To get you the best support for your business account, I'll transfer you to an agent. You'll need to use your phone keypad instead of talking to the virtual assistant. Just a moment while I connect you."
    elif reason == "secondary_language_live_agent":
        queue = "Spanish_Language_Support"
        action = "Emit verbatim secondary_language_live_agent: Lo conectaré con un representante que pueda ayudarle. Por favor espere."
    elif "billing" in reason:
        queue = "Billing_Specialists"

    return {
        "status": "success",
        "handover_id": "HO-9912",
        "queue": queue,
        "reason": reason,
        "agent_action": action,
    }
