from cloudshell.cp.docker.models.docker_clients import DockerClients
from docker import DockerClient


class DockerSessionProvider(object):
    def __init__(self):
        return

    def get_clients(self, cloudshell_session, docker_resource_model):
        """
        :param cloudshell.api.cloudshell_api.CloudShellAPISession cloudshell_session:
        :param docker_resource_model:
        :return:
        :rtype: DockerClients
        """
        dockerd_api_client = self._get_dockerd_api_client(cloudshell_session=cloudshell_session,
                                                          docker_resource_model=docker_resource_model)

        return DockerClients(dockerd_client=dockerd_api_client)

    def _get_dockerd_api_client(self, cloudshell_session, docker_resource_model):
        api_client = DockerClient(base_url='tcp://192.168.0.252:2375',
                                  timeout=60,
                                  tls=False,
                                  user_agent='Quali CloudShell',
                                  version='auto')

        api_client.ping()

        return api_client
