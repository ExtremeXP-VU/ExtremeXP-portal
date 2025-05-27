from flask import Flask, request, g
from flask_cors import CORS, cross_origin
from userAuthHandler import userAuthHandler
from projectHandler import projectHandler
from workflowHandler import workflowHandler
from categoryHandler import categoryHandler
from taskHandler import taskHandler
from convertorHandler import convertorHandler

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
    token = request.headers.get("Authorization")
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


@app.route("/work/", methods=["GET"])
@cross_origin()
def index():
    return "workflow service connected"


# PROJECTS
@app.route("/work/projects", methods=["GET"])
@cross_origin()
def get_projects():
    projects = projectHandler.get_projects(g.username)
    return {
        "message": "projects retrieved",
        "data": {"projects": projects},
    }, 200


@app.route("/work/projects/create", methods=["OPTIONS", "POST"])
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


@app.route("/work/projects/<proj_id>/update", methods=["OPTIONS", "PUT"])
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


@app.route("/work/projects/<proj_id>/delete", methods=["OPTIONS", "DELETE"])
@cross_origin()
def delete_project(proj_id):
    if not projectHandler.project_exists(proj_id):
        return {"message": "project does not exist"}, 404
    projectHandler.delete_project(proj_id)
    workflowHandler.delete_workflows(proj_id)
    return {"message": "project deleted"}, 204


# WORKFLOWS
@app.route("/work/projects/<proj_id>/workflows", methods=["GET"])
@cross_origin()
def get_workflows(proj_id):
    workflows = workflowHandler.get_workflows(proj_id)
    return {
        "message": "workflows retrieved",
        "data": {"workflows": workflows},
    }, 200


@app.route("/work/projects/workflows/<work_id>", methods=["GET"])
@cross_origin()
def get_workflow(work_id):
    workflow = workflowHandler.get_workflow(work_id)
    return {
        "message": "workflow retrieved",
        "data": {"workflow": workflow},
    }, 200


@app.route("/work/projects/<proj_id>/workflows/create", methods=["OPTIONS", "POST"])
@cross_origin()
def create_workflow(proj_id):
    work_name = request.json["work_name"]
    graphical_model = request.json["graphical_model"]
    if workflowHandler.detect_duplicate(proj_id, work_name):
        return {
            "error": ERROR_DUPLICATE,
            "message": "Workflow name already exists",
        }, 409
    res = workflowHandler.create_workflow(
        g.username, proj_id, work_name, graphical_model
    )
    return {"message": "Workflow created", "data": {"id_workflow": res}}, 201


@app.route(
    "/work/projects/<proj_id>/workflows/<work_id>/delete",
    methods=["OPTIONS", "DELETE"],
)
@cross_origin()
def delete_workflow(proj_id, work_id):
    if not workflowHandler.workflow_exists(work_id):
        return {"message": "this workflow does not exist"}, 404
    workflowHandler.delete_workflow(work_id, proj_id)
    return {"message": "workflow deleted"}, 204


@app.route(
    "/work/projects/<proj_id>/workflows/<work_id>/update/name",
    methods=["OPTIONS", "PUT"],
)
@cross_origin()
def update_workflow_name(proj_id, work_id):
    work_name = request.json["work_name"]
    if workflowHandler.detect_duplicate(proj_id, work_name):
        return {
            "error": ERROR_DUPLICATE,
            "message": "Workflow name already exists",
        }, 409
    workflowHandler.update_workflow_name(work_id, proj_id, work_name)
    return {"message": "workflow name updated"}, 200


@app.route(
    "/work/projects/<proj_id>/workflows/<work_id>/update/graphical_model",
    methods=["OPTIONS", "PUT"],
)
@cross_origin()
def update_experiment_graphical_model(proj_id, work_id):
    graphical_model = request.json["graphical_model"]
    workflowHandler.update_workflow_graphical_model(
        work_id, proj_id, graphical_model
    )
    return {"message": "workflow graphical model updated"}, 200


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


# EXECUTION
@app.route("/work/execute/convert/<work_id>", methods=["OPTIONS", "POST"])
@cross_origin()
def convert_to_source_model(work_id):
    if not workflowHandler.workflow_exists(work_id):
        return {"error": ERROR_NOT_FOUND, "message": "experiment not found"}, 404
    work = workflowHandler.get_workflow(work_id)
    convert_res = convertorHandler.convert(work)

    if not convert_res["success"]:
        return {"error": "Error converting model", "message": convert_res["error"]}, 500
    return {"message": "source model converted", "data": convert_res["data"]}, 200


# 406: Not Acceptable
