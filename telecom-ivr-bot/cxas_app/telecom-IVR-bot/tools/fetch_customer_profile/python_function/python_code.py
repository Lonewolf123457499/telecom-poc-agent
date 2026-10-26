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

"""fetch_customer_profile tool implementation."""


def fetch_customer_profile(clid: str = "") -> dict:
    """Fetch customer profile and account identification.

    Args:
        clid: 10-digit caller telephone number.

    Returns:
        dict: Identification and profile data with agent_action guidance.
    """
    context.variables["identification_status"] = "Pass"
    context.variables["auth_state"] = "Identified"
    if clid:
        context.variables["clid"] = clid

    # Deterministic mock branch for offline evaluation
    if clid == "5559876543":
        context.variables["business_flag"] = "true"
        context.variables["cirn"] = "CRN-3341"
        context.variables["billing_account"] = "BUS-774411"
        return {
            "identification_status": "Pass",
            "customer_type": "Existing",
            "business_flag": "true",
            "is_prepaid": "false",
            "region": "Region-A",
            "cirn": "CRN-3341",
            "billing_account": "BUS-774411",
            "agent_action": "Business account detected. Hand over immediately per business_handoff protocol.",
        }

    if clid == "5554443322":
        return {
            "identification_status": "Pass",
            "customer_type": "Existing",
            "business_flag": "false",
            "is_prepaid": "false",
            "region": "Region-B",
            "cirn": "CRN-1102",
            "billing_account": "ACC-552211",
            "service_status": "suspended",
            "balance_owed": "85.50",
            "agent_action": "Account suspended for non-payment. Direct to balance clearance before restoring.",
        }

    # Default consumer profile
    return {
        "identification_status": "Pass",
        "customer_type": "Existing",
        "business_flag": "false",
        "is_prepaid": "false",
        "region": "Region-A",
        "cirn": "CRN-8821",
        "billing_account": "ACC-992144",
        "agent_action": "Caller profile retrieved. Proceed with authentication ladder.",
    }
