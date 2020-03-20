"""
统一异常码和消息
"""

# HTTP请求的数据不合格
INVALID_DATA = 20000
MSG_INVALID_DATA = "无效的请求数据"

NO_DATA = 404
MSG_NO_DATA = "指定的资源本应存在"

NOT_OWNER = 20001
MSG_NOT_OWNER = "你不是该资源的拥有者"

LOGIN_REQUIRED = 401
MSG_LOGIN_REQUIRED = "请登录"

# 读写数据库出现异常
DB_ERROR = 30000
MSG_DB_ERROR = "数据库操作出错"
