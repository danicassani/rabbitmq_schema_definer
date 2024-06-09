from django.shortcuts import redirect
from .dict_getters import get_full_dict
from .models import Schema

import json

# Create your views here.

def index(request):
    schema = Schema.objects.first()

    full_dict = get_full_dict(schema)

    print(full_dict)
    # Define the file path
    file_path = "data.json"

    # Write the dictionary to a JSON file
    with open(file_path, 'w') as json_file:
        json.dump(full_dict, json_file, indent=4)

    return redirect("/admin")

