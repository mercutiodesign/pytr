import _csv
import csv
import pathlib
from typing import Any

import pytr.event
from pytr_export import sort_events


def write_event(writer: "_csv.Writer", event: dict[str, Any], parsed: pytr.event.Event):
    date = event["timestamp"][:10]

    value = round(event["amount"]["value"], 2)
    parts = [event.get(k) for k in ("title", "subtitle") if event.get(k)]

    # add reference to incoming / outgoing transfers
    for section in event.get("details", {}).get("sections", []):
        if section.get("type") == "table":
            for r in section.get("data", []):
                if r.get("title") in {"IBAN", "Referenz"}:
                    parts.append(r.get("detail", {}).get("text"))

    if parsed.note in ("card_successful_transaction", "card_refund"):
        parts.append("Kartentransaktion")

    match parsed.event_type:
        case pytr.event.ConditionalEventType.PRIVATE_MARKETS_ORDER:
            parts.append("Private Markets Order")
        case pytr.event.ConditionalEventType.TRADE_INVOICE:
            parts.append("Trade Invoice")

        case pytr.event.ConditionalEventType.SAVEBACK:
            # generate incoming amount for saveback
            writer.writerow([date, " | ".join(parts + ["Earned"]), str(-value)])

    writer.writerow([date, " | ".join(parts), str(value)])


def main():
    root = pathlib.Path(__file__).parent.parent.parent

    cut_off = max(root.glob("archive-*.csv")).stem[-10:]
    print(f"{cut_off=}")

    # f"{title} {subtitle} ({event_dict['id']})"
    new_events = [
        (c, pytr.event.Event.from_dict(c))
        for c in sort_events.sort_events()["all_events.json"]
        if c.get("status", "").upper() != "CANCELED"
        and c.get("amount", {}).get("value")
        and c["timestamp"][:10] > cut_off
    ]

    for c, e in new_events:
        if e.event_type:
            c["eventType"] = e.event_type
        else:
            desc = {k: c[k] for k in ["title", "subtitle", "id"]}
            print(f"ignored event: {desc} -> {e}")

    if sorted_events := [r for r in new_events if r[1].event_type]:
        latest = sorted_events[0][0]["timestamp"][:10]
        target = root / f"archive-{latest}.csv"

        with open(target, "w") as fp:
            writer = csv.writer(fp, lineterminator="\n")

            writer.writerow(["Date", "Description", "Value"])
            for event, parsed in sorted_events:
                write_event(writer, event, parsed)
        print(f"wrote {target}")
    else:
        print(f"no additional relevant events > {cut_off}")


if __name__ == "__main__":
    main()
