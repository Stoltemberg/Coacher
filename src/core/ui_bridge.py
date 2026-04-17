import json
import re
import sys
from typing import Any


_JS_NAME_RE = re.compile(r"^[A-Za-z_$][A-Za-z0-9_$]*(?:\.[A-Za-z_$][A-Za-z0-9_$]*)*$")
_FAILURE_MESSAGES: dict[str, str] = {}


def is_safe_js_function_name(function_name: str) -> bool:
    """Return True when the name is a valid dotted JS identifier path."""
    return bool(function_name) and bool(_JS_NAME_RE.fullmatch(function_name))


def js_stringify(value: Any) -> str:
    """
    Serialize a Python value into a JavaScript expression safely.

    We rely on JSON encoding because it is valid JavaScript for the primitive
    and container types we pass to the UI bridge.
    """
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def build_js_call(function_name: str, *args: Any) -> str:
    """
    Build a JavaScript function call from pre-serialized JSON-safe arguments.

    The function name is restricted to dotted identifier paths to avoid
    injection through the call target itself.
    """
    if not is_safe_js_function_name(function_name):
        raise ValueError(f"Unsafe JavaScript function name: {function_name!r}")

    serialized_args = ", ".join(js_stringify(arg) for arg in args)
    return f"{function_name}({serialized_args})"


def evaluate_js_call(window: Any, function_name: str, *args: Any) -> bool:
    """
    Safely invoke a UI JavaScript function through pywebview.

    Returns True when the call was dispatched successfully, False when the
    window is missing or the call could not be sent.
    """
    if window is None:
        _report_bridge_failure(function_name, "window indisponível")
        return False

    try:
        js_code = build_js_call(function_name, *args)
        window.evaluate_js(js_code)
        _clear_bridge_failure(function_name)
        return True
    except Exception as exc:
        _report_bridge_failure(function_name, str(exc))
        return False


def _report_bridge_failure(function_name: str, message: str) -> None:
    previous = _FAILURE_MESSAGES.get(function_name)
    if previous == message:
        return

    _FAILURE_MESSAGES[function_name] = message
    print(
        f"[UI Bridge] Falha em {function_name}: {message}",
        file=sys.stderr,
    )


def _clear_bridge_failure(function_name: str) -> None:
    if function_name in _FAILURE_MESSAGES:
        print(
            f"[UI Bridge] Recuperado: {function_name}",
            file=sys.stderr,
        )
        _FAILURE_MESSAGES.pop(function_name, None)
