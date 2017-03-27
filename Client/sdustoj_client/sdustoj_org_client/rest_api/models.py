from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres import fields as pg_fields


# -- Resources ------------------------------------------------------------------------------------

class Resource(models.Model):
    """
    资源
    """
    creator = models.CharField(max_length=150, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    updater = models.CharField(max_length=150, null=True)
    update_time = models.DateTimeField(auto_now=True)

    available = models.BooleanField(default=True)
    deleted  = models.BooleanField(default=False)

    class Meta:
        abstract = True


# -- User -----------------------------------------------------------------------------------------

class IdentityChoices(object):
    root = 'ROOT'
    user_admin = 'USER_ADMIN'
    org_admin = 'ORG_ADMIN'
    edu_admin = 'EDU_ADMIN'
    teacher = 'TEACHER_ADMIN'
    student = 'STUDENT'

IDENTITY_CHOICES = (
    IdentityChoices.root,
    IdentityChoices.user_admin,
    IdentityChoices.org_admin,
    IdentityChoices.edu_admin,
    IdentityChoices.teacher,
    IdentityChoices.student
)

SITE_IDENTITY_CHOICES = (
    IdentityChoices.root,
    IdentityChoices.user_admin,
    IdentityChoices.org_admin
)


class UserProfile(Resource):
    """
    用户信息
    """
    SEX_CHOICES = ('MALE', 'FEMALE', 'SECRET')

    user = models.OneToOneField(User, related_name='profile', to_field='id', primary_key=True,
                                on_delete=models.CASCADE)
    username = models.CharField(max_length=150)

    # 所有人可见的信息
    name = models.CharField(max_length=150, null=True)
    sex = models.CharField(max_length=8, default='secret')

    phone = models.CharField(max_length=16, null=True)
    email = models.EmailField(max_length=128, null=True)

    github = models.CharField(max_length=128, null=True)
    qq = models.CharField(max_length=128, null=True)
    weixin = models.CharField(max_length=128, null=True)
    blog = models.CharField(max_length=128, null=True)

    introduction = models.TextField(max_length=256, null=True)
    last_login = models.DateTimeField(null=True)

    # 网站管理员可见的信息
    is_staff = models.BooleanField(default=False)       # 如果为True，则归于网站管理员之列，可访问管理页面
    ip = models.GenericIPAddressField(null=True)

    identities = pg_fields.JSONField(default={})        # 身份信息

    def get_site_identities(self):
        ret = []
        for k, v in self.identities.items():
            if v is True:
                ret.append(k)
        return ret

    def __str__(self):
        return '<UserProfile %s of User %s>' % (self.user, self.username)


class Student(Resource):
    IDENTITY_WORD = IdentityChoices.student

    id = models.BigAutoField(primary_key=True)

    user = models.ForeignKey(User, related_name='student_identities', to_field='id',
                             on_delete=models.CASCADE)
    profile = models.ForeignKey(UserProfile, related_name='student_identities', to_field='user',
                                on_delete=models.CASCADE)
    organization = models.ForeignKey('Organization', related_name='students', to_field='id',
                                     on_delete=models.CASCADE)

    student_id = models.CharField(max_length=32)
    grade = models.CharField(max_length=32)
    class_in = models.CharField(max_length=128)


class Teacher(Resource):
    IDENTITY_WORD = IdentityChoices.teacher

    id = models.BigAutoField(primary_key=True)

    user = models.ForeignKey(User, related_name='teacher_identities', to_field='id',
                             on_delete=models.CASCADE)
    profile = models.ForeignKey(UserProfile, related_name='teacher_identities', to_field='user',
                                on_delete=models.CASCADE)
    organization = models.ForeignKey('Organization', related_name='teachers', to_field='id',
                                     on_delete=models.CASCADE)

    teacher_id = models.CharField(max_length=32)


class EduAdmin(Resource):
    IDENTITY_WORD = IdentityChoices.edu_admin

    id = models.BigAutoField(primary_key=True)

    user = models.ForeignKey(User, related_name='edu_admin_identities', to_field='id',
                             on_delete=models.CASCADE)
    profile = models.ForeignKey(UserProfile, related_name='edu_admin_identities', to_field='user',
                                on_delete=models.CASCADE)
    organization = models.ForeignKey('Organization', related_name='edu_admins', to_field='id',
                                     on_delete=models.CASCADE)

    name = models.CharField(max_length=150, null=True)
    sex = models.CharField(max_length=8, default='secret')

    phone = models.CharField(max_length=16, null=True)
    email = models.EmailField(max_length=128, null=True)


# -- Organization ---------------------------------------------------------------------------------

class Organization(Resource):
    id = models.BigAutoField(primary_key=True)

    name = models.CharField(max_length=150, unique=True)
    caption = models.CharField(max_length=150)
    introduction = models.TextField(max_length=1024, null=True)

    parent = models.ForeignKey('self', related_name='children', to_field='id', null=True,
                               on_delete=models.CASCADE)

    number_organizations = models.IntegerField(default=0)
    number_students = models.IntegerField(default=0)
    number_teachers = models.IntegerField(default=0)
    number_admins = models.IntegerField(default=0)

    def __str__(self):
        return '<Organization %s: %s>' % (self.id, self.name)
