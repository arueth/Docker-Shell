from cloudshell.core.context.error_handling_context import ErrorHandlingContext
from cloudshell.cp.docker.domain.context.docker_api_session_context import DockerApiSessionContext
from cloudshell.cp.docker.domain.context.docker_resource_model_context import DockerResourceModelContext
from cloudshell.cp.docker.domain.services.parsers.docker_models_parser import DockerModelsParser
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from cloudshell.shell.core.session.logging_session import LoggingSessionContext


class DockerShellContext(object):
    def __init__(self, context, docker_session_manager):
        """
        Initializes an instance of DockerShellContext
        :param ResourceCommandContext context: Command context
        """
        self.context = context
        self.docker_session_manager = docker_session_manager
        self.model_parser = DockerModelsParser()

    def __enter__(self):
        """
        Initializes all docker shell context dependencies
        :rtype DockerShellContextModel:
        """
        with LoggingSessionContext(self.context) as logger:
            with ErrorHandlingContext(logger):
                with CloudShellSessionContext(self.context) as cloudshell_session:
                    with DockerResourceModelContext(self.context, self.model_parser) as docker_resource_model:
                        with DockerApiSessionContext(docker_session_manager=self.docker_session_manager,
                                                     cloudshell_session=cloudshell_session,
                                                     docker_resource_model=docker_resource_model) as docker_api:
                            return DockerShellContextModel(logger=logger,
                                                           cloudshell_session=cloudshell_session,
                                                           docker_resource_model=docker_resource_model,
                                                           docker_api=docker_api)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Called upon end of the context. Does nothing
        :param exc_type: Exception type
        :param exc_val: Exception value
        :param exc_tb: Exception traceback
        :return:
        """
        return


class DockerShellContextModel(object):
    def __init__(self, logger, cloudshell_session, docker_resource_model, docker_api):
        """
        :param logging.Logger logger:
        :param cloudshell.api.cloudshell_api.CloudShellAPISession cloudshell_session:
        :param docker_resource_model:
        :param docker_api:
        :return:
        """
        self.logger = logger
        self.cloudshell_session = cloudshell_session
        self.docker_resource_model = docker_resource_model
        self.docker_api = docker_api
