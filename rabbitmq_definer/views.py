from django.shortcuts import render
from .dict_getters import get_full_dict
from django.http import HttpRequest, HttpResponse
from .models import Schema
from django.http import FileResponse

from .constants import SCHEMA_DEFINITIONS_PATH
from django.core.files.temp import NamedTemporaryFile
from wsgiref.util import FileWrapper

import json, os

# Create your views here.

def home(request: HttpRequest):
    if request.method == 'POST':
        # action = request.POST.get('action')
        schema_pk = request.POST.get('schema')
        schema = Schema.objects.get(pk=schema_pk) if schema_pk else None
        try:
            full_dict = get_full_dict(schema)

            file_path = SCHEMA_DEFINITIONS_PATH

            # Write the dictionary to a JSON file
            with open(file_path, 'w') as json_file:
                json.dump(full_dict, json_file, indent=4)

            response = FileResponse(open(file_path, 'rb'), content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="{file_path}"'
            
            # Remove the file after serving
            os.remove(file_path)
            
            return response

        except Exception as e:
            print(f"Exception getting full dict: {e}")
        
    
    # else and except refresh the view
    schemas = Schema.objects.all()
    context = {"schemas": schemas}

    return render(request, "home.html", context)
    



