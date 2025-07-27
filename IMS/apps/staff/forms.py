from django import forms
from django.core.validators import FileExtensionValidator
from .models import Staff

class StaffUploadForm(forms.Form):
    excel_file = forms.FileField(
        label='Excel File',
        validators=[
            FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])
        ],
        widget=forms.FileInput(attrs={
            'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 transition-colors border border-gray-300 rounded-lg',
            'accept': '.xlsx,.xls'
        })
    )

class StaffEditForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['staff_id', 'name', 'staff_category', 'designation', 
                 'dept_category', 'dept_name', 'mobile', 'email', 
                 'date_of_joining', 'is_active']
        widgets = {
            'date_of_joining': forms.DateInput(attrs={'type': 'date'}),
        }