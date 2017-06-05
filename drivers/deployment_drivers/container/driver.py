import jsonpickle
from cloudshell.api.cloudshell_api import InputNameValue
from cloudshell.cp.docker.common.deploy_data_holder import DeployDataHolder
from cloudshell.cp.docker.models.deploy_docker_container_resource_model import DeployDockerContainerResourceModel
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from cloudshell.shell.core.session.logging_session import LoggingSessionContext


class DockerContainer(ResourceDriverInterface):
    def __init__(self):
        return

    def initialize(self, context):
        return

    def cleanup(self):
        return

    def Deploy(self, context, Name=None):
        with LoggingSessionContext(context) as logger:
            with CloudShellSessionContext(context) as session:
                logger.info('Deploy started')

                app_request = jsonpickle.decode(context.resource.app_context.app_request_json)

                # Cloudshell >= v7.2 have no Cloud Provider attribute, fill it from the cloudProviderName context attr
                cloud_provider_name = app_request["deploymentService"].get("cloudProviderName")

                if cloud_provider_name:
                    context.resource.attributes['Cloud Provider'] = cloud_provider_name

                # create deployment resource model and serialize it to json
                docker_container_deployment_model = self._convert_context_to_deployment_resource_model(context.resource)

                container_resource_name = app_request['name']
                deployment_info = self._get_deployment_info(docker_container_deployment_model, container_resource_name)

                self.vaidate_deployment_container_model(docker_container_deployment_model)

                command_inputs = self._get_command_inputs_list(deployment_info)
                logger.info('Executing deploy_container on %s' % docker_container_deployment_model.cloud_provider)
                logger.info('Command Inputs: [%s: %s]' % (command_inputs[0].Name, command_inputs[0].Value))

                # Calls command on the Docker Host cloud provider
                result = session.ExecuteCommand(context.reservation.reservation_id,
                                                docker_container_deployment_model.cloud_provider,
                                                "Resource",
                                                "deploy_container",
                                                command_inputs,
                                                False)

                logger.info('Deploy completed')
                logger.info('Output: %s' % result.Output)

                return result.Output

    def vaidate_deployment_container_model(self, docker_container_deployment_model):
        if docker_container_deployment_model.cloud_provider == '':
            raise Exception("The name of the Cloud Provider is empty.")

        return

    # todo: remove this to a common place
    def _convert_context_to_deployment_resource_model(self, resource):
        deployed_resource = DeployDockerContainerResourceModel()

        deployed_resource.cloud_provider = resource.attributes['Cloud Provider']
        deployed_resource.docker_image = resource.attributes['Docker Image']
        deployed_resource.docker_image_command = resource.attributes['Docker Image Command']
        deployed_resource.docker_image_tag = resource.attributes['Docker Image Tag']

        return deployed_resource

    def _get_deployment_info(self, image_model, name):
        return DeployDataHolder({'app_name': name, 'docker_params': image_model})

    def _get_command_inputs_list(self, data_holder):
        return [InputNameValue('request', jsonpickle.encode(data_holder, unpicklable=False))]
