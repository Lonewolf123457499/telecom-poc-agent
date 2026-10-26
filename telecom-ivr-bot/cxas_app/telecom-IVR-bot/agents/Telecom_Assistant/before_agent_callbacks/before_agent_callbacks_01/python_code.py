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

"""before_agent_callback for Telecom_Assistant."""

from typing import Optional


def before_agent_callback(callback_context: CallbackContext) -> Optional[Content]:
    state = callback_context.state

    # Early return if identification already executed or caller identified
    if state.get("identification_status") or state.get("auth_state") in ("Identified", "Authenticated") or state.get("clid"):
        return None

    clid = state.get("clid", "")
    if not clid:
        state["auth_state"] = "Guest"
        state["customer_type"] = "Existing"
        state["business_flag"] = "false"
        state["region"] = "Region-A"
        return None

    # BR-TV-002: Restricted caller check
    blocked_clids = ["0000000000", "9999999999"]
    if clid in blocked_clids:
        state["_action_trigger"] = "restricted_caller_deflect"
        return None

    # Identify caller via profile lookup
    try:
        profile = tools.fetch_customer_profile(clid=clid)
        state["identification_status"] = profile.get("identification_status", "Pass")
        state["auth_state"] = "Identified"
        state["customer_type"] = profile.get("customer_type", "Existing")
        state["business_flag"] = profile.get("business_flag", "false")
        state["is_prepaid"] = profile.get("is_prepaid", "false")
        state["region"] = profile.get("region", "Region-A")
        if profile.get("cirn"):
            state["cirn"] = profile.get("cirn")
        if profile.get("billing_account"):
            state["billing_account"] = profile.get("billing_account")
    except Exception as e:
        state["identification_status"] = "Pass"
        state["auth_state"] = "Identified"
        state["business_flag"] = "false"
        state["region"] = "Region-A"

    return None
