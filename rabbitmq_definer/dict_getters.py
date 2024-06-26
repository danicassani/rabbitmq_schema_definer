from .models import Schema, Service, BindedService, Federation, MqUser
import hashlib, base64

def __get_base64_hash(input_string: str) -> str:
    # Choose the hashing algorithm
    hash_object = hashlib.sha256()
    
    # Encode the input string to bytes and update the hash object
    hash_object.update(input_string.encode('utf-8'))
    
    # Get the binary digest of the hash
    binary_digest = hash_object.digest()
    
    # Convert the binary digest to its Base64 representation
    base64_representation = base64.b64encode(binary_digest).decode('utf-8')
    
    return base64_representation


def __format_permission(user: MqUser, service: Service):
    permission_dict = {
            "user": user.username,
            "vhost": service.name,
            "configure": ".*",
            "read": ".*",
            "write": ".*",
        }
    
    return permission_dict

def __format_queue(queue_name, vhost_name):
    queue_dict = {
        "name": queue_name,
        "vhost": vhost_name,
        "durable": True,
        "auto_delete": False,
        "arguments": {}
    }
    
    return queue_dict


def __format_exchange(exchange_name, vhost_name):
    exchange_dict = {
        "name": exchange_name,
        "vhost":  vhost_name,
        "durable": True,
        "auto_delete": False,
        "internal": False,
        "arguments": {}
    }

    return exchange_dict

def __format_binding(source_exchange_name: str, destination_name: str, vhost_name: str, routing_key: str):
    binging_dict ={
        "source": source_exchange_name,
        "vhost": vhost_name,
        "destination": destination_name,
        "destination_type": "",
        "routing_key": routing_key,
        "arguments": {}
    }

    if destination_name.endswith("_E"):
        binging_dict["destination_type"]="exchange"
    elif destination_name.endswith("_Q"):
        binging_dict["destination_type"]="queue"

    return binging_dict

def __format_federation(federation: Federation):
    federation_dict = {
        "username": federation.service.federation_user.username,
        "password": federation.service.federation_user.password,
        "dst-host": federation.hostname,
        "port": federation.port,
        "exchange": f"SEND2{federation.destination_level}_E",
        "max-hops": federation.max_hops,
        "vhost": federation.service.name,
        "upstream-name": federation.name
    }

    return federation_dict

def __format_queuesize_policy(service_name: str):
    queuesize_policy_dict = {
            "vhost": service_name,
            "policy-name": "QUEUESIZE_P",
            "pattern": ".*",
            "apply-to": "queues",
            "definition": {
               "max-length": 10000
            },
            "priority": 0
        }
    
    return queuesize_policy_dict

def __format_federation_policy(federation: Federation):
    federation_policy_dict = {
            "vhost": federation.service.name,
            "policy-name": federation.name + "P",
            "pattern": f"FROM{federation.destination_level}_E",
            "apply-to": "exchanges",
            "definition": {
                "federation-upstream": federation.name
            },
            "priority": 0
        }
    
    return federation_policy_dict

def __format_mqtt_to_service_shovel(mqttio_shoveluser: MqUser, service: Service):
    mqtt_input_shovel_dict = {
        "src-user": mqttio_shoveluser.username,
        "src-password": mqttio_shoveluser.password,
        "src-vhost": "MQTT_IO",
        "src-type": "queue",
        "src-queue": f"{service.name}_Q",
        "dest-user": service.shovel_user.username,
        "dest-password": service.shovel_user.password,
        "dest-vhost": service.name,
        "dest-type": "exchange",
        "dest-exchange": "MQTT_E" 
    }
    
    return mqtt_input_shovel_dict

def __format_service_to_mqtt_shovel(mqttio_shoveluser: MqUser, service: Service):
    mqtt_output_shovel_dict = {
        "src-user": service.shovel_user.username,
        "src-password": service.shovel_user.password,
        "src-vhost": service.name,
        "src-type": "queue",
        "src-queue": "SEND2MQTTIO_Q",
        "dest-user": mqttio_shoveluser.username,
        "dest-password": mqttio_shoveluser.password,
        "dest-vhost": "MQTT_IO",
        "dest-type": "exchange",
        "dest-exchange": "MQTT_IO_E" 
    }
    
    return mqtt_output_shovel_dict

def __format_service_to_db_shovel(db_service_shoveluser: MqUser, service: Service):
    db_service_shovel_dict = {
        "src-user": service.shovel_user.username,
        "src-password": service.shovel_user.password,
        "src-vhost": service.name,
        "src-type": "queue",
        "src-queue": "SEND2DB_Q",
        "dest-user": db_service_shoveluser.username,
        "dest-password": db_service_shoveluser.password,
        "dest-vhost": "DB_SERVICE",
        "dest-type": "exchange",
        "dest-exchange": f"FROM{service.name}_E" 
    }
    
    return db_service_shovel_dict

def get_users_and_permissions(schema: Schema):
    aditional_users: list[MqUser] = list(schema.aditional_users.all())
    binded_services: list[BindedService] = list(schema.binded_services.all())
    
    service_users : list[MqUser] = []
    permissions_output = []

    for binded_service in binded_services:
        service_users.append(binded_service.service.normal_user)
        permissions_output.append(__format_permission(binded_service.service.normal_user, binded_service.service))
        service_users.append(binded_service.service.federation_user)
        permissions_output.append(__format_permission(binded_service.service.federation_user, binded_service.service))
        service_users.append(binded_service.service.shovel_user)
        permissions_output.append(__format_permission(binded_service.service.shovel_user, binded_service.service))


    all_users_model_list = aditional_users + service_users

    users_output = []

    for user in all_users_model_list:
        user_dict = {
            "name": user.username,
            "password_hash": __get_base64_hash(user.password)
        }
        if user.admin:
            user_dict["tags"] = ["administrator"]
        else:
            user_dict["tags"] = []


        users_output.append(user_dict)


    for aditional_user in aditional_users:
        permission_dict = {
            "user": aditional_user.username,
            "vhost": "MQTT_IO",
            "configure": ".*",
            "read": ".*",
            "write": ".*",
        }
        permissions_output.append(permission_dict)

    
    return users_output, permissions_output


def get_vhosts(schema: Schema):
    binded_services: list[BindedService] = list(schema.binded_services.all())
    
    vhosts_list = []
    
    for binded_service in binded_services:
        vhosts_list.append({ "name": binded_service.service.name })

    return vhosts_list


def get_global_parameters(schema: Schema):
    global_parameters = [
        {
            "name": "cluster_name",
            "value": schema.name
        }
    ]
    
    return global_parameters


def get_queues(schema: Schema):
    bind_services: list[BindedService] = schema.binded_services.all()

    queues_list = []
    

    for bind_service in bind_services:
        service: Service = bind_service.service

        queues_list.append(__format_queue("BUSINESS_Q", service.name))
        queues_list.append(__format_queue("ERROR_Q", service.name))
        queues_list.append(__format_queue("SEND2DB_Q", service.name))

        if bind_service.mqtt_output_enabled:
            queues_list.append(__format_queue("SEND2MQTTIO_Q", service.name))
        
        if Federation.objects.filter(service=service).count() > 0:
            queues_list.append(__format_queue("FROMBROKER_Q", service.name))

        #TODO Chequear si falta alguno

    queues_list.append(__format_queue("SEND2JRU_Q", "DB_SERVICE"))
    queues_list.append(__format_queue("ERROR_Q", "DB_SERVICE"))

    return queues_list



def get_exchanges(schema: Schema):
    bind_services: list[BindedService] = schema.binded_services.all()

    exchange_list = []

    for bind_service in bind_services:
        service: Service = bind_service.service

        exchange_list.append(__format_exchange("SEND2DB_E", service.name))
        exchange_list.append(__format_exchange("ERROR_E", service.name))

        if bind_service.mqtt_output_enabled:
            exchange_list.append(__format_exchange("MQTT_E", service.name))
        
        if bind_service.mqtt_input_enabled:
            exchange_list.append(__format_exchange("SEND2MQTTIO_E", service.name))

        exchange_list.append(__format_exchange("SEND2JRU_E ", "DB_SERVICE"))
        exchange_list.append(__format_exchange("FROMVHOSTS_E ", "DB_SERVICE"))
        exchange_list.append(__format_exchange("ERROR_E ", "DB_SERVICE"))

        federations = Federation.objects.filter(service=service)

        if len(federations) > 0:
            exchange_list.append(__format_exchange("FROMLOWER_E ", "DB_SERVICE"))
            exchange_list.append(__format_exchange("FROMUPPER_E ", "DB_SERVICE"))
            exchange_list.append(__format_exchange("FROMCMW_E ", "DB_SERVICE")) #TODO Chequear esto
            
        for federation in federations:
            exchange_list.append(__format_exchange(f"FROM{federation.destination_level}_E", service.name))
            exchange_list.append(__format_exchange(f"SEND{schema.level}_E", service.name))

        #TODO Chequear si falta alguno

    return exchange_list


def get_bindings(schema: Schema):
    bind_services: list[BindedService] = schema.binded_services.all()

    bindings_list = []

    for bind_service in bind_services:
        service: Service = bind_service.service
        bindings_list.append(__format_binding("ERROR_E", "ERROR_Q", service.name, "#"))
        bindings_list.append(__format_binding("SEND2DB_E", "SEND2DB_Q", service.name, "*.*.*.*.*.*.*.*.*"))

        for mqtt_routing_key in bind_service.mqtt_binding_routing_keys.split(','):
            if bind_service.mqtt_output_enabled:
                bindings_list.append(__format_binding("MQTT_E", "BUSINESS_Q", service.name, mqtt_routing_key))

        if bind_service.mqtt_input_enabled:
            bindings_list.append(__format_binding("SEND2MQTTIO_E", "SEND2MQTTIO_Q", service.name,  "*.*.*.*.*.*.101.*.*"))
        
        federations = Federation.objects.filter(service=service)

        for federation in federations:
            for fed_routing_key in federation.federations_binding_routing_keys.split(','):
                bindings_list.append(__format_binding(f"FROM{federation.destination_level}", "BUSINESS_Q", service.name,  fed_routing_key)) #BUSINESS_Q o FROMBROKER_Q ¿?¿? 

    return bindings_list



def get_full_schema_definitions(schema: Schema):
    global_paramterers = get_global_parameters(schema)
    users, permissions = get_users_and_permissions(schema)
    vhosts = get_vhosts(schema)
    queues = get_queues(schema)
    exchanges = get_exchanges(schema)
    bindings = get_bindings(schema)
    
    full_schema_definitions_dict = {
        "global_parameters": global_paramterers,
        "vhosts": vhosts,
        "users": users,
        "permissions": permissions,
        "queues": queues,
        "exchanges": exchanges,
        "bindings": bindings
    }
    return full_schema_definitions_dict


def get_full_federations(schema: Schema):
    definitions = {}

    schema_federations: list[Federation] = list(schema.federations.all())
    
    for federation in schema_federations:
        definitions[federation.name] = __format_federation(federation)

    full_federations_dict = {
        "path_prefix": "/api/parameters",
        "component": "federation-upstream",
        "ack-mode": "on-confirm",
        "uri_prefix": "amqps",
        "trust-user-id": False,
        "headers":{
            "content-type": "application/json"
        },
        "definitions": definitions
    }
    
    return full_federations_dict


def get_full_policies(schema: Schema):
    definitions = {}

    schema_federations: list[Federation] = list(schema.federations.all())
    binded_services: list[BindedService] = list(schema.binded_services.all())
    
    for binded_service in binded_services:
        policy_key = f"{binded_service.service.name}_QUEUESIZE_P"
        definitions[policy_key] = __format_queuesize_policy(binded_service.service.name)
    
    for federation in schema_federations:
        policy_key = federation.name[:-1] + "P"
        definitions[policy_key] = __format_federation_policy(federation)

    full_policies_dict = {
        "path_prefix": "/api/policies",
        "ack-mode": "on-confirm",
        "uri_prefix": "amqp",
        "header":{
            "content-type": "application/json"
        },
        "definitions": definitions
    }

    return full_policies_dict


def get_full_shovels(schema: Schema):
    definitions = {}

    binded_services: list[BindedService] = list(schema.binded_services.all())

    for binded_service in binded_services:
        if binded_service.mqtt_input_enabled:
            mqtt_to_service_shovel_name = f"mqttio_to_{binded_service.service.name.lower()}_S"
            definitions[mqtt_to_service_shovel_name] = __format_mqtt_to_service_shovel(schema.mqttioshoveluser, binded_service.service)

        if binded_service.mqtt_output_enabled:
            service_to_mqtt_shovel_name = f"{binded_service.service.name.lower()}_to_mqttio_S"
            definitions[service_to_mqtt_shovel_name] = __format_service_to_mqtt_shovel(schema.mqttioshoveluser, binded_service.service)

        service_to_db_shovel_name = f"{binded_service.service.name.lower()}_to_dbservice_S"
        definitions[service_to_db_shovel_name] = __format_service_to_db_shovel(schema.dbshoveluser, binded_service.service)

    full_shovels_dict = {
        "path": "/api/shovels",
        "path_prefix": "/api/parameters/shovel/",
        "src-protocol": "amqp091",
        "dest-protocol": "amqp091",
        "src-delete-after": "never",
        "dest-add-forward-headers": False,
        "ack-mode": "on-confirm",
        "src-prefetch-count": 10,
        "reconnect-delay": 5,
        "uri_prefix": "amqp",
        "header":{
            "content-type": "application/json"
        },
        "definitions": definitions
    }
    
    return full_shovels_dict