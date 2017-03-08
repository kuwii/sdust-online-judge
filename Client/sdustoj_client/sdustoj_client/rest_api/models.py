from django.db import models
from django.contrib.auth.models import User


# -- Utils -------------------------------------------------------------------------------------------------------------

class Resource(models.Model):
    creator = models.CharField(max_length=150, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    updater = models.CharField(max_length=150, null=True)
    update_time = models.DateTimeField(auto_now=True)

    available = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


class NameMixin(models.Model):
    name = models.CharField(max_length=150)
    introduction = models.TextField(max_length=1024)

    class Meta:
        abstract = True


# -- Organization ------------------------------------------------------------------------------------------------------

class Organization(Resource):
    id = models.BigAutoField(primary_key=True)

    name = models.CharField(max_length=150)
    info = models.TextField()

    org_class = models.IntegerField()
    parent = models.ForeignKey(
        'self', related_name='children', to_field='id', null=True, on_delete=models.CASCADE
    )

    number_organizations = models.IntegerField(default=0)   # 下设机构数量
    number_course_meta = models.IntegerField(default=0)     # 包含课程基类数量
    number_categories = models.IntegerField(default=0)      # 包含题库数量
    number_users = models.IntegerField(default=0)           # 包含用户数量
    number_admins = models.IntegerField(default=0)          # 包含管理员数量
    number_teachers = models.IntegerField(default=0)        # 包含教师数量
    number_students = models.IntegerField(default=0)        # 包含学生数量

    def __str__(self):
        return '<Organization[%s] %s: class %s>' % (self.id, self.name, self.org_class)


# -- Course & Group ----------------------------------------------------------------------------------------------------

class CourseMeta(Resource, NameMixin):
    id = models.BigAutoField(primary_key=True)
    organization = models.ForeignKey(Organization, related_name='course_meta', to_field='id', on_delete=models.CASCADE)

    number_courses = models.IntegerField(default=0)         # 包含课程数量
    number_course_groups = models.IntegerField(default=0)   # 包含课程组数量
    number_categories = models.IntegerField(default=0)      # 包含题库数量
    number_users = models.IntegerField(default=0)           # 包含用户数量
    number_teachers = models.IntegerField(default=0)        # 包含教师数量
    number_students = models.IntegerField(default=0)        # 包含学生数量


class CourseObject(Resource, NameMixin):
    id = models.BigAutoField(primary_key=True)
    organization = models.ForeignKey(
        Organization, related_name='course_objects', to_field='id', on_delete=models.CASCADE
    )

    number_work_groups = models.IntegerField(default=0)


class Course(CourseObject):
    course_id = models.BigAutoField(primary_key=True)
    meta = models.ForeignKey(
        CourseMeta, related_name='courses', to_field='id', on_delete=models.CASCADE
    )
    start_time = models.DateField()
    end_time = models.DateField()


class CourseGroup(CourseObject):
    group_id = models.BigAutoField(primary_key=True)
    courses = models.ManyToManyField(
        Course, related_name='groups', through='CourseGroupRelation', through_fields=('group', 'course')
    )
    number_courses = models.IntegerField(default=0)


class CourseGroupRelation(Resource):
    id = models.BigAutoField(primary_key=True)
    organization = models.ForeignKey(
        Organization, related_name='course_group_relations', to_field='id', on_delete=models.CASCADE
    )

    course = models.ForeignKey(
        Course, related_name='group_relations', to_field='id', on_delete=models.CASCADE
    )
    group = models.ForeignKey(
        CourseGroup, related_name='course_relations', to_field='id', on_delete=models.CASCADE
    )


# -- Work & Group ------------------------------------------------------------------------------------------------------

class WorkGroup(Resource, NameMixin):
    id = models.BigAutoField(primary_key=True)
    organization = models.ForeignKey(
        Organization, related_name='work_groups', to_field='id', on_delete=models.CASCADE
    )
    course_object = models.ForeignKey(
        CourseObject, related_name='work_groups', to_field='id', on_delete=models.CASCADE
    )

    works = models.ManyToManyField(
        'Work', related_name='groups', through='WorkGroupRelation', through_fields=('group', 'work')
    )

    number_works = models.IntegerField(default=0)


class Work(Resource, NameMixin):
    id = models.BigAutoField(primary_key=True)
    organization = models.ForeignKey(
        Organization, related_name='works', to_field='id', on_delete=models.CASCADE
    )

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()


class WorkGroupRelation(Resource):
    id = models.BigAutoField(primary_key=True)
    organization = models.ForeignKey(
        Organization, related_name='work_group_relations', to_field='id', on_delete=models.CASCADE
    )

    work = models.ForeignKey(Work, related_name='group_relations', to_field='id', on_delete=models.CASCADE)
    group = models.ForeignKey(WorkGroup, related_name='work_relations', to_field='id', on_delete=models.CASCADE)


# -- User --------------------------------------------------------------------------------------------------------------

class Person(Resource):
    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(User, related_name='person', to_field='username', on_delete=models.CASCADE)

    name = models.CharField(max_length=150)
    sex = models.CharField(max_length=8, null=True)
    phone = models.CharField(max_length=16, null=True)
    email = models.EmailField(max_length=128, null=True)

    last_login = models.DateTimeField(null=True)
    ip = models.GenericIPAddressField(null=True)


class Student(Resource):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(Person, related_name='student_info', to_field='user', on_delete=models.CASCADE)
    organization = models.ForeignKey(
        Organization, related_name='students', to_field='id', on_delete=models.CASCADE
    )
    studentID = models.CharField(max_length=32)


class Teacher(Resource):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(Person, related_name='teacher_info', to_field='user', on_delete=models.CASCADE)
    organization = models.ForeignKey(
        Organization, related_name='teachers', to_field='id', on_delete=models.CASCADE
    )
    teacherID = models.CharField(max_length=32)


class EduAdmin(Resource):
    """
    教务管理员
    """
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(Person, related_name='edu_admin_info', to_field='user', on_delete=models.CASCADE)
    organization = models.ForeignKey(
        Organization, related_name='admins', to_field='id', on_delete=models.CASCADE
    )


class OrgAdmin(Resource):
    """
    机构管理员
    """
    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(Person, related_name='org_admin_info', to_field='user', on_delete=models.CASCADE)


class UserAdmin(Resource):
    """
    用户管理员
    """
    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(Person, related_name='user_admin_info', to_field='user', on_delete=models.CASCADE)


class SiteAdmin(Resource):
    """
    系统管理员
    """
    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(Person, related_name='site_admin_info', to_field='user', on_delete=models.CASCADE)


IDENTITIES = {
    'Student': Student,
    'Teacher': Teacher,
    'EduAdmin': EduAdmin,
    'OrgAdmin': OrgAdmin,
    'UserAdmin': UserAdmin,
    'SiteAdmin': SiteAdmin
}
