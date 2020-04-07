from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from apps.comments.models import Comment
from apps.labels_v2.models import Label
from apps.userpage.models import UserProfile
from apps.utils.models import BaseModel
from apps.votes.models import Vote

from apps.userpage_v2.models import FavoriteCollection
from apps.creator_v2.models import ReadNums


class Question(BaseModel):
    """问题，标题不能重复"""

    title = models.CharField(max_length=100, unique=True, null=False, blank=False, verbose_name="问题标题")
    content = models.TextField(null=True, blank=True, verbose_name="问题描述")
    author = models.ForeignKey(to=UserProfile, null=False, verbose_name="提问者")
    labels = models.ManyToManyField(to=Label, verbose_name="问题的标签")
    comments = GenericRelation(to=Comment)
    followers = models.ManyToManyField(to=UserProfile, related_name="followed_questions", through="QuestionFollow",
                                       through_fields=("question", "user"), verbose_name="关注者")

    read_nums = GenericRelation(to=ReadNums)

    class Meta:
        db_table = "question"
        verbose_name = "问题"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title

    @property
    def kind(self):
        return "question"

    @property
    def url(self):
        return settings.FRONT_HOST + "/question/" + str(self.pk) + "/"


class Answer(BaseModel):
    """问题的回答，每个问题每个用户只能正式回答一次，但可以修改或有多个草稿"""

    content = models.TextField(null=False, blank=False, verbose_name="回答内容")
    # 发表评论是用到了该字段名，不能随意改名
    is_draft = models.BooleanField(null=False, blank=False, verbose_name="是否是草稿")
    question = models.ForeignKey(to=Question, null=False, verbose_name="问题")
    author = models.ForeignKey(to=UserProfile, null=False, verbose_name="回答者")
    comments = GenericRelation(to=Comment)
    votes = GenericRelation(to=Vote)

    # 添加收藏关系
    collect = GenericRelation(to=FavoriteCollection)
    read_nums = GenericRelation(to=ReadNums)

    class Meta:
        db_table = "answer"
        verbose_name = "回答"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content[:20]

    @property
    def kind(self):
        return "answer"

    @property
    def url(self):
        return settings.FRONT_HOST + "/question/" + str(self.question.pk) + "/answer/" + str(self.pk) + "/"


class QuestionFollow(BaseModel):
    """用户与问题的多对多关注关系，插入行时注意防止重复"""

    user = models.ForeignKey(to=UserProfile, null=False, verbose_name="关注者")
    question = models.ForeignKey(to=Question, null=False, verbose_name="关注的问题")

    class Meta:
        db_table = "question_follow"
        verbose_name = "问题关注"
        verbose_name_plural = verbose_name

    def __str__(self):
        return " ".join((self.user.nickname, "关注了", self.question.title))


class QuestionInvite(BaseModel):
    """邀请回答

    邀请被转化成了通知，所以用户不必查看或拒绝邀请，甚至邀请也不必保存。记录下来，一是防止重复邀请，二是查询被邀请者是否回答。

    用户可以发出邀请，但不能撤销邀请，因为可能发生如下情况：
    用户A邀请了用户B，邀请被记录，并异步生成通知
    1分钟后A撤销了邀请，此时通知还没有生成
    2分钟后生成了通知，它不应该存在
    3分钟后B登录，收到了通知
    """

    status = models.BooleanField(null=False, default=False, verbose_name="是否已回答")
    inviting = models.ForeignKey(to=UserProfile, null=False, related_name="sent_invitations", verbose_name="邀请者")
    invited = models.ForeignKey(to=UserProfile, null=False, related_name="received_invitations", verbose_name="被邀请者")
    question = models.ForeignKey(to=Question, null=False, verbose_name="问题")

    class Meta:
        db_table = "question_invite"
        verbose_name = "邀请回答"
        verbose_name_plural = verbose_name
