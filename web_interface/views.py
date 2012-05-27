from django.http import HttpResponse
from django.shortcuts import render_to_response
from models import PreviewRequest
from forms import PreviewRequestForm
from django.core.mail import send_mail
import subprocess
import hashlib
import os
import sys
import threading
from datetime import datetime

def index(request):
    return render_to_response('index.html', { 'form' : PreviewRequestForm(), 'year' : datetime.now().year })

def submit_generation_request(request):
    if request.method == 'POST':
        preview_request = PreviewRequest()
        form = PreviewRequestForm(request.POST, instance=preview_request)
        if form.is_valid():
            preview_request.save()

            class Worker(threading.Thread):
                def run(self):
                    print 'Initiating worker'
                    requests = PreviewRequest.objects.filter(generated=False).all()


                    PROJECT_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../media')
                    macos = '../bin/macos/webimage'
                    linux64 = '../bin/linux64/webimage'

                    webimage_path = \
                        os.path.join(os.path.abspath(os.path.dirname(__file__)), macos) if sys.platform == 'darwin' \
                        else os.path.join(os.path.abspath(os.path.dirname(__file__)), linux64)


                    for r in requests:
                        img_name = '%s.jpg' % hashlib.sha1('%s%s' % (r.url, str(r.requested_on))).hexdigest()
                        img_path = os.path.join(PROJECT_PATH, img_name)
                        command = []
                        if sys.platform == 'darwin':
                            command = [webimage_path, r.url, img_path, '1024']
                        elif sys.platform == 'linux2' or sys.platform == 'linux':
                            command = ['xvfb-run', '--server-args="-screen 0, 1024x768x24"', webimage_path, r.url, img_path, '1024']
                        print command
                        if subprocess.call(command):
                            print 'Error!'
                            return
                        r.image_path = '/media/%s' % img_name
                        r.generated = True
                        r.save()

                        send_mail('The Website preview generator tool',
                            'Hello there,\nThe website preview you requested is ready. '
                            'Visit the following address to see the generated preview:'
                            '\n http://previewtool.raphaelcruzeiro.com%s' % r.image_path,
                            'noreply@raphaelcruzeiro.com', [r.email], fail_silently=True,)


            Worker().start()

            return render_to_response('success.html', { 'email' : preview_request.email, 'year' : datetime.now().year })
        return render_to_response('index.html', { 'form' : form })
