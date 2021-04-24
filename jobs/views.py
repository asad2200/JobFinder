from django.http.response import HttpResponse
from jobs.models import Application
from django.shortcuts import render
from employer.models import Job, Qualification
from dashboard.models import Profile
from helpers import upload_s3, get_s3
# Create your views here.


def view_job(request, code):

    job = Job.objects.get(code=code)
    qualifications = Qualification.objects.filter(job_id=job.id)

    company = Profile.objects.get(id=job.profile).name

    return render(request, "jobs/job.html", {
        'company': company,
        'job': job,
        'qualifications': qualifications,
    })


def apply_job(request, code):
    try:
        application = Application.objects.get(
            applicant_id=request.user.id, job_id=Job.objects.get(code=code).id)
        status = {
            0: 'Your request is in waiting',
            1: 'Your request is viewed',
            2: 'Your request is rejected',
        }

        return render(request, "employer/invalid.html", {
            'message': f'You already applied for this job on {application.timestamp}. {status[application.status]} '
        })
    except Application.DoesNotExist:
        pass
    if request.method == 'POST':
        applicant_id = request.user.id
        job_id = Job.objects.get(code=code).id
        file_code = upload_s3(request)
        cover_letter = request.POST["coverletter"]

        Application(applicant_id=applicant_id, job_id=job_id,
                    resume=file_code, cover_letter=cover_letter).save()

        return render(request, "employer/success.html", {
            'message': "Applied succesfully!!"+file_code
        })
    else:
        job = Job.objects.get(code=code)
        company = Profile.objects.get(id=job.profile).name
        profile = Profile.objects.get(user_id=request.user.id)
        return render(request, "jobs/apply.html", {
            'job': job,
            'company': company,
            'profile': profile,
        })


def view_resume(request, code):
    filedata = get_s3(code)
    response = HttpResponse(filedata["Body"])
    response["Content-Type"] = "application/pdf"
    return response
