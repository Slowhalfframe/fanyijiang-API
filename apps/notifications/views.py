from apps.utils.api import CustomAPIView
from apps.notifications.models import Notification
from apps.notifications.serializers import NotificationsSerializer

from apps.userpage.models import UserProfile
from apps.utils.decorators import validate_identity


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

        if no_type:
            NOTIFICATION_TYPE = ['LAN', 'LAR', 'LC', 'CAN', 'CAR', 'CQ', 'R', 'FAN', 'FAR', 'A', 'I', 'O']
            if no_type.upper() not in NOTIFICATION_TYPE:
                return self.error('错误的通知类型', 10089)
            # TODO 是否要根据日期进行筛选
            nos = Notification.objects.filter(recipient__uid=uid, verb=no_type.upper())
        else:
            nos = Notification.objects.filter(recipient__uid=uid)
        # 在获取的时候就已经把所有未读的变成已读
        Notification.objects.filter(recipient__uid=uid, unread=True).update(unread=False)
        # data = NotificationsSerializer(nos, many=True).data

        data = self.paginate_data(request, nos, NotificationsSerializer)
        # 重组数据格式
        if display_type == 'all':
            results = data['results']
            results_data = list()
            while 0 < len(results):
                first_result = results[0]
                first_time = first_result.get('format_time')
                r_data = {'no_date': first_time, 'data_list': list()}
                for r in results[:]:
                    if r.get('format_time') == first_time:
                        r.pop('format_time')
                        r_data['data_list'].append(r)
                        results.remove(r)
                results_data.append(r_data)
            data['results'] = results_data
        return self.success(data)
