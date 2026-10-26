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

"""set_session_state tool implementation."""


def set_session_state(key: str = "", value: str = "") -> dict:
    """Sets a session variable in runtime conversation state.

    Args:
        key: Variable name.
        value: Variable value.

    Returns:
        dict: Confirmation of state update.
    """
    if key:
        context.variables[key] = value
    return {
        "success": True,
        "key": key,
        "value": value,
        "agent_action": f"Session variable '{key}' updated to '{value}'.",
    }
