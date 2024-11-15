from django import forms
from .models import ForumPost, ForumComment

class PostForm(forms.ModelForm):
    category = forms.ChoiceField(
        choices=[
            ('general', 'General Discussion'),
            ('kali', 'Kali Linux'),
            ('python', 'Python Security'),
            ('pentesting', 'Penetration Testing'),
            ('ctf', 'CTF Discussion'),
            ('tools', 'Security Tools'),
            ('help', 'Help & Support')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = ForumPost
        fields = ['title', 'content', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = ForumComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
