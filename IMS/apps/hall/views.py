import pandas as pd
from django.shortcuts import render
from .models import Room

def hall_management(request):
    # Initialize context with all required data
    context = {
        'rooms': Room.objects.all(),
        'blocks': Room.objects.values_list('block', flat=True).distinct(),
        'dept_types': Room.objects.values_list('dept_category', flat=True).distinct(),
        'departments': Room.objects.values_list('dept_name', flat=True).distinct(),
    }

    if request.method == "POST" and 'file' in request.FILES:
        excel_file = request.FILES['file']
        print(f"Processing file: {excel_file.name}")  # Debug
        
        try:
            # Read the Excel file
            df = pd.read_excel(excel_file)
            print("Columns in file:", df.columns.tolist())  # Debug
            
            # Process each row
            processed = 0
            for _, row in df.iterrows():
                try:
                    hall_no = str(row['hall_no']).strip()
                    if not hall_no:
                        continue
                        
                    Room.objects.update_or_create(
                        hall_no=hall_no,
                        defaults={
                            'dept_category': str(row.get('dept_category', '')),
                            'dept_name': str(row.get('dept_name', '')),
                            'strength': int(row.get('strength', 0)),
                            'days': int(row.get('days', 0)),
                            'block': "-",
                            'staff_allotted': "Not Allotted",
                            'benches': 0,
                        }
                    )
                    processed += 1
                except Exception as e:
                    print(f"Error in row: {e}")
                    continue

            context['message'] = f"Successfully processed {processed} records"
            # Refresh the data
            context.update({
                'rooms': Room.objects.all(),
                'blocks': Room.objects.values_list('block', flat=True).distinct(),
                'dept_types': Room.objects.values_list('dept_category', flat=True).distinct(),
                'departments': Room.objects.values_list('dept_name', flat=True).distinct(),
            })
            
        except Exception as e:
            print(f"Error processing file: {e}")
            context['error'] = f"Error processing file: {str(e)}"

    return render(request, 'hall/hall_management.html', context)

def hall_list(request):
    rooms = Room.objects.all()
    return render(request, 'hall/hall_list.html', {'halls': rooms})