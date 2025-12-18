import json
import pathlib
from typing import Any


def sort_events() -> dict[str, list[Any]]:
    root = pathlib.Path(__file__).parent.parent.parent

    all_events: dict[str, list[Any]] = {}
    for path in sorted((root / "data").glob("*event*.json")):
        print("sorting", path.name)

        with path.open() as fp:
            events = sorted(json.load(fp), key=lambda c: (c["timestamp"], c["id"]), reverse=True)

        with path.open("w") as fp:
            json.dump(events, fp, ensure_ascii=False, indent=2)

        all_events[path.name] = events
    return all_events


if __name__ == "__main__":
    sort_events()
