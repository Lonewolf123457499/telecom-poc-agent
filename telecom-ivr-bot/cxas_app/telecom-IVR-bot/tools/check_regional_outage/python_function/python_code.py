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

"""check_regional_outage tool implementation."""


def check_regional_outage(region: str = "Region-A", lob: str = "tv") -> dict:
    """Checks for active network or equipment outages.

    Args:
        region: Service territory code.
        lob: Line of business.

    Returns:
        dict: Outage status and restoration ETA.
    """
    if region == "Region-C" or "outage" in lob.lower():
        return {
            "active": True,
            "restoration_eta_iso": "2026-10-20T16:00:00Z",
            "message": "Active outage detected in region.",
            "agent_action": "Emit verbatim outage_active copy: I see there's an active outage in your area. We're working on it. Would you like me to text you when it's restored?",
        }

    return {
        "active": False,
        "restoration_eta_iso": "",
        "message": "No active outages reported in this area.",
        "agent_action": "No regional outage. Disambiguate tv_sub_type before starting diagnostics.",
    }
