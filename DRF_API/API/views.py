from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
import datetime
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from .serializers import *
# from .helper import modify_input_for_multiple_files
from .models import *
import random
from django.db.models import F
from rest_framework import status
from .uploadToS3 import upload_to_aws

class UserViewSet(ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # def create(self, request):
    #     serializer = self.serializer_class(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response({'message': 'Cotizacion creada correctamente.'}, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# User Login API
class MyTokenObtainPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = MyTokenObtainPairSerializer

class HomePage(APIView):
    @staticmethod
    def get(request, subject_id):
        Student.objects.update_or_create(user=request.auth)
        context = {"Message": "Success",
                   "status": 200
                   }
        return Response(context)



class RoutineListWrittenView(APIView):
    @staticmethod
    def get(request, subject_id):
        subject_obj = Subject.objects.get(id=subject_id)
        question_obj = Topic.objects.filter(subject=subject_obj, date__gte=datetime.date.today()).order_by('date')
        context = {'time': "পরীক্ষার দিন ২৪ ঘণ্টার যেকোনো সময় পরীক্ষা দিন।",
                   'title': subject_obj.textfield + " এর মডেল টেস্টের রুটিন"}
        li = []
        increment = 0
        for ques in question_obj:
            increment = increment + 1
            d = {'syllabus': ques.syllabus, 'exam_name_type': ques.subject.examcategory.get_exam_name(),
                 'exam_system_type': ques.subject.examcategory.get_exam_system()}
            exam_date = ques.date
            if exam_date > datetime.datetime(2024, 2, 2).date():
                d['date'] = 'To Be Determined'
            else:
                d['date'] = datetime.datetime.strftime(exam_date, '%b %d, %Y')
            if exam_date == datetime.datetime.now().date():
                d['exam'] = True
                d['status'] = "RUNNING"
            else:
                d['exam'] = False
                d['status'] = "UPCOMING"
            li.append(d)
        context['routine'] = li
        return Response(context, status=status.HTTP_200_OK)


class ViewQuestion(APIView):
    @staticmethod
    def get(request, pk):
        student_id = Student.objects.get(user=request.auth)
        context = {}
        question_obj = get_object_or_404(Topic, pk=pk)
        context['time'] = question_obj.examtime
        all_question = []

        obj, created = UserAnswerSheet.objects.update_or_create(sender=student_id, topic=question_obj)
        if obj:
            answer_sheet_obj = obj
        else:
            answer_sheet_obj = created
        for i in question_obj.singlequestion_set.all():
            obj1, created1 = AnswerSheet.objects.update_or_create(single_question=i, answer_object=answer_sheet_obj)
            if obj1:
                answer_sheet_id = obj1.id
            else:
                answer_sheet_id = created1.id
            di = {'answer_id': answer_sheet_id, 'question': i.question, 'mark': i.mark}
            all_question.append(di)
        context['answer_sheet_id'] = answer_sheet_obj.id
        context['all_questions'] = all_question
        return Response(context)


class SendImage(APIView):

    def get(self, request):
        answer_sheet = self.request.query_params.get('answer_sheet')
        all_images = ImageAnswer.objects.filter(answer_sheet__id=answer_sheet)
        serializer = ImageAnswerSerializer(all_images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def post(request):
        # user_id = request.user.id
        user_id = 2
        topic_id = request.data.get("topic_id")
        question_id = request.data.get("question_id")
        page_number = request.data.get("page_number")
        image_name = request.data.get("image_name")

        image_upload_status, image_link = upload_to_aws(image_name, user_id, topic_id, question_id, page_number)
        ImageAnswer.objects.create(image_link=image_link, image_order=page_number, topic_id=topic_id)
        return Response({"message": "image uploaded"}, status=status.HTTP_201_CREATED)
        # answer_sheet = request.data['answer_sheet']
        # images = dict(request.data.lists())['image']
        # flag = 1
        # arr = []
        # image_order = 1
        # for img_name in images:
        #

        #     modified_data = modify_input_for_multiple_files(answer_sheet,
        #                                                     img_name, image_order)
        #     file_serializer = ImageAnswerSerializer(data=modified_data)
        #     if file_serializer.is_valid():
        #         file_serializer.save()
        #         image_order = image_order + 1
        #         arr.append(file_serializer.data)
        #     else:
        #         flag = 0
        #
        # if flag == 1:
        #     return Response(arr, status=status.HTTP_201_CREATED)
        # else:
        #     return Response(arr, status=status.HTTP_400_BAD_REQUEST)


class SubmitQuestion(APIView):
    @staticmethod
    def post(request):
        context = {"pair_number": "4"}
        return Response(context)


class TeacherList(generics.ListAPIView):
    queryset = Teacher.objects.filter(enable=True)
    serializer_class = TeacherSerializers


class SentAnswer(APIView):
    @staticmethod
    def post(request):
        receiver_id = request.data['receiver_id']
        is_teacher = True if request.data['is_teacher'] == "1" else False
        answer_obj = UserAnswerSheet.objects.get(pk=request.data['answer_obj'])
        student_obj = Student.objects.get(user=request.auth)
        UserMark.objects.update_or_create(sender=student_obj, reciver=receiver_id, is_teacher=is_teacher,
                                                         answer_object=answer_obj)
        return Response({"MESSAGE": "SUCCESS"}, status=status.HTTP_201_CREATED)


class AnswerView(APIView):

    @staticmethod
    def get(request, user_mark_id):
        li = []
        queryset = UserMark.objects.get(pk=user_mark_id)
        context = {'exam_review_id': queryset.reciver, 'is_teacher': queryset.is_teacher}
        for obj in AnswerSheet.objects.filter(answer_object=queryset.answer_object):
            result = {'id': obj.id, 'question': obj.single_question.question, 'real_mark': obj.single_question.mark,
                      'provided_marks': obj.provided_marks}
            li.append(result)
        context['questions'] = li
        return Response({'Response': context})


class GetTeachersFilter(generics.ListAPIView):
    serializer_class = TeacherSerializers
    pagination_class = PageNumberPagination

    def list(self, request, t_type, *args, **kwargs):
        rating = self.request.query_params.get('rating')
        if rating.lower() != 'desc':
            queryset = Teacher.objects.filter(expert_type=t_type, enable=True).order_by('rating')
            serializer = TeacherSerializers(queryset, many=True)
        else:
            queryset = Teacher.objects.filter(expert_type=t_type, enable=True).order_by('-rating')
            serializer = TeacherSerializers(queryset, many=True)
        return Response(serializer.data)


class FavouriteTeacherView(APIView):
    @staticmethod
    def get(request, format=None):
        # queryset = FavouriteTeacher.objects.raw(''' select t.name, from api_favouriteteacher f join api_student s on f.student_id = s.user_id join api_teacher t on t.user_id =f.teacher_id ''')
        student_id = Student.objects.get(user=request.auth)
        queryset = FavouriteTeacher.objects.filter(student_id=student_id)
        serializer = FavouriteTeacherSerializers(queryset, many=True)
        return Response(serializer.data)

    @staticmethod
    def post(request, format=None):
        student_id = Student.objects.get(user=request.auth)
        teacher_id = request.data['teacher_id']
        queryset = FavouriteTeacher.objects.filter(Q(teacher_id=teacher_id) & Q(student_id=student_id))
        if queryset.count() == 0:
            FavouriteTeacher.objects.update_or_create(student_id=student_id, teacher_id=teacher_id)
            return Response({"message": "Favourite teacher added"})
        elif queryset.count() > 10:
            return Response({"message": "You cannot have more than 10 favourite teacher"})
        else:
            return Response({"message": "Already added as favourite"})


class StudentResultList(APIView):
    @staticmethod
    def get(request):
        context = {}

        student_obj = Student.objects.get(user=request.auth)
        user_answer = UserAnswerSheet.objects.filter(sender=student_obj)
        li = []
        for i in user_answer:
            obj = {'answer_id': i.id, 'topic_id': i.topic.id, 'topic': i.topic.syllabus}

            li.append(obj)
        context['answers'] = li
        return Response(context)


class QuestionResultList(APIView):
    @staticmethod
    def get(request, answer_id):
        context = {}
        student_obj = Student.objects.get(user=request.auth)
        mar_obj = UserMark.objects.filter(
            Q(answer_object=answer_id) & Q(sender=student_obj))  # sender = student_obj, answer_object__id = answer_id)
        li = []
        for i in mar_obj:
            obj = {}
            if i.is_teacher:
                obj['mark_id'] = i.id
                obj['user_name'] = Teacher.objects.get(pk=i.reciver).user.display_name
                obj['obtain_mark'] = i.total_mark
                obj['total_mark'] = i.answer_object.topic.total_mark
            else:
                obj['mark_id'] = i.id
                obj['user_name'] = "Pair to Pair Review"
                obj['obtain_mark'] = i.total_mark
                obj['total_mark'] = i.answer_object.topic.total_mark
            li.append(obj)
        context['answers'] = li
        return Response(context)


class SpecificAnswers(APIView):

    @staticmethod
    def get(request, mark_id):
        context = {}
        queryset = UserMark.objects.get(pk=mark_id)
        context['rating'] = queryset.rating
        answer_sheet = AnswerSheet.objects.filter(answer_object=queryset.answer_object)

        serializer = AnswerSheetSerializers(answer_sheet, many=True)
        context['questions'] = serializer.data

        return Response(context)


class ExaminerProfile(APIView):
    @staticmethod
    def get(request):
        context = {}
        teacher = Teacher.objects.get(user=request.auth)
        pending_count = UserMark.objects.filter(reciver=request.auth.id, is_teacher=True, is_accepted=1).count()
        context['pending_count'] = pending_count
        context['name'] = teacher.user.display_name
        context['institute'] = teacher.institute
        context['enable'] = teacher.enable
        context['rating'] = teacher.rating
        context['acceptance_rate'] = teacher.acceptance_rate
        context['average_time'] = teacher.average_time
        return Response(context)


class PendingRequests(APIView):
    @staticmethod
    def get(request):
        context = []
        Teacher.objects.get(user=request.auth)
        pending_count = UserMark.objects.filter(reciver=request.auth.id, is_teacher=True, rating=None)
        for i in pending_count:
            pen = {'mark_id': i.id,
                   'answer_id': i.answer_object.id,
                   'topic': i.answer_object.topic.syllabus,
                   'is_accepted': i.is_accepted,
                   'is_checked': i.is_checked}
            context.append(pen)

        return Response(context)


def get_total_marks(request, student_id, topic_id, question_id):
    total_marks = 0
    question_id = request.data.get('question')
    student_id = request.data.get('student')
    topic_id = request.data.get('topic')
    queryset = AnswerSheet.objects.filter(Q(question_id=question_id) & Q(student_id=student_id) & Q(topic_id=topic_id))
    serializer = AnswerSheetSerializers(queryset)
    total_marks = serializer.data.get('provided_marks') or 0
    return total_marks, queryset


class QuestionAssessmentByTeacher(APIView):

    @staticmethod
    def get(request, student_id, topic_id, question_id):
        # print(student_id, topic_id, question_id)
        request.data['provided_marks'], queryset = get_total_marks(request, student_id, topic_id, question_id)
        request.data['student_id'] = student_id
        request.data['topic_id'] = topic_id
        request.data['question_id'] = question_id
        # serializer = TotalMarksSerializer(queryset, many=True)
        # print(serializer.data)

        return Response(request.data)

    @staticmethod
    def post(request):
        serializer = AnswerSheetSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(request.data)


class SingleQuestionResultList(APIView):

    @staticmethod
    def get(request, student_id, topic_id, question_id):
        # request.data['provided_marks'], queryset = get_total_marks(student_id, topic_id, question_id)

        queryset = AnswerSheet.objects.filter(
            Q(student_id=student_id) & Q(topic_id=topic_id) & Q(question_id=question_id)).order_by('-id')[:1]
        # queryset = AnswerSheet.objects.all().last()
        serializer = GetSingleQuestionResultSerializer(queryset, many=True)
        return Response(serializer.data)


# class TopicResult(APIView):
#
#     @staticmethod
#     def get(request):
#         queryset = Exam.objects.all()
#         serializer = TopicResultSerializer(queryset, many=True)
#         return Response(serializer.data)


# class Accept(APIView):
#     @staticmethod
#     def post(request):
#         # teacher_id = request.user.id
#         teacher_id = request.data.get('teacher_id')
#         try:
#             Exam.objects.filter(Q(topic_id=request.data.get('topic_id')) & Q(teacher_id=teacher_id) & Q(
#                 student_id=request.data.get('student_id'))).update(accepted_at=datetime.now(), is_accepted=True)
#             return Response({"message": "Accepted"})
#         except Exception as e:
#             return Response({"message": "You cannot accept this topic"})

class SubmitCheckedTopic(APIView):
    @staticmethod
    def average_time(queryset):
        response_time = 0
        count = len(queryset)

        for item in queryset:
            time_difference = (item.teacher_submitted_at - item.accepted_at).total_seconds()
            response_time += int(time_difference) / count

        return str(datetime.timedelta(seconds=response_time))

    @staticmethod
    def acceptance_rate(teacher_id):
        total_request = UserMark.objects.filter(teacher_id=teacher_id).count()
        # print(total_request)
        is_checked_count = UserMark.objects.filter(Q(teacher_id=teacher_id) & Q(is_accepted=True)).count()
        # print(is_checked_count)
        percentage = int(is_checked_count / total_request) * 100
        return percentage

    # def post(self, request):
    #
    #     # teacher_id = request.user.id
    #     receiver = request.data.get('teacher_id')
    #     item = UserMark.objects.filter(Q(topic_id=request.data.get('topic_id')) & Q(teacher_id=receiver) & Q(
    #         student_id=request.data.get('sender_id')))
    #
    #     if item.count() == 0:
    #         return Response({"message": "You have already checked this topic"})
    #
    #
    #     else:
    #         # Exam.objects.filter(Q(topic_id=request.data.get('topic_id')) & Q(teacher_id=teacher_id) & Q(
    #         #     student_id=request.data.get('student_id'))).update(teacher_submitted_at=datetime.now())
    #         update_teacher_submitted_at = UserMark.objects.filter(
    #             Q(topic_id=request.data.get('topic_id')) & Q(teacher_id=teacher_id) & Q(
    #                 student_id=request.data.get('student_id')))
    #         # print(update_teacher_submitted_at)
    #         update_teacher_submitted_at.update(teacher_submitted_at=datetime.now())
    #         update_teacher_submitted_at.update(is_checked=True)
    #         obj = UserMark.objects.filter(Q(accepted_at__isnull=False) & Q(teacher_submitted_at__isnull=False))
    #         avg_response_time = self.average_time(obj)
    #         acceptance_rate = self.acceptance_rate(teacher_id)
    #         queryset = Teacher.objects.filter(user_id=teacher_id)
    #         queryset.update(avg_response_time=avg_response_time)
    #         queryset.update(acceptance_rate=acceptance_rate)
    #         return Response({"message": "Submitted successfully"})

# class PeerToPeer(APIView):
#
#     def post(self, request):
#         # current_user_id = request.user.id
#         topic_id = self.request.query_params.get('topic_id')
#         current_user_id = 2
#         check = UserAnswerSheet.objects.get(topic_id=topic_id, sender_id=current_user_id)
#         if check:
#             user_answer_sheet_obj_id = check.id
#         else:
#             user_answer_sheet_obj = UserAnswerSheet.objects.create(topic_id=topic_id, sender_id=current_user_id)
#             user_answer_sheet_obj_id = user_answer_sheet_obj.id
#         student = Student.objects.exclude(user_id=current_user_id)
#         serializer = StudentSerializers(student, many=True)
#         id_list = []
#         for obj in serializer.data:
#             id_list.append(obj['user'])
#         count = [0, 1, 2, 3]
#         student = Student.objects.filter(user_id__in=id_list, peer_to_peer_count__in=count)
#         updated_id = []
#         for obj in student:
#             updated_id.append(obj.user_id)
#         if len(updated_id) >= 4:
#             updated_id = random.sample(id_list, 4)
#         serializer = StudentSerializers(student, many=True)
#         for id in updated_id:
#             assign = UserMark.objects.create(sender_id=current_user_id, receiver_id=id, is_teacher=False,
#                                              answer_object_id=user_answer_sheet_obj_id)
#             assign.save()
#         Student.objects.filter(user_id__in=updated_id).update(peer_to_peer_count=F('peer_to_peer_count')+1)
#         return Response(serializer.data)


# class SubmitCheckedTopic(APIView):
#     def average_time(self, queryset):
#         response_time = 0
#         count = len(queryset)
#
#         for item in queryset:
#             time_difference = (item.teacher_submitted_at - item.accepted_at).total_seconds()
#             response_time += int(time_difference) / count
#
#         return str(timedelta(seconds=response_time))
#
#     def acceptance_rate(self, teacher_id):
#         total_request = Exam.objects.filter(teacher_id=teacher_id).count()
#         # print(total_request)
#         is_checked_count = Exam.objects.filter(Q(teacher_id=teacher_id) & Q(is_accepted=True)).count()
#         # print(is_checked_count)
#         percentage = int(is_checked_count / total_request) * 100
#         return percentage
#
#     def post(self, request):
#
#         # teacher_id = request.user.id
#         teacher_id = request.data.get('teacher_id')
#         item = Exam.objects.filter(Q(topic_id=request.data.get('topic_id')) & Q(teacher_id=teacher_id) & Q(
#             student_id=request.data.get('student_id')))
#
#         if item.count() == 0:
#             return Response({"message": "You have already checked this topic"})
#
#
#         else:
#              Exam.objects.filter(Q(topic_id=request.data.get('topic_id')) & Q(teacher_id=teacher_id) & Q(
#                  student_id=request.data.get('student_id'))).update(teacher_submitted_at=datetime.now())
#             update_teacher_submitted_at = Exam.objects.filter(
#                 Q(topic_id=request.data.get('topic_id')) & Q(teacher_id=teacher_id) & Q(
#                     student_id=request.data.get('student_id')))
#             # print(update_teacher_submitted_at)
#             update_teacher_submitted_at.update(teacher_submitted_at=datetime.now())
#             update_teacher_submitted_at.update(is_checked=True)
#             obj = Exam.objects.filter(Q(accepted_at__isnull=False) & Q(teacher_submitted_at__isnull=False))
#             avg_response_time = self.average_time(obj)
#             acceptance_rate = self.acceptance_rate(teacher_id)
#             queryset = Teacher.objects.filter(user_id=teacher_id)
#             queryset.update(avg_response_time=avg_response_time)
#             queryset.update(acceptance_rate=acceptance_rate)
#             return Response({"message": "Submitted successfully"})


# class TopicResult(APIView):
#
#     def get(self, request, format=None):
#         response = []
#         id = self.request.query_params.get('topic_id')
#         queryset = SingleQuestion.objects.filter(topic_id=id)
#         for obj in queryset:
#             result = {}
#             result['id'] = obj.id
#             result['question'] = obj.question
#             result['mark'] = obj.mark
#             response.append(result)
#         return Response({'all_questions': response})


class RatingView(APIView):

    @staticmethod
    def post(request):
        data = request.data
        serializer = RatingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

    @staticmethod
    def get(request, from_id, to_id):
        queryset = Rating.objects.filter(rating_from=from_id, rating_to=to_id)
        serializer = GetRatingSerializer(queryset, many=True)
        return Response(serializer.data)


class GetTopicQuestions(APIView):

    @staticmethod
    def get(request, topic_id, student_id):
        total_marks, marks_obtained, question_ids = 0, 0, []
        queryset = SingleQuestion.objects.filter(topic_id=topic_id)
        serializer = SingleQuestionSerializers(queryset, many=True)
        for item in serializer.data:
            total_marks += item['mark']
            question_ids.append(item['id'])
        serializer.data[0].get('subject')
        for i in question_ids:
            obtained_marks, marks_queryset = get_total_marks(request, topic_id=topic_id, student_id=student_id,
                                                             question_id=i)

            marks_obtained += float(obtained_marks)
        results = {
            "data": serializer.data,
            "total_marks": total_marks,
            "student_id": student_id,
            "topic_id": topic_id,
            "marks_obtained": marks_obtained,
        }
        return Response(results)


class PeerToPeer(APIView):

    def post(self, request):
        # current_user_id = request.user.id
        topic_id = self.request.query_params.get('topic_id')
        current_user_id = 2
        try:
            check = UserAnswerSheet.objects.get(topic_id=topic_id, sender_id=current_user_id)
            user_answer_sheet_obj_id = check.id
        except Exception as e:
            user_answer_sheet_obj = UserAnswerSheet.objects.create(topic_id=topic_id, sender_id=current_user_id)
            user_answer_sheet_obj_id = user_answer_sheet_obj.id
        student = Student.objects.exclude(user_id=current_user_id)
        serializer = StudentSerializers(student, many=True)
        id_list = []
        for obj in serializer.data:
            id_list.append(obj['user'])
        student = Student.objects.filter(user_id__in=id_list, peer_to_peer_count__in=[0, 1, 2, 3])
        updated_id = []
        for obj in student:
            updated_id.append(obj.user_id)
        if len(updated_id) >= 4:
            updated_id = random.sample(id_list, 4)
        # serializer = StudentSerializers(student, many=True)
        for id in updated_id:
            UserMark.objects.create(sender_id=current_user_id, receiver_id=id, is_teacher=False,
                                             answer_object_id=user_answer_sheet_obj_id)
        return Response({"message": "Peer to peer send"}, status=status.HTTP_201_CREATED)


class PtoPAcceptRequest(APIView):

    @staticmethod
    def get(request):
        try:
            # current_user_id = request.user.
            current_user_id = 10
            receiver_id = current_user_id
            sender_id = request.query_params.get('sender_id')
            answer_obj_id = request.query_params.get('answer_obj_id')
            UserMark.objects.filter(receiver_id=receiver_id, sender_id=sender_id, answer_object_id=answer_obj_id).update(is_accepted=True)
            Student.objects.filter(user_id=current_user_id).update(peer_to_peer_count=F('peer_to_peer_count')+1)
            return Response({"message": "Accepted"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class PtoPRejectRequest(APIView):

    @staticmethod
    def get(request):
        try:
            # current_user_id = request.user.
            current_user_id = 2
            receiver_id = current_user_id
            # sender_id = request.query_params.get('sender_id')
            # answer_obj_id = request.query_params.get('answer_obj_id')
            id = request.query_params.get("id")
            UserMark.objects.filter(id=id).update(is_accepted=False, is_checked=False)
            return Response({"message": "Rejected"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class PtoPPendingRequest(APIView):
    # permission_classes = [IsAuthenticated, ]

    @staticmethod
    def get(request):
        try:
            # current_user_id = request.user.id
            current_user_id = 5
            response = {}
            data = []
            pending = UserMark.objects.filter(receiver_id=current_user_id, is_accepted__isnull=True, is_checked=False)
            for obj in pending:
                result = {"id": obj.id, "answer_object_id": obj.answer_object_id, "sender_id": obj.sender_id}
                data.append(result)
            response['pending_data'] = data
            response["pending_count"] = pending.count()
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)