"""Tests for `python manage.py import_companies <file.csv>` (issue #33). No network is used."""

import os
import tempfile
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase, TestCase

from .management.commands.import_companies import normalise_website, parse_stage
from .models import Company

SAMPLE_CSV = Path(__file__).parent / "sample_data" / "companies_sample.csv"
HEADER = "name,website,description,location,stage\n"


class ImportCompaniesTests(TestCase):
    def write_csv(self, text, encoding="utf-8"):
        f = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding=encoding, newline="")
        f.write(text)
        f.close()
        self.addCleanup(os.remove, f.name)
        return f.name

    def run_import(self, text=None, path=None, **write_kwargs):
        path = path or self.write_csv(text, **write_kwargs)
        out = StringIO()
        call_command("import_companies", path, stdout=out)
        return out.getvalue()

    # --- create / update / running twice ---

    def test_creates_companies_with_all_columns(self):
        output = self.run_import(HEADER + 'Acme Fake,https://acme.example.com,Rockets.,"Boston, MA",Seed\n')
        company = Company.objects.get(name="Acme Fake")
        self.assertEqual(company.website, "https://acme.example.com")
        self.assertEqual(company.description, "Rockets.")
        self.assertEqual(company.location, "Boston, MA")
        self.assertEqual(company.stage, Company.Stage.SEED)
        self.assertIn("Imported 1, updated 0, unchanged 0, skipped 0.", output)

    def test_adds_https_when_website_has_no_scheme(self):
        self.run_import(HEADER + "Acme Fake,acme.example.com,,,\n")
        self.assertEqual(Company.objects.get().website, "https://acme.example.com")

    def test_updates_company_matched_by_normalised_website(self):
        Company.objects.create(name="Acme Fake", website="https://www.acme.example.com/", location="Boston, MA")
        output = self.run_import(HEADER + "Acme Fake Inc,HTTP://Acme.Example.com,New description,,Series A\n")
        self.assertEqual(Company.objects.count(), 1)
        company = Company.objects.get()
        self.assertEqual(company.name, "Acme Fake Inc")
        self.assertEqual(company.description, "New description")
        self.assertEqual(company.stage, Company.Stage.SERIES_A)
        self.assertEqual(company.location, "Boston, MA")  # blank cell kept the old value
        self.assertEqual(company.website, "https://www.acme.example.com/")  # stored address unchanged
        self.assertIn("Imported 0, updated 1, unchanged 0, skipped 0.", output)

    def test_running_twice_creates_no_duplicates(self):
        first = self.run_import(path=str(SAMPLE_CSV))
        count = Company.objects.count()
        second = self.run_import(path=str(SAMPLE_CSV))
        self.assertEqual(Company.objects.count(), count)
        self.assertIn("Imported 6, updated 0, unchanged 0, skipped 2.", first)
        self.assertIn("Imported 0, updated 0, unchanged 6, skipped 2.", second)

    def test_same_website_twice_in_one_file_updates_instead_of_duplicating(self):
        output = self.run_import(
            HEADER + "Acme Fake,https://acme.example.com,,,Seed\nAcme Fake,www.acme.example.com/,,,Series A\n"
        )
        self.assertEqual(Company.objects.get().stage, Company.Stage.SERIES_A)
        self.assertIn("Imported 1, updated 1, unchanged 0, skipped 0.", output)

    def test_existing_companies_without_website_are_left_alone(self):
        Company.objects.create(name="Demo Co")  # like the demo data from `seed`
        self.run_import(HEADER + "Acme Fake,https://acme.example.com,,,\n")
        self.assertEqual(Company.objects.count(), 2)

    # --- skipped rows ---

    def test_skips_rows_missing_name_or_website_and_reports_them(self):
        output = self.run_import(
            HEADER
            + "Good Fake,https://good.example.com,,,\n"
            + ",https://noname.example.com,,,\n"
            + "No Site Fake,,,,\n"
        )
        self.assertEqual(list(Company.objects.values_list("name", flat=True)), ["Good Fake"])
        self.assertIn("Imported 1, updated 0, unchanged 0, skipped 2.", output)
        self.assertIn("Skipped row 3: no name.", output)
        self.assertIn("Skipped row 4 (No Site Fake): no website.", output)

    def test_skips_new_website_whose_name_belongs_to_another_company(self):
        Company.objects.create(name="Acme Fake", website="https://acme.example.com")
        output = self.run_import(HEADER + "Acme Fake,https://other.example.com,,,\n")
        self.assertEqual(Company.objects.count(), 1)
        self.assertEqual(Company.objects.get().website, "https://acme.example.com")
        self.assertIn("Skipped row 2 (Acme Fake): the name is already used by another company", output)
        self.assertIn("skipped 1.", output)

    def test_skips_rename_onto_a_name_another_company_uses(self):
        Company.objects.create(name="Acme Fake", website="https://acme.example.com")
        Company.objects.create(name="Beta Fake", website="https://beta.example.com")
        output = self.run_import(HEADER + "Beta Fake,https://acme.example.com,,,\n")
        self.assertEqual(Company.objects.get(website="https://acme.example.com").name, "Acme Fake")
        self.assertIn("Skipped row 2 (Beta Fake): this website belongs to 'Acme Fake'", output)

    def test_skips_websites_that_are_not_http_or_https(self):
        bad = [
            "javascript:alert(1)",
            "JavaScript:alert(document.cookie)",
            "ftp://files.example.com",
            "mailto:founder@example.com",
            "data:text/html,hello",
            "not a website",
            "https://",
        ]
        rows = "".join(f'Bad Fake {i},"{url}",,,\n' for i, url in enumerate(bad))
        output = self.run_import(HEADER + rows)
        self.assertFalse(Company.objects.exists())
        self.assertIn(f"skipped {len(bad)}.", output)
        self.assertIn("Skipped row 2 (Bad Fake 0): website 'javascript:alert(1)' is not a web address", output)
        self.assertIn("Skipped row 4 (Bad Fake 2): website 'ftp://files.example.com' is not a web address", output)

    def test_bad_website_never_overwrites_or_matches_existing_company(self):
        Company.objects.create(name="Acme Fake", website="https://acme.example.com")
        output = self.run_import(HEADER + "Acme Fake,javascript://acme.example.com,,,\n")
        self.assertEqual(Company.objects.get().website, "https://acme.example.com")
        self.assertIn("skipped 1.", output)

    def test_accepts_http_https_and_bare_addresses(self):
        self.run_import(
            HEADER
            + "One Fake,http://one.example.com,,,\n"
            + "Two Fake,HTTPS://Two.Example.com/about,,,\n"
            + "Three Fake,three.example.com,,,\n"
            + "Four Fake,four.example.com:8080,,,\n"
        )
        self.assertEqual(
            dict(Company.objects.values_list("name", "website")),
            {
                "One Fake": "http://one.example.com",
                "Two Fake": "HTTPS://Two.Example.com/about",
                "Three Fake": "https://three.example.com",
                "Four Fake": "https://four.example.com:8080",
            },
        )
        for company in Company.objects.all():
            self.assertTrue(company.website.lower().startswith(("http://", "https://")), company.website)

    def test_ignores_completely_blank_lines(self):
        output = self.run_import(HEADER + "Acme Fake,https://acme.example.com,,,\n,,,,\n")
        self.assertIn("Imported 1, updated 0, unchanged 0, skipped 0.", output)

    # --- headers and file format ---

    def test_headers_ignore_case_spaces_order_and_extra_columns(self):
        self.run_import(" Website , NAME ,Funding Total, Stage\nhttps://acme.example.com,Acme Fake,$1M,seed\n")
        company = Company.objects.get()
        self.assertEqual((company.name, company.stage), ("Acme Fake", Company.Stage.SEED))

    def test_handles_excel_utf8_bom(self):
        self.run_import(HEADER + "Café Fake,https://cafe.example.com,,,\n", encoding="utf-8-sig")
        self.assertEqual(Company.objects.get().name, "Café Fake")

    def test_missing_required_column_is_an_error_and_imports_nothing(self):
        path = self.write_csv("name,description\nAcme Fake,Rockets\n")
        with self.assertRaisesMessage(CommandError, "Missing required column(s): website"):
            call_command("import_companies", path, stdout=StringIO())
        self.assertFalse(Company.objects.exists())

    def test_missing_file_is_an_error(self):
        with self.assertRaisesMessage(CommandError, "File not found"):
            call_command("import_companies", "/no/such/file.csv", stdout=StringIO())

    def test_non_utf8_file_is_an_error(self):
        path = self.write_csv(HEADER + "Café Fake,https://cafe.example.com,,,\n", encoding="latin-1")
        with self.assertRaisesMessage(CommandError, "not saved as UTF-8"):
            call_command("import_companies", path, stdout=StringIO())

    def test_empty_file_is_an_error(self):
        with self.assertRaisesMessage(CommandError, "is empty"):
            call_command("import_companies", self.write_csv(""), stdout=StringIO())

    # --- stage ---

    def test_unknown_stage_is_left_blank_with_a_note(self):
        output = self.run_import(HEADER + "Acme Fake,https://acme.example.com,,,Debt Financing\n")
        self.assertEqual(Company.objects.get().stage, "")
        self.assertIn("stage 'Debt Financing' not recognised, left blank", output)
        self.assertIn("Imported 1,", output)

    def test_sample_file_stages(self):
        self.run_import(path=str(SAMPLE_CSV))
        stages = dict(Company.objects.values_list("name", "stage"))
        self.assertEqual(stages["Velvet Anvil Robotics (FAKE)"], Company.Stage.SERIES_B_PLUS)
        self.assertEqual(stages["Moonbeam Ledger (FAKE)"], Company.Stage.PRE_SEED)
        self.assertEqual(stages["Bubblewrap Bank (FAKE)"], "")


class HelperTests(SimpleTestCase):
    def test_normalise_website(self):
        for url in ["https://www.acme.com/", "http://acme.com", "ACME.com", "www.Acme.com//", " https://acme.com "]:
            self.assertEqual(normalise_website(url), "acme.com", url)
        self.assertEqual(normalise_website("https://acme.com/jobs/"), "acme.com/jobs")
        self.assertEqual(normalise_website(""), "")

    def test_parse_stage(self):
        S = Company.Stage
        cases = {
            "Pre-seed": S.PRE_SEED, "pre_seed": S.PRE_SEED, "Pre-Seed": S.PRE_SEED, "Angel": S.PRE_SEED,
            "Seed": S.SEED, "SEED": S.SEED,
            "Series A": S.SERIES_A, "series_a": S.SERIES_A,
            "Series B": S.SERIES_B_PLUS, "Series B+": S.SERIES_B_PLUS, "series_b_plus": S.SERIES_B_PLUS,
            "Series C": S.SERIES_B_PLUS, "series f": S.SERIES_B_PLUS,
            "": "", "  ": "", "Private Equity": "", "Venture - Series Unknown": "", "Seedling": "",
        }
        for value, expected in cases.items():
            self.assertEqual(parse_stage(value), expected, value)
