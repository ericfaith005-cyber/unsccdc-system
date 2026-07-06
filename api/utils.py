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