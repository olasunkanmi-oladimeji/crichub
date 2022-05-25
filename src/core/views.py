
from django.shortcuts import render,get_object_or_404,redirect
from core.models import Post,Comment,Contact
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from core.forms import CommentForm, PostForm,UpdateForm,ContactForm
from django.views import generic
from django.urls import reverse_lazy
from django.http import HttpResponse
from store.models import Item

def HomeView(request):
    post =Post.objects.order_by('-publish_date').filter(publish_date__lt=timezone.now())

    page = request.GET.get('page', 1)

    paginator = Paginator(post, 10)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    posted =Post.objects.order_by('publish_date').filter(publish_date__lt=timezone.now())

    page = request.GET.get('page', 1)

    paginator = Paginator(posted, 10)
    try:
        past = paginator.page(page)
    except PageNotAnInteger:
        past = paginator.page(1)
    except EmptyPage:
        past = paginator.page(paginator.num_pages)

    #Product

    product  = Item.objects.all().order_by('-id')

    page = request.GET.get('page', 1)

    paginator = Paginator(product, 4)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    

    return render(request,'blog/home-page.html',{
                                                'past':past,
                                                'posts':posts,
                                                'page_obj':page_obj,
    })

def AboutView(request):

    post =Post.objects.order_by('-publish_date').filter(publish_date__lt=timezone.now())

    page = request.GET.get('page', 1)

    paginator = Paginator(post, 10)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    #Product

    product  = Item.objects.all().order_by('-id')

    page = request.GET.get('page', 1)

    paginator = Paginator(product, 4)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            
            form.save()
            HttpResponse("Thank You For Contacting Us We Will get back to you within 24hr")
            
    else:
        form = CommentForm()
    return render(request,'blog/about-us.html',{'page_obj':page_obj,'posts':posts,})


    

def PostView(request,id):
    posted =Post.objects.order_by('publish_date').filter(publish_date__lt=timezone.now())
    post = get_object_or_404(Post,id=id)

    page = request.GET.get('page', 1)

    paginator = Paginator(posted, 10)
    try:
        past = paginator.page(page)
    except PageNotAnInteger:
        past = paginator.page(1)
    except EmptyPage:
        past = paginator.page(paginator.num_pages)

    if request.method == "POST":
        form = CommentForm(request.POST or None)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('blog:post_detail', id=post.pk)
    else:
        form = CommentForm()
    return render(request,'blog/single-post.html',{'post':post,'form':form,'past':past})


@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('blog:post_detail', id=comment.post.pk)

@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    return redirect('blog:post_detail', id=comment.post.pk)

@login_required
def post_approve(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.approve_post()
    return redirect('blog:post_detail', id=post.pk)

def postCreate(request):

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():

            post = form.save(commit=False)
            post.author = request.user
            post.image = request.FILES.get('image')
            post.video = request.FILES.get('video')


            post.save()
            return redirect("blog:post_detail", id=post.id)
    else:
        form = PostForm()
    return render(request, "blog/post_create.html", {"form": form})

def PostlistView(request):
    post =Post.objects.all().order_by('-publish_date')
    page = request.GET.get('page', 1)

    paginator = Paginator(post, 10)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request,'blog/post_list.html',{'posts':posts })
    


class PostDelete(generic.DeleteView):
    model = Post
    success_url = reverse_lazy('blog:draft')
    template_name = 'blog/post_delete.html'

class PostUpdate(generic.UpdateView):
    model = Post
    form_class = UpdateForm

    template_name = 'blog/post_update.html'

