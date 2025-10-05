import json
import csv
import time
import re
import google.generativeai as genai

# =====================
# CONFIG
# =====================
API_KEY = "AIzaSyDD4vDYp3_1uheoLWMSC_SH5HItsaXuP64"   # 👈 Replace this with your key
INPUT_FILE = "combined.json"
CSV_FILE = "salary_output.csv"
JSON_FILE = "output_with_salary.json"
CHECKPOINT_INTERVAL = 100    # save every 100 profiles
MAX_RETRIES = 3              # retry API call if it fails
SLEEP_BETWEEN_CALLS = 1      # seconds (to avoid rate limit)

# =====================
# INIT GEMINI
# =====================
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# =====================
# LOAD JSON
# =====================
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

results = []

# =====================
# PREPARE CSV WRITER
# =====================
csv_file = open(CSV_FILE, "a", newline="", encoding="utf-8")
csv_writer = csv.writer(csv_file)

# Write header only if file empty
if csv_file.tell() == 0:
    csv_writer.writerow([
        "current_position", "current_company", "years_of_experience",
        "education_degree", "city", "country", "salary_estimate", "median_salary"
    ])

# =====================
# HELPER: Extract Median Salary
# =====================
def extract_median_salary(salary_range_str):
    """
    Extracts numeric values from salary range and calculates median.
    Examples: "8-10 LPA" → 9, "500000-600000 INR" → 550000
    """
    try:
        # Remove common words and extract numbers
        numbers = re.findall(r'[\d,]+\.?\d*', salary_range_str.replace(',', ''))
        
        if len(numbers) >= 2:
            low = float(numbers[0])
            high = float(numbers[1])
            
            # Check if it's in lakhs/crores format (typically smaller numbers)
            if low < 1000 and 'L' in salary_range_str.upper():
                low *= 100000
                high *= 100000
            elif low < 100 and 'CR' in salary_range_str.upper():
                low *= 10000000
                high *= 10000000
            
            median = int((low + high) / 2)
            return median
        elif len(numbers) == 1:
            # Single value provided
            val = float(numbers[0])
            if val < 1000 and 'L' in salary_range_str.upper():
                val *= 100000
            elif val < 100 and 'CR' in salary_range_str.upper():
                val *= 10000000
            return int(val)
        else:
            return 0
    except Exception as e:
        print(f"⚠️ Could not parse salary: {salary_range_str} - {e}")
        return 0

# =====================
# HELPER: Gemini Call with Retry
# =====================
def get_salary_estimate(profile):
    prompt = f"""
    You are a professional compensation analyst in India.
    Based on the candidate profile below, give the most accurate estimate of their 
    annual salary in INR.

    Candidate Profile:
    {json.dumps(profile, indent=2)}

    Rules:
    1. Only consider realistic salaries for the **city and role mentioned**.
    2. Give the salary as a range with **maximum 20-25% difference** between min and max.
    3. Use the following logic:
        - Determine role, years of experience, skills, and certifications.
        - Compare with typical market salaries in India for similar profiles.
        - Consider location cost of living.
        - Avoid extreme outliers.
    4. Output **exactly as**: "X - Y LPA" or "X - Y INR" (use lakhs for clarity when appropriate)
    5. **Keep the range tight** - no more than 25% difference between low and high values.
    
    Examples of good ranges:
    - "8 - 10 LPA" (25% range)
    - "15 - 18 LPA" (20% range)
    - "600000 - 720000 INR" (20% range)
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"⚠️ Attempt {attempt} failed: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(2 * attempt)  # exponential backoff
            else:
                return "ERROR"

# =====================
# MAIN LOOP
# =====================
for idx, chunk in enumerate(data, start=45):
    # Handle missing current company
    if not chunk.get("current_company"):
        salary = "0 INR"
        median_salary = 0
    else:
        salary = get_salary_estimate(chunk)
        median_salary = extract_median_salary(salary)

    # Append to JSON structure
    chunk["salary_estimate"] = salary
    chunk["median_salary"] = median_salary
    results.append(chunk)

    # Write to CSV
    csv_writer.writerow([
        chunk.get("current_position", ""),
        chunk.get("current_company", ""),
        chunk.get("years_of_experience", ""),
        chunk.get("education_degree", ""),
        chunk.get("city", ""),
        chunk.get("country", ""),
        salary,
        median_salary
    ])

    print(f"✅ Processed {idx}/{len(data)} → {salary} (Median: ₹{median_salary:,})")

    # Checkpoint save
    if idx % CHECKPOINT_INTERVAL == 0:
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"💾 Checkpoint saved at record {idx}")

    time.sleep(SLEEP_BETWEEN_CALLS)

# =====================
# FINAL SAVE
# =====================
with open(JSON_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

csv_file.close()
print("🎉 Processing complete! Data saved to CSV + JSON")
print(f"📊 Total records processed: {len(data)}")