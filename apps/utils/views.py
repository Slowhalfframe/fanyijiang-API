import base64, hashlib, os

from django import forms
from django.core.cache import cache
from django.conf import settings

from apps.utils.api import CustomAPIView


class ImageUploadForm(forms.Form):
    image = forms.FileField()


class UploadImage(CustomAPIView):
    def post(self, request):
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['image']
        else:
            return self.error('上传失败', 10023)
        image_base64_data = base64.b64encode(image.read())
        image_base64_md5 = hashlib.md5(image_base64_data).hexdigest()

        # 获取图片base64的hash值集合
        UPLOAD_IMAGE_SET = cache.get('UPLOAD_IMAGE_SET') or set()

        suffix = os.path.splitext(image.name)[-1].lower().replace('\"', '')
        if suffix not in ['.gif', '.jpg', '.jpeg', '.bmp', '.png']:
            return self.error('不支持的文件格式', 10036)

        image_name = image_base64_md5 + suffix

        # 判断服务器缓存内是否已经有该文件，有直接返回路径，没有则写入文件
        if image_base64_md5 not in UPLOAD_IMAGE_SET:
            # 保存文件
            try:
                with open(os.path.join(settings.UPLOAD_DIR, image_name), 'wb') as imageFile:
                    for chunk in image:
                        imageFile.write(chunk)
                UPLOAD_IMAGE_SET.add(image_base64_md5)
            except IOError as e:
                print(e, '文件保存失败')
                return self.error('文件上传失败，请尝试重新上传！', 10023)

        image_path = "{}/{}".format(settings.UPLOAD_PREFIX, image_name)

        return self.success(image_path)
