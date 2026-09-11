import os
import json
import threading
import requests
from config.settings import AUTO_TRIGGER_SEVERITIES, SENTRYLOOP_INTERNAL_INVOKE_URL, SKIP_AUTO_TRIGGER_FOR, INTERNAL_TRIGGER_SECRET, MAX_TRIGGERS_PER_HOUR, COOLDOWN_MINUTES

def maybe_trigger_investigation(conn, service: str, severity: str, node_or_route: str | None, event_type: str = "", message: str = "", context: dict | None = None):

    if service in SKIP_AUTO_TRIGGER_FOR:
        return

    if severity not in AUTO_TRIGGER_SEVERITIES:
        return

    key = node_or_route or ""

    try:
        with conn.cursor() as cur:

            cur.execute(
                "SELECT COUNT(*) FROM trigger_locks WHERE created_at > NOW() - INTERVAL '1 hour'"
            )

            (recent_count,) = cur.fetchone()
            if recent_count >= MAX_TRIGGERS_PER_HOUR:
                print(f"[sentryloop_trigger] hit global cap ({recent_count}/hr), skipping {service}/{key}")
                return

            cur.execute(
                """
                DELETE FROM trigger_locks
                WHERE service = %s AND node_or_route = %s AND severity = %s
                  AND created_at < NOW() - (%s || ' minutes')::interval
                """,
                (service, key, severity, COOLDOWN_MINUTES),
            )

            cur.execute(
                """
                INSERT INTO trigger_locks (service, node_or_route, severity)
                VALUES (%s, %s, %s)
                ON CONFLICT (service, node_or_route, severity) DO NOTHING
                RETURNING id
                """,
                (service, key, severity),
            )
            got_lock = cur.fetchone() is not None
        conn.commit()
    except Exception as e:
        print(f"[sentryloop_trigger] lock check failed: {e}")
        return

    if not got_lock:
        return

    incident_text = _build_incident_text(service, severity, key, event_type, message, context)
    _fire_investigation(service, incident_text)


def _build_incident_text(service: str, severity: str, node_or_route: str, event_type: str, message: str, context: dict | None) -> str:

    lines = [
        "Automated error event detected in production.",
        f"Service: {service}",
        f"Severity logged: {severity}",
    ]

    if event_type:
        lines.append(f"Event type: {event_type}")

    if node_or_route:
        lines.append(f"Node/route: {node_or_route}")

    lines.append(f"Message: {message or '(no message provided)'}")

    if context:
        context_str = json.dumps(context)[:500]
        lines.append(f"Context: {context_str}")

    return "\n".join(lines)


def _fire_investigation(service: str, incident_text: str):
    def _send():
        try:
            requests.post(
                SENTRYLOOP_INTERNAL_INVOKE_URL,
                json={"incident": incident_text, "service": service},
                headers={"Authorization": f"Bearer {INTERNAL_TRIGGER_SECRET}"},
                timeout=5,
            )
            
        except Exception as e:
            print(f"[sentryloop_trigger] failed to reach sentryloop: {e}")

    threading.Thread(target=_send, daemon=True).start()