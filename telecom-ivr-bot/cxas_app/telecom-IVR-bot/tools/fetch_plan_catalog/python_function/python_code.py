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

"""fetch_plan_catalog tool implementation."""


def fetch_plan_catalog(lob: str = "tv", customer_type: str = "Existing") -> dict:
    """Retrieves curated plan options (strictly 2-3 plans).

    Args:
        lob: Line of business.
        customer_type: Existing or New customer.

    Returns:
        dict: Curated plan choices.
    """
    return {
        "status": "success",
        "plans": [
            {
                "id": "PLAN-TV-ESSENTIAL",
                "name": "Essential TV",
                "price": "$45.00 per month",
                "features": "80+ channels with Cloud DVR",
            },
            {
                "id": "PLAN-TV-PREMIER",
                "name": "Premier TV",
                "price": "$70.00 per month",
                "features": "180+ channels including premium sports and 4K streaming",
            },
        ],
        "agent_action": "Present exactly these 2 curated plans. Do not present additional plans to avoid analysis paralysis.",
    }
