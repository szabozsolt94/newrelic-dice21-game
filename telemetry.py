import newrelic.agent

def track_event(event_name, **attributes):
    print(f"[EVENT] {event_name}: {attributes}")

    try:
        newrelic.agent.record_custom_event(
            event_name,
            attributes
        )
    except Exception as e:
        print(f"New Relic error: {e}")