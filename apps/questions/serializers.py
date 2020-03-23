from rest_framework import serializers

from .models import Question, Answer, QuestionFollow, QuestionInvite, QAComment
from apps.labels.models import Label
from apps.articles.models import Article
from apps.userpage.models import UserProfile, FollowedUser


class QuestionCreateSerializer(serializers.ModelSerializer):
    """用于提问时的反序列化验证和写入数据库"""
    labels = serializers.ListField(required=True)

    class Meta:
        model = Question
        fields = ("title", "content", "user_id", "labels")

    def validate_labels(self, value):
        value = Label.objects.filter(name__in=value)
        if not value:
            raise serializers.ValidationError("问题的标签不存在")
        return value


class NewQuestionSerializer(serializers.ModelSerializer):
    """用于提问成功后的序列化"""
    nickname = serializers.SerializerMethodField()
    labels = serializers.StringRelatedField(many=True)

    class Meta:
        model = Question
        fields = ("title", "content", "nickname", "labels", "id")

    def get_nickname(self, obj):
        user = UserProfile.objects.get(uid=obj.user_id)
        return user.nickname


class FollowedQuestionSerializer(serializers.ModelSerializer):
    """本人关注的问题的序列化"""

    class Meta:
        model = Question
        fields = ("title", "content", "id")


class AnswerCreateSerializer(serializers.ModelSerializer):
    author_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Answer
        fields = ("question", "content", "user_id", "id", "author_info")
        read_only_fields = ("id", "author_info")
        extra_kwargs = {
            "user_id": {
                "write_only": True
            }
        }

    def get_author_info(self, obj: Answer):
        author = UserProfile.objects.get(uid=obj.user_id)
        data = {
            "nickname": author.nickname,
            "slug": author.slug,
            "avatar": author.avatar,
        }
        return data


class QuestionFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionFollow
        fields = ("question", "user_id")


class InviteCreateSerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S", read_only=True)

    class Meta:
        model = QuestionInvite
        fields = ("question", "create_at", "inviting", "invited", "status", "id")
        read_only_fields = ("create_at", "status", "id")

    def validate(self, attrs):
        if attrs["inviting"] == attrs["invited"]:
            raise serializers.ValidationError("不能邀请自己")
        try:
            Answer.objects.get(question=attrs["question"], user_id=attrs["invited"])
        except Answer.DoesNotExist:
            pass
        except Exception as e:
            raise serializers.ValidationError(e.args)
        else:
            raise serializers.ValidationError("不能邀请已回答用户")
        return attrs


class QACommentCreateSerializer(serializers.ModelSerializer):
    qa_id = serializers.PrimaryKeyRelatedField(source="content_object", read_only=True)
    create_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S", read_only=True)
    author_info = serializers.SerializerMethodField(read_only=True)
    receiver_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = QAComment
        fields = ("user_id", "author_info", "receiver_info", "content", "create_at", "reply_to_user", "qa_id", "id")
        read_only_fields = ("id", "author_info", "receiver_info")
        extra_kwargs = {
            "reply_to_user": {
                "write_only": True
            },
            "user_id": {
                "write_only": True
            }
        }

    def get_author_info(self, obj):
        author = UserProfile.objects.get(uid=obj.user_id)
        data = {
            "nickname": author.nickname,
            "slug": author.slug,
            "avatar": author.avatar,
        }
        return data

    def get_receiver_info(self, obj):
        receiver = UserProfile.objects.get(uid=obj.reply_to_user)
        data = {
            "nickname": receiver.nickname,
            "slug": receiver.slug,
            "avatar": receiver.avatar,
        }
        return data


class QACommentDetailSerializer(serializers.ModelSerializer):
    vote_count = serializers.SerializerMethodField()
    create_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S", read_only=True)
    author_info = serializers.SerializerMethodField()
    receiver_info = serializers.SerializerMethodField(read_only=True)
    voted = serializers.SerializerMethodField()

    class Meta:
        model = QAComment
        fields = ("id", "author_info", "receiver_info", "content", "create_at", "voted", "vote_count")

    def get_vote_count(self, obj):
        return obj.vote.filter(value=True).count() - obj.vote.filter(value=False).count()

    def get_author_info(self, obj):
        author = UserProfile.objects.get(uid=obj.user_id)
        data = {
            "nickname": author.nickname,
            "slug": author.slug,
            "avatar": author.avatar,
        }
        return data

    def get_receiver_info(self, obj):
        receiver = UserProfile.objects.get(uid=obj.reply_to_user)
        data = {
            "nickname": receiver.nickname,
            "slug": receiver.slug,
            "avatar": receiver.avatar,
        }
        return data

    def get_voted(self, obj):
        me = self.context["me"]
        if not me:
            return None
        my_vote = obj.vote.filter(user_id=me.uid).first()
        if not my_vote:
            return None
        return my_vote.value


class AnswerInLabelDiscussSerializer(serializers.ModelSerializer):
    """只用于序列化，使用时通过context传入me的值"""
    create_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S")
    vote_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    answer_id = serializers.IntegerField(source="id")
    answer_content = serializers.CharField(source="content")
    currentUserVote = serializers.SerializerMethodField(method_name="get_voted")
    author_info = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = (
            "answer_id", "answer_content", "create_at", "vote_count", "comment_count", "currentUserVote", "author_info"
        )

    def get_vote_count(self, obj):
        return obj.vote.filter(value=True).count() - obj.vote.filter(value=False).count()

    def get_comment_count(self, obj):
        return obj.comment.count()

    def get_voted(self, obj):
        """返回None表示未投票，True表示赞成，False表示反对"""
        me = self.context["me"]  # None或者当前登录的UserProfile对象
        if not me:
            # <<<<<<< master
            return None
        my_vote = obj.vote.filter(user_id=me.uid).first()
        if not my_vote:
            return None
        return my_vote.value

    def get_author_info(self, obj: Answer):
        author = UserProfile.objects.get(uid=obj.user_id)
        data = {
            "nickname": author.nickname,
            "avatar": author.avatar,
            "autograph": author.autograph,
            "slug": author.slug,
        }
        return data


# =======
# return False
# return obj.collect.filter(favorite__user_id=me).exists()  # TODO 这个查询正确吗？
# return obj.collect.filter(favorite__user__uid=me).exists()
# >>>>>>> master


class QuestionInLabelDiscussSerializer(serializers.ModelSerializer):
    """只用于序列化，使用时通过context传入me的值"""
    top_answer = serializers.SerializerMethodField()
    question_id = serializers.IntegerField(source="id")
    question_title = serializers.CharField(source="title")

    class Meta:
        model = Question
        fields = ("question_id", "question_title", "content", "top_answer")

    def get_top_answer(self, obj):
        answers = obj.answer_set.all()
        if not answers:
            return {}
        top_answer = max(answers, key=lambda x: x.comment.count())  # TODO 暂定为评论数量最多的回答
        me = self.context["me"]
        s = AnswerInLabelDiscussSerializer(instance=top_answer, context={"me": me})
        return s.data


class AnswerWithAuthorInfoSerializer(serializers.ModelSerializer):
    create_at = serializers.DateTimeField(format="%Y%m%d %H:%M:%S")
    vote_count = serializers.SerializerMethodField()
    author_info = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    i_agreed = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = ("id", "content", "vote_count", "comment_count", "i_agreed", "create_at", "author_info")

    def get_vote_count(self, obj):
        return obj.vote.filter(value=True).count() - obj.vote.filter(value=False).count()

    def get_comment_count(self, obj):
        return obj.comment.count()

    def get_i_agreed(self, obj):
        if "me" in self.context:  # 当前登录的UserProfile对象或None，有两种获取方式
            me = self.context["me"]
        else:
            me = obj.me
        if not me:
            return None
        my_vote = obj.vote.filter(user_id=me.uid).first()
        if not my_vote:
            return None
        return my_vote.value

    def get_author_info(self, obj):
        if "me" in self.context:
            me = self.context["me"]
        else:
            me = obj.me
        if not me:  # 为未登录用户返回粗糙的数据
            data = {
                "nickname": "旗渡用户",
                "avatar": None,
                "autograph": None,
                "slug": None,
            }
        else:
            author = UserProfile.objects.get(uid=obj.user_id)
            data = {
                "nickname": author.nickname,
                "avatar": author.avatar,
                "autograph": author.autograph,
                "slug": author.slug,
                "answer_count": Answer.objects.filter(user_id=author.uid).count(),
                "article_count": Article.objects.filter(user_id=author.uid).count(),
                "follower_count": author.as_idol.count(),
                "i_followed_author": FollowedUser.objects.filter(fans=me, idol=author).exists()
            }
        return data


class TwoAnswersSerializer(serializers.Serializer):
    question = serializers.SerializerMethodField()
    answer = AnswerWithAuthorInfoSerializer()
    another_answer = AnswerWithAuthorInfoSerializer()

    def get_question(self, obj: dict):
        answer = obj["answer"]
        question = answer.question
        me = self.context["me"]
        if not me:
            followed = False
        else:
            followed = question.questionfollow_set.filter(user_id=me.uid).exists()
        data = {
            "id": question.id,
            "title": question.title,
            "answer_count": question.answer_set.count(),
            "comment_count": question.comment.count(),
            "followed": followed,
        }
        return data
