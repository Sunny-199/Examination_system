from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView
router = DefaultRouter()
router.register(r'register', UserViewSet, basename='register'),

urlpatterns = [
    path('', include(router.urls)),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('home/<int:subject_id>/', HomePage.as_view()),
    path('routine-list/<int:subject_id>/', RoutineListWrittenView.as_view()),
    path('get-question/<int:pk>/', ViewQuestion.as_view()),
    path('image-upload/', SendImage.as_view()),
    path('send-answer/', SentAnswer.as_view(), name='get_answer'),
    path('answer-view/<int:user_mark_id>/', AnswerView.as_view(), name='get_answer'),
    path('submit-question/', SubmitQuestion.as_view(), name='submit-question'),
    path('get-teacher-and-expert/<str:t_type>/', GetTeachersFilter.as_view(), name='rating_teacher'),
    path('favourite_teacher/', FavouriteTeacherView.as_view(), name='favourite_teacher'),
    path('student-result-list/', StudentResultList.as_view(), name='student-result-list'),
    path('question-result-list/<int:answer_id>/', QuestionResultList.as_view(), name='single_question_result'),
    path('specific-answers/<int:mark_id>/', SpecificAnswers.as_view(), name='specific-answers'),
    path('peer_to_peer/', PeerToPeer.as_view(), name='peer_to_peer'),
    path('peer_to_peer_status/', PtoPAcceptRequest.as_view(), name='peer_to_peer_status'),
    path('peer_to_peer_pending/', PtoPPendingRequest.as_view(), name='peer_to_peer_pending'),
    path('peer_to_peer_reject/', PtoPRejectRequest.as_view(), name='peer_to_peer_reject'),

    # Exminer view

    path('examiner-home/', ExaminerProfile.as_view()),
    path('pending-request/', PendingRequests.as_view()),
    # path('assessment/', written_views.QuestionAssessmentByTeacher.as_view(), name='assessment')
    # path('image_upload/',written_views.AnswerUpload.as_view(), name='image_upload'),
    # path('single_question_result/', written_views.SpecificAnswers.as_view(), name='single_question_result'),
    # path('assessment/', written_views.QuestionAssessmentByTeacher.as_view(), name='assessment'),
    # path('assessment/student/<int:student_id>/topic/<int:topic_id>/question/<int:question_id>/', written_views.QuestionAssessmentByTeacher.as_view(), name='assessment'),
    # path('answer_submit/', written_views.AnswerSubmit.as_view(), name='Answer_submit'),
    # path('send_answer/', written_views.SendAnswerToTeacher.as_view(), name='send_answer'),
    # path('topic_result/', written_views.TopicResult.as_view(), name='topic_result'),
    # path('accept/', written_views.Accept.as_view(), name='accept'),
    # path('submit_checked_topic/', written_views.SubmitCheckedTopic.as_view(), name='submit_checked_topic'),
    # path('get_single_answer_list/student/<int:student_id>/topic/<int:topic_id>/question/<int:question_id>/', written_views.SingleQuestionResultList.as_view(), name='get_single_answer_list'),
    # path('rating/from/<int:from_id>/to/<int:to_id>/', written_views.RatingView.as_view(), name='rating'),
    # path('rating/', written_views.RatingView.as_view(), name='rating'),
    # path('topic_question/topic/<int:topic_id>/student/<int:student_id>/', written_views.GetTopicQuestions.as_view(), name='topic_question')
]