from django.conf.urls import url

from . import views

urlpatterns = [

    url(r"^user_info/(?P<user_slug>[-\w]+)$", views.UserInfoAPIView.as_view(), name="user_info"),

    # 用户自己创建或者修改收藏夹视图
    url(r'^self_favorites$', views.SelfFavoritesAPIView.as_view(), name='self_favorites'),

    # 用户内容分类相关视图---------------------------------------------
    # 获取某一个用户的收藏夹列表
    url(r"^favorites_list/(?P<user_slug>[-\w]+)$", views.FavoritesListAPIView.as_view(), name="favorites_list"),
    # 获取用户的发起的提问列表
    url(r"^question_list/(?P<user_slug>[-\w]+)$", views.QuestionListAPIView.as_view(), name="question_list"),
    # 获取用户回答列表
    url(r"^answer_list/(?P<user_slug>[-\w]+)$", views.AnswerListAPIView.as_view(), name="answer_list"),
    # 获取用户文章列表
    url(r"^article_list/(?P<user_slug>[-\w]+)$", views.ArticleListAPIView.as_view(), name="article_list"),
    # 获取用户想法列表
    url(r"^think_list/(?P<user_slug>[-\w]+)$", views.ThinkListAPIView.as_view(), name="think_list"),

    # 用户关注内容相关视图 ---------------------------------------------------------
    # 关注用户与取关
    url(r'^following_user/(?P<user_slug>[-\w]+)$', views.FollowingUserAPIView.as_view(), name='following_user'),
    # 关注收藏夹
    url(r'^following_favorites/(?P<pk>\d+)$', views.FollowingFavoritesAPIView.as_view(), name='following_favorites'),

    # 查看用户关注的收藏夹
    url(r'followed_favorites/(?P<user_slug>[-\w]+)$', views.FollowedFavoritesAPIView.as_view(), name='followed_favorites'),
    # 查看用户关注的标签
    url(r'followed_labels/(?P<user_slug>[-\w]+)$', views.FollowedLabelAPIView.as_view(), name='followed_labels'),
    # 查看用户关注的问题
    url(r'followed_questions/(?P<user_slug>[-\w]+)$', views.FollowedQuestionsAPIView.as_view(), name='followed_questions'),
    # 查看用户关注的用户或者被关注的用户
    url(r'followed_user/(?P<user_slug>[-\w]+)$', views.FollowedUserAPIView.as_view(), name='followed_user'),

    # --------------------------------------------
    # 收藏某一个内容
    url(r'collected/(?P<user_slug>[-\w]+)/(?P<content_type>\w+)/(?P<object_id>\d+)$', views.CollectedAPIView.as_view()),

    # 查看某一个收藏夹的内容
    url(r'favorites_content/(?P<pk>\d+)$', views.FavoritesContentAPIView.as_view(), name='favorites_content'),
    # 接受统一用户中心发送过来的更新请求
    url(r"^uc_update$", views.UcUpdateAPIView.as_view(), name="uc_update"),

]