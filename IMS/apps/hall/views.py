import pandas as pd
from django.shortcuts import render
from .models import Room

def hall_management(request):
    print("\n===== NEW REQUEST =====")  # Debug
    print(f"Request method: {request.method}")  # Debug
    
    # Initialize context with all required data
    context = {
        'rooms': Room.objects.all(),
        'blocks': Room.objects.values_list('block', flat=True).distinct(),
        'dept_types': Room.objects.values_list('dept_category', flat=True).distinct(),
        'departments': Room.objects.values_list('dept_name', flat=True).distinct(),
    }

    if request.method == "POST":
        print("\nPOST request received")  # Debug
        print("Request.FILES contents:", request.FILES)  # Debug
        print("Request.POST contents:", request.POST)  # Debug
        
        if 'file' not in request.FILES:
            print("\nERROR: No file found in request.FILES")  # Debug
            context['error'] = "No file was uploaded"
            return render(request, 'hall/hall_management.html', context)
            
        excel_file = request.FILES['file']
        print(f"\nFile detected: {excel_file.name}")  # Debug
        print(f"File size: {excel_file.size} bytes")  # Debug
        print(f"Content type: {excel_file.content_type}")  # Debug
        
        try:
            print("\nAttempting to read Excel file...")  # Debug
            df = pd.read_excel(excel_file)
            print("SUCCESS: File read successfully")  # Debug
            print("Columns in file:", df.columns.tolist())  # Debug
            print("First row sample:", df.iloc[0].to_dict() if not df.empty else "Empty DataFrame")  # Debug

            # Rest of your processing code...
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
                    print(f"Row processing error: {e}")  # Debug
                    continue

            context['message'] = f"Successfully processed {processed} records"
            # Refresh data
            context.update({
                'rooms': Room.objects.all(),
                'blocks': Room.objects.values_list('block', flat=True).distinct(),
                'dept_types': Room.objects.values_list('dept_category', flat=True).distinct(),
                'departments': Room.objects.values_list('dept_name', flat=True).distinct(),
            })
            
        except Exception as e:
            print(f"\nERROR processing file: {str(e)}")  # Debug
            context['error'] = f"Error processing file: {str(e)}"

    return render(request, 'hall/hall_management.html', context)

def hall_list(request):
    rooms = Room.objects.all()
    return render(request, 'hall/hall_list.html', {'halls': rooms})