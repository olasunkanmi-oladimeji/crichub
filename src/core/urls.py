from core.views import (HomeView,AboutView,PostView,comment_approve
                        ,comment_remove,post_approve,postCreate,PostlistView,
                        PostDelete,PostUpdate)
from django.urls import path

app_name="blog"

urlpatterns = [
    path("", HomeView),
    path("About-Crichub", AboutView, name="aboutus"),
    path("<id>", PostView, name="post_detail"),
    path('comment/<int:pk>/approve/', comment_approve, name='comment_approve'),
    path('comment/<int:pk>/remove/', comment_remove, name='comment_remove'),
    path('publish/<int:pk>',post_approve,name='post_approve'),
    path('new/post',postCreate,name='postCreate'),
    path('post-list/',PostlistView,name='draft'),
    path('delete/post/<int:pk>',PostDelete.as_view(),name='PostDelete'),
    path('Post/Update/<int:pk>',PostUpdate.as_view(),name='PostUpdate'),

    
]
