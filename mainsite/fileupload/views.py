import datetime
import os
from io import BytesIO
from os.path import join, isfile, isdir

from captcha.models import CaptchaStore
from django.conf import settings
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .forms import UploadFileForm, UploadIconModelForm
from .models import UploadIcons
from .utility import make_thumbnail


def home(request):
    if request.method == 'GET':
        action = request.GET.get('do')
        if action == 'del':
            try:
                image_id = request.GET.get('id')

                # print('id: %s' % image_id)
                obj = UploadIcons.objects.get(pk=image_id)
                # print(obj)
                image_title = obj.Title
                # print(image_title)
                obj.delete()
                message = "圖片 [%s] 已被刪除." % image_title
                print(message)
                return HttpResponseRedirect(reverse('fileupload:home'))
            except Exception as e:
                message = 'Can not fine the image ! <br> %s' % e
        elif action == 'del_file':
            file_name = request.GET.get('file')
            folder = settings.MEDIA_ROOT + '/upload/'
            full_path = join(folder, file_name)
            os.remove(full_path)
            print('%s had been remove.' % file_name)
            return HttpResponseRedirect(reverse('fileupload:home'))


    if request.method == 'POST':
        receive_form = UploadFileForm(request.POST, request.FILES)
        receive_file = request.FILES['file']
        if receive_form.is_valid():
            message = 'The file %s (%d bytes) is correct.' % (receive_file, receive_file.size)
            # print(type(receive_file))
            # print('The size of file is %d bytes' % receive_file.size)
            now_time = datetime.datetime.now()
            # 避免相同檔名覆蓋
            new_file_name = now_time.strftime('%Y%m%d_%H%M%S'+'.jpg')
            # print('File Name is %s' % new_file_name)
            path_file = settings.MEDIA_ROOT + '/upload/'
            # print('Path: %s' % path_file)

            with open(path_file + new_file_name, 'wb+') as file_save_to:
                for chunk in receive_file.chunks():
                    file_save_to.write(chunk)

        return redirect(reverse('fileupload:home'))

    upload_path = settings.MEDIA_ROOT + '/upload/'
    # print('Path: %s' % upload_path)

    if os.path.exists(upload_path.strip().replace('?', '')):
        # print('***目錄已存在')
        pass
    else:
        os.makedirs(upload_path.strip().replace('?', ''))
        print('***目錄不存在，建立目錄')

    # 取得所有檔案與子目錄名稱
    files = os.listdir(upload_path)
    # print('The files in the folder: %s' % files)

    # 以迴圈處理
    image_path = settings.MEDIA_URL + 'upload/'
    images_list = []
    for file in files:
        # 產生檔案的絕對路徑
        fullpath = join(upload_path, file)
        # 判斷 fullpath 是檔案還是目錄
        if isfile(fullpath):

            images_list.append({'file': file, 'path': image_path + file})

            # print("檔案:", file, " 路徑：", fullpath)
        elif isdir(fullpath):
            print("目錄：", file)
    icons = UploadIcons.objects.all()
    upload_form = UploadFileForm
    icon_form = UploadIconModelForm
    return render(request, 'fileupload/home.html', locals())


def savetomodel(request):
    if request.method == 'POST':
        receive_form = UploadIconModelForm(request.POST, request.FILES)
        icon_title = request.POST.get('Title')
        # print(icon_title)
        capt = request.POST.get("captcha_1", None)  # User Key In
        key = request.POST.get("captcha_0", None)  # Database store

        if check_captcha(capt, key):

            # Reduce image size
            post_image = request.FILES.get('IconImage')
            print(post_image)
            file_string = BytesIO()
            for part in post_image.chunks():  # 將上傳的資料儲存於記憶體
                file_string.write(part)
                file_string.flush()

            file_name = post_image.name
            image = make_thumbnail(file_string, file_name, size=(800, 800))

            if receive_form.is_valid():
                # 如果檢驗全部通過
                print('Data Pass Valid.')  # 這裡全部都沒問題
            else:
                print('Data Error: %s' % receive_form.errors)

            try:
                new_image = UploadIcons.objects.create()
                new_image.Title = icon_title
                new_image.IconImage = image
                # print('Save')
                new_image.save()
                print('圖片 [%s] 已上傳。' % icon_title)

            except Exception as e:
                print('The erro: %s' % e)

            return redirect(reverse('fileupload:home'))
        else:
            icons = UploadIcons.objects.all()
            upload_form = UploadFileForm
            icon_form = UploadIconModelForm
            captcha_message = 'Wrong Captcha ! 驗證碼錯誤！'
            return render(request, 'fileupload/home.html', locals())

def update(request, image_id):
    print('Update Image ID:', image_id)
    pick_data = get_object_or_404(UploadIcons, pk=image_id)
    title = request.POST.get('update_title')
    image_file = request.FILES.get('update_image')
    print("File Object:", image_file)
    pick_data.Title = title
    if image_file != None:
        pick_data.IconImage = image_file
    else:
        pass
    # print(image_id)
    # print(title)
    # print(image_file)
    print('Update Image: %s' % pick_data.Title)
    pick_data.save()
    return HttpResponseRedirect(reverse('fileupload:home'))

# 刪除使用 FileField 或是 ImageField 儲存的檔案
@receiver(post_delete, sender=UploadIcons)
def post_save_image(sender, instance, *args, **kwargs):
    """ Clean Old Image file """
    try:
        instance.IconImage.delete(save=False)
    except:
        pass


# 更新使用 FileField 或是 ImageField 儲存的檔案
@receiver(pre_save, sender=UploadIcons)
def pre_save_image(sender, instance, *args, **kwargs):
    """ instance old image file will delete from os """
    try:
        old_img = instance.__class__.objects.get(id=instance.id).IconImage.path
        try:
            new_img = instance.IconImage.path
        except:
            new_img = None
        if new_img != old_img:
            import os
            if os.path.exists(old_img):
                os.remove(old_img)
    except:
        pass


# 確認驗證碼

def check_captcha(captchaStr, captchaHashkey):

    if captchaStr and captchaHashkey:
        try:
            # 依據 hashkey 獲取response值
            get_captcha = CaptchaStore.objects.get(hashkey=captchaHashkey)
            if get_captcha.response == captchaStr.lower():  # 驗證通過
                return True
        except:
            return False
    else:
        return False
