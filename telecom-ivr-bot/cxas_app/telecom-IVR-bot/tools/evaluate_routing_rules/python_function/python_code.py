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

"""evaluate_routing_rules tool implementation."""


def evaluate_routing_rules(utterance: str = "") -> dict:
    """Classifies user utterance into target module route and auth level.

    Args:
        utterance: Raw or processed caller text.

    Returns:
        dict: Target route module, confidence score, and auth requirement.
    """
    text = utterance.lower()

    if any(k in text for k in ["bill", "charge", "refund", "autopay", "payment", "dispute"]):
        return {
            "route": "Billing_Agent",
            "confidence": 0.95,
            "requires_auth": True,
            "agent_action": "Route the caller to Billing_Agent.",
        }

    if any(k in text for k in ["internet", "tv", "signal", "down", "outage", "wifi", "repair"]):
        return {
            "route": "Tech_Support_Agent",
            "confidence": 0.95,
            "requires_auth": True,
            "agent_action": "Route the caller to Tech_Support_Agent.",
        }

    if any(k in text for k in ["new plan", "add tv", "buy", "order", "upgrade", "warranty"]):
        return {
            "route": "Sales_Agent",
            "confidence": 0.90,
            "requires_auth": False,
            "agent_action": "Route the caller to Sales_Agent.",
        }

    if any(k in text for k in ["appointment", "technician", "reschedule", "ticket status", "slot"]):
        return {
            "route": "Appointment_Agent",
            "confidence": 0.95,
            "requires_auth": True,
            "agent_action": "Route the caller to Appointment_Agent.",
        }

    if any(k in text for k in ["password", "mfa", "login", "fraud", "suspend", "restore", "account"]):
        return {
            "route": "Account_Agent",
            "confidence": 0.95,
            "requires_auth": True,
            "agent_action": "Route the caller to Account_Agent.",
        }

    return {
        "route": "Telecom_Assistant",
        "confidence": 0.50,
        "requires_auth": False,
        "agent_action": "Ask caller to clarify their request.",
    }
