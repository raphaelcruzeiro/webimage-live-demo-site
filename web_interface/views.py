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
from threading import Lock
import shlex
from datetime import datetime

lock = Lock()

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
                    lock.acquire()

                    try:
                        print 'Initiating worker'
                        requests = PreviewRequest.objects.filter(generated=False).all()


                        PROJECT_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../media')
                        macos = '../bin/macos/webimage'
                        linux64 = '../bin/linux64/webimage'

                        webimage_path =\
                        os.path.join(os.path.abspath(os.path.dirname(__file__)), macos) if sys.platform == 'darwin'\
                        else os.path.join(os.path.abspath(os.path.dirname(__file__)), linux64)


                        for r in requests:
                            img_name = '%s.jpg' % hashlib.sha1('%s%s' % (r.url, str(r.requested_on))).hexdigest()
                            img_path = os.path.join(PROJECT_PATH, img_name)
                            command = []
                            if sys.platform == 'darwin':
                                command = shlex.split('%s %s %s 1024' % (webimage_path, r.url, img_path))
                            elif sys.platform == 'linux2' or sys.platform == 'linux':
                                command = shlex.split('xvfb-run --server-args="-screen 0, 1024x768x24" %s %s %s 1024' % (webimage_path, r.url, img_path))
                            print command
                            if subprocess.call(command):
                                print 'Error!'
                                return
                            r.image_path = '/media/%s' % img_name
                            r.generated = True
                            r.save()

                            thumbpath = '%s_thumb.jpg' % r.image_path[0:-4]

                            send_mail('The Website preview generator tool',
                                'Hello there,\nThe website preview you requested is ready. '
                                'Visit the following addresses to see the generated preview and the half size thumb:'
                                '\n http://previewtool.raphaelcruzeiro.com%s\nhttp://previewtool.raphaelcruzeiro.com%s' % (r.image_path, thumbpath),
                                'noreply@raphaelcruzeiro.com', [r.email], fail_silently=True,)
                    finally:
                        lock.release()


            Worker().start()

            return render_to_response('success.html', { 'email' : preview_request.email, 'year' : datetime.now().year })
        return render_to_response('index.html', { 'form' : form })
