from flask import request
from flask_restx import Namespace, Resource, reqparse
from overseer.flask import cache
from overseer.observer import retrieve_suspicious_instances
from loguru import logger
from overseer.classes.instance import Instance
from overseer.database import functions as database

api = Namespace('v1', 'API Version 1' )

from overseer.apis.models.v1 import Models

models = Models(api)

# Used to for the flask limiter, to limit requests per url paths
def get_request_path():
    # logger.info(dir(request))
    return f"{request.remote_addr}@{request.method}@{request.path}"


class Suspicions(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument("Client-Agent", default="unknown:0:unknown", type=str, required=False, help="The client name and version.", location="headers")
    get_parser.add_argument("activity_suspicion", required=False, default=20, type=int, help="How many users per local post+comment to consider suspicious", location="args")
    get_parser.add_argument("csv", required=False, type=bool, help="Set to true to return just the domains as a csv. Mutually exclusive with domains", location="args")
    get_parser.add_argument("domains", required=False, type=bool, help="Set to true to return just the domains as a list. Mutually exclusive with csv", location="args")

    @api.expect(get_parser)
    @logger.catch(reraise=True)
    @cache.cached(timeout=10, query_string=True)
    @api.marshal_with(models.response_model_model_Suspicions_get, code=200, description='Suspicious Instances', skip_none=True)
    def get(self):
        '''A List with the details of all suspicious instances
        '''
        self.args = self.get_parser.parse_args()
        sus_instances = retrieve_suspicious_instances(self.args.activity_suspicion)
        if self.args.csv:
            return {"csv": ",".join([instance["domain"] for instance in sus_instances])},200
        if self.args.domains:
            return {"domains": [instance["domain"] for instance in sus_instances]},200
        return {"instances": sus_instances},200


class Whitelist(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument("Client-Agent", default="unknown:0:unknown", type=str, required=False, help="The client name and version.", location="headers")
    get_parser.add_argument("endorsements", required=False, default=1, type=int, help="Limit to this amount of endorsements of more", location="args")
    get_parser.add_argument("domain", required=False, type=str, help="Filter by instance domain", location="args")
    get_parser.add_argument("csv", required=False, type=bool, help="Set to true to return just the domains as a csv. Mutually exclusive with domains", location="args")
    get_parser.add_argument("domains", required=False, type=bool, help="Set to true to return just the domains as a list. Mutually exclusive with csv", location="args")

    @api.expect(get_parser)
    @logger.catch(reraise=True)
    @cache.cached(timeout=10, query_string=True)
    @api.marshal_with(models.response_model_model_Instances_get, code=200, description='Instances', skip_none=True)
    def get(self):
        '''A List with the details of all instances and their endorsements
        '''
        self.args = self.get_parser.parse_args()
        instance_details = []
        for instance in database.get_all_instances():
            logger.debug(instance)
            instance_details.append(instance.get_details())
        if self.args.csv:
            return {"csv": ",".join([instance["domain"] for instance in instance_details])},200
        if self.args.domains:
            return {"domains": [instance["domain"] for instance in instance_details]},200
        logger.debug(instance_details)
        return {"instances": instance_details},200

