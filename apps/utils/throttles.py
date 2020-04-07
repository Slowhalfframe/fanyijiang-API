from rest_framework.throttling import BaseThrottle

VISIT_RECORD = {}


class VisitThrottle(BaseThrottle):

    def __init__(self):
        self.history = None

    def allow_request(self, request, view):
        remote_addr = request.META.get('REMOTE_ADDR')
        print(remote_addr)
        import time
        ctime = time.time()

        if remote_addr not in VISIT_RECORD:
            VISIT_RECORD[remote_addr] = [ctime, ]
            return True

        history = VISIT_RECORD.get(remote_addr)
        self.history = history

        while history and history[-1] < ctime - 60:
            history.pop()

        if len(history) < 3:
            history.insert(0, ctime)
            return True
        else:
            return False

    def wait(self):
        import time
        ctime = time.time()
        return 60 - (ctime - self.history[-1])
