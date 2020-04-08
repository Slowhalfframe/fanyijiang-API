# 提问

* 请求API

  * 旧：
  * `/api/questions/`
  * 新：提问后自动关注
  * `/api/v2/questions/`

* 请求体参数

    原先的`labels`是标签名称的列表或逗号拼接的字符串，现在改为标签ID的列表或逗号拼接的字符串

* 旧返回数据

```json
{
    "code": 0,
    "data": {
        "title": "可逆矩阵",
        "content": "定义是什么？怎么判断？怎么求？",
        "nickname": "小学生",//已废弃
        "labels": [//从名称列表改变为对象列表
            "代数",
            "线性代数"
        ],
        "id": 1
    }
}
```

* 新返回数据

```json
{
    "code": 0,
    "data": {
        "id": 1,
        "type": "question",//新增数据
        "title": "什么是闭包？",
        "content": null,
        "author": {//新增数据，比原先的nickname更详细
            "id": "45c48cce2e2d7fbdea1afc51c7c6ad26",
            "type": "people",
            "slug": "qin",
            "nickname": "秦",
            "gender": null,
            "avatar": null,
            "autograph": null,
            "homepage": "http://192.168.0.107:9000/people/qin/"
        },
        "labels": [//改为对象列表
            {
                "id": 1,
                "type": "label",
                "name": "数学",
                "intro": null,
                "avatar": null
            }
        ],
        "create_at": "20200406 15:42:33",
        "update_at": "20200406 15:42:33",
        "answer_count": 0,//新增数据，回答数
        "comment_count": 0,//新增数据，评论数
        "follower_count": 1,//新增数据，关注者人数
        "read_nums": 3434,//新增数据，阅读次数，目前是假数据
        "is_followed": true,//新增数据，当前登录用户是否已关注该问题
        "is_answered": false//新增数据，当前登录用户是否已回答过该问题
    }
}
```

# 回答问题

* 请求API

  * 旧：
  * `/api/questions/(?P<question_id>\d+)/answers/`
  * 新：回答也可以是草稿，正式回答会删除同问题的其他回答草稿
  * `/api/v2/questions/<question_id>/answers/`

* 请求体参数

    增加如下参数：

    |is_draft|<span style="color:red;">是</span>|bool|是否是草稿|

* 旧返回数据

```json
{
    "code": 0,
    "data": {
        "question": 1,//改为对象
        "content": "随意的回答",
        "id": 9,
        "author_info": {//改名为author
            "nickname": "手机用户4zvDTn3",
            "slug": "shou-ji-yong-hu-4zvdtn3",
            "avatar": "/avatar/36dda3061ff7738850aa522ddb900f27.jpg"
        }
    }
}
```

* 新返回数据

```json
{
    "code": 0,
    "data": {
        "id": 1,
        "type": "answer",//新增数据
        "content": "包含该集合的最小闭集",
        "is_draft": true,//新增数据，是否是草稿
        "question": {//原先为ID，现在是问题对象
            "id": 1,
            "type": "question",
            "title": "什么是闭包？",
            "content": null,
            "author": {
                "id": "45c48cce2e2d7fbdea1afc51c7c6ad26",
                "type": "people",
                "slug": "qin",
                "nickname": "秦",
                "gender": null,
                "avatar": null,
                "autograph": null,
                "homepage": "http://192.168.0.107:9000/people/qin/"
            },
            "labels": [
                {
                    "id": 1,
                    "type": "label",
                    "name": "数学",
                    "intro": null,
                    "avatar": null
                }
            ],
            "create_at": "20200406 15:42:33",
            "update_at": "20200406 15:42:33"
        },
        "author": {//原先的author_info，增加了一些信息
            "id": "45c48cce2e2d7fbdea1afc51c7c6ad26",
            "type": "people",
            "slug": "qin",
            "nickname": "秦",
            "gender": null,
            "avatar": null,
            "autograph": null,
            "homepage": "http://192.168.0.107:9000/people/qin/"
        },
        "create_at": "20200406 16:11:04",
        "update_at": "20200406 16:11:04",
        "comment_count": 0,//新增数据，回答的评论数
        "vote_count": 0,//新增数据，回答的赞成票数
        "is_voted": null,//新增数据，当前用户是否已经投票或者票值
        "is_commented": false//新增数据，当前用户是否已经评论过该回答
    }
}
```

# 修改回答

* 请求API

  * 旧：
  * `/api/questions/(?P<question_id>\d+)/answers/`
  * 新：可以修改草稿，也可以在修改时发表，正式发表会删除草稿
  * `/api/v2/questions/<question_id>/answers/<answer_id>/`

* URL参数

    新增如下参数（原先一个人只能回答一次，不需要回答ID即可确定他的回答）：

    |answer_id|<span style="color:red">是</span>|integer|回答ID|

* 请求体参数

    增加如下参数：

    |is_draft|<span style="color:red;">是</span>|bool|是否是草稿|

* 返回数据

    新旧返回数据分别与回答问题的新旧数据一致

# 删除回答

* 请求API

  * 旧：
  * `/api/questions/(?P<question_id>\d+)/answers/`
  * 新：可以删除草稿
  * `/api/v2/questions/<question_id>/answers/<answer_id>/`

* URL参数

    新增如下参数（原先一个人只能回答一次，不需要回答ID即可确定他的回答）：

    |answer_id|<span style="color:red">是</span>|integer|回答ID|

# 关注问题

* 请求API

  * 旧：
  * `/api/questions/follows/`
  * 新：
  * `/api/v2/questions/<question_id>/follow/`

* 参数变动

    原先的请求体参数`id`现在移动到了URL的`question_id`处，含义不变

# 取消关注问题

* 请求API

  * 旧：
  * `/api/questions/follows/?id=<id>`
  * 新：
  * `/api/v2/questions/<question_id>/follow/`

* 参数变动

    原先的查询字符串`?id=<id>`现在移动到了URL的`question_id`处，含义不变

# 查看本人关注的问题

* 请求API

  * 旧：只能查询本人关注的问题，可分页，文档未明说
  * `/api/questions/follows/`
  * 新：改为根据用户slug查询他关注的问题，可分页
  * `/api/v2/questions/follow/?slug=<slug>&limit=<limit>&offset=<offset>`

* 请求头参数

    不再强制登录

* 查询字符串参数

    新的API参数如下：

    |slug|<span style="color:red;">是</span>|string|用户slug|

    |limit|<span style="color:cyan;">否</span>|integer|最多几条结果|

    |offset|<span style="color:cyan;">否</span>|integer|跳过几条结果|

* 旧返回数据

```json
{
    "code": 0,
    "data": {
        "results": [
            {
                "title": "1111？",
                "content": "",
                "id": 7
            }
        ],
        "total": 1
    }
}
```

* 新返回数据

    与提问的新返回数据格式相同，只是进行了分页

# 邀请回答

* 请求API

  * 旧：
  * `/api/questions/invitations/`
  * 新：
  * `/api/v2/questions/<question_id>/invite/`

* 参数变化

    原先的参数都在请求体里，现在`id`移动到了URL的`question_id`处，`invited_slug`改名为`slug`

# 撤销未回答的邀请

* 请求API

  * 旧：完全废弃，邀请不可撤销
  * `/api/questions/invitations/?id=<id>&invited_slug=<invited_slug>`

# 拒绝未回答的邀请

* 请求API

  * 旧：完全废弃，不再实现该功能
  * `/api/questions/invitations/`

# 查询邀请

* 请求API

  * 旧：完全废弃，不再实现该功能
  * `/api/questions/invitations/`

# 查询可邀请的用户

* 请求API

  * 旧：
  * `/api/questions/invitations/users/?question=<id>`
  * 新：最多返回15个用户
  * `/api/v2/questions/<question_id>/invite/users/`

* 参数变化

    问题的ID从查询字符串移动到了URL里

* 旧返回数据

```json
{
    "code": 0,
    "data": [
        {
            "nickname": "手机用户6Rl5hNU",
            "avatar": "/avatar/default_avatar.jpg",
            "slug": "shou-ji-yong-hu-6rl5hnu",
            "status": "false"//改名为is_invited，改为bool
        }
    ]
}
```

* 新返回数据

```json
{
    "code": 0,
    "data": [
        {
            "id": "1679091c5a880faf6fb5e6087eb1b2dc",
            "type": "people",
            "slug": "euler",
            "nickname": "Euler",
            "gender": null,
            "avatar": null,
            "autograph": null,
            "homepage": "http://192.168.0.107:9000/people/euler/",
            "is_invited": false//原先的status，现在为bool
        }
    ]
}
```

# 发表问答评论

* 请求API

  * 旧：改用评论的统一接口
  * `/api/questions/comments/`
  * 新：可以对问题、回答、评论发表评论
  * `/api/v2/comments/<kind>/<id>/`

* URL参数

    新增如下参数：

    |kind|<span style="color:red;">是</span>|string|只能是question、answer、comment|

    |id|<span style="color:red;">是</span>|integer|问题或回答或评论的ID|

* 请求体参数

    原先的`type`和`id`转移到了URL里，`content`保持不变

* 旧返回数据

```json
{
    "code": 0,
    "data": {
        "author_info": {//改名为author
            "nickname": "手机用户4zvDTn3",
            "slug": "shou-ji-yong-hu-4zvdtn3",
            "avatar": "/avatar/36dda3061ff7738850aa522ddb900f27.jpg"
        },
        "receiver_info": {//改名为respondent
            "nickname": "手机用户4zvDTn3",
            "slug": "shou-ji-yong-hu-4zvdtn3",
            "avatar": "/avatar/36dda3061ff7738850aa522ddb900f27.jpg"
        },
        "content": "深刻的评论",
        "create_at": "20200319 18:25:26",
        "qa_id": 1,//已废弃
        "id": 3
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
        "author": {//原先的author_info，评论的作者
            "id": "45c48cce2e2d7fbdea1afc51c7c6ad26",
            "type": "people",
            "slug": "qin",
            "nickname": "秦",
            "gender": null,
            "avatar": null,
            "autograph": null,
            "homepage": "http://192.168.0.107:9000/people/qin/",
            "is_author": true,
            "is_me": true
        },
        "respondent": {//原先的receiver_info，被评论对象的作者
            "id": "45c48cce2e2d7fbdea1afc51c7c6ad26",
            "type": "people",
            "slug": "qin",
            "nickname": "秦",
            "gender": null,
            "avatar": null,
            "autograph": null,
            "homepage": "http://192.168.0.107:9000/people/qin/",
            "is_author": true,
            "is_me": true
        },
        "create_at": "20200406 18:12:50",
        "update_at": "20200406 18:12:50",
        "children": [],//新增数据，子评论
        "vote_count": 0,//新增数据，评论的赞成票数
        "comment_count": 0,//新增数据，评论的子评论数
        "is_voted": null,//新增数据，当前用户是否已经投票或者票值
        "is_commented": false//新增数据，当前用户是否已经评论该评论
    }
}
```

# 撤销本人发表的问答评论

* 请求API

  * 旧：改用评论的统一接口
  * `/api/questions/comments/?id=<id>`
  * 新：
  * `/api/v2/comments/<comment_id>/`

* 参数变化

    评论的ID从查询字符串移动到了URL里

# 修改本人的问答评论

* 请求API

  * 旧：改用评论的统一接口
  * `/api/questions/comments/`
  * 新：
  * `/api/v2/comments/<comment_id>/`

* 请求方法

    从PATCH改为PUT

* 参数变化

    原先的请求体参数`id`移动到了URL里，`content`保持不变

* 返回数据

    新旧数据分别与发表评论的新旧数据一致

# 问答和评论投票

* 请求API

  * 旧：改用投票的统一接口
  * `/api/questions/votes/`
  * 新：新的投票或直接修改原先的投票
  * `/api/v2/votes/<kind>/<id>/`

* URL参数

    |kind|<span style="color:red;">是</span>|string|可以是answer或comment|

    |id|<span style="color:red;">是</span>|integer|被投票对象的ID|

* 请求体参数

    原先的参数`type`和`id`已经转移到了URL里，`value`现在建议采用，虽然某些字符串和数字也是有效的

# 撤销问答和评论投票

* 请求API

  * 旧：改用投票的统一接口
  * `/api/questions/votes/?id=<id>&type=<type>`
  * 新：
  * `/api/v2/votes/<kind>/<id>/`

* URL和查询字符串参数

    原先的查询字符串参数已废弃，改为如下URL参数：

    |kind|<span style="color:red;">是</span>|string|可以是answer或comment|

    |id|<span style="color:red;">是</span>|integer|被投票对象的ID|

# 查看问题详情

* 请求API

  * 旧：
  * `/api/questions/(?P<question_id>\d+)/`
  * 新：未决定返回数据格式！！！
  * `/api/v2/questions/<question_id>/?limit=<limit>&offset=<offset>`

# 查看回答详情

* 请求API

  * 旧：除自身外，额外返回一个回答
  * `/api/questions/(?P<question_id>\d+)/answers/(?P<answer_id>\d+)/`
  * 新：作者可以查看草稿，只返回自身
  * `/api/v2/questions/<question_id>/answers/<answer_id>/`

* 旧返回数据

```json
{
    "code": 0,
    "data": {//主要特点是问题与回答是分开的，而且是两个回答
        "question": {//去除了统计信息、与当前登录用户的关联信息
            "id": 1,
            "title": "我的第一个问题",
            "answer_count": 1,
            "comment_count": 0,
            "followed": false
        },
        "answer": {//回答自身
            "id": 1,
            "content": "这是一篇回答内容",
            "vote_count": 0,
            "comment_count": 0,
            "i_agreed": null,//改名为is_voted
            "create_at": "20200311 11:51:39",
            "author_info": {//改名为author
                "nickname": "手机用户4zvDTn3",
                "avatar": "/avatar/36dda3061ff7738850aa522ddb900f27.jpg",
                "autograph": "CXV工程师",
                "slug": "shou-ji-yong-hu-4zvdtn3",
                "answer_count": 3,//已废弃
                "article_count": 2,//已废弃
                "follower_count": 0,//已废弃
                "i_followed_author": false//已废弃
            }
        },
        "another_answer": null//另一个回答
    }
}
```

* 新返回数据

```json
{
    "code": 0,
    "data": {
        "id": 5,
        "type": "answer",//新增数据
        "content": "该集合与它的极限点集合的并",
        "is_draft": true,//新增数据
        "question": {//问题对象，现在附属于回答
            "id": 1,
            "type": "question",
            "title": "什么是闭包？",
            "content": null,
            "author": {
                "id": "45c48cce2e2d7fbdea1afc51c7c6ad26",
                "type": "people",
                "slug": "qin",
                "nickname": "秦",
                "gender": null,
                "avatar": null,
                "autograph": null,
                "homepage": "http://192.168.0.107:9000/people/qin/"
            },
            "labels": [
                {
                    "id": 1,
                    "type": "label",
                    "name": "数学",
                    "intro": null,
                    "avatar": null
                }
            ],
            "create_at": "20200406 15:42:33",
            "update_at": "20200406 15:42:33"
        },
        "author": {//原先的author_info，不含统计信息、与当前用户的关联信息
            "id": "45c48cce2e2d7fbdea1afc51c7c6ad26",
            "type": "people",
            "slug": "qin",
            "nickname": "秦",
            "gender": null,
            "avatar": null,
            "autograph": null,
            "homepage": "http://192.168.0.107:9000/people/qin/"
        },
        "create_at": "20200406 16:23:34",
        "update_at": "20200406 16:34:50",
        "comment_count": 0,//新增数据，回答的评论数
        "vote_count": 0,//新增数据，回答的赞成票数
        "is_voted": null,//原先的i_agreed，当前用户是否已经投票或票值
        "is_commented": false//新增数据，当前用户是否已经评论
    }
}
```

# 查看问题的所有评论

* 请求API

  * 旧：改用评论的统一接口，有分页，文档未明说
  * `/api/questions/(?P<question_id>\d+)/comments/`
  * 新：可分页
  * `/api/v2/comments/question/<id>/?limit=<limit>&offset=<offset>`

* URL和查询字符串参数

    |id|<span style="color:red;">是</span>|integer|问题的ID|

    |limit|<span style="color:cyan;">否</span>|integer|最多几条结果|

    |offset|<span style="color:cyan;">否</span>|integer|跳过几条结果|

* 返回数据

    新旧数据分别与写评论的新旧数据一致，但都进行了分页

# 查看回答的所有评论

* 请求API

  * 旧：改用评论的统一接口，有分页，文档未明说
  * `/api/questions/(?P<question_id>\d+)/answers/(?P<answer_id>\d+)/comments/`
  * 新：可分页
  * `/api/v2/comments/answer/<id>/?limit=<limit>&offset=<offset>`

* URL和查询字符串参数

    |id|<span style="color:red;">是</span>|integer|回答的ID|

    |limit|<span style="color:cyan;">否</span>|integer|最多几条结果|

    |offset|<span style="color:cyan;">否</span>|integer|跳过几条结果|

* 返回数据

    新旧数据分别与写评论的新旧数据一致，但都进行了分页

# 新增了一些与回答草稿有关的API
