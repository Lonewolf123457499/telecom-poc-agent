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

"""validate_authentication_otp tool implementation."""


def validate_authentication_otp(code: str = "") -> dict:
    """Validates the customer-provided OTP code.

    Args:
        code: 6-digit OTP passcode string.

    Returns:
        dict: Authentication result and remaining retry count.
    """
    clean_code = code.replace(" ", "").replace("-", "")
    if clean_code in ("000000", "999999", "invalid"):
        fail_count = int(context.variables.get("otp_fail_count", 0)) + 1
        context.variables["otp_fail_count"] = fail_count
        context.variables["auth_status"] = "Fail"

        if fail_count >= 3:
            tools.execute_live_agent_handover(reason="auth_failure_handoff")
            return {
                "auth_status": "Fail",
                "attempts_remaining": 0,
                "error": "MAX_ATTEMPTS_EXCEEDED",
                "message": "Maximum OTP verification attempts exceeded.",
                "agent_action": "Emit verbatim live_agent_handoff line and escalate with reason auth_failure_handoff.",
            }

        return {
            "auth_status": "Fail",
            "attempts_remaining": max(0, 3 - fail_count),
            "error": "INVALID_OTP",
            "message": "The code entered did not match.",
            "agent_action": "Inform customer code is incorrect, prompt to re-enter.",
        }

    context.variables["otp_fail_count"] = 0

    context.variables["auth_status"] = "Pass"
    context.variables["auth_state"] = "Authenticated"
    context.variables["_just_authenticated"] = "true"
    return {
        "auth_status": "Pass",
        "auth_state": "Authenticated",
        "attempts_remaining": 3,
        "message": "Authentication successful.",
        "agent_action": "Caller identity verified. Proceed to authorized customer intent.",
    }
