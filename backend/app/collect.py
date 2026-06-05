"""
Run a single collector manually.
Usage: python -m app.collect <provider_id>
"""

import sys
from app.database import get_supabase
from app.collectors import REGISTRY


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m app.collect <provider_id>")
        print(f"Available: {', '.join(REGISTRY.keys())}")
        sys.exit(1)

    pid = sys.argv[1]
    CollectorClass = REGISTRY.get(pid)
    if not CollectorClass:
        print(f"Unknown provider: {pid}")
        print(f"Available: {', '.join(REGISTRY.keys())}")
        sys.exit(1)

    supabase = get_supabase()
    collector = CollectorClass(supabase)
    count = collector.run()
    print(f"✅ {pid}: {count} models collected")


if __name__ == "__main__":
    main()
