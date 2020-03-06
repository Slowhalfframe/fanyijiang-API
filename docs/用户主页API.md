# 用户主页API

## 网管地址
- http://xxx:xxx/api/userpage

# 公共API
### 1.获取用户信息

**请求API：**
- `/`+用户url别名slug
- 例: `/shou-ji-yong-hu-8nd93mz`

**请求方式：**
- GET    

**参数：** 
无
 **返回示例**

``` 
  {
    "code": 0,
    "data": {
        "uid": "c9f0f895fb98ab9159f51fd0297e236d",
        "nickname": "手机用户8Nd93MZ",
        "avatar": "/avatar\\default_avatar.jpg",
        "autograph": null,
        "industry": null,
        "employment_history": [],
        "education_history": [],
        "locations": [],
        "description": null,
        "slug": "shou-ji-yong-hu-8nd93mz",
        "create_content_nums": {
            "think_count": 0,
            "article_count": 0,
            "answer_count": 1,
            "question_count": 4,
            "collect_count": 0
        }
    }
}
```
------------------

### 2.个人成就

**请求API：**
- `/self_achievement/`+用户url别名slug
- 例: `/self_achievement/shou-ji-yong-hu-8nd93mz`

**请求方式：**
- GET    

**参数：** 
无
 **返回示例**

``` 
  {
    "code": 0,
    "data": {
        "upvote_count": 0,
        "collect_count": 0
    }
}
```
------------------

### 2.用户关注

**需要在请求头中设置authorization验证token**

#### 2.1 获取当前用户我是否已经关注,用于在其他用户主页关注按钮判定
**请求API：**
- `/following_user/`+用户url别名slug
- 例: `/following_user/shou-ji-yong-hu-8nd93mz`

**请求方式：**
- GET    

**参数** 

无

 **返回示例**

``` 
 {
    "code": 0,
    "data": {
        "followed": false
    }
}
```
------------------

#### 2.2 关注用户
**请求API：**
- `/following_user/`+用户url别名slug
- 例: `/following_user/shou-ji-yong-hu-8nd93mz`

**请求方式：**
- POST    

**参数：** 
无
 **返回示例**

``` 
 {
    "code": 0,
    "data": null
}
```
------------------

#### 2.3 取消关注
**请求API：**
- `/following_user/`+用户url别名slug
- 例: `/following_user/shou-ji-yong-hu-8nd93mz`

**请求方式：**
- DELETE    

**参数：** 
无
 **返回示例**

``` 
 {
    "code": 0,
    "data": null
}
```
------------------

### 3 用户发起的问题列表
**请求API：**
- `/question_list/`+用户url别名slug
- 例: `/question_list/shou-ji-yong-hu-8nd93mz`

**请求方式：**
- GET    

**参数：** 
无
 **返回示例**

``` 
 {
    "code": 0,
    "data": {
        "total": 4,
        "results": [
            {
                "id": 3,
                "title": "问题3",
                "content": null,
                "create_time": "20200225 22:30:09",
                "answer_count": 0,
                "follow_count": 0
            },
            {
                "id": 4,
                "title": "问题4",
                "content": null,
                "create_time": "20200227 13:47:09",
                "answer_count": 0,
                "follow_count": 0
            },
            {
                "id": 5,
                "title": "问题5",
                "content": null,
                "create_time": "20200227 13:47:23",
                "answer_count": 0,
                "follow_count": 0
            },
            {
                "id": 6,
                "title": "问题6",
                "content": null,
                "create_time": "20200227 13:47:33",
                "answer_count": 1,
                "follow_count": 0
            }
        ]
    }
}
```
------------------

### 4 用户的回答列表
**请求API：**
- `/answer_list/`+用户url别名slug
- 例: `/answer_list/shou-ji-yong-hu-8nd93mz`

**请求方式：**
- GET    

**参数：** 
无
 **返回示例**

``` 
 {
    "code": 0,
    "data": {
        "results": [
            {
                "id": 3,
                "content": "回答3",
                "question_id": 1,
                "question_title": "问题！",
                "user_info": {
                    "user_slug": "shou-ji-yong-hu-8nd93mz",
                    "avatar": "/avatar\\default_avatar.jpg",
                    "nickname": "手机用户8Nd93MZ"
                }
            }
        ],
        "total": 1
    }
}
```
------------------

### 5 用户的文章列表
**请求API：**
- `/article_list/`+用户url别名slug
- 例: `/article_list/shou-ji-yong-hu-8nd93mz`

**请求方式：**
- GET    

**参数：** 
无
 **返回示例**

``` 
{
    "code": 0,
    "data": {
        "results": [
            {
                "title": "纹章3",
                "content": "达到",
                "update_time": "20200304 16:50:20",
                "comment_count": 0,
                "upvote_count": 0,
                "author_info": {
                    "nickname": "手机用户8Nd93MZ",
                    "slug": "shou-ji-yong-hu-8nd93mz",
                    "avatar": "/avatar\\default_avatar.jpg"
                }
            }
        ],
        "total": 1
    }
}
```
------------------

### 6 用户的想法列表
**请求API：**
- `/think_list/`+用户url别名slug
- 例: `/think_list/shou-ji-yong-hu-8nd93mz`

**请求方式：**
- GET    

**参数：** 
无
 **返回示例**

``` 
{
    "code": 0,
    "data": {
        "total": 0,
        "results": []
    }
}
```
------------------

### 7 收藏夹列表
**请求API：**
- `/favorites_list/`+用户url别名slug
- 例: `/favorites_list/shou-ji-yong-hu-8nd93mz`

**请求方式：**
- GET    

**参数：** 
无
 **返回示例**

``` 
{
    "code": 0,
    "data": {
        "total": 0,
        "results": []
    }
}
```
------------------

### 8 收藏夹列表
**请求API：**
- `/favorites_list/`+用户url别名slug
- 例: `/favorites_list/shou-ji-yong-hu-8nd93mz`

**请求方式：**
- GET    

**参数：** 
无
 **返回示例**

``` 
{
    "code": 0,
    "data": {
        "total": 0,
        "results": []
    }
}
```
------------------

### 9 关注用户数量和被关注的数量
**请求API：**
- `/followed_user_count/`+用户url别名slug
- 例: `/followed_user_count/shou-ji-yong-hu-8nd93mz`

**请求方式：**
- GET    

**参数：** 
无
 **返回示例**

``` 
{
    "code": 0,
    "data": {
        "idol_nums": 0,
        "fans_nums": 2
    }
}
```
------------------

### 9 关注用户详情

**需要在请求头中设置authorization验证token**

**请求API：**
- `/followed_user/`+用户url别名slug
- 例: `/followed_user/shou-ji-yong-hu-8nd93mz`

**请求方式：**
- GET    

**参数：** 

|参数名|必选|说明|
|:-----|:----|:------|
|include|是|粉丝或者偶像, idol:我关注的人,fans:关注我的人|

 **返回示例**

``` 
{
    "code": 0,
    "data": {
        "idol_nums": 0,
        "fans_nums": 2
    }
}
```
------------------

### 10 关注的收藏夹

**请求API：**
- `/followed_favorites/`+用户url别名slug
- 例: `/followed_favorites/shou-ji-yong-hu-8nd93mz`

**请求方式：**
- GET    

**参数：** 

无

 **返回示例**

``` 
{
    "code": 0,
    "data": {
        "results": [],
        "total": 0
    }
}
```
------------------

### 11 关注的收藏夹

**请求API：**
- `/followed_labels/`+用户url别名slug
- 例: `/followed_labels/shou-ji-yong-hu-8nd93mz`

**请求方式：**
- GET    

**参数：** 

无

 **返回示例**

``` 
{
    "code": 0,
    "data": {
        "results": [],
        "total": 0
    }
}
```
------------------

### 12 关注的问题

**请求API：**
- `/followed_questions/`+用户url别名slug
- 例: `/followed_questions/shou-ji-yong-hu-8nd93mz`

**请求方式：**
- GET    

**参数：** 

无

 **返回示例**

``` 
{
    "code": 0,
    "data": {
        "results": [],
        "total": 0
    }
}
```
------------------

### 13 个人成就

**请求API：**
- `/self_achievement/`+用户url别名slug
- 例: `/self_achievement/shou-ji-yong-hu-8nd93mz`

**请求方式：**
- GET    

**参数：** 

无

 **返回示例**

``` 
{
    "code": 0,
    "data": {
        "upvote_count": 0,
        "collect_count": 0
    }
}
```
------------------

### 13 个人收藏夹创建、修改、删除操作

#### 13.1 创建
**请求API：**
- `/self_favorites/`+用户url别名slug
- 例: `/self_favorites/shou-ji-yong-hu-8nd93mz`

**请求方式：**
- POST    

**参数：** 

|参数名|必选|说明|
|:---|:----|:---|
|title|是|收藏夹标题|
|content|否|收藏夹介绍|
|status|是|收藏夹状态，public：公开，private：私有|

 **返回示例**

``` 
{
    "code": 0,
    "data": null
}
```
------------------

#### 13.2 修改
**请求API：**
- `/self_favorites/`+用户url别名slug
- 例: `/self_favorites/shou-ji-yong-hu-8nd93mz`

**请求方式：**
- PUT    

**参数：** 

|参数名|必选|说明|
|:---|:----|:---|
|title|是|收藏夹标题|
|content|否|收藏夹介绍|
|status|是|收藏夹状态，public：公开，private：私有|

 **返回示例**

``` 
{
    "code": 0,
    "data": null
}
```
------------------

#### 13.2 删除
**请求API：**
- `/self_favorites/`+用户url别名slug
- 例: `/self_favorites/shou-ji-yong-hu-8nd93mz`

**请求方式：**
- DELETE    

**参数：** 

|参数名|必选|说明|
|:---|:----|:---|
|fa_id|是|收藏夹ID|

 **返回示例**

``` 
{
    "code": 0,
    "data": null
}
```
------------------

### 14 当收藏某一个内容时，首选出现收藏夹列表，其中包括已经收藏该内容的收藏夹
**请求API：**
- `/collected/`+用户url别名slug + 收藏的内容类型 + 收藏的内容ID
- 例: `/collected/shou-ji-yong-hu-8nd93mz/answer/1`

**请求方式：**
- GET    

**参数：** 
无

 **返回示例**

``` 
{
    "data": [
        {
            "collected": true,
            "id": 1,
            "content_count": 1,
            "title": "我的第一个收藏夹"
        },
        {
            "collected": false,
            "id": 2,
            "content_count": 0,
            "title": "我的第二个收藏夹"
        }
    ],
    "code": 0
}
```
------------------

### 14 某一个收藏夹的内容

#### 14.1 获取内容

**请求API：**
- `/favorites_content/`+用户url别名slug + 收藏夹ID
- 例: `/favorites_content/shou-ji-yong-hu-8nd93mz/1`

**请求方式：**
- GET    

**参数：** 
无

 **返回示例**

``` 
{
    "data": {
        "total": 1,
        "results": [
            {
                "details": {
                    "question": 1,
                    "content": "回答",
                    "user_id": "45c48cce2e2d7fbdea1afc51c7c6ad26",
                    "pk": 1
                }
            }
        ]
    },
    "code": 0
}
```
------------------

#### 14.2 添加内容

**请求API：**
- `/favorites_content/`+用户url别名slug + 收藏夹ID
- 例: `/favorites_content/shou-ji-yong-hu-8nd93mz/1`

**请求方式：**
- POST    

**参数：** 

|参数名称|必选|说明|
|:---|:----|:----|
|content_type|是|内容类型：answer：回答；article:文章|
|object_id|是|内容的ID|

 **返回示例**

``` 
{
    "data": null
    "code": 0
}
```
------------------

#### 14.3 删除内容

**请求API：**
- `/favorites_content/`+用户url别名slug + 收藏夹ID
- 例: `/favorites_content/shou-ji-yong-hu-8nd93mz/1`

**请求方式：**
- DELETE    

**参数：** 

|参数名称|必选|说明|
|:---|:----|:----|
|content_type|是|内容类型：answer：回答；article:文章|
|object_id|是|内容的ID|

 **返回示例**

``` 
{
    "data": null
    "code": 0
}
```
------------------





