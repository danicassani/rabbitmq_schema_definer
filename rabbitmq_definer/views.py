from django.shortcuts import render
from .dict_getters import get_full_schema_definitions, get_full_federations, get_full_policies, get_full_shovels
from django.http import HttpRequest, FileResponse
from django.http.response import HttpResponseBadRequest
from .models import Schema

from .constants import *
import json, os

# Create your views here.

def home(request: HttpRequest):
    if request.method == 'POST':
        action = request.POST.get('action')
        schema_pk = request.POST.get('schema')
        schema = Schema.objects.get(pk=schema_pk) if schema_pk else None
        file_path = ""
        
        if action == SCHEMA_DEFINITIONS_ACTION:
            file_path = SCHEMA_DEFINITIONS_PATH
            try:
                full_dict = get_full_schema_definitions(schema)
            except Exception as e:
                print(f"Exception getting schema definitions: {e}")
        
        elif action == FEDERATIONS_ACTION:
            file_path = FEDERATIONS_PATH
            try:
                full_dict = get_full_federations(schema)
            except Exception as e:
                print(f"Exception getting federations: {e}")
            
        elif action == POLICIES_ACTION:
            file_path = POLICIES_PATH
            try:
                full_dict = get_full_policies(schema)
            except Exception as e:
                print(f"Exception getting policies: {e}")
            
        elif action == SHOVELS_ACTION:
            file_path = SHOVELS_PATH
            try:
                full_dict = get_full_shovels(schema)
            except Exception as e:
                print(f"Exception getting shovels: {e}")
        
        else:
            return HttpResponseBadRequest()
            
        try:
            # Write the dictionary to a JSON file
            with open(file_path, 'w') as json_file:
                json.dump(full_dict, json_file, indent=4)

            response = FileResponse(open(file_path, 'rb'), content_type='application/json')

        except Exception as e:
            print(f"Exception getting full dict: {e}")
        
        response['Content-Disposition'] = f'attachment; filename="{file_path}"'
        
        # Remove the file after serving
        os.remove(file_path)
        
        return response
    
    # else and except refresh the view
    schemas = Schema.objects.all()
    context = {"schemas": schemas}

    return render(request, "home.html", context)
    



