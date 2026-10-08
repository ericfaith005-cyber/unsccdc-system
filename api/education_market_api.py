import json
from decimal import Decimal
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import EducationUploadAuthorization, EducationVideo, NationalBook, NationalBookOrder

def _body(request):
    try: return json.loads(request.body or '{}')
    except Exception: return {}

def _staff(request):
    u=getattr(request,'user',None)
    return bool(u and u.is_authenticated and (u.is_staff or u.is_superuser))

def _video(request,v):
    return {'id':v.id,'title':v.title,'description':v.description,'video':request.build_absolute_uri(v.video_file.url) if v.video_file else '',
            'thumbnail':request.build_absolute_uri(v.thumbnail.url) if v.thumbnail else '','school':v.school.name,'subject':v.subject,
            'level':v.education_level,'class_name':v.class_name,'topic':v.topic,'teacher':v.teacher_name,'category':v.category,
            'views':v.views_count,'saves':v.saves_count,'featured':v.is_featured}

def education_stream(request):
    qs=EducationVideo.objects.filter(moderation_status='APPROVED').select_related('school').order_by('-is_featured','-approved_at','-created_at')[:100]
    return JsonResponse([_video(request,x) for x in qs],safe=False)

def education_verify_code(request):
    if request.method!='POST': return JsonResponse({'detail':'POST required'},status=405)
    code=str(_body(request).get('code','')).strip().upper()
    try: a=EducationUploadAuthorization.objects.select_related('school').get(code=code)
    except EducationUploadAuthorization.DoesNotExist: return JsonResponse({'valid':False,'detail':'Invalid authorization code'},status=404)
    return JsonResponse({'valid':a.is_valid(),'school':a.school.name,'status':a.status,'expires_at':a.expires_at,'uploads_remaining':max(0,a.max_uploads-a.uploads_used)})

@csrf_exempt
def education_upload(request):
    if request.method!='POST': return JsonResponse({'detail':'POST required'},status=405)
    code=str(request.POST.get('code','')).strip().upper(); title=str(request.POST.get('title','')).strip(); video=request.FILES.get('video')
    if not code or not title or not video: return JsonResponse({'detail':'code, title and video are required'},status=400)
    try:
        with transaction.atomic():
            a=EducationUploadAuthorization.objects.select_for_update().select_related('school').get(code=code)
            if not a.is_valid(): return JsonResponse({'detail':'Authorization expired, suspended, revoked or exhausted'},status=403)
            v=EducationVideo.objects.create(school=a.school,authorization=a,title=title,description=request.POST.get('description',''),video_file=video,
                subject=request.POST.get('subject',''),education_level=request.POST.get('education_level',''),class_name=request.POST.get('class_name',''),
                topic=request.POST.get('topic',''),teacher_name=request.POST.get('teacher_name',''),category=request.POST.get('category','LESSON'))
            a.consume()
        return JsonResponse({'ok':True,'video':_video(request,v)},status=201)
    except EducationUploadAuthorization.DoesNotExist: return JsonResponse({'detail':'Invalid authorization code'},status=403)

def education_view(request,pk):
    try: v=EducationVideo.objects.get(pk=pk,moderation_status='APPROVED')
    except EducationVideo.DoesNotExist: return JsonResponse({'detail':'Video not found'},status=404)
    v.views_count+=1; v.save(update_fields=['views_count']); return JsonResponse({'ok':True,'views':v.views_count})

def education_save(request,pk):
    try: v=EducationVideo.objects.get(pk=pk,moderation_status='APPROVED')
    except EducationVideo.DoesNotExist: return JsonResponse({'detail':'Video not found'},status=404)
    v.saves_count+=1; v.save(update_fields=['saves_count']); return JsonResponse({'ok':True,'saves':v.saves_count})

@csrf_exempt
def education_moderate(request,pk):
    if not _staff(request): return JsonResponse({'detail':'Staff access required'},status=403)
    b=_body(request); status=str(b.get('status','')).upper()
    if status not in {'PENDING','APPROVED','REJECTED','SUSPENDED'}: return JsonResponse({'detail':'Invalid moderation status'},status=400)
    try: v=EducationVideo.objects.get(pk=pk)
    except EducationVideo.DoesNotExist: return JsonResponse({'detail':'Video not found'},status=404)
    v.moderation_status=status; v.moderation_reason=str(b.get('reason',''))
    if status=='APPROVED': v.approved_at=timezone.now(); v.approved_by=request.user
    v.save(); return JsonResponse({'ok':True,'video':_video(request,v)})

def book_market(request):
    qs=NationalBook.objects.filter(is_active=True).order_by('-id')
    out=[]
    for b in qs:
        out.append({'id':b.id,'title':b.title,'author':b.author,'price':float(b.price),'description':b.description,'stock':b.stock_available,
            'cover_image':request.build_absolute_uri(b.cover_image.url) if b.cover_image else '',
            'education_level':getattr(b,'education_level',''),'class_name':getattr(b,'class_name',''),'subject':getattr(b,'subject',''),
            'publisher':getattr(b,'publisher',''),'isbn':getattr(b,'isbn',''),'featured':getattr(b,'is_featured',False)})
    return JsonResponse(out,safe=False)

@csrf_exempt
def book_create_order(request):
    if request.method!='POST': return JsonResponse({'detail':'POST required'},status=405)
    b=_body(request)
    try: book_id=int(b.get('book_id')); qty=max(1,int(b.get('quantity',1)))
    except Exception: return JsonResponse({'detail':'Invalid book_id or quantity'},status=400)
    with transaction.atomic():
        try: book=NationalBook.objects.select_for_update().get(pk=book_id,is_active=True)
        except NationalBook.DoesNotExist: return JsonResponse({'detail':'Book unavailable'},status=404)
        if qty>book.stock_available: return JsonResponse({'detail':'Insufficient stock'},status=409)
        total=(book.price*qty).quantize(Decimal('0.01')); deposit=(total*Decimal('0.10')).quantize(Decimal('0.01')); balance=total-deposit
        order=NationalBookOrder.objects.create(book=book,buyer_name=str(b.get('buyer_name','')).strip(),phone=str(b.get('phone','')).strip(),location=str(b.get('location','')).strip(),quantity=qty,total_cost=total,escrow_fee=deposit)
        book.stock_available-=qty; book.save(update_fields=['stock_available'])
    return JsonResponse({'ok':True,'order_id':order.order_id,'status':order.status,'total':float(total),'deposit_10_percent':float(deposit),'balance':float(balance),'dispatch_locked':order.status!='PAID'},status=201)

@csrf_exempt
def book_deposit_confirm(request):
    if request.method!='POST': return JsonResponse({'detail':'POST required'},status=405)
    b=_body(request); oid=str(b.get('order_id','')).strip(); ref=str(b.get('reference','')).strip()
    if not oid or not ref or str(b.get('status','')).upper() not in {'PAID','SUCCESS','CONFIRMED'}: return JsonResponse({'detail':'Successful payment confirmation required'},status=400)
    try: o=NationalBookOrder.objects.get(order_id=oid)
    except NationalBookOrder.DoesNotExist: return JsonResponse({'detail':'Order not found'},status=404)
    o.status='PAID'; o.save(update_fields=['status'])
    return JsonResponse({'ok':True,'order_id':oid,'status':'PAID','total':float(o.total_cost),'deposit':float(o.escrow_fee),'balance':float(o.total_cost-o.escrow_fee),'dispatch_locked':False})

def book_order_status(request,order_id):
    try:o=NationalBookOrder.objects.get(order_id=order_id)
    except NationalBookOrder.DoesNotExist:return JsonResponse({'detail':'Order not found'},status=404)
    return JsonResponse({'order_id':o.order_id,'status':o.status,'total':float(o.total_cost),'deposit':float(o.escrow_fee),'balance':float(o.total_cost-o.escrow_fee),'dispatch_locked':o.status!='PAID' and o.status!='DISPATCHED' and o.status!='DELIVERED'})

@csrf_exempt
def book_dispatch(request,order_id):
    if not _staff(request): return JsonResponse({'detail':'Staff access required'},status=403)
    try:o=NationalBookOrder.objects.get(order_id=order_id)
    except NationalBookOrder.DoesNotExist:return JsonResponse({'detail':'Order not found'},status=404)
    if o.status!='PAID': return JsonResponse({'detail':'DISPATCH BLOCKED: 10% deposit has not been confirmed'},status=409)
    o.status='DISPATCHED'; o.save(update_fields=['status']); return JsonResponse({'ok':True,'order_id':o.order_id,'status':o.status})
