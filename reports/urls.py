from django.urls import path
from reports.views import (
    author_dashboard, submit_report, resubmit_report, submit_final_report, report_detail_author,
    request_extension, author_support,
    convener_dashboard, assign_reviewer, update_status, report_detail_convener,
    send_back_to_author, convener_confirm_decision, request_final_report, convener_send_final_to_head,
    grant_extension, send_resubmission_reminder, convener_support_inbox, convener_respond_support,
    convener_dismiss_report, convener_undismiss_report, convener_delete_report,
    head_dashboard, head_review_report, head_send_to_library,
    reviewer_dashboard, submit_review,
    librarian_dashboard, assign_doi,
    serve_encrypted_pdf,
)

urlpatterns = [
    # Author
    path('author/', author_dashboard, name='author_dashboard'),
    path('author/submit/', submit_report, name='submit_report'),
    path('author/resubmit/<int:report_id>/', resubmit_report, name='resubmit_report'),
    path('author/final-report/<int:report_id>/', submit_final_report, name='submit_final_report'),
    path('author/report/<int:report_id>/', report_detail_author, name='report_detail_author'),
    path('author/request-extension/<int:report_id>/', request_extension, name='request_extension'),
    path('author/support/', author_support, name='author_support'),

    # Convener
    path('convener/', convener_dashboard, name='convener_dashboard'),
    path('convener/assign/<int:report_id>/', assign_reviewer, name='assign_reviewer'),
    path('convener/status/<int:report_id>/', update_status, name='update_status'),
    path('convener/report/<int:report_id>/', report_detail_convener, name='report_detail_convener'),
    path('convener/send-back/<int:report_id>/', send_back_to_author, name='send_back_to_author'),
    path('convener/confirm-decision/<int:report_id>/', convener_confirm_decision, name='convener_confirm_decision'),
    path('convener/request-final/<int:report_id>/', request_final_report, name='request_final_report'),
    path('convener/send-to-head/<int:report_id>/', convener_send_final_to_head, name='convener_send_final_to_head'),
    path('convener/grant-extension/<int:report_id>/', grant_extension, name='grant_extension'),
    path('convener/send-reminder/<int:report_id>/', send_resubmission_reminder, name='send_resubmission_reminder'),
    path('convener/support/', convener_support_inbox, name='convener_support_inbox'),
    path('convener/support/<int:support_id>/respond/', convener_respond_support, name='convener_respond_support'),
    path('convener/dismiss/<int:report_id>/', convener_dismiss_report, name='convener_dismiss_report'),
    path('convener/undismiss/<int:report_id>/', convener_undismiss_report, name='convener_undismiss_report'),
    path('convener/delete/<int:report_id>/', convener_delete_report, name='convener_delete_report'),

    # Head
    path('head/', head_dashboard, name='head_dashboard'),
    path('head/review/<int:report_id>/', head_review_report, name='head_review_report'),
    path('head/send-to-library/<int:report_id>/', head_send_to_library, name='head_send_to_library'),

    # Reviewer
    path('reviewer/', reviewer_dashboard, name='reviewer_dashboard'),
    path('reviewer/review/<int:report_id>/', submit_review, name='submit_review'),

    # Librarian
    path('librarian/', librarian_dashboard, name='librarian_dashboard'),
    path('librarian/assign-doi/<int:report_id>/', assign_doi, name='assign_doi'),

    # Secure encrypted file serving
    path('file/', serve_encrypted_pdf, name='serve_encrypted_pdf'),
]
