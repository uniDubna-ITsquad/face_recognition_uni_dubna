from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.http import JsonResponse
from django.conf import settings
from main_server.models import Cameras, ScreensFeatures, ProcessedScreens
from django.views.decorators.csrf import csrf_exempt
import datetime
import json
import cv2

def get_ind_from_time(time):
    ind = 0
    
    if ('hour' in dir(time)):
        ind += time.hour * 5 * 60 * 60
    if ('minute' in dir(time)):
        ind += time.minute * 5 * 60
    if ('second' in dir(time)):
        ind += time.second * 5
    if ('seconds' in dir(time)):
        ind += time.seconds * 5
    if ('microsecond' in dir(time)):
        ind += round(time.microsecond / 1000 / 200)
    if ('microseconds' in dir(time)):
        ind += round(time.microseconds / 1000 / 200)
    
    return ind

def get_time_by_ind(ind):
    time = datetime.timedelta(
        microseconds = ind * 200000
    )
    return time

def index(request):
    if request.method == 'GET':
        res = ''
        distinct_public_screens = ProcessedScreens.objects.all().filter(
            path__contains = 'public'
        ).distinct(
            'camera_ip'
        )

        for distinct_screen in distinct_public_screens:
            res += f"""\
            <p><a href='{distinct_screen.camera_ip.ip}'>{distinct_screen.camera_ip.ip}</a></p>
            """
        print(res)
        return HttpResponse(res)
    raise Http404("Poll does not exist")

def cam(request, cam_ip):
    if request.method == 'GET':
        res = ''
        cam_screens_dates = ProcessedScreens.objects.all().filter(
            path__contains = 'public',
            camera_ip = cam_ip
        ).distinct(
            'camera_ip', 'date__date'
        ).order_by(
            'date__date'
        )
        for cam_date in cam_screens_dates:
            year = cam_date.date.year
            month = cam_date.date.month
            day = cam_date.date.day
            link = '{}/{}/{}/{}/preview'.format(
                cam_ip, year, month, day
            )
            text = '{}-{}-{}'.format(
                year, month, day
            )
            res += '<p><a href="{}">{}</a></p>\n'.format(
                link, text
            )
        return HttpResponse(res)
    raise Http404("Poll does not exist")

@csrf_exempt
def cam_preview(request, cam_ip, year, month, day):
    if request.method == 'GET':
        cam_screens_times = ProcessedScreens.objects.all().filter(
            path__contains = 'public',
            camera_ip = cam_ip,
            date__date = datetime.datetime(year, month, day)
        ).order_by(
            'date'
        )

        time_data = {}
        pre_ind = None
        pre_list = None
        for screen_param in cam_screens_times:
            time = screen_param.date.time()
            ind = get_ind_from_time(time)
            val = '1' if screen_param.total_face > 0 else '0'
            if ind - 1 == pre_ind:
                pre_list.append(val)
            else:
                pre_list = [val]
                time_data[ind] = pre_list
            pre_ind = ind

        data = {}
        data['test'] = 'test'
        data['time_data'] = time_data

        # print(data)

        form_action_url = ''
        context = {
            'form_action_url': form_action_url,
            'data': data
        }
        return render(request, 'cam_preview.html', context)
    if request.method == 'POST':

        ind = int(request.POST['ind'])

        time = get_time_by_ind(ind)
        find_date = datetime.datetime(year, month, day) + time

        find_date_gt = find_date - datetime.timedelta(microseconds = 100 * 1000)
        find_date_lt = find_date + datetime.timedelta(microseconds = 100 * 1000)

        res_screen = ProcessedScreens.objects.all().filter(
            camera_ip = cam_ip,
            date__gt = find_date_gt,
            date__lt = find_date_lt
        )[0]


        screen_path = \
            settings.MEDIA_ROOT + \
            res_screen.path.replace('media/public', '')

        frame_nd = cv2.imread(screen_path)

        data = {'frame': frame_nd.tolist()}
        return HttpResponse(json.dumps(data), content_type="application/json")
        # return JsonResponse(data)

    raise Http404("Poll does not exist")