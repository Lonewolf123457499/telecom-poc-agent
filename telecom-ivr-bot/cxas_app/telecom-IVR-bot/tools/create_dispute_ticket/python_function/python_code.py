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

"""create_dispute_ticket tool implementation."""


def create_dispute_ticket(charge_id: str = "", reason: str = "", notes: str = "") -> dict:
    """Logs dispute or executes auto-credit for disputed charge.

    Args:
        charge_id: Disputed charge identifier.
        reason: Justification reason.
        notes: Context notes.

    Returns:
        dict: Ticket ID, resolution timeline, or credit confirmation.
    """
    return {
        "status": "success",
        "ticket_id": "DISP-9921",
        "adjusted_amount": "12.50",
        "eta_business_days": 2,
        "is_auto_credited": True,
        "agent_action": "Emit verbatim refund_confirmation_pattern: Your refund of $12.50 will appear on your next statement within 2 business days.",
    }
