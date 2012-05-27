from django.db import models

class PreviewRequest(models.Model):
    requested_on = models.DateTimeField(auto_now_add=True)
    email = models.EmailField()
    url = models.URLField()
    image_path = models.URLField(editable=False)
    generated = models.BooleanField(default=False, editable=False)
    sent = models.BooleanField(default=False, editable=False)

    def img(self):
        return '<img alt="" src"%s" />' % str(self.image_path).replace(' ', '/') if self.image_path is not None else 'No preview yet'
    img.allow_tags = True
