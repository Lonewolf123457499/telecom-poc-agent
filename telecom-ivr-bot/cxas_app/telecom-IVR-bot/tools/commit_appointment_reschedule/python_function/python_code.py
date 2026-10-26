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

"""commit_appointment_reschedule tool implementation."""


def commit_appointment_reschedule(appt_id: str = "", new_slot: str = "") -> dict:
    """Commits rescheduled technician appointment slot.

    Args:
        appt_id: Current appointment ID.
        new_slot: Chosen new slot window.

    Returns:
        dict: Confirmation status, scheduled date/time, and SMS dispatch status.
    """
    return {
        "status": "success",
        "confirmed": True,
        "appt_id": appt_id or "APT-8812",
        "new_date": "Thursday, October 22, between 8:00 AM and 12:00 PM",
        "sms_sent": True,
        "agent_action": "Confirm the new date/time back to caller and inform them an SMS confirmation has been sent.",
    }
