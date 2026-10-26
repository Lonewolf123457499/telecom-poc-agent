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

"""fetch_availability_slots tool implementation."""


def fetch_availability_slots(zip_code: str = "", service_type: str = "") -> dict:
    """Finds open technician service windows.

    Args:
        zip_code: Service location postal code.
        service_type: Installation or repair.

    Returns:
        dict: Curated list of 2-3 available appointment slots.
    """
    return {
        "status": "success",
        "slots": [
            {
                "slot_id": "SLOT-1",
                "date": "Thursday, October 22",
                "window": "8:00 AM to 12:00 PM",
                "technician_id": "TECH-104",
            },
            {
                "slot_id": "SLOT-2",
                "date": "Thursday, October 22",
                "window": "1:00 PM to 5:00 PM",
                "technician_id": "TECH-109",
            },
            {
                "slot_id": "SLOT-3",
                "date": "Friday, October 23",
                "window": "8:00 AM to 12:00 PM",
                "technician_id": "TECH-112",
            },
        ],
        "agent_action": "Present exactly 2-3 slots to caller. Ask caller to choose their preferred window.",
    }
