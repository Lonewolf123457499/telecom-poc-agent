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

"""fetch_recent_bills tool implementation."""


def fetch_recent_bills(billing_account: str = "") -> dict:
    """Retrieves recent invoices and itemized charges.

    Args:
        billing_account: Billing account number.

    Returns:
        dict: Invoices and line items.
    """
    return {
        "status": "success",
        "bills": [
            {
                "id": "INV-1092",
                "date": "2026-10-01",
                "total_amount": "85.50",
                "line_items": [
                    {"charge_id": "CHG-101", "description": "High-Speed Internet", "amount": "73.00"},
                    {"charge_id": "CHG-102", "description": "AppleStreaming", "amount": "12.50"},
                ],
            }
        ],
        "auto_credit_limit": 25.00,
        "agent_action": "Check line items against customer dispute. Small-dollar charges <= $25.00 are auto-eligible for refund.",
    }
