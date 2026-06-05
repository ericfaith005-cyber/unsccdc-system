import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UNSCCDC.settings')
django.setup()

from django.contrib.auth.models import User

if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@unsccdc.com", "Imperial2026!")
    print("--- 👑 THE KING HAS BEEN BORN IN SUPABASE ---")
else:
    print("--- 🏛️ THE THRONE IS ALREADY OCCUPIED ---")