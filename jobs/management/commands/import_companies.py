"""`python manage.py import_companies <file.csv>`: load startups from a CSV file (e.g. a Crunchbase export).

The CSV needs a header row with these columns (any order, any capitalisation, extra columns are ignored):
  name, website      required
  description, location, stage   optional

How each row is handled:
- Companies are matched by website. "https://www.acme.com/" and "http://acme.com" count as the same
  company. A match is updated; anything else creates a new company. Running the same file twice
  creates no duplicates.
- A blank cell never wipes out information we already have (it just leaves that field as it was).
- Rows with no name or no website are skipped. So is a row whose website is new but whose name already
  belongs to a different company (company names must be unique in our database).
- Stage accepts our labels ("Series A"), our codes ("series_a") and common Crunchbase wording
  ("Series C" -> Series B+, "Angel" -> Pre-seed). Anything else is left blank, with a note.

Everything happens in one database transaction: if something unexpected goes wrong halfway, nothing
from this run is kept. At the end it prints "Imported X, updated Y, unchanged Z, skipped N" and one line
per skipped row (with its row number as shown in Excel / Google Sheets, where the header is row 1).
"""

import csv
import re
from urllib.parse import urlsplit

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from jobs.models import Company

Stage = Company.Stage

REQUIRED_COLUMNS = ["name", "website"]
OPTIONAL_COLUMNS = ["description", "location", "stage"]
COPIED_FIELDS = ["name", "description", "location", "stage", "website"]


def normalise_website(url):
    """Turn a website into a key for matching: lowercase host, no scheme, no "www.", no trailing slash.

    "https://www.Acme.com/" and "http://acme.com" both become "acme.com". Returns "" for a blank value.
    """
    url = (url or "").strip()
    if not url:
        return ""
    if "://" not in url:
        url = "//" + url  # lets urlsplit find the host in "acme.com/jobs"
    parts = urlsplit(url)
    host = parts.netloc.lower()
    if host.startswith("www."):
        host = host[len("www."):]
    return host + parts.path.rstrip("/")


def clean_website(url):
    """The website as we store it: trimmed, with https:// added if the file left the scheme out."""
    url = url.strip()
    if "://" not in url:
        url = "https://" + url
    return url


def parse_stage(value):
    """Map a stage from the file to one of our Stage codes. Returns "" if blank or not recognised."""
    text = re.sub(r"[\s_\-]+", " ", (value or "").strip().lower())
    if not text:
        return ""
    if text in ("pre seed", "preseed", "angel"):
        return Stage.PRE_SEED
    if text == "seed":
        return Stage.SEED
    if re.match(r"series a\b", text):
        return Stage.SERIES_A
    if re.match(r"series [b-z]\b", text):  # Series B, B+, "b plus", C, D, ...
        return Stage.SERIES_B_PLUS
    return ""


class Command(BaseCommand):
    help = "Import companies from a CSV file (columns: name, website, description, location, stage)."

    def add_arguments(self, parser):
        parser.add_argument("csv_file", help="Path to the CSV file, e.g. jobs/sample_data/companies_sample.csv")

    def handle(self, *args, **options):
        path = options["csv_file"]
        try:
            # utf-8-sig quietly removes the invisible "BOM" marker that Excel puts at the start of CSV files.
            with open(path, newline="", encoding="utf-8-sig") as f:
                rows = list(csv.reader(f))
        except FileNotFoundError:
            raise CommandError(f"File not found: {path}")
        except UnicodeDecodeError:
            raise CommandError(
                f"Could not read {path}: it is not saved as UTF-8 text. "
                "In Excel use File > Save As > 'CSV UTF-8'; in Google Sheets use File > Download > CSV."
            )

        if not rows:
            raise CommandError(f"{path} is empty: expected a header row with at least: {', '.join(REQUIRED_COLUMNS)}.")

        # Find each column by its header, ignoring capitalisation and surrounding spaces.
        header = [h.strip().lower() for h in rows[0]]
        missing = [c for c in REQUIRED_COLUMNS if c not in header]
        if missing:
            raise CommandError(
                f"Missing required column(s): {', '.join(missing)}. Nothing was imported. "
                f"The header row must include: {', '.join(REQUIRED_COLUMNS)} "
                f"(optional: {', '.join(OPTIONAL_COLUMNS)}). Found: {', '.join(h for h in header if h) or 'nothing'}."
            )
        positions = {c: header.index(c) for c in REQUIRED_COLUMNS + OPTIONAL_COLUMNS if c in header}

        with transaction.atomic():
            counts, skipped, notes = self.import_rows(rows[1:], positions)

        for line in notes:
            self.stdout.write(self.style.WARNING(line))
        for line in skipped:
            self.stdout.write(self.style.WARNING(line))
        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {counts['created']}, updated {counts['updated']}, "
                f"unchanged {counts['unchanged']}, skipped {len(skipped)}."
            )
        )

    def import_rows(self, rows, positions):
        counts = {"created": 0, "updated": 0, "unchanged": 0}
        skipped, notes = [], []

        # Existing companies, looked up by normalised website and by name.
        by_website, names = {}, {}
        for company in Company.objects.order_by("id"):
            names[company.name] = company
            if company.website:
                by_website.setdefault(normalise_website(company.website), company)

        # Row 1 is the header, so the first company is row 2 (the same number Excel shows).
        for row_number, cells in enumerate(rows, start=2):
            values = {c: (cells[i].strip() if i < len(cells) else "") for c, i in positions.items()}
            if not any(cell.strip() for cell in cells):
                continue  # a completely empty line (common at the end of Excel exports)

            name, website = values["name"], values.get("website", "")
            if not name:
                skipped.append(f"Skipped row {row_number}: no name.")
                continue
            if not website:
                skipped.append(f"Skipped row {row_number} ({name}): no website.")
                continue

            raw_stage = values.get("stage", "")
            stage = parse_stage(raw_stage)
            if raw_stage and not stage:
                notes.append(f"Note: row {row_number} ({name}): stage '{raw_stage}' not recognised, left blank.")

            key = normalise_website(website)
            company = by_website.get(key)
            created = company is None

            owner = names.get(name)
            if owner is not None and (company is None or owner.pk != company.pk):
                if created:
                    reason = f"the name is already used by another company (website: {owner.website or 'none'})"
                else:
                    reason = f"this website belongs to '{company.name}', but the name '{name}' is already used by another company"
                skipped.append(f"Skipped row {row_number} ({name}): {reason}.")
                continue

            new_values = {
                "name": name,
                "description": values.get("description", ""),
                "location": values.get("location", ""),
                "stage": stage,
                "website": clean_website(website),
            }
            if created:
                company = Company()
            old_name = company.name
            changed = False
            for field in COPIED_FIELDS:
                if field == "website" and not created:
                    continue  # it already matches; keep the address as it was first saved
                value = new_values[field]
                if value and getattr(company, field) != value:  # blank cells never wipe existing data
                    setattr(company, field, value)
                    changed = True

            try:
                company.full_clean(validate_unique=False)  # checks lengths and that the website looks valid
            except ValidationError as error:
                problems = "; ".join(f"{field}: {' '.join(msgs)}" for field, msgs in error.message_dict.items())
                skipped.append(f"Skipped row {row_number} ({name}): {problems}")
                if not created:
                    company.refresh_from_db()  # undo the in-memory changes so later rows see the saved version
                continue

            if created:
                company.save()
                counts["created"] += 1
                by_website[key] = company
            elif changed:
                company.save()
                counts["updated"] += 1
                names.pop(old_name, None)
            else:
                counts["unchanged"] += 1
            names[company.name] = company

        return counts, skipped, notes
