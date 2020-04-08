from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class UserProfile(models.Model):
    uid = models.CharField(verbose_name='用户ID', primary_key=True, max_length=255)

    nickname = models.CharField(max_length=15, verbose_name='用户昵称', null=True, blank=True)

    GENDER_CHOICES = ((1, '男'), (0, '女'))

    gender = models.CharField(choices=GENDER_CHOICES, null=True, blank=True, max_length=1)

    avatar = models.CharField(max_length=100, verbose_name='头像路径', null=True, blank=True)

    autograph = models.CharField(max_length=255, verbose_name='个性签名', null=True, blank=True)

    # 所在行业
    industry = models.CharField(max_length=20, verbose_name='所属行业', null=True, blank=True)

    # 居住地
    location = models.ManyToManyField('UserLocations', related_name='user_location')

    # 个人介绍
    description = models.TextField(verbose_name='个人介绍', null=True, blank=True)

    # slug
    slug = models.SlugField(max_length=150, null=True, blank=True, verbose_name='(URL)别名', unique=True)

    page_image = models.CharField(max_length=100, verbose_name='主页图片', null=True, blank=True)

    class Meta:
        db_table = 'db_user_profile'

    @property
    def kind(self):
        return "people"


class UserEmploymentHistory(models.Model):
    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='user_employment_history')
    company = models.CharField(max_length=100, verbose_name='公司名称')
    position = models.CharField(max_length=100, verbose_name='公司职位', null=True, blank=True)

    class Meta:
        db_table = 'db_user_employment_history'


class UserEducationHistory(models.Model):
    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='user_education_history')
    school = models.CharField(max_length=100, verbose_name='学校名称')
    major = models.CharField(max_length=50, verbose_name='专业方向', null=True, blank=True)
    education = models.CharField(max_length=50, verbose_name='学历', null=True, blank=True)
    in_year = models.CharField(max_length=4, verbose_name='入学年份', null=True, blank=True)
    out_year = models.CharField(max_length=4, verbose_name='毕业年份', null=True, blank=True)

    class Meta:
        db_table = 'db_user_education_history'


class UserLocations(models.Model):
    name = models.CharField(max_length=10, verbose_name='居住地名称')
    location_pic = models.CharField(max_length=255, verbose_name='地址图片', null=True, blank=True)

    class Meta:
        db_table = 'db_user_locations'


class FollowedUser(models.Model):
    fans = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='as_fans')
    idol = models.ForeignKey("UserProfile", on_delete=models.CASCADE, related_name='as_idol')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='关注时间')

    class Meta:
        db_table = 'db_followed_user'


class UserFavorites(models.Model):
    user = models.ForeignKey('UserProfile', related_name='favorites', on_delete=models.CASCADE)
    title = models.CharField(max_length=150, verbose_name='收藏夹标题')
    intro = models.TextField(verbose_name='介绍', null=True, blank=True)
    STATUS = (('public', 'public'), ('private', 'private'))
    status = models.CharField(choices=STATUS, default='public', verbose_name='收藏夹状态', max_length=10)
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    # follows = GenericRelation(UserFollows) # 通过GenericRelation关联到UserFollows表，不是实际的字段

    class Meta:
        db_table = 'db_user_favorites'


class FollowedFavorites(models.Model):
    user = models.ForeignKey('UserProfile', related_name='followed_fa_user', on_delete=models.CASCADE)
    fa = models.ForeignKey('UserFavorites', related_name='followed_fa', on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='关注时间')

    class Meta:
        db_table = 'db_followed_favorite'


class FavoriteCollection(models.Model):
    favorite = models.ForeignKey('UserFavorites', related_name='favorite_collect')
    create_at = models.DateTimeField(auto_now_add=True, verbose_name='收藏时间', null=True, blank=True)
    content_type = models.ForeignKey(ContentType, related_name='collect_on', on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        db_table = 'db_favorite_collect'
        unique_together = ('favorite', 'object_id', 'content_type')
