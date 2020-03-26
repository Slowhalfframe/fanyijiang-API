"""
统一异常码和消息
"""

# HTTP请求的数据不合格
INVALID_DATA = 20000
MSG_INVALID_DATA = "请求数据无效或已经被占用"
MSG_NO_KW = "必须有关键字"

NO_DATA = 404
MSG_NO_DATA = "指定的资源本应存在"

NOT_OWNER = 20001
MSG_NOT_OWNER = "你不是该资源的拥有者"

LABEL_USING = 20002
MSG_LABEL_USING = "该标签正在被某个文章或问题使用"

INVITATION_DONE = 20003
MSG_INVITATION_DONE = "只能处理未回答的邀请"

NO_LABELS = 20004
MSG_NO_LABELS = "为文章或问题指定的标签不存在"

INVALID_SLUG = 20005
MSG_INVALID_SLUG = "无效的用户别名"

LOGIN_REQUIRED = 401
MSG_LOGIN_REQUIRED = "请登录"

# 读写数据库出现异常
DB_ERROR = 30000
MSG_DB_ERROR = "数据库操作出错"
