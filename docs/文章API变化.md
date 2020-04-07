# 发表文章

* 请求API

  * 旧：
  * `/api/articles/`
  * 新：支持写草稿
  * `/api/v2/articles/`

* 请求体参数

  * `image`统一更名为`cover`
  * `labels`原先是标签名称的列表或逗号拼接的字符串，现在是标签ID的列表或逗号拼接的字符串
  * 表示文章状态的参数从`status`变为`is_draft`，分别描述如下：

    |status|否|string|draft或published，默认为draft|

    |is_draft|<span style="color:red;">是</span>|bool|没有默认值|

* 旧返回数据

```json
{
    "code": 0,
    "data": {
        "id": 1,
        "author_info": {//改名为author
            "nickname": "haoran·zhang",
            "avatar": "/avatar/0b5171bc39a9aec05a8f6cb7a185b769.jpg",
            "slug": "zhanghaoran",
            "autograph": "CV工程师"
        },
        "title": "我的第一篇文章",
        "content": "文章内容文章内容",
        "image": null,//改名为cover
        "status": "published",//改名为is_draft，类型改为bool
        "create_at": "20200311 11:48:00",
        "update_at": "20200311 11:48:03",
        "labels": [
            {
                "id": 1,
                "name": "标签"
            }
        ]
    }
}
```

* 新返回数据

```json
{
    "code": 0,
    "data": {
        "id": 1,
        "type": "article",//新增数据
        "title": "闭区间套引理",
        "content": "闭区间套之交非空",
        "cover": null,//原先的image
        "is_draft": false,//原先的status，现为bool
        "author": {//原先的author_info
            "id": "45c48cce2e2d7fbdea1afc51c7c6ad26",//新增数据
            "type": "people",//新增数据
            "slug": "qin",
            "nickname": "秦",
            "gender": null,//新增数据
            "avatar": null,
            "autograph": null,
            "homepage": "http://192.168.0.107:9000/people/qin/" //新增数据
        },
        "labels": [
            {
                "id": 1,
                "type": "label",//新增数据
                "name": "数学",
                "intro": null,//新增数据
                "avatar": null//新增数据
            }
        ],
        "create_at": "20200406 14:04:01",
        "update_at": "20200406 14:04:01",
        "comment_count": 0,//新增数据，评论数
        "vote_count": 0,//新增数据，赞成票数
        "follower_count": 0,//新增数据，关注者数
        "is_voted": null,//新增数据，null或bool，表示未投票或当前用户的票值
        "is_commented": false,//新增数据，bool,当前用户是否已经评论
        "is_followed": false//新增数据，bool，当前用户是否已经关注
    }
}
```

# 更新文章

* 请求API

  * 旧：
  * `/api/articles/`
  * 新：也可以修改草稿
  * `/api/v2/articles/<article_id>/`

* 请求体参数

  * 不再需要`id`，已经放到了URL里
  * `image`统一更名为`cover`
  * `labels`原先是标签名称的列表或逗号拼接的字符串，现在是标签ID的列表或逗号拼接的字符串
  * 表示文章状态的参数从`status`变为`is_draft`，分别描述如下：

    |status|否|string|draft或published，默认为draft|

    |is_draft|<span style="color:red;">是</span>|bool|没有默认值|

* 返回数据

    新旧数据分别与写文章的新旧数据一致

# 发表草稿

* 请求API

  * 旧：
  * `/api/articles/`
  * 新：
  * `/api/v2/articles/drafts/`

* 请求方法由PATCH变为POST

# 查看非草稿文章的列表

* 请求API

  * 旧：可分页，文档没有明说
  * `/api/articles/`
  * 新：可分页
  * `/api/v2/articles/?limit=<limit>&offset=<offset>`

* 返回数据

与写文章、修改文章类似，只是进行了分页

# 查看草稿箱

* 请求API

  * 旧：可分页，文档没有明说
  * `/api/articles/drafts/`
  * 新：可分页
  * `/api/v2/articles/drafts/?limit=<limit>&offset=<offset>`

* 返回数据

与写文章、修改文章类似，只是进行了分页

# 查看文章详情

* 请求API

  * 旧：
  * `/api/articles/(?P<article_id>\d+)/`
  * 新：也可以查看草稿，查看草稿需要登录
  * `/api/v2/articles/<article_id>/`

* 旧返回数据

```json
{
    "code": 0,
    "data": {
        "id": 1,
        "author_info": {//改名为author
            "nickname": "haoran·zhang",
            "avatar": "/avatar/0b5171bc39a9aec05a8f6cb7a185b769.jpg",
            "slug": "zhanghaoran",
            "autograph": "CV工程师"
        },
        "title": "我的第一篇文章",
        "content": "文章内容",
        "image": null,//改名为cover
        "status": "published",//改名为is_draft，改为bool类型
        "create_at": "20200311 11:48:00",
        "update_at": "20200311 11:48:03",
        "labels": [],
        "vote_count": 0,
        "comment_count": 0,
        "voted":null//改名为is_voted
    }
}
```

* 新返回数据

与写文章、修改文章等一致

# 伪删除文章

* 请求API

  * 旧：
  * `/api/articles/(?P<article_id>\d+)/`
  * 新：可以删除草稿
  * `/api/v2/articles/<article_id>/`

# 评论文章

* 请求API

  * 旧：完全废弃
  * `/api/articles/comments/`
  * 新：采用统一的评论接口，支持对评论发表评论
  * `/api/v2/comments/<kind>/<id>/`

* URL参数

    |kind|<span style="color:red;">是</span>|string|只能是article或comment|

    |id|<span style="color:red;">是</span>|integer|文章或评论的ID|

* 请求体参数

    |content|<span style="color:red;">是</span>|string|评论内容|

* 旧返回数据

```json
{
    "code": 0,
    "data": {
        "id": 3,
        "article": 1,//废弃数据
        "author_info": {//改名为author
            "nickname": "手机用户4zvDTn3",
            "avatar": "/avatar/36dda3061ff7738850aa522ddb900f27.jpg",
            "slug": "shou-ji-yong-hu-4zvdtn3"
        },
        "receiver_info": {//改名为respondent
            "nickname": "haoran·zhang",
            "avatar": "/avatar/0b5171bc39a9aec05a8f6cb7a185b769.jpg",
            "slug": "zhanghaoran"
        },
        "content": "妙笔生花",
        "create_at": "20200319 12:07:00",
        "vote_count": 0,
        "is_author":false//评论者是否是文章作者，已经移动到了author和respondent里
    }
}
```

* 新返回数据

```json
{
    "code": 0,
    "data": {
        "id": 1,
        "type": "comment",//新增数据
        "content": "closure",
        "author": {//原名author_info
            "id": "45c48cce2e2d7fbdea1afc51c7c6ad26",//新增数据
            "type": "people",//新增数据
            "slug": "qin",
            "nickname": "秦",
            "gender": null,
            "avatar": null,
            "autograph": null,
            "homepage": "http://192.168.0.107:9000/people/qin/",//新增数据
            "is_author": true,//新增数据，评论者是否是文章作者
            "is_me": true//新增数据，评论者是不是当前登录用户
        },
        "respondent": {//原名receiver_info
            "id": "45c48cce2e2d7fbdea1afc51c7c6ad26",//新增数据
            "type": "people",//新增数据
            "slug": "qin",
            "nickname": "秦",
            "gender": null,
            "avatar": null,
            "autograph": null,
            "homepage": "http://192.168.0.107:9000/people/qin/",//新增数据
            "is_author": true,//新增数据，被评论者是否是文章作者
            "is_me": true//新增数据，被评论者是不是当前登录用户
        },
        "create_at": "20200406 18:12:50",
        "update_at": "20200406 18:12:50",
        "children": [],//新增数据，评论的子评论
        "vote_count": 0,
        "comment_count": 0,//新增数据，评论的子评论数
        "is_voted": null,//新增数据，bool或null，当前登录用户是否已投票或票值
        "is_commented": false//新增数据，当前登录用户是否已经评论该评论
    }
}
```

# 撤销评论文章

* 请求API

  * 旧：
  * `/api/articles/comments/?id=<id>`
  * 新：采用统一的评论接口，支持撤销评论的评论
  * `/api/v2/comments/<comment_id>/`

* 参数

    原先的`id`和现在的`comment_id`都是评论的ID

# 修改文章评论

* 请求API

  * 旧：
  * `/api/articles/comments/`
  * 新：采用统一的评论接口，支持修改评论的评论
  * `/api/v2/comments/<comment_id>/`

* 请求体参数

    废弃`id`参数，保留`content`参数

* 返回数据

    新旧数据分别与发表评论的新旧数据一致

# 文章和评论投票

* 请求API

  * 旧：完全废弃
  * `/api/articles/votes/`
  * 新：采用统一的投票接口，可投票或直接修改原来的投票
  * `/api/v2/votes/<kind>/<id>/`

* URL参数

    |kind|<span style="color:red;">是</span>|string|只能是article或comment|

    |id|<span style="color:red;">是</span>|integer|文章或评论的ID|

* 请求体参数

    |value|<span style="color:red;">是</span>|bool|赞成还是反对|

# 撤销文章和评论投票

* 请求API

  * 旧：
  * `/api/articles/votes/?id=<id>&type=<type>`
  * 新：采用统一的投票接口
  * `/api/v2/votes/<kind>/<id>/`

* 参数

    原来的查询字符串参数改为URL参数，`type`改名为`kind`，只能是article或comment，`id`的含义不变

# 获取文章的所有评论

* 请求API

  * 旧：可分页，文档未明说
  * `/api/articles/(?P<article_id>\d+)/comments/`
  * 新：采用统一的评论接口，可分页，支持获取评论的评论
  * `/api/v2/comments/<kind>/<id>/?limit=<limit>&offset=<offset>`

* URL和查询字符串参数

    |kind|<span style="color:red;">是</span>|string|只能是article或comment|

    |id|<span style="color:red;">是</span>|integer|被评论对象的ID|

    |limit|<span style="color:cyan;">否</span>|integer|最多几条结果|

    |offset|<span style="color:cyan;">否</span>|integer|跳过几条结果|

** 返回结果

新旧结果与写评论、修改评论的新旧结果一致，只是都进行了分页

# 根据当前文章获取推荐的文章

* 请求API

  * 旧：
  * `/api/articles/(?P<article_id>\d+)/recommend/`
  * 新：未实现！！！

# v2实现了关注文章的相关API，v1没有
