from django.shortcuts import render
from .models import InvigilationConstraint
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json



def invigilation_settings(request):
    constraints = InvigilationConstraint.objects.all().order_by('name')
    return render(request, 'invigilation_settings/invigilation_settings.html', {
        'constraints': constraints
    })

@require_POST
@csrf_exempt
def update_constraints(request):
    try:
        data = json.loads(request.body)
        for change in data.get('changes', []):
            constraint = InvigilationConstraint.objects.get(pk=change['id'])
            setattr(constraint, change['field'], change['value'])
            constraint.save()
        return JsonResponse({'message': 'Constraints updated successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
