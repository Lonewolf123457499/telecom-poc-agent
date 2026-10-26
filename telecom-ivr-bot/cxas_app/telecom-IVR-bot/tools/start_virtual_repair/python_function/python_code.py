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

"""start_virtual_repair tool implementation."""


def start_virtual_repair(cirn: str = "", lob: str = "", symptom: str = "") -> dict:
    """Starts diagnostic virtual repair workflow.

    Args:
        cirn: Customer reference number.
        lob: Line of business.
        symptom: Reported technical issue symptom.

    Returns:
        dict: Session token, diagnostic query, and recommended troubleshooting steps.
    """
    return {
        "status": "success",
        "session_id": "VR-5521",
        "symptom": symptom,
        "first_diagnostic_question": "Can you check if the power and status lights on your receiver box are solid green or blinking?",
        "step_count": 3,
        "requires_sms": True,
        "agent_action": "Troubleshooting has >2 sequential steps. Offer SMS-delivered steps first to avoid cognitive overload.",
    }
