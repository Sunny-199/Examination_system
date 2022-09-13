from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'
        # exclude = ['password']
    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
class UserSerializertwo(serializers.ModelSerializer):

    class Meta:
        model = User
        # fields = '__all__'
        exclude = ['password']

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    USERNAME_FIELD = 'email'
    def validate(self, attrs):
        password = attrs.get('password')
        user_obj = User.objects.filter(email=attrs.get('email'))
        if user_obj:
            credentials = {
                'email': user_obj[0].email,
                'password': password
            }
            user = User.objects.get(email=user_obj[0].email)
            # print(user.check_password(password))
            # user = authenticate(request=self.context['request'], email=user_obj[0].email, password=password)
            if user.check_password(password):
                refresh = self.get_token(user)
                data = {
                        'success': True,
                        'status': 200,
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'role': user.role,
                        'email': user.email,
                        'message': 'Login successfully'
                    }
                return data
            return {"message": 'please enter valid email and password', 'status': 400}
        else:
            return {"message": 'please enter valid email and password', 'status': 400}
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        return token

class SubjectSerializers(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields ='__all__'
class UserRatingSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'role']


class RatingSerializer(serializers.ModelSerializer):
    # rating_from = UserSerializer(read_only=True)
    # rating_to = UserSerializer(read_only=True)
    class Meta:
        model = Rating
        fields ='__all__'


class GetRatingSerializer(serializers.ModelSerializer):
    rating_from = UserRatingSerializer(read_only=True)
    rating_to = UserRatingSerializer(read_only=True)
    class Meta:
        model = Rating
        fields ='__all__'

class StudentSerializers(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields ='__all__'

class TeacherSerializers(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ('id', 'institute', 'rating', 'acceptance_rate', 'average_time')

class SingleQuestionSerializers(serializers.ModelSerializer):
    class Meta:
        model = SingleQuestion
        fields =('id', 'question', 'mark')

class AnswerSheetSerializers(serializers.ModelSerializer):
    question = serializers.CharField(source='single_question.question')
    original_mark = serializers.DecimalField(source='single_question.mark', max_digits=5, decimal_places=2,)
    class Meta:
        model = AnswerSheet
        fields =('question', 'original_mark', 'provided_marks', 'comment')


class FavouriteTeacherSerializers(serializers.ModelSerializer):
    student = StudentSerializers(read_only=True)
    teacher = TeacherSerializers(read_only=True)

    class Meta:
        model = FavouriteTeacher
        fields = '__all__'


class ImageAnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = ImageAnswer
        fields = '__all__'

class GetSingleQuestionResultSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnswerSheet
        fields = '__all__'
