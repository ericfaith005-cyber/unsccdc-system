@api_view(['POST'])
@permission_classes([AllowAny])
def staff_hub_auth(request):
    """OFFICIAL STAFF Hub Hub Hub COMMAND UPLINK"""
    d = request.data
    name = d.get('name', '').strip()
    pin = d.get('pin', '').strip()

    # 🔎 Search the vault
    staff = Staff.objects.filter(full_name__iexact=name, secure_pin=pin).first()
    
    if staff:
        # 🕵️ CRITICAL THINKING: We detect the role name automatically
        # to prevent the 'AttributeError'
        staff_role = getattr(staff, 'role', getattr(staff, 'position', 'Official Staff'))
        
        return Response({
            "status": "STAFF_AUTHORIZED",
            "name": staff.full_name,
            "role": staff_role, # 💎 FIX: Safe attribute access
            "school": staff.school.name if staff.school else "National Hub"
        })
    
    return Response({"status": "DENIED", "msg": "Invalid Command Credentials."}, status=401)