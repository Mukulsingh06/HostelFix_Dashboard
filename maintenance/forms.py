from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Complaint, ComplaintComment


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all',
            'placeholder': 'Username',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all',
            'placeholder': 'Password',
            'autocomplete': 'current-password',
        })
    )


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all',
        'placeholder': 'Choose a username',
    }))
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all',
        'placeholder': 'First name',
    }))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all',
        'placeholder': 'Last name',
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'w-full px-4 py-3 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all',
        'placeholder': 'Email address',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all',
        'placeholder': 'Create a password',
    }))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all',
        'placeholder': 'Confirm password',
    }))
    phone = forms.CharField(max_length=15, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all',
        'placeholder': 'Phone number',
    }))
    hostel_block = forms.ChoiceField(choices=UserProfile.BLOCK_CHOICES, widget=forms.Select(attrs={
        'class': 'w-full px-4 py-3 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all',
    }))
    room_number = forms.CharField(max_length=10, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all',
        'placeholder': 'Room number (e.g., 204)',
    }))

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('password2'):
            raise forms.ValidationError("Passwords do not match.")
        if User.objects.filter(username=cleaned.get('username')).exists():
            raise forms.ValidationError("Username already taken.")
        return cleaned


INPUT_CLASS = 'w-full px-4 py-3 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all'


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['title', 'category', 'urgency', 'hostel_block', 'room_number', 'description', 'attachment']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'Brief summary of the issue',
            }),
            'category': forms.Select(attrs={'class': INPUT_CLASS}),
            'urgency': forms.Select(attrs={'class': INPUT_CLASS}),
            'hostel_block': forms.Select(attrs={'class': INPUT_CLASS}),
            'room_number': forms.TextInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'Room number',
            }),
            'description': forms.Textarea(attrs={
                'class': INPUT_CLASS,
                'rows': 4,
                'placeholder': 'Describe the issue in detail — what happened, when, and exactly where...',
            }),
            'attachment': forms.ClearableFileInput(attrs={
                'class': 'hidden',
                'id': 'attachment-input',
                'accept': 'image/*',
            }),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = ComplaintComment
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': INPUT_CLASS,
                'rows': 2,
                'placeholder': 'Write a comment...',
            }),
        }
