from datetime import datetime, timezone

def main():
    print("Hello from lead-qualifier-project!")
    # Get current UTC time
    now_utc = datetime.now(timezone.utc)

    # Format without microsecond precision and append 'Z'
    formatted = now_utc.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
    print(formatted)


if __name__ == "__main__":
    main()
