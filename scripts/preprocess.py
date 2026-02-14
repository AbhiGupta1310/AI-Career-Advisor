"""
Data preprocessing script.
Converts raw LinkedIn JSON profiles into structured CSV files.

Usage:
    python -m scripts.preprocess --json-dir data/raw --output-dir data/processed
"""

import argparse
import csv
import json
import os
import re
from datetime import datetime


def parse_duration_text(duration: str) -> int:
    """Convert duration text (e.g., '3 yrs 1 mo') into total months."""
    if not duration:
        return 0
    years = months = 0
    y_match = re.search(r"(\d+)\s*yr", duration)
    m_match = re.search(r"(\d+)\s*mo", duration)
    if y_match:
        years = int(y_match.group(1))
    if m_match:
        months = int(m_match.group(1))
    return years * 12 + months


def calculate_years_of_experience(experience_list: list) -> float | str:
    """Calculate total years of experience from experience entries."""
    total_months = 0
    for exp in experience_list:
        if "duration" in exp and exp["duration"]:
            total_months += parse_duration_text(exp["duration"])
            continue

        start = exp.get("startDate", {})
        end = exp.get("endDate", {})

        try:
            start_year = int(start.get("year"))
            start_month = int(start.get("month", 1))
            start_date = datetime(start_year, start_month, 1)
        except (TypeError, ValueError):
            continue

        if end and "year" in end:
            end_year = int(end.get("year"))
            end_month = int(end.get("month", 1))
            end_date = datetime(end_year, end_month, 1)
        else:
            end_date = datetime.today()

        diff = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        total_months += max(diff, 0)

    return round(total_months / 12, 1) if total_months > 0 else ""


def process_json_file(json_path: str, output_dir: str) -> str:
    """Process a single JSON file into a CSV file."""
    basename = os.path.splitext(os.path.basename(json_path))[0]
    output_csv = os.path.join(output_dir, f"{basename}.csv")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    os.makedirs(output_dir, exist_ok=True)

    csv_headers = [
        "current_position",
        "current_company",
        "years_of_experience",
        "total_skills",
        "education_degree",
        "education_institution",
        "certifications",
        "city",
        "state",
        "country",
        "profile_type",
    ]

    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(csv_headers)

        for profile in data:
            element = profile.get("element", {})

            # Current position & company
            current_position = ""
            current_company = ""
            if element.get("experience"):
                current_position = element["experience"][0].get("position", "")
            if element.get("currentPosition"):
                current_company = element["currentPosition"][0].get("companyName", "")

            # Years of experience
            years_exp = calculate_years_of_experience(element.get("experience", []))

            # Skills
            skills = [s.get("name") for s in element.get("skills", []) if s.get("name")]
            skills_str = ", ".join(skills)

            # Education
            education_degree = ""
            education_institution = ""
            if element.get("education"):
                edu = element["education"][0]
                education_degree = edu.get("degree", "")
                education_institution = edu.get("schoolName", "")

            # Certifications
            certifications = [
                c.get("title") for c in element.get("certifications", []) if c.get("title")
            ]
            certs_str = ", ".join(certifications)

            # Location
            location = element.get("location", {}).get("parsed", {})
            city = location.get("city", "")
            state = location.get("state", "")
            country = location.get("country", "")

            # Profile type from filename
            profile_type = basename.replace("_final", "").replace("_finals", "")

            writer.writerow(
                [
                    current_position,
                    current_company,
                    years_exp,
                    skills_str,
                    education_degree,
                    education_institution,
                    certs_str,
                    city,
                    state,
                    country,
                    profile_type,
                ]
            )

    return output_csv


def main():
    parser = argparse.ArgumentParser(
        description="Convert raw JSON profiles to structured CSV files."
    )
    parser.add_argument(
        "--json-dir",
        default="data/raw",
        help="Directory containing JSON files (default: data/raw)",
    )
    parser.add_argument(
        "--output-dir",
        default="data/processed",
        help="Output directory for CSV files (default: data/processed)",
    )
    args = parser.parse_args()

    json_files = [f for f in os.listdir(args.json_dir) if f.endswith(".json")]

    if not json_files:
        print(f"⚠️  No JSON files found in {args.json_dir}")
        return

    print(f"📂 Found {len(json_files)} JSON files in {args.json_dir}")

    for json_file in json_files:
        json_path = os.path.join(args.json_dir, json_file)
        output_path = process_json_file(json_path, args.output_dir)
        print(f"  ✅ {json_file} → {output_path}")

    print(f"\n✅ All {len(json_files)} files processed → {args.output_dir}")


if __name__ == "__main__":
    main()
