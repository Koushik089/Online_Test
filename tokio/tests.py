from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from tokio.models import Question, ExamSession, StudentResponse, UserProfile, Notification
from voting.models import Poll, Candidate, Vote

class OnlineExamSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='student1', password='password123', email='student1@example.com')
        self.admin = User.objects.create_superuser(username='admin1', password='password123', email='admin1@example.com')
        
        # Seed questions
        self.q1 = Question.objects.create(
            subject='dbms',
            question_text='What is SQL?',
            option_a='Structured Query Language',
            option_b='Simple Query Language',
            option_c='Sequential Query Language',
            option_d='Server Query Language',
            correct_answer='a'
        )
        self.q2 = Question.objects.create(
            subject='computer_network',
            question_text='What port does HTTP use?',
            option_a='443',
            option_b='80',
            option_c='21',
            option_d='22',
            correct_answer='b'
        )

    def test_landing_and_auth_pages(self):
        # Index landing page
        res = self.client.get(reverse('wellcome'))
        self.assertEqual(res.status_code, 200)

        # Login student
        login_res = self.client.post(reverse('student_login'), {'username': 'student1', 'password': 'password123'})
        self.assertEqual(login_res.status_code, 302)

        # Dashboard / Hero page
        hero_res = self.client.get(reverse('hero'))
        self.assertEqual(hero_res.status_code, 200)

    def test_missing_views_exist(self):
        self.client.login(username='student1', password='password123')
        
        # Leaderboard
        lb_res = self.client.get(reverse('leaderboard'))
        self.assertEqual(lb_res.status_code, 200)

        # Performance Analytics
        perf_res = self.client.get(reverse('performance'))
        self.assertEqual(perf_res.status_code, 200)

        # Notifications
        notif_res = self.client.get(reverse('notifications_list'))
        self.assertEqual(notif_res.status_code, 200)

    def test_exam_flow_and_ajax(self):
        self.client.login(username='student1', password='password123')
        
        # Start DBMS exam
        res = self.client.get(reverse('DBMS'))
        self.assertEqual(res.status_code, 200)
        
        session = ExamSession.objects.filter(user=self.user, subject='dbms').first()
        self.assertIsNotNone(session)
        self.assertEqual(session.duration_minutes, 15)

        # AJAX save answer
        save_res = self.client.post(
            reverse('save_answer'),
            data={'session_id': str(session.id), 'question_id': self.q1.id, 'selected_answer': 'a'},
            content_type='application/json'
        )
        self.assertEqual(save_res.status_code, 200)
        self.assertJSONEqual(save_res.content, {'status': 'success'})

        # AJAX bookmark question
        bm_res = self.client.post(
            reverse('bookmark_question'),
            data={'session_id': str(session.id), 'question_id': self.q1.id},
            content_type='application/json'
        )
        self.assertEqual(bm_res.status_code, 200)
        self.assertJSONEqual(bm_res.content, {'status': 'success', 'bookmarked': True})

        # Submit Exam
        sub_res = self.client.post(reverse('submit_exam'), {'session_id': str(session.id)})
        self.assertEqual(sub_res.status_code, 302)

        session.refresh_from_db()
        self.assertTrue(session.completed)
        self.assertTrue(session.passed)
        self.assertEqual(session.score, 1)

    def test_pdf_generation(self):
        self.client.login(username='student1', password='password123')
        session = ExamSession.objects.create(
            user=self.user, subject='dbms', score=1, total_questions=1, percentage=100.0, passed=True, completed=True
        )
        
        # Download score PDF
        pdf_res = self.client.get(reverse('download_result_pdf', kwargs={'session_id': session.id}))
        self.assertEqual(pdf_res.status_code, 200)
        self.assertEqual(pdf_res['Content-Type'], 'application/pdf')

        # Download certificate PDF
        cert_res = self.client.get(reverse('download_certificate_pdf', kwargs={'session_id': session.id}))
        self.assertEqual(cert_res.status_code, 200)
        self.assertEqual(cert_res['Content-Type'], 'application/pdf')

    def test_voting_system(self):
        self.client.login(username='student1', password='password123')
        
        # Create Poll
        poll = Poll.objects.create(title='Best Subject 2026', description='Vote for best topic')
        c1 = Candidate.objects.create(poll=poll, name='DBMS')
        c2 = Candidate.objects.create(poll=poll, name='Computer Networks')

        # Cast Vote
        vote_res = self.client.post(reverse('cast_vote', kwargs={'poll_id': poll.id}), {'candidate': c1.id})
        self.assertEqual(vote_res.status_code, 302)

        c1.refresh_from_db()
        self.assertEqual(c1.votes_count, 1)

        # Prevent double voting
        double_res = self.client.post(reverse('cast_vote', kwargs={'poll_id': poll.id}), {'candidate': c2.id})
        self.assertEqual(double_res.status_code, 302)
        c2.refresh_from_db()
        self.assertEqual(c2.votes_count, 0)

