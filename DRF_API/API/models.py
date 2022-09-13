from django.db import models

# from questions.models import User, Subject

from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser, PermissionsMixin, )

ROLE = (('teacher', 'Teacher'),
        ('student', 'Student'))
TEACHER_TYPE = (('expert', 'Expert'),
                ('academic', 'Academic'))


class UserManager(BaseUserManager):
    def _create_user(self, email: str, password: str = None, **kwargs):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            email=self.normalize_email(email),
            **kwargs
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str = None, password=None, **kwargs):
        kwargs.setdefault('is_superuser', False)
        return self._create_user(email=email, password=password, **kwargs)

    def create_superuser(self, email, password, **kwargs):
        kwargs.setdefault('is_superuser', True)
        if kwargs.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if password is None:
            raise TypeError('Superusers must have a password.')
        user = self._create_user(email=email, password=password, **kwargs)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        'email address',
        max_length=255,
        unique=True,
        error_messages={'unique': "A user with that email already exists.", }
    )
    username = models.CharField(max_length=100)
    is_active = models.BooleanField('active',
                                    default=True,
                                    help_text=('Designates whether this user should be treated as active. '
                                               'Unselect this instead of deleting accounts.'
                                               ),
                                    )
    is_staff = models.BooleanField('staff status',
                                   default=False,
                                   help_text='Designates whether the user can log into this admin site.',
                                   )
    role = models.CharField(max_length=20, choices=ROLE)
    contact = models.BigIntegerField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    class Meta:
        db_table = "user"
        verbose_name = 'user'
        verbose_name_plural = 'users'


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    peer_to_peer_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user)


class Teacher(models.Model):
    class EXPERTTYPE(models.TextChoices):
        TEACHER = 'TE', _("TEACHER")
        EX = 'EX', _("EXPERT")

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    institute = models.TextField(null=True, blank=True)
    enable = models.BooleanField(default=True)
    rating = models.DecimalField(default=0.0, max_digits=4, decimal_places=2)
    expert_type = models.CharField(max_length=15, choices=EXPERTTYPE.choices, default=EXPERTTYPE.EX)
    acceptance_rate = models.DecimalField(default=0.0, max_digits=4, decimal_places=2)
    average_time = models.DecimalField(default=0.0, max_digits=4, decimal_places=2)
    create_date = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

    # def name(self):
    #     return self.user.display_name
    #
    # def id(self):
    #     return self.pk


class Subject(models.Model):
    name = models.CharField(max_length=100)
    create_date = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class FavouriteTeacher(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Topic(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    question_number = models.PositiveSmallIntegerField()
    syllabus = models.TextField()
    question_payment = models.DecimalField(max_digits=5, decimal_places=2)
    total_mark = models.IntegerField(default=100)
    examtime = models.IntegerField()
    demo_answer = models.TextField(blank=True, null=True)
    create_date = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject.name
    # def __str__(self):
    #     return "%s__%s" % (self.subject.type, self.id)


class SingleQuestion(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    question = models.TextField()
    mark = models.DecimalField(max_digits=5, decimal_places=2)
    create_date = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s__%s" % (self.topic, self.id)


class Rating(models.Model):
    sender = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    receiver = models.PositiveIntegerField(default=1)
    is_teacher = models.BooleanField(default=True)
    rating = models.PositiveSmallIntegerField(default=0)
    comment = models.TextField(null=True, blank=True)
    create_date = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)


class UserAnswerSheet(models.Model):
    sender = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True)
    create_date = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    # def __str__(self):
    #     return self.sender.user.idname + "-" + str(self.id)


class AnswerSheet(models.Model):
    single_question = models.ForeignKey(SingleQuestion, on_delete=models.CASCADE, null=True, blank=True)
    answer_object = models.ForeignKey(UserAnswerSheet, on_delete=models.CASCADE, null=True, blank=True)
    provided_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    comment = models.TextField(null=True, blank=True)
    create_date = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s-%s" % (self.answer_object, self.single_question)


class ImageAnswer(models.Model):
    image_link = models.CharField(max_length=500, null=True, blank=True)
    # answer_sheet = models.ForeignKey(AnswerSheet, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True)
    image_order = models.IntegerField(default=1)
    create_date = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s" % self.topic


class UserMark(models.Model):
    sender = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    # receiver_count = models.PositiveIntegerField(default=1, null=True, blank=True)
    is_teacher = models.BooleanField(default=True, null=True, blank=True)
    answer_object = models.ForeignKey(UserAnswerSheet, on_delete=models.CASCADE, null=True, blank=True)
    total_mark = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    rating = models.ForeignKey(Rating, on_delete=models.CASCADE, null=True, blank=True)
    is_accepted = models.BooleanField(default=None, null=True, blank=True)
    is_checked = models.BooleanField(default=False, null=True, blank=True)
    accept_timestamp = models.DateTimeField(null=True, blank=True)
    create_date = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)


# class PeerToPeer(models.Model):
#     sender = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
#     receiver = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
#     created_at = models.DateTimeField(auto_now=True)
#     updated_at = models.DateTimeField(auto_now_add=True)
