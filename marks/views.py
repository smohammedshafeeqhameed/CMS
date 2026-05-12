try:
    import openpyxl
except ImportError:
    openpyxl = None
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from academics.models import Subject, Enrollment
from users.models import User
from decimal import Decimal

class FacultyRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_faculty

class DownloadMarksTemplateView(LoginRequiredMixin, FacultyRequiredMixin, View):
    def get(self, request):
        course_id = request.GET.get('course')
        semester = request.GET.get('semester')

        if not course_id or not semester:
            messages.error(request, "Please select both Course and Semester.")
            return redirect('dashboard')

        # Get students mapped to the selected course and semester via their profile
        try:
            course_int = int(course_id)
            sem_int = int(semester)
        except (ValueError, TypeError):
            messages.error(request, "Invalid Course or Semester selected.")
            return redirect('dashboard')

        students = User.objects.filter(
            role='STUDENT',
            student_profile__course_id=course_int,
            student_profile__current_semester=sem_int
        ).distinct()
        
        if not students:
            messages.warning(request, "No students found for the selected Course and Semester.")
            return redirect('dashboard')

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = f"Marks_Sem{semester}"

        # Headers
        headers = ['STUDENT ID', 'STUDENT NAME', 'CGPA', 'TOTAL MARKS']
        ws.append(headers)

        # Data rows
        for student in students:
            row = [
                student.username, 
                student.get_full_name() or student.username,
                student.gpa if hasattr(student, 'gpa') else 0,
                student.total_marks if hasattr(student, 'total_marks') else 0
            ]
            ws.append(row)

        # UI cleanup
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if cell.value and len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except: pass
            ws.column_dimensions[column].width = max_length + 5

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=Marks_Upload_Template.xlsx'
        wb.save(response)
        return response

class UploadMarksExcelView(LoginRequiredMixin, FacultyRequiredMixin, View):
    def post(self, request):
        excel_file = request.FILES.get('marks_excel')
        if not excel_file:
            messages.error(request, "No file uploaded.")
            return redirect('dashboard')

        try:
            wb = openpyxl.load_workbook(excel_file)
            ws = wb.active
            rows = list(ws.rows)
            
            if len(rows) < 2:
                messages.error(request, "The Excel file is empty.")
                return redirect('dashboard')

            headers = [cell.value for cell in rows[0]]
            # Find indices for ID, Total Marks, and CGPA
            try:
                id_idx = headers.index('STUDENT ID')
                total_idx = headers.index('TOTAL MARKS')
                cgpa_idx = headers.index('CGPA')
            except ValueError:
                messages.error(request, "Excel structure mismatch. Please use the downloaded template.")
                return redirect('dashboard')

            update_count = 0
            for row in rows[1:]:
                student_id = row[id_idx].value
                total_val = row[total_idx].value
                cgpa_val = row[cgpa_idx].value

                if student_id:
                    try:
                        clean_username = str(student_id).strip()
                        student = User.objects.get(username__iexact=clean_username, role='STUDENT')
                        
                        if total_val is not None:
                            student.total_marks = Decimal(str(total_val))
                        if cgpa_val is not None:
                            student.gpa = Decimal(str(cgpa_val))
                            # Also update StudentProfile.cgpa if it exists
                            if hasattr(student, 'student_profile'):
                                student.student_profile.cgpa = Decimal(str(cgpa_val))
                                student.student_profile.save()
                                
                        student.save()
                        update_count += 1
                    except (User.DoesNotExist, ValueError):
                        continue

            messages.success(request, f"Successfully updated marks for {update_count} students.")
        except Exception as e:
            messages.error(request, f"Error processing marks file: {str(e)}")

        return redirect('dashboard')
