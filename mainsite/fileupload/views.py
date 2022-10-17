import datetime
import os
from os.path import join, isfile, isdir

from django.shortcuts import render, redirect
from django.urls import reverse

from mainsite.settings import MEDIA_KEY_PREFIX
from .forms import UploadFileForm, UploadIconModelForm
from .models import UploadIcons


def home(request):
    if request.method == 'POST':
        receive_form = UploadFileForm(request.POST, request.FILES)
        receive_file = request.FILES['file']
        if receive_form.is_valid():
            message = 'The file %s (%d bytes) is correct.' % (receive_file, receive_file.size)
            print(type(receive_file))
            print('The size of file is %d bytes' % receive_file.size)
            now_time = datetime.datetime.now()
            # 避免相同檔名覆蓋
            new_file_name = now_time.strftime('%Y%m%d_%H%M%S_' + receive_file.name)
            print('File Name is %s' % new_file_name)
            path_file = MEDIA_KEY_PREFIX + 'upload/'
            print('Path: %s' % path_file)

            if os.path.exists(path_file.strip().replace('?', '')):
                print('***目錄已存在')
            else:
                os.makedirs(path_file.strip().replace('?', ''))
                print('***目錄不存在，建立目錄')

            with open(path_file + new_file_name, 'wb+') as file_save_to:
                for chunk in receive_file.chunks():
                    file_save_to.write(chunk)

        return redirect(reverse('fileupload:home'))

    upload_path = MEDIA_KEY_PREFIX + 'upload/'
    print('Path: %s' % upload_path)

    if os.path.exists(upload_path.strip().replace('?', '')):
        print('***目錄已存在')
    else:
        os.makedirs(upload_path.strip().replace('?', ''))
        print('***目錄不存在，建立目錄')
    # 取得所有檔案與子目錄名稱
    files = os.listdir(upload_path)
    print('The files in the folder: %s' % files)
    # 以迴圈處理
    images_list = []
    for file in files:
        # 產生檔案的絕對路徑
        fullpath = join(upload_path, file)
        # 判斷 fullpath 是檔案還是目錄
        if isfile(fullpath):
            images_list.append(fullpath)
            print("檔案:", file, " 路徑：", fullpath)
        elif isdir(fullpath):
            print("目錄：", file)
    icons = UploadIcons.objects.all()
    upload_form = UploadFileForm
    icon_form = UploadIconModelForm
    return render(request, 'fileupload/home.html', locals())


def savetomodel(request):
    if request.method == 'POST':
        receive_form = UploadIconModelForm(request.POST, request.FILES)
        if receive_form.is_valid():
            receive_form.save()

    return redirect(reverse('fileupload:home'))
