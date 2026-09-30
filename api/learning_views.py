
import json

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import Parent, Staff, Student
from .learning_models import (
    LearningAssignment,
    LearningAssignmentSubmission,
    LearningLesson,
    LearningProgress,
    LearningQuiz,
    LearningQuizAttempt,
    LearningTopic,
)


def _learning_response(data, status=200):
    response = JsonResponse(data, status=status)
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type, X-Sovereign-Client"
    return response


def _json_body(request):
    try:
        value = json.loads(request.body or "{}")
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _clean_class_name(value):
    return str(value or "").strip()


def _authenticate_actor(body):
    mode = str(body.get("mode") or "parent").strip().lower()
    pin = str(body.get("pin") or "").strip()

    if mode in {"parent", "student"}:
        student_id = str(body.get("student_id") or "").strip()

        if not student_id or not pin:
            return None, None, "Student identity is incomplete."

        student = Student.objects.filter(
            account_number__iexact=student_id,
            is_active=True,
        ).select_related("school", "parent_link").first()

        if not student:
            return None, None, "Student account not found."

        parent = student.parent_link

        if parent and str(parent.unique_code).strip() == pin:
            return student, None, None

        # This branch allows a future direct student PIN without weakening
        # the existing parent flow; by default the current registry has
        # no separate student PIN.
        return None, None, "Learning authorization failed."

    if mode == "staff":
        staff_name = str(body.get("staff_name") or "").strip()

        if not staff_name or not pin:
            return None, None, "Staff identity is incomplete."

        staff = Staff.objects.filter(
            full_name__iexact=staff_name,
            secure_pin=pin,
        ).select_related("school").first()

        if not staff:
            return None, None, "Staff learning authorization failed."

        return None, staff, None

    return None, None, "Unsupported learning access mode."


def _student_scope(student):
    class_name = _clean_class_name(student.current_class)
    school = student.school
    return school, class_name


def _visible_subject_ids(school, class_name):
    return list(
        LearningTopic.objects.filter(
            school=school,
            class_name=class_name,
            is_published=True,
        )
        .values_list("subject_id", flat=True)
        .distinct()
    )


def _subject_summary(student, subject):
    lessons = list(
        LearningLesson.objects.filter(
            topic__school=student.school,
            topic__class_name=_clean_class_name(student.current_class),
            topic__subject=subject,
            topic__is_published=True,
            is_published=True,
        )
        .select_related("topic")
    )

    lesson_ids = [lesson.id for lesson in lessons]
    progress_map = {
        row.lesson_id: row
        for row in LearningProgress.objects.filter(
            student=student,
            lesson_id__in=lesson_ids,
        )
    }

    completed = 0
    progress_total = 0

    for lesson in lessons:
        row = progress_map.get(lesson.id)
        value = 100 if row and row.completed else (
            float(row.progress_percent) if row else 0
        )
        if value >= 100:
            completed += 1
        progress_total += value

    progress_percent = (
        round(progress_total / len(lessons), 2)
        if lessons
        else 0
    )

    return {
        "id": subject.id,
        "name": subject.name,
        "code": subject.code or "",
        "level": subject.level,
        "lesson_count": len(lessons),
        "completed_lessons": completed,
        "progress_percent": progress_percent,
    }


def _serialize_lesson(student, lesson):
    progress = LearningProgress.objects.filter(
        student=student,
        lesson=lesson,
    ).first()

    value = 100 if progress and progress.completed else (
        float(progress.progress_percent) if progress else 0
    )

    return {
        "id": lesson.id,
        "title": lesson.title,
        "summary": lesson.summary,
        "content": lesson.content,
        "video_url": lesson.video_url,
        "document_url": lesson.document_url,
        "duration_minutes": lesson.duration_minutes,
        "order": lesson.order,
        "topic_id": lesson.topic_id,
        "topic_name": lesson.topic.title,
        "subject_id": lesson.topic.subject_id,
        "subject_name": lesson.topic.subject.name,
        "progress_percent": round(value, 2),
        "completed": bool(progress and progress.completed),
    }


@csrf_exempt
def learning_overview(request):
    if request.method == "OPTIONS":
        return _learning_response({})

    if request.method != "POST":
        return _learning_response({"message": "POST required."}, 405)

    body = _json_body(request)
    student, staff, error = _authenticate_actor(body)

    if error:
        return _learning_response({"message": error}, 403)

    if staff:
        return _staff_learning_overview(staff)

    school, class_name = _student_scope(student)

    subjects = []
    for subject_id in _visible_subject_ids(school, class_name):
        from .models import Subject
        subject = Subject.objects.filter(id=subject_id).first()
        if subject:
            subjects.append(_subject_summary(student, subject))

    lesson_ids = list(
        LearningLesson.objects.filter(
            topic__school=school,
            topic__class_name=class_name,
            topic__is_published=True,
            is_published=True,
        ).values_list("id", flat=True)
    )

    lesson_count = len(lesson_ids)
    completed_lessons = LearningProgress.objects.filter(
        student=student,
        lesson_id__in=lesson_ids,
        completed=True,
    ).count()

    completed_sum = 0
    progress_rows = list(
        LearningProgress.objects.filter(
            student=student,
            lesson_id__in=lesson_ids,
        )
    )
    for row in progress_rows:
        completed_sum += 100 if row.completed else float(row.progress_percent)

    overall_progress = (
        round(completed_sum / lesson_count, 2)
        if lesson_count
        else 0
    )

    continue_row = (
        LearningProgress.objects.filter(
            student=student,
            lesson_id__in=lesson_ids,
            completed=False,
        )
        .exclude(progress_percent=0)
        .select_related(
            "lesson__topic__subject",
        )
        .order_by("-updated_at")
        .first()
    )

    if not continue_row:
        continue_row = (
            LearningProgress.objects.filter(
                student=student,
                lesson_id__in=lesson_ids,
            )
            .select_related("lesson__topic__subject")
            .order_by("-updated_at")
            .first()
        )

    continue_lesson = None
    if continue_row:
        continue_lesson = _serialize_lesson(student, continue_row.lesson)

    assignments = []
    for assignment in LearningAssignment.objects.filter(
        school=school,
        class_name=class_name,
        is_published=True,
    ).select_related("subject").order_by("due_at", "-created_at")[:20]:
        assignments.append(
            {
                "id": assignment.id,
                "title": assignment.title,
                "instructions": assignment.instructions,
                "due_at": (
                    assignment.due_at.isoformat()
                    if assignment.due_at
                    else ""
                ),
                "subject_id": assignment.subject_id,
                "subject_name": assignment.subject.name,
                "total_points": assignment.total_points,
            }
        )

    assessments = []
    for quiz in LearningQuiz.objects.filter(
        school=school,
        class_name=class_name,
        is_published=True,
    ).select_related("subject").prefetch_related("questions")[:20]:
        assessments.append(
            {
                "id": quiz.id,
                "title": quiz.title,
                "instructions": quiz.instructions,
                "subject_id": quiz.subject_id,
                "subject_name": quiz.subject.name,
                "question_count": quiz.questions.count(),
                "pass_mark": quiz.pass_mark,
            }
        )

    return _learning_response(
        {
            "status": "ok",
            "student": {
                "id": student.account_number,
                "name": student.full_name,
                "school": school.name,
                "class_name": class_name,
            },
            "summary": {
                "lesson_count": lesson_count,
                "completed_lessons": completed_lessons,
                "progress_percent": overall_progress,
            },
            "continue_lesson": continue_lesson,
            "subjects": subjects,
            "assignments": assignments,
            "assessments": assessments,
        }
    )


def _staff_learning_overview(staff):
    class_names = list(
        staff.assignments.values_list("target_class", flat=True).distinct()
    )

    assignments = list(
        staff.assignments.select_related("subject", "school")
    )

    return _learning_response(
        {
            "status": "ok",
            "staff": {
                "id": staff.staff_id,
                "name": staff.full_name,
                "school": staff.school.name,
            },
            "summary": {
                "lesson_count": LearningLesson.objects.filter(
                    topic__school=staff.school,
                ).count(),
                "completed_lessons": 0,
                "progress_percent": 0,
            },
            "subjects": [
                {
                    "id": item.subject_id,
                    "name": item.subject.name,
                    "code": item.subject.code or "",
                    "level": item.subject.level,
                    "lesson_count": LearningLesson.objects.filter(
                        topic__school=staff.school,
                        topic__subject=item.subject,
                        is_published=True,
                    ).count(),
                    "completed_lessons": 0,
                    "progress_percent": 0,
                }
                for item in assignments
            ],
            "assignments": [],
            "assessments": [],
            "staff_classes": class_names,
        }
    )


@csrf_exempt
def learning_subject(request):
    if request.method == "OPTIONS":
        return _learning_response({})

    body = _json_body(request)
    student, staff, error = _authenticate_actor(body)

    if error:
        return _learning_response({"message": error}, 403)

    subject_id = body.get("subject_id")
    if not subject_id:
        return _learning_response({"message": "subject_id is required."}, 400)

    if staff:
        school = staff.school
        class_names = list(
            staff.assignments.filter(
                subject_id=subject_id,
            ).values_list("target_class", flat=True)
        )
        lessons_qs = LearningLesson.objects.filter(
            topic__school=school,
            topic__subject_id=subject_id,
            topic__is_published=True,
            is_published=True,
        )
        if class_names:
            lessons_qs = lessons_qs.filter(topic__class_name__in=class_names)
    else:
        school, class_name = _student_scope(student)
        lessons_qs = LearningLesson.objects.filter(
            topic__school=school,
            topic__class_name=class_name,
            topic__subject_id=subject_id,
            topic__is_published=True,
            is_published=True,
        )

    lessons = list(
        lessons_qs.select_related("topic__subject").order_by(
            "topic__order",
            "order",
            "id",
        )
    )

    from .models import Subject
    subject = Subject.objects.filter(id=subject_id).first()

    lesson_payload = [
        (
            _serialize_lesson(student, lesson)
            if student
            else {
                "id": lesson.id,
                "title": lesson.title,
                "summary": lesson.summary,
                "duration_minutes": lesson.duration_minutes,
                "order": lesson.order,
                "topic_id": lesson.topic_id,
                "topic_name": lesson.topic.title,
                "subject_id": lesson.topic.subject_id,
                "subject_name": lesson.topic.subject.name,
                "progress_percent": 0,
                "completed": False,
            }
        )
        for lesson in lessons
    ]

    return _learning_response(
        {
            "status": "ok",
            "subject": {
                "id": subject.id if subject else subject_id,
                "name": subject.name if subject else "Subject",
                "code": subject.code if subject else "",
                "level": subject.level if subject else "",
            },
            "lessons": lesson_payload,
        }
    )


@csrf_exempt
def learning_lesson(request):
    if request.method == "OPTIONS":
        return _learning_response({})

    body = _json_body(request)
    student, staff, error = _authenticate_actor(body)

    if error:
        return _learning_response({"message": error}, 403)

    lesson_id = body.get("lesson_id")
    if not lesson_id:
        return _learning_response({"message": "lesson_id is required."}, 400)

    lesson = LearningLesson.objects.filter(
        id=lesson_id,
        is_published=True,
        topic__is_published=True,
    ).select_related("topic__subject", "topic__school").first()

    if not lesson:
        return _learning_response({"message": "Lesson not found."}, 404)

    if staff:
        allowed = staff.assignments.filter(
            school=lesson.topic.school,
            subject=lesson.topic.subject,
            target_class=lesson.topic.class_name,
        ).exists()
        if not allowed:
            return _learning_response({"message": "Lesson outside your assignment."}, 403)
        payload = {
            "id": lesson.id,
            "title": lesson.title,
            "summary": lesson.summary,
            "content": lesson.content,
            "video_url": lesson.video_url,
            "document_url": lesson.document_url,
            "duration_minutes": lesson.duration_minutes,
            "topic_id": lesson.topic_id,
            "topic_name": lesson.topic.title,
            "subject_id": lesson.topic.subject_id,
            "subject_name": lesson.topic.subject.name,
            "progress_percent": 0,
            "completed": False,
        }
    else:
        if (
            lesson.topic.school_id != student.school_id
            or lesson.topic.class_name != _clean_class_name(student.current_class)
        ):
            return _learning_response({"message": "Lesson outside your learning plan."}, 403)
        payload = _serialize_lesson(student, lesson)

    return _learning_response({"status": "ok", "lesson": payload})


@csrf_exempt
def learning_progress(request):
    if request.method == "OPTIONS":
        return _learning_response({})

    body = _json_body(request)
    student, staff, error = _authenticate_actor(body)

    if error or staff:
        return _learning_response(
            {"message": error or "Only a learner can save progress."},
            403,
        )

    lesson_id = body.get("lesson_id")
    if not lesson_id:
        return _learning_response({"message": "lesson_id is required."}, 400)

    lesson = LearningLesson.objects.filter(
        id=lesson_id,
        is_published=True,
        topic__school=student.school,
        topic__class_name=_clean_class_name(student.current_class),
        topic__is_published=True,
    ).first()

    if not lesson:
        return _learning_response({"message": "Lesson is not available."}, 404)

    completed = bool(body.get("completed", False))
    progress_percent = body.get("progress_percent", 100 if completed else 0)
    last_position_seconds = body.get("last_position_seconds", 0)

    try:
        progress_percent = max(0, min(100, float(progress_percent)))
    except Exception:
        progress_percent = 0

    try:
        last_position_seconds = max(0, int(last_position_seconds))
    except Exception:
        last_position_seconds = 0

    progress, _ = LearningProgress.objects.get_or_create(
        student=student,
        lesson=lesson,
    )

    progress.progress_percent = progress_percent
    progress.last_position_seconds = last_position_seconds

    if completed or progress_percent >= 100:
        progress.completed = True
        progress.progress_percent = 100
        progress.completed_at = progress.completed_at or timezone.now()

    progress.save()

    return _learning_response(
        {
            "status": "ok",
            "progress": {
                "lesson_id": lesson.id,
                "progress_percent": float(progress.progress_percent),
                "completed": progress.completed,
                "last_position_seconds": progress.last_position_seconds,
            },
        }
    )


@csrf_exempt
def learning_quiz(request):
    if request.method == "OPTIONS":
        return _learning_response({})

    body = _json_body(request)
    student, staff, error = _authenticate_actor(body)

    if error:
        return _learning_response({"message": error}, 403)

    quiz_id = body.get("quiz_id")
    if not quiz_id:
        return _learning_response({"message": "quiz_id is required."}, 400)

    quiz = LearningQuiz.objects.filter(
        id=quiz_id,
        is_published=True,
    ).select_related("subject", "school").prefetch_related("questions").first()

    if not quiz:
        return _learning_response({"message": "Assessment not found."}, 404)

    if student:
        if (
            quiz.school_id != student.school_id
            or quiz.class_name != _clean_class_name(student.current_class)
        ):
            return _learning_response({"message": "Assessment outside your learning plan."}, 403)

    if staff and quiz.school_id != staff.school_id:
        return _learning_response({"message": "Assessment outside your school."}, 403)

    questions = []
    for question in quiz.questions.all():
        questions.append(
            {
                "id": question.id,
                "question": question.question,
                "options": {
                    "A": question.option_a,
                    "B": question.option_b,
                    "C": question.option_c,
                    "D": question.option_d,
                },
                "points": question.points,
                "order": question.order,
            }
        )

    return _learning_response(
        {
            "status": "ok",
            "quiz": {
                "id": quiz.id,
                "title": quiz.title,
                "instructions": quiz.instructions,
                "subject_name": quiz.subject.name,
                "pass_mark": quiz.pass_mark,
                "questions": questions,
            },
        }
    )


@csrf_exempt
def learning_quiz_submit(request):
    if request.method == "OPTIONS":
        return _learning_response({})

    body = _json_body(request)
    student, staff, error = _authenticate_actor(body)

    if error or staff:
        return _learning_response(
            {"message": error or "Only a learner can submit an assessment."},
            403,
        )

    quiz_id = body.get("quiz_id")
    answers = body.get("answers", {})

    if not quiz_id or not isinstance(answers, dict):
        return _learning_response(
            {"message": "quiz_id and answers are required."},
            400,
        )

    quiz = LearningQuiz.objects.filter(
        id=quiz_id,
        school=student.school,
        class_name=_clean_class_name(student.current_class),
        is_published=True,
    ).prefetch_related("questions").first()

    if not quiz:
        return _learning_response({"message": "Assessment not found."}, 404)

    score = 0
    total_points = 0

    for question in quiz.questions.all():
        total_points += question.points
        submitted = str(answers.get(str(question.id), "")).upper()
        if submitted == question.correct_option:
            score += question.points

    percentage = (
        round((score / total_points) * 100, 2)
        if total_points
        else 0
    )
    passed = percentage >= quiz.pass_mark

    attempt = LearningQuizAttempt.objects.create(
        student=student,
        quiz=quiz,
        score=score,
        total_points=total_points,
        passed=passed,
        answers_json=answers,
    )

    return _learning_response(
        {
            "status": "ok",
            "attempt": {
                "id": attempt.id,
                "score": score,
                "total_points": total_points,
                "percentage": percentage,
                "passed": passed,
                "submitted_at": attempt.submitted_at.isoformat(),
            },
        }
    )


@csrf_exempt
def learning_assignment_submit(request):
    if request.method == "OPTIONS":
        return _learning_response({})

    body = _json_body(request)
    student, staff, error = _authenticate_actor(body)

    if error or staff:
        return _learning_response(
            {"message": error or "Only a learner can submit an assignment."},
            403,
        )

    assignment_id = body.get("assignment_id")
    response_text = str(body.get("response_text") or "").strip()

    if not assignment_id or not response_text:
        return _learning_response(
            {"message": "assignment_id and response_text are required."},
            400,
        )

    assignment = LearningAssignment.objects.filter(
        id=assignment_id,
        school=student.school,
        class_name=_clean_class_name(student.current_class),
        is_published=True,
    ).first()

    if not assignment:
        return _learning_response(
            {"message": "Assignment not found."},
            404,
        )

    submission, _ = LearningAssignmentSubmission.objects.update_or_create(
        student=student,
        assignment=assignment,
        defaults={"response_text": response_text},
    )

    return _learning_response(
        {
            "status": "ok",
            "submission": {
                "id": submission.id,
                "assignment_id": assignment.id,
                "submitted_at": submission.submitted_at.isoformat(),
            },
        }
    )
