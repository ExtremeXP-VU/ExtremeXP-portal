from flask import Flask, request, g, send_file, jsonify, make_response
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
from userAuthHandler import userAuthHandler
from projectHandler import projectHandler
from experimentHandler import experimentHandler
from categoryHandler import categoryHandler
from taskHandler import taskHandler
from datasetHandler import datasetHandler
from convertorHandler import convertorHandler
import logging
import json
import mimetypes
import requests
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
cors = CORS(app)  # cors is added in advance to allow cors requests
app.config["CORS_HEADERS"] = "Content-Type"

ERROR_FORBIDDEN = "Error: Forbidden"
ERROR_DUPLICATE = "Error: Duplicate name"
ERROR_NOT_FOUND = "Error: Not found"

ENDPOINT_WITHOUT_AUTH = []


# there's a bug in flask_cors that headers is None when using before_request for OPTIONS request
@app.before_request
def verify_user():
    if request.endpoint in ENDPOINT_WITHOUT_AUTH:
        return None
    # get token from params {'token': 'token'}
    token = request.args.get("token")
    if token is None:
        return {"error": ERROR_FORBIDDEN, "message": "token is not provided"}, 403
    auth_res = userAuthHandler.verify_user(token)
    if not auth_res["valid"] or auth_res["username"] is None:
        return {"error": ERROR_FORBIDDEN, "message": auth_res["error_type"]}, 403
    g.username = auth_res["username"]


@app.after_request
def after_request(response):
    # to enable cors response
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    return response


@app.route("/exp/", methods=["GET"])
@cross_origin()
def index():
    return "experiment service connected"


# PROJECTS
@app.route("/exp/projects", methods=["GET"])
@cross_origin()
def get_projects():
    projects = projectHandler.get_projects(g.username)
    return {
        "message": "projects retrieved",
        "data": {"projects": projects},
    }, 200


@app.route("/exp/projects/create", methods=["OPTIONS", "POST"])
@cross_origin()
def create_project():
    proj_name = request.json["name"]
    if projectHandler.detect_duplicate(g.username, proj_name):
        return {
            "error": ERROR_DUPLICATE,
            "message": "Project name already exists",
        }, 409

    res = projectHandler.create_project(g.username, proj_name)
    return {"message": "Project created.", "data": {"id_project": res}}, 201


@app.route("/exp/projects/<proj_id>/update", methods=["OPTIONS", "PUT"])
@cross_origin()
def update_project_info(proj_id):
    proj_name = request.json["name"]
    get_proj = projectHandler.get_project(proj_id)
    if get_proj["name"] != proj_name:
        if projectHandler.detect_duplicate(g.username, proj_name):
            return {
                "error": ERROR_DUPLICATE,
                "message": "Project name already exists",
            }, 409
    description = request.json["description"]  # can be empty
    projectHandler.update_project_info(proj_id, proj_name, description)
    return {"message": "project info updated"}, 200


@app.route("/exp/projects/<proj_id>/delete", methods=["OPTIONS", "DELETE"])
@cross_origin()
def delete_project(proj_id):
    if not projectHandler.project_exists(proj_id):
        return {"message": "project does not exist"}, 404
    projectHandler.delete_project(proj_id)
    experimentHandler.delete_experiments(proj_id)
    datasetHandler.delete_datasets(proj_id)
    return {"message": "project deleted"}, 204


# EXPERIMENTS
@app.route("/exp/projects/<proj_id>/experiments", methods=["GET"])
@cross_origin()
def get_experiments(proj_id):
    experiments = experimentHandler.get_experiments(proj_id)
    return {
        "message": "experiments retrieved",
        "data": {"experiments": experiments},
    }, 200


@app.route("/exp/projects/experiments/<exp_id>", methods=["GET"])
@cross_origin()
def get_experiment(exp_id):
    experiment = experimentHandler.get_experiment(exp_id)
    return {
        "message": "experiment retrieved",
        "data": {"experiment": experiment},
    }, 200


@app.route("/exp/projects/<proj_id>/experiments/create", methods=["OPTIONS", "POST"])
@cross_origin()
def create_experiment(proj_id):
    exp_name = request.json["exp_name"]
    graphical_model = request.json["graphical_model"]
    if experimentHandler.detect_duplicate(proj_id, exp_name):
        return {
            "error": ERROR_DUPLICATE,
            "message": "Experiment name already exists",
        }, 409
    res = experimentHandler.create_experiment(
        g.username, proj_id, exp_name, graphical_model
    )
    return {"message": "Experiment created", "data": {"id_experiment": res}}, 201


@app.route(
    "/exp/projects/<proj_id>/experiments/<exp_id>/delete",
    methods=["OPTIONS", "DELETE"],
)
@cross_origin()
def delete_experiment(proj_id, exp_id):
    if not experimentHandler.experiment_exists(exp_id):
        return {"message": "this experiment does not exist"}, 404
    experimentHandler.delete_experiment(exp_id, proj_id)
    return {"message": "experiment deleted"}, 204


@app.route(
    "/exp/projects/<proj_id>/experiments/<exp_id>/update/name",
    methods=["OPTIONS", "PUT"],
)
@cross_origin()
def update_experiment_name(proj_id, exp_id):
    exp_name = request.json["exp_name"]
    if experimentHandler.detect_duplicate(proj_id, exp_name):
        return {
            "error": ERROR_DUPLICATE,
            "message": "Experiment name already exists",
        }, 409
    experimentHandler.update_experiment_name(exp_id, proj_id, exp_name)
    return {"message": "experiment name updated"}, 200


@app.route(
    "/exp/projects/<proj_id>/experiments/<exp_id>/update/graphical_model",
    methods=["OPTIONS", "PUT"],
)
@cross_origin()
def update_experiment_graphical_model(proj_id, exp_id):
    graphical_model = request.json["graphical_model"]
    experimentHandler.update_experiment_graphical_model(
        exp_id, proj_id, graphical_model
    )
    return {"message": "experiment graphical model updated"}, 200


# CATEGORIES
@app.route("/task/categories", methods=["GET"])
@cross_origin()
def get_categories():
    categories = categoryHandler.get_categories(g.username)
    return {
        "message": "categories retrieved",
        "data": {"categories": categories},
    }, 200


@app.route("/task/categories/create", methods=["OPTIONS", "POST"])
@cross_origin()
def create_category():
    category_name = request.json["name"]
    if categoryHandler.detect_duplicate(g.username, category_name):
        return {
            "error": ERROR_DUPLICATE,
            "message": "Category name already exists",
        }, 409

    res = categoryHandler.create_category(g.username, category_name)
    return {"message": "Category created.", "data": {"id_category": res}}, 201


@app.route("/task/categories/<category_id>/update", methods=["OPTIONS", "PUT"])
@cross_origin()
def update_category_name(category_id):
    category_name = request.json["name"]
    get_category = categoryHandler.get_category(category_id)
    if get_category["name"] != category_name:
        if categoryHandler.detect_duplicate(g.username, category_name):
            return {
                "error": ERROR_DUPLICATE,
                "message": "Category name already exists",
            }, 409
    categoryHandler.update_category_name(category_id, category_name)
    return {"message": "category name updated"}, 200


@app.route("/task/categories/<category_id>/delete", methods=["OPTIONS", "DELETE"])
@cross_origin()
# FIXME: delete official category should not be allowed
def delete_category(category_id):
    if not categoryHandler.category_exists(category_id):
        return {"error": ERROR_NOT_FOUND, "message": "category does not exist"}, 404
    categoryHandler.delete_category(category_id)
    taskHandler.delete_tasks(category_id)
    return {"message": "category deleted"}, 204


# TASKS
@app.route("/task/categories/<category_id>/tasks", methods=["GET"])
@cross_origin()
def get_tasks(category_id):
    tasks = taskHandler.get_tasks(category_id, g.username)
    return {
        "message": "tasks retrieved",
        "data": {"tasks": tasks},
    }, 200


@app.route("/task/categories/tasks/<task_id>", methods=["GET"])
@cross_origin()
def get_task(task_id):
    task = taskHandler.get_task(task_id)
    return {
        "message": "task retrieved",
        "data": {"task": task},
    }, 200


@app.route("/task/categories/<category_id>/tasks/create", methods=["OPTIONS", "POST"])
@cross_origin()
def create_task(category_id):
    task_name = request.json["name"]
    task_provider = request.json["provider"]
    graphical_model = request.json["graphical_model"]
    if taskHandler.detect_duplicate(category_id, task_name):
        return {
            "error": ERROR_DUPLICATE,
            "message": "Task name already exists",
        }, 409
    res = taskHandler.create_task(
        g.username, category_id, task_name, task_provider, graphical_model
    )
    return {"message": "Task created", "data": {"id_task": res}}, 201


@app.route(
    "/task/categories/tasks/<task_id>/delete",
    methods=["OPTIONS", "DELETE"],
)
@cross_origin()
def delete_task(task_id):
    if not taskHandler.task_exists(task_id):
        return {"error": ERROR_NOT_FOUND, "message": "this task does not exist"}, 404
    taskHandler.delete_task(task_id)
    return {"message": "task deleted"}, 204


@app.route(
    "/task/categories/<category_id>/tasks/<task_id>/update/info",
    methods=["OPTIONS", "PUT"],
)
@cross_origin()
def update_task_info(category_id, task_id):
    task_name = request.json["name"]
    task_description = request.json["description"]
    if taskHandler.detect_duplicate(category_id, task_name):
        return {
            "error": ERROR_DUPLICATE,
            "message": "Task name already exists",
        }, 409
    taskHandler.update_task_info(task_id, task_name, task_description)
    return {"message": "task information updated"}, 200


@app.route(
    "/task/categories/tasks/<task_id>/update/graphical_model",
    methods=["OPTIONS", "PUT"],
)
@cross_origin()
def update_task_graphical_model(task_id):
    graphical_model = request.json["graphical_model"]
    taskHandler.update_task_graphical_model(task_id, graphical_model)
    return {"message": "task graphical model updated"}, 200


# DATASETS
@app.route("/exp/projects/<proj_id>/datasets", methods=["GET"])
@cross_origin()
def get_datasets(proj_id):
    datasets = datasetHandler.get_datasets(proj_id)
    return {
               "message": "datasets retrieved",
               "data": {"datasets": datasets},
           }, 200


@app.route("/exp/projects/<proj_id>/datasets/create", methods=["OPTIONS", "POST"])
@cross_origin()
def create_dataset(proj_id):
    # Ensure the dataset_name parameter is present
    if "dataset_name" not in request.form:
        return jsonify({"error": "Missing dataset_name parameter"}), 400
    if "description" not in request.form:
        return jsonify({"error": "Missing dataset_name parameter"}), 400
    description=request.form.get('description')
    dataset_name = request.form["dataset_name"]
    # Ensure the file is part of the request
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    file = request.files["file"]
    filename = secure_filename(file.filename)
    dataset_content = file.read()
    # Handle metadata if it is provided
    metadata = request.form.get('metadata')
    if metadata:
        try:
            metadata = json.loads(metadata)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON format for metadata"}), 400
    else:
        metadata = []

    # Call the datasetHandler method
    dataset_id = datasetHandler.create_dataset(
        g.username, proj_id, dataset_name, dataset_content,description, metadata
    )

    if dataset_id:
        return jsonify({"message": "Dataset created", "data": {"id_dataset": dataset_id}}), 201
    else:
        return jsonify({"error": "Failed to create dataset"}), 500




@app.route(
    "/exp/projects/<proj_id>/datasets/<dataset_id>/update/name",
    methods=["OPTIONS", "PUT"],
)
@cross_origin()
def update_dataset_name(proj_id, dataset_id):
    dataset_name = request.json["dataset_name"]
    if datasetHandler.detect_duplicate(proj_id, dataset_name):
        return {
                   "error": ERROR_DUPLICATE,
                   "message": "Dataset name already exists",
               }, 409
    datasetHandler.update_dataset_name(dataset_id, proj_id, dataset_name)
    return {"message": "dataset name updated"}, 200

@app.route(
    "/exp/projects/<proj_id>/datasets/<dataset_id>/update/description",
    methods=["OPTIONS", "PUT"],
)
@cross_origin()
def update_dataset_description(proj_id, dataset_id):
    dataset_description = request.json["description"]
    datasetHandler.update_dataset_description(dataset_id, proj_id, dataset_description)
    return {"message": "dataset description updated"}, 200

@app.route(
    "/exp/projects/<proj_id>/datasets/<dataset_id>/delete",
    methods=["OPTIONS", "DELETE"],
)
@cross_origin()
def delete_dataset(proj_id, dataset_id):
    if not datasetHandler.dataset_exists(dataset_id):
        return {"message": "this dataset does not exist"}, 404
    datasetHandler.delete_dataset(dataset_id, proj_id)
    return {"message": "dataset deleted"}, 204


@app.route("/exp/projects/<proj_id>/datasets/<dataset_id>/download", methods=["GET"])
def download_dataset(proj_id, dataset_id):
    try:
        # Retrieve the dataset from the handler
        result = datasetHandler.download_dataset(proj_id, dataset_id)
        
        # Check if the result is valid
        if result:
            file_content = result.get('content')
            mime_type = result.get('mime_type', 'application/octet-stream')
            
            # Determine the file extension based on MIME type
            extension = mimetypes.guess_extension(mime_type) or ''
            filename = f"{dataset_id}{extension}"
            
            # Create and return the response with the file
            response = make_response(send_file(
                file_content,
                as_attachment=True,
                download_name=filename,
                mimetype=mime_type
            ))
            
            # Set appropriate headers for file download
            response.headers["Content-Disposition"] = f"attachment; filename={filename}"
            response.headers["Content-Type"] = mime_type
            return response
        
        # If the result is not valid, return an error message
        else:
            return jsonify({"message": "Failed to download dataset"}), 500
    
    # Catch and handle any exceptions
    except Exception as e:
        return jsonify({"message": str(e)}), 500



@app.route("/exp/projects/<proj_id>/datasets/download", methods=["GET"])
@cross_origin()
def download_datasets(proj_id):
    result = datasetHandler.download_datasets(proj_id)
    if result:
        zip_file = result["zip_file"]
        zip_name = result["zip_name"]
        return send_file(zip_file, as_attachment=True, download_name=zip_name)
    else:
        return jsonify({"error": "Failed to download datasets"}), 500

# EXECUTION
@app.route("/exp/execute/convert/<exp_id>", methods=["OPTIONS", "POST"])
@cross_origin()
def convert_to_source_model(exp_id):
    if not experimentHandler.experiment_exists(exp_id):
        return {"error": ERROR_NOT_FOUND, "message": "experiment not found"}, 404
    exp = experimentHandler.get_experiment(exp_id)
    convert_res = convertorHandler.convert(exp)

    app.logger.info('Executing experiment...')
    url = 'http://exp-eng-service:5556/exp/run'
    response = requests.post(url, json=exp)
    app.logger.info(response.text)

    if not convert_res["success"]:
        return {"error": "Error converting model", "message": convert_res["error"]}, 500
    return {"message": "source model converted", "data": convert_res["data"]}, 200


# 406: Not Acceptable
