# api/utils.py
# Change this on line 3 of api/utils.py:
from .models import Student, School
import pdfplumber
import re

def auto_arrange_pdf_data(pdf_file_path, school_id):
    # Dynamic import inside function blocks cyclic dependency loops
    from api.models import Student, School 
    
    active_school = School.objects.get(id=school_id)
    
    with pdfplumber.open(pdf_file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
                
            lines = text.split("\n")
            for line in lines:
                # Optimized regex matching raw text layout arrays:
                # Pattern: [PRN/PaymentCode] [Name] [Class] [Stream] [Gender] [Age]
                # Sample text line expected: 3700123456 John_Doe S.1 North M 14
                match = re.match(r"^(\S+)\s+([\w\s_-]+?)\s+(S\.\d|P\.\d)\s+(\S+)\s+([MF])\s+(\d+)$", line.strip(), re.IGNORECASE)
                
                if match:
                    prn, raw_name, cls, strm, gnd, age_val = match.groups()
                    clean_name = raw_name.replace("_", " ").strip()
                    
                    # Updates existing profile or populates a fresh student record automatically
                    Student.objects.update_or_create(
                        payment_code=prn.strip(),
                        defaults={
                            'full_name': clean_name,
                            'current_class': cls.strip().upper(),
                            'stream': strm.strip(),
                            'gender': gnd.strip().upper(),
                            'age': int(age_val),
                            'school': active_school,
                            'is_active': True
                        }
                    )

# 🏛️ THE Hub Hub Hub Hub Hub NATIONAL GRADING ENGINE
def get_national_grading(score, level="O-LEVEL"):
    """
    Converts raw scores into official grades based on Ugandan standards.
    Supports O-Level (UCE) and A-Level (UACE).
    """
    if score is None: score = 0
    
    # 💎 1. A-LEVEL LOGIC (Principal Points)
    if level.upper() in ["A-LEVEL", "UACE", "S5", "S6"]:
        if score >= 80: return "A", 6, "EXCEPTIONAL", "Principal Pass"
        if score >= 70: return "B", 5, "OUTSTANDING", "Principal Pass"
        if score >= 60: return "C", 4, "VERY GOOD", "Principal Pass"
        if score >= 50: return "D", 3, "GOOD", "Principal Pass"
        if score >= 40: return "E", 2, "SATISFACTORY", "Principal Pass"
        if score >= 35: return "O", 1, "BASIC", "Subsidiary Pass"
        return "F", 0, "UNSATISFACTORY", "Fail"

    # 💎 2. O-LEVEL LOGIC (Standard D1-F9)
    else:
        if score >= 80: return "D1", 1, "EXCEPTIONAL", "Distinction"
        if score >= 75: return "D2", 2, "OUTSTANDING", "Distinction"
        if score >= 70: return "C3", 3, "VERY GOOD", "Credit"
        if score >= 65: return "C4", 4, "GOOD", "Credit"
        if score >= 60: return "C5", 5, "ABOVE AVERAGE", "Credit"
        if score >= 50: return "C6", 6, "SATISFACTORY", "Credit"
        if score >= 45: return "P7", 7, "BASIC", "Pass"
        if score >= 40: return "P8", 8, "ELEMENTARY", "Pass"
        return "F9", 9, "UNSATISFACTORY", "Fail"