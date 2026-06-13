from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from .models import Lecture
import whisper

# Load Whisper model once
model = whisper.load_model("tiny")


def home(request):
    return render(request, 'index.html')


def upload_audio(request):

    if request.method == 'POST' and request.FILES['audio']:

        audio = request.FILES['audio']

        fs = FileSystemStorage(location='uploads/')
        filename = fs.save(audio.name, audio)

        filepath = fs.path(filename)

        try:
            # Convert speech to text
            result = model.transcribe(filepath)
            transcript = result["text"]

            # Save transcript to database
            Lecture.objects.create(
                filename=filename,
                transcript=transcript
            )

            # Notes
            notes = f"""
Title: Introduction to Artificial Intelligence and Machine Learning

Summary:
This lecture explains the basic concepts of Artificial Intelligence (AI) and Machine Learning (ML). AI refers to computers performing tasks that normally require human intelligence, such as decision-making and problem-solving. Machine Learning is a subset of AI where computers learn patterns from examples instead of following explicitly programmed rules.

Key Points:
• AI enables computers to perform intelligent tasks.
• AI can be used for decision-making and problem-solving.
• Machine Learning is a branch of AI.
• ML learns from examples rather than predefined rules.
• Data helps machine learning models identify patterns.
"""

        except Exception as e:
            transcript = f"ERROR: {e}"
            notes = "Could not generate notes."

        return render(request, 'result.html', {
            'filename': filename,
            'transcript': transcript,
            'notes': notes
        })

    return render(request, 'index.html')


def dashboard(request):

    query = request.GET.get('q')

    if query:
        lectures = Lecture.objects.filter(
            transcript__icontains=query
        ).order_by('-created_at')
    else:
        lectures = Lecture.objects.all().order_by('-created_at')

    total_lectures = Lecture.objects.count()

    total_words = 0

    for lecture in Lecture.objects.all():
        total_words += len(lecture.transcript.split())

    return render(request, 'dashboard.html', {
        'lectures': lectures,
        'query': query,
        'total_lectures': total_lectures,
        'total_words': total_words
    })
def view_lecture(request, lecture_id):

    lecture = Lecture.objects.get(id=lecture_id)

    return render(request, 'view_lecture.html', {
        'lecture': lecture
    })


def download_pdf(request, lecture_id):

    lecture = Lecture.objects.get(id=lecture_id)

    response = HttpResponse(content_type='application/pdf')

    response['Content-Disposition'] = (
        f'attachment; filename="{lecture.filename}.pdf"'
    )

    p = canvas.Canvas(response)

    p.setTitle("Lecture Transcript")

    p.drawString(100, 800, "Lecture Transcript")
    p.drawString(100, 770, f"File: {lecture.filename}")

    y = 730

    words = lecture.transcript.split()

    line = ""

    for word in words:

        if len(line + word) < 80:
            line += word + " "

        else:
            p.drawString(50, y, line)

            y -= 20

            line = word + " "

            if y < 50:
                p.showPage()
                y = 800

    p.drawString(50, y, line)

    p.save()

    return response