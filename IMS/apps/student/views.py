from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
import pandas as pd
from .models import Student

class student_upload_view(View):
    def get(self, request):
        students = Student.objects.all()
    
        # Get unique filter options from DB
        batches = Student.objects.values_list('batch', flat=True).distinct()
        dept_ids = Student.objects.values_list('dept_id', flat=True).distinct()
        degrees = Student.objects.values_list('degree', flat=True).distinct()
        branches = Student.objects.values_list('branch', flat=True).distinct()
        categories = Student.objects.values_list('category', flat=True).distinct()
        sections = Student.objects.values_list('section', flat=True).distinct()
    
        # Get filter values from GET params
        selected_batch = request.GET.get('batch', 'All')
        selected_dept_id = request.GET.get('dept_id', 'All')
        selected_degree = request.GET.get('degree', 'All')
        selected_branch = request.GET.get('branch', 'All')
        selected_category = request.GET.get('category', 'All')
        selected_section = request.GET.get('section', 'All')
    
        # Apply filters if not "All"
        if selected_batch != 'All':
            students = students.filter(batch=selected_batch)
        if selected_dept_id != 'All':
            students = students.filter(dept_id=selected_dept_id)
        if selected_degree != 'All':
            students = students.filter(degree=selected_degree)
        if selected_branch != 'All':
            students = students.filter(branch=selected_branch)
        if selected_category != 'All':
            students = students.filter(category=selected_category)
        if selected_section != 'All':
            students = students.filter(section=selected_section)
    
        context = {
            'students': students,
            'filter_fields': [
                ('batch', batches, selected_batch),
                ('dept_id', dept_ids, selected_dept_id),
                ('degree', degrees, selected_degree),
                ('branch', branches, selected_branch),
                ('category', categories, selected_category),
                ('section', sections, selected_section),
            ],
        }
        
        return render(request, 'student/student.html', context)


    def post(self, request):
            excel_file = request.FILES.get('excel_file')
            if not excel_file:
                return render(request, 'student/student.html', {'error': 'Please upload a file.'})

            try:
                df = pd.read_excel(excel_file)
            except Exception:
                return render(request, 'student/student.html', {'error': 'Invalid Excel file format.'})

            # Normalize headers
            df.columns = [col.strip().lower() for col in df.columns]

            # Remove 'unnamed: 0' if it exists
            df = df.loc[:, ~df.columns.str.contains('^unnamed')]

            expected_headers = [
                'batch', 'dept_id', 'degree', 'branch',
                'reg_no', 'roll_no', 'name', 'dob',
                'category', 'section', 'gender'
            ]

            if df.columns.tolist() != expected_headers:
                return render(request, 'student/student.html', {
                    'error': f"Excel headers do not match.<br>Expected: {expected_headers}<br>Got: {df.columns.tolist()}"
                })

            for _, row in df.iterrows():
                Student.objects.update_or_create(
                    reg_no=row['reg_no'],
                    defaults={
                        'batch': row['batch'],
                        'dept_id': row['dept_id'],
                        'degree': row['degree'],
                        'branch': row['branch'],
                        'roll_no': row['roll_no'],
                        'name': row['name'],
                        'dob': row['dob'],
                        'category': row['category'],
                        'section': row['section'],
                        'gender': row['gender'],
                    }
                )

            messages.success(request, "Student data uploaded successfully.")
            return redirect('student_upload')


