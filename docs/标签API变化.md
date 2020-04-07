# 新建标签

**请求API**

* 旧：
* `/api/labels/`
* 新：
* `/api/v2/labels/`

**请求体参数**

增加如下参数：

|avatar|<span style="color:cyan;">否</span>|string|标签配图路径|

**返回数据**

原格式不变，增加了一些属性

# 删除标签及其关系

**请求API**

* 旧：
* `/api/labels/?name=<name>`
* 新：
* `/api/v2/labels/<label_id>/`

# 修改标签

**请求API**

* 旧：
* `/api/labels/`
* 新：
* `/api/v2/labels/<label_id>/`

**请求体参数**

取消`old_name`参数，增加如下参数：

|avatar|<span style="color:cyan;">否</span>|string|标签配图路径|

**返回数据**

原格式不变，增加了一些属性

# 获取顶级标签

**请求API**

* 旧：可分页
* `/api/labels/`
* 新：可分页
* `/api/v2/labels/?limit=<limit>&offset=<offset>`

**返回数据**

原格式不变，增加了一些属性

# 新建标签关系

**请求API**

* 旧：完全废弃
* `/api/labels/relations/`
* 新：
* `/api/v2/labels/<label_id>/children/`

**新接口请求体参数**

|id|<span style="color:red;">是</span>|integer|子标签ID|

**新接口返回数据**

无

# 删除标签关系

**请求API**

* 旧：完全废弃
* `/api/labels/relations/?parent=<parent>&child=<child>`
* 新：
* `/api/v2/labels/<label_id>/children/?id=<id>`

**新接口URL和查询字符串参数**

|label_id|<span style="color:red;">是</span>|integer|标签ID|

|id|<span style="color:red;">是</span>|integer|子标签ID|

**返回数据**

空

# 获取指定标签及其子标签

**请求API**

* 旧：完全废弃
* `/api/labels/relations/(?P<pk>\d+)`
* 获取指定标签的子标签，不含自身，可分页：
* `/api/v2/labels/<label_id>/children/?limit=<limit>&offset=<offset>`
* 获取指定标签的父标签，不含自身，可分页：
* `/api/v2/labels/<label_id>/parents/?limit=<limit>&offset=<offset>`

# 关注标签

**请求API**

* 旧：
* `/api/labels/follows/`
* 新：
* `/api/v2/labels/<label_id>/follow/`

**请求体参数**

不再需要

# 取消关注标签

**请求API**

* 旧：
* `/api/labels/follows/?name=<name>`
* 新：
* `/api/v2/labels/<label_id>/follow/`

# 查看本人关注的标签

**请求API**

* 旧：
* `/api/labels/follows/`
* 新：改为根据用户的slug查询他关注的标签
* `/api/v2/labels/follow/?slug=<slug>`

**请求头参数**

不再强制登录

# 查看标签详情

**请求API**

* 旧：
* `/api/labels/(?P<label_id>\d+)/`
* 新：
* `/api/v2/labels/<label_id>/`

**返回数据**

不再返回父标签`parent`、子标签`children`，本人是否已关注由`followed`改为`is_followed`

# 获取标签详情之讨论页面的问题

**请求API**

* 旧：
* `/api/labels/(?P<label_id>\d+)/discussion/`
* 新：未实现！！！

# 按关键字搜索标签

**请求API**

* 旧：
* `/api/labels/search/?kw=关键字`
* 新：未实现！！！

# 标签矩阵

**请求API**

* 旧：
* `/api/labels/wander/`
* 新：未实现！！！

# 按标题推荐标签

**请求API**

* 旧：
* `/api/labels/advice/?title=<title>`
* 新：未实现！！！
