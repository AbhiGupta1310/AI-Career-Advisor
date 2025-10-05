import json
import csv
import re
import os
from datetime import datetime

# Directory containing JSON files
json_dir = "json"

# Get all JSON files in the directory
json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]

# Function to convert duration text (e.g., "3 yrs 1 mo") into months
def parse_duration_text(duration):
    if not duration:
        return 0
    years = 0
    months = 0
    y_match = re.search(r"(\d+)\s*yr", duration)
    m_match = re.search(r"(\d+)\s*mo", duration)
    if y_match:
        years = int(y_match.group(1))
    if m_match:
        months = int(m_match.group(1))
    return years * 12 + months

# Function to calculate total years of experience
def calculate_years_of_experience(experience_list):
    total_months = 0
    for exp in experience_list:
        # First try duration string
        if "duration" in exp and exp["duration"]:
            total_months += parse_duration_text(exp["duration"])
            continue

        # Otherwise use startDate and endDate
        start = exp.get("startDate", {})
        end = exp.get("endDate", {})

        try:
            start_year = int(start.get("year"))
            start_month = int(start.get("month", 1))
            start_date = datetime(start_year, start_month, 1)
        except:
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

# Process each JSON file
for json_file in json_files:
    print(f"Processing {json_file}...")
    
    # Create output CSV filename
    output_csv = f"csv/{os.path.splitext(json_file)[0]}.csv"
    
    # Load JSON data
    with open(os.path.join(json_dir, json_file), "r", encoding="utf-8") as f:
        data = json.load(f)

    # Create csv directory if it doesn't exist
    os.makedirs("csv", exist_ok=True)

    # Prepare CSV
    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
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
            "profile_type"  # Adding profile type based on JSON filename
        ])

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

            # Education (highest degree)
            education_degree = ""
            education_institution = ""
            if element.get("education"):
                edu = element["education"][0]
                education_degree = edu.get("degree", "")
                education_institution = edu.get("schoolName", "")

            # Certifications
            certifications = [c.get("title") for c in element.get("certifications", []) if c.get("title")]
            certs_str = ", ".join(certifications)

            # Location
            location = element.get("location", {}).get("parsed", {})
            city = location.get("city", "")
            state = location.get("state", "")
            country = location.get("country", "")

            # Get profile type from filename (e.g., "blockchain_developer" from "blockchain_developer_final.json")
            profile_type = os.path.splitext(json_file)[0].replace("_final", "")

            # Write row
            writer.writerow([
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
                profile_type
            ])

    print(f"✅ Created CSV file: {output_csv}")

print("\n✅ All JSON files have been processed and CSV files have been created in the csv directory")
