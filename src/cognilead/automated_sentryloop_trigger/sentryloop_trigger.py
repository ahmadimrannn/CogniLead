import logging
import requests
from config.settings import AUTO_TRIGGER_SEVERITIES, COOLDOWN_MINUTES, SENTRYLOOP_INVOKE_URL

def maybe_trigger_investigation(conn, service: str, severity: str, route: str | None):
    """
    Call this right after an event row is committed to the events table.
    Decides if this event should start an investigation, and if so, starts it.
    Never raises, a broken trigger should never break normal error logging.
    """
    if severity not in AUTO_TRIGGER_SEVERITIES:
        return

    route_key = route or ""

    try:
        with conn.cursor() as cur:
            # throw away any lock for this exact signature that's expired
            cur.execute(
                """
                DELETE FROM trigger_locks
                WHERE service = %s AND route = %s AND severity = %s
                  AND created_at < NOW() - (%s || ' minutes')::interval
                """,
                (service, route_key, severity, COOLDOWN_MINUTES),
            )

            cur.execute(
                """
                INSERT INTO trigger_locks (service, route, severity)
                VALUES (%s, %s, %s)
                ON CONFLICT (service, route, severity) DO NOTHING
                RETURNING id
                """,
                (service, route_key, severity),
            )
            got_lock = cur.fetchone() is not None
        conn.commit()
    except Exception:
        logging.exception("trigger lock check failed, skipping auto-trigger")
        return

    if not got_lock:
        return

    _fire_investigation(service, severity, route)


def _fire_investigation_from_vercel(service, severity, route):
    try:
        requests.post(
            SENTRYLOOP_INVOKE_URL,
            json={"service": service, "severity": severity, "route": route},
            timeout=3,  # keeping it tight because it adds to the latency
        )
    except Exception:
        logging.exception("failed to reach sentryloop invoke endpoint")


_fire_investigation = _fire_investigation_from_vercel