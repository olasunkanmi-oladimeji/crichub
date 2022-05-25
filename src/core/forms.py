from django import forms
from core.models import Post,Comment,Contact


class PostForm(forms.ModelForm):
    """Form definition for Post."""

    class Meta:
        """Meta definition for Postform."""

        model = Post
        fields = ('title','author','content','image','video')

        widgets = {
            'title' : forms.TextInput(attrs={'class' :'form-control'}),
            'author' : forms.Select(attrs={'class' :'form-control'}),
            'content' : forms.Textarea(attrs={'class' :'form-control'}),
            'image' : forms.TextInput(attrs={'class' :'form-control','type':'file', 'id':'formFile'}),
            'video' : forms.TextInput(attrs={'class' :'form-control','type':'file', 'id':'formFile'})

        }


class CommentForm(forms.ModelForm):
    """Form definition for MODELNAME."""

    class Meta:
        """Meta definition for MODELNAMEform."""

        model = Comment
        fields = ('body',)

class ContactForm(forms.ModelForm):
    """Form definition for MODELNAME."""
    class Meta:
        """Meta definition for MODELNAMEform."""

        model = Contact
        fields = ('name','email','message')

class UpdateForm(forms.ModelForm):
    """Form definition for Post."""

    class Meta:
        """Meta definition for Postform."""

        model = Post
        fields = ('title','author','content','image','video')

        widgets = {
            'title' : forms.TextInput(attrs={'class' :'form-control'}),
            'author' : forms.Select(attrs={'class' :'form-control'}),
            'content' : forms.Textarea(attrs={'class' :'form-control'}),

            'image' : forms.TextInput(attrs={'class' :'form-control','type':'file', 'id':'formFile'}),
            'video' : forms.TextInput(attrs={'class' :'form-control','type':'file', 'id':'formFile'})

        }
