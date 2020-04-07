from apps.utils_v2.api import CustomAPIView
from apps.notifications_v2.models import Notification
from apps.notifications_v2.serializers import NotificationsSerializer

from apps.userpage.models import UserProfile
from apps.utils_v2.decorators import validate_identity


class NotificationAPIView(CustomAPIView):
    '''获取所有通知'''

    @validate_identity
    def get(self, request):
        uid = request._request.uid
        user = UserProfile.objects.filter(uid=uid).first()
        if not user:
            return self.error('用户不存在', 404)
        no_type = request.GET.get('no_type')
        display_type = request.GET.get('display_type')
        print(no_type)
        if no_type:
            no_type_list = no_type.upper().split(',')
            # NOTIFICATION_TYPE = ['LAN', 'LAR', 'LC', 'CAN', 'CAR', 'CQ', 'R', 'FAN', 'FAR', 'A', 'I', 'O']
            # if no_type.upper() not in NOTIFICATION_TYPE:
            #     return self.error('错误的通知类型', 10089)
            # TODO 是否要根据日期进行筛选
            nos = Notification.objects.filter(recipient__uid=uid, verb__in=no_type_list)
        else:
            nos = Notification.objects.filter(recipient__uid=uid)
        # 在获取的时候就已经把所有未读的变成已读
        Notification.objects.filter(recipient__uid=uid, unread=True).update(unread=False)
        # data = NotificationsSerializer(nos, many=True).data
        # nos = [no for no in nos if no.action_object != None]
        data = self.paginate_data(request, nos, NotificationsSerializer)
        # 重组数据格式
        if display_type == 'all':
            # TODO 建议
            # a = {}
            # for i in data["results"]:
            #     if i.get("format_time") not in a:
            #         a[i.get("format_time")] = [i]
            #     else:
            #         a[i.get("format_time")].append(i)
            # data["results"] = [{"no_date":key,"data_list":value} for key,value in a.items()]
            results = data['results']
            results_data = list()
            while 0 < len(results):
                first_result = results[0]
                first_time = first_result.get('format_time')
                r_data = {'no_date': first_time, 'data_list': list()}
                for r in results[:]:
                    if r.get('format_time') == first_time:
                        r_data['data_list'].append(r)
                        results.remove(r)
                results_data.append(r_data)
            data['results'] = results_data
        return self.success(data)


class UnReadCountAPIView(CustomAPIView):
    @validate_identity
    def get(self, request):
        uid = request._request.uid
        count = Notification.objects.filter(recipient__uid=uid, unread=True).count()
        return self.success(count)