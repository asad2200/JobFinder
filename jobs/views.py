import math
from django.http.response import HttpResponse
from jobs.models import Application
from django.shortcuts import render
from employer.models import Job, Qualification
from dashboard.models import Profile
from helpers import upload_s3, get_s3
# Create your views here.


def view_jobs(request):
    alljobs = []
    jobs = Job.objects.all().order_by("-id")
    for job in jobs:
        company = Profile.objects.get(id=job.profile).name
        alljobs.append([job, company])

    return render(request, "jobs/jobs.html", {
        'jobs': alljobs,
    })


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
            2: 'Your request is accepted',
            3: 'Your request is rejected',
        }

        return render(request, "dashboard/invalid.html", {
            'message': f'You already applied for this job on {application.timestamp}. {status[application.status]} '
        })
    except Application.DoesNotExist:
        pass

    if request.method == 'POST':
        applicant_id = request.user.id
        job_id = Job.objects.get(code=code).id
        # TODO: file_code = upload_s3(request)
        file_code = ''
        cover_letter = request.POST["coverletter"]

        Application(applicant_id=applicant_id, job_id=job_id,
                    resume=file_code, cover_letter=cover_letter, status=0).save()

        return render(request, "dashboard/success.html", {
            'message': "Applied succesfully!!"
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
    # TODO: filedata = get_s3(code)
    filedata = ''
    response = HttpResponse(filedata["Body"])
    response["Content-Type"] = "application/pdf"
    return response


def search_job(request):
    if request.GET.get("q"):
        alljobs = []
        q = request.GET['q']
        jobs = Job.objects.filter(title__icontains=q).order_by("-id")
        pages = 1 if len(jobs) <= 4 else math.ceil(len(jobs)/4) + 1
        for job in jobs:
            company = Profile.objects.get(id=job.profile).name
            alljobs.append([job, company])
        start = 0
        if request.GET.get("p"):
            p = int(request.GET.get("p"))
            start = 4 * int(p-1)

        return render(request, "jobs/search-job.html", {
            'jobs': alljobs[start:start+4],
            'pages': range(pages-1),
            'query': q,
        })
    else:
        return render(request, "jobs/search-job.html")
