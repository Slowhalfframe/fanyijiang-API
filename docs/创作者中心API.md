# 创作者中心

## 网管地址
- http://xxx:xxx/api/creator

# 公共API
### 1.创作者中心主页

**请求API：**
- `/`

**请求方式：**
- GET    

**参数：** 
无
 **返回示例**

``` 
  {
    "code": 0,
    "data": {
        "creator_data": {
            "upvotes": {
                "ysd_upvote": 0,
                "total_upvote": 0
            },
            "read_nums": {
                "total_ysd_read_nums": 0,
                "total_read_nums": 5466
            },
            "fans": {
                "total_fans": 2,
                "ysd_add_fans": 0
            }
        },
        "recent_data": [
            {
                "create_at": "2020-03-03T14:24:40",
                "read_nums": 0,
                "display_content": "111",
                "id": 26,
                "collect_count": 0,
                "comment_count": 0,
                "upvote_count": 0,
                "display_title": "问题6",
                "type": "answer"
            },
            {
                "create_at": "2020-03-03T14:23:44",
                "read_nums": 0,
                "display_content": "111",
                "id": 25,
                "collect_count": 0,
                "comment_count": 0,
                "upvote_count": 0,
                "display_title": "问题7",
                "type": "answer"
            },
            {
                "create_at": "2020-02-25T18:11:31",
                "read_nums": 0,
                "display_content": "内容111",
                "id": 1,
                "collect_count": 0,
                "comment_count": 0,
                "upvote_count": 0,
                "display_title": "文章1",
                "type": "article"
            }
        ]
    }
}
```
------------------

### 2.内容分析页

**请求API：**
- `/creator_data`

**请求方式：**
- GET    

**参数：** 

|参数名|必选|说明|
|:---|:---|:---|
|include|是|内容类型：answer:回答；article:文章；think:想法|

 **返回示例**

``` 
{
    "code": 0,
    "data": {
        "ysd_upvote_nums": 0,
        "upvote_nums": 0,
        "read_nums": 0,
        "ysd_read_nums": 0,
        "total_count": 0
    }
}
```
------------------

### 3.内容分析页所有回答等

**请求API：**
- `/statistics_date_content`

**请求方式：**
- GET    

**参数：** 

|参数名|必选|说明|
|:---|:---|:---|
|data_type|是|内容类型：answer:回答；article:文章；think:想法|
|begin_date|是|开始日期，格式为：20200222|
|end_date|是|结束日期，格式为：20200301|

 **返回示例**

``` 
{
    "code": 0,
    "data": [
        {
            "comment_nums": 0,
            "statistics_date": "20200222",
            "upvote_nums": 0,
            "read_nums": 0,
            "collect_nums": 0
        },
        {
            "comment_nums": 0,
            "statistics_date": "20200223",
            "upvote_nums": 0,
            "read_nums": 2,
            "collect_nums": 0
        },
        {
            "comment_nums": 0,
            "statistics_date": "20200224",
            "upvote_nums": 0,
            "read_nums": 0,
            "collect_nums": 0
        },
        {
            "comment_nums": 0,
            "statistics_date": "20200225",
            "upvote_nums": 0,
            "read_nums": 0,
            "collect_nums": 1
        },
        {
            "comment_nums": 0,
            "statistics_date": "20200226",
            "upvote_nums": 0,
            "read_nums": 0,
            "collect_nums": 0
        },
        {
            "comment_nums": 0,
            "statistics_date": "20200227",
            "upvote_nums": 0,
            "read_nums": 0,
            "collect_nums": 0
        },
        {
            "comment_nums": 0,
            "statistics_date": "20200228",
            "upvote_nums": 0,
            "read_nums": 0,
            "collect_nums": 0
        },
        {
            "comment_nums": 0,
            "statistics_date": "20200229",
            "upvote_nums": 0,
            "read_nums": 0,
            "collect_nums": 0
        }
    ]
}
```
------------------

### 4.单篇内容分析

**请求API：**
- `/single_content`

**请求方式：**
- GET    

**参数：** 

|参数名|必选|说明|
|:---|:---|:---|
|data_type|是|内容类型：answer:回答；article:文章；think:想法|
|begin_date|是|开始日期，格式为：20200222|
|end_date|是|结束日期，格式为：20200301|

 **返回示例**

``` 
{
    "code": 0,
    "data": [
        {
            "comment_nums": 0,
            "id": 2,
            "upvote_nums": 0,
            "read_nums": 1857,
            "title": "回答2",
            "collect_nums": 0,
            "create_at": "2020-02-23T16:57:52"
        },
        {
            "comment_nums": 0,
            "id": 3,
            "upvote_nums": 0,
            "read_nums": 111,
            "title": "回答3",
            "collect_nums": 0,
            "create_at": "2020-02-23T17:01:10"
        },
        {
            "comment_nums": 0,
            "id": 4,
            "upvote_nums": 0,
            "read_nums": 1002,
            "title": "回答4",
            "collect_nums": 0,
            "create_at": "2020-02-23T17:10:20"
        }
    ]
}
```
------------------

### 5.问题推荐

**请求API：**
- `/recommend_question`

**请求方式：**
- GET    

**参数：** 

|参数名|必选|说明|
|:---|:---|:---|
|question_type|是|问题类型：recommend:为你推荐；new:最新问题；invited:邀请回答|
|offset|否|分页偏移量|
|limmit|否|每页多少条目|

 **返回示例**

``` 
{
    "data": [
        {
            "id": 3,
            "answer_count": 0,
            "content": null,
            "title": "问题3",
            "follow_count": 0
        },
        {
            "id": 5,
            "answer_count": 0,
            "content": null,
            "title": "问题5",
            "follow_count": 0
        },
        {
            "id": 4,
            "answer_count": 0,
            "content": null,
            "title": "问题4",
            "follow_count": 0
        }
    ],
    "code": 0
}
```
------------------

### 6.创作者榜单

**请求API：**
- `/creator_list`

**请求方式：**
- GET    

**参数：** 

|参数名|必选|说明|
|:---|:---|:---|
|several_id|否|无则是所有榜单，有则是某一个榜单里边的内容|


 **返回示例：所有榜单**

``` 
{
    "code": 0,
    "data": [
        {
            "title": "第8期榜单",
            "image": null,
            "id": 8
        },
        {
            "title": "第7期榜单",
            "image": null,
            "id": 7
        },
        {
            "title": "第6期榜单",
            "image": null,
            "id": 6
        },
        {
            "title": "第5期榜单",
            "image": null,
            "id": 5
        },
        {
            "title": "第4期榜单",
            "image": null,
            "id": 4
        },
        {
            "title": "第3期榜单",
            "image": null,
            "id": 3
        },
        {
            "title": "第2期榜单",
            "image": null,
            "id": 2
        },
        {
            "title": "第1期榜单",
            "image": null,
            "id": 1
        }
    ]
}
```

**返回示例：某一个榜单的内荣**

``` 
{
    "code": 0,
    "data": [
        {
            "author_data": {
                "nickname": "手机用户98hB5co",
                "avatar": "/avatar\\default_avatar.jpg"
            },
            "score": 1672500,
            "title": "问题2",
            "content_type": "answer",
            "id": 2
        },
        {
            "author_data": {
                "nickname": "手机用户111111",
                "avatar": "/avatar\\default_avatar.jpg"
            },
            "score": 903000,
            "title": "问题！",
            "content_type": "answer",
            "id": 4
        },
        {
            "author_data": {
                "nickname": "手机用户98hB5co",
                "avatar": "/avatar\\default_avatar.jpg"
            },
            "score": 790000,
            "title": "问题！",
            "content_type": "answer",
            "id": 1
        },
        {
            "author_data": {
                "nickname": "手机用户8Nd93MZ",
                "avatar": "/avatar\\default_avatar.jpg"
            },
            "score": 101100,
            "title": "问题！",
            "content_type": "answer",
            "id": 3
        },
        {
            "author_data": {
                "nickname": "手机用户98hB5co",
                "avatar": "/avatar\\default_avatar.jpg"
            },
            "score": 1200,
            "title": "文章1",
            "content_type": "article",
            "id": 1
        }
    ]
}
```

---------