#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""This module contains a Secret Manager hook."""

from __future__ import annotations

from collections.abc import Sequence
from functools import cached_property
from typing import TYPE_CHECKING

from google.api_core.gapic_v1.method import DEFAULT, _MethodDefault
from google.cloud.secretmanager_v1 import (
    AccessSecretVersionResponse,
    Secret,
    SecretManagerServiceClient,
    SecretPayload,
    SecretVersion,
)

from airflow.providers.google.common.consts import CLIENT_INFO
from airflow.providers.google.common.hooks.base_google import GoogleBaseHook

if TYPE_CHECKING:
    from google.api_core.retry import Retry
    from google.cloud.secretmanager_v1.services.secret_manager_service.pagers import ListSecretsPager


class GoogleCloudSecretManagerHook(GoogleBaseHook):
    """
    Hook for the Google Cloud Secret Manager API.

    See https://cloud.google.com/secret-manager
    """

    @cached_property
    def client(self):
        """
        Create a Secret Manager Client.

        :return: Secret Manager client.
        """
        return SecretManagerServiceClient(credentials=self.get_credentials(), client_info=CLIENT_INFO)

    def get_conn(self) -> SecretManagerServiceClient:
        """
        Retrieve the connection to Secret Manager.

        :return: Secret Manager client.
        """
        return self.client

    @GoogleBaseHook.fallback_to_default_project_id
    def create_secret(
        self,
        project_id: str,
        secret_id: str,
        secret: dict | Secret | None = None,
        retry: Retry | _MethodDefault = DEFAULT,
        timeout: float | None = None,
        metadata: Sequence[tuple[str, str]] = (),
    ) -> Secret:
        """
        Create a secret.

        .. seealso::
            For more details see API documentation:
            https://cloud.google.com/python/docs/reference/secretmanager/latest/google.cloud.secretmanager_v1.services.secret_manager_service.SecretManagerServiceClient#google_cloud_secretmanager_v1_services_secret_manager_service_SecretManagerServiceClient_create_secret

        :param project_id: Required. ID of the GCP project that owns the job.
            If set to ``None`` or missing, the default project_id from the GCP connection is used.
        :param secret_id: Required. ID of the secret to create.
        :param secret: Optional. Secret to create.
        :param retry: Optional. Designation of what errors, if any, should be retried.
        :param timeout: Optional. The timeout for this request.
        :param metadata: Optional. Strings which should be sent along with the request as metadata.
        :return: Secret object.
        """
        _secret = secret or {"replication": {"automatic": {}}}
        response = self.client.create_secret(
            request={
                "parent": f"projects/{project_id}",
                "secret_id": secret_id,
                "secret": _secret,
            },
            retry=retry,
            timeout=timeout,
            metadata=metadata,
        )
        self.log.info("Secret Created: %s", response.name)
        return response

    @GoogleBaseHook.fallback_to_default_project_id
    def add_secret_version(
        self,
        project_id: str,
        secret_id: str,
        secret_payload: dict | SecretPayload | None = None,
        retry: Retry | _MethodDefault = DEFAULT,
        timeout: float | None = None,
        metadata: Sequence[tuple[str, str]] = (),
    ) -> SecretVersion:
        """
        Add a version to the secret.

        .. seealso::
            For more details see API documentation:
            https://cloud.google.com/python/docs/reference/secretmanager/latest/google.cloud.secretmanager_v1.services.secret_manager_service.SecretManagerServiceClient#google_cloud_secretmanager_v1_services_secret_manager_service_SecretManagerServiceClient_add_secret_version

        :param project_id: Required. ID of the GCP project that owns the job.
            If set to ``None`` or missing, the default project_id from the GCP connection is used.
        :param secret_id: Required. ID of the secret to create.
        :param secret_payload: Optional. A secret payload.
        :param retry: Optional. Designation of what errors, if any, should be retried.
        :param timeout: Optional. The timeout for this request.
        :param metadata: Optional. Strings which should be sent along with the request as metadata.
        :return: Secret version object.
        """
        response = self.client.add_secret_version(
            request={
                "parent": f"projects/{project_id}/secrets/{secret_id}",
                "payload": secret_payload,
            },
            retry=retry,
            timeout=timeout,
            metadata=metadata,
        )
        self.log.info("Secret version added: %s", response.name)
        return response

    @GoogleBaseHook.fallback_to_default_project_id
    def list_secrets(
        self,
        project_id: str,
        page_size: int = 0,
        page_token: str | None = None,
        secret_filter: str | None = None,
        retry: Retry | _MethodDefault = DEFAULT,
        timeout: float | None = None,
        metadata: Sequence[tuple[str, str]] = (),
    ) -> ListSecretsPager:
        """
        List secrets.

        .. seealso::
            For more details see API documentation:
            https://cloud.google.com/python/docs/reference/secretmanager/latest/google.cloud.secretmanager_v1.services.secret_manager_service.SecretManagerServiceClient#google_cloud_secretmanager_v1_services_secret_manager_service_SecretManagerServiceClient_list_secrets

        :param project_id: Required. ID of the GCP project that owns the job.
            If set to ``None`` or missing, the default project_id from the GCP connection is used.
        :param page_size: Optional, number of results to return in the list.
        :param page_token: Optional, token to provide to skip to a particular spot in the list.
        :param secret_filter: Optional. Filter string.
        :param retry: Optional. Designation of what errors, if any, should be retried.
        :param timeout: Optional. The timeout for this request.
        :param metadata: Optional. Strings which should be sent along with the request as metadata.
        :return: Secret List object.
        """
        response = self.client.list_secrets(
            request={
                "parent": f"projects/{project_id}",
                "page_size": page_size,
                "page_token": page_token,
                "filter": secret_filter,
            },
            retry=retry,
            timeout=timeout,
            metadata=metadata,
        )
        self.log.info("Secrets list obtained")
        return response

    @GoogleBaseHook.fallback_to_default_project_id
    def secret_exists(self, project_id: str, secret_id: str) -> bool:
        """
        Check whether secret exists.

        :param project_id: Required. ID of the GCP project that owns the job.
            If set to ``None`` or missing, the default project_id from the GCP connection is used.
        :param secret_id: Required. ID of the secret to find.
        :return: True if the secret exists, False otherwise.
        """
        secret_filter = f"name:{secret_id}"
        secret_name = self.client.secret_path(project_id, secret_id)
        for secret in self.list_secrets(project_id=project_id, page_size=100, secret_filter=secret_filter):
            if secret.name.split("/")[-1] == secret_id:
                self.log.info("Secret %s exists.", secret_name)
                return True
        self.log.info("Secret %s doesn't exists.", secret_name)
        return False

    @GoogleBaseHook.fallback_to_default_project_id
    def access_secret(
        self,
        project_id: str,
        secret_id: str,
        secret_version: str = "latest",
        retry: Retry | _MethodDefault = DEFAULT,
        timeout: float | None = None,
        metadata: Sequence[tuple[str, str]] = (),
    ) -> AccessSecretVersionResponse:
        """
        Access a secret version.

        .. seealso::
            For more details see API documentation:
            https://cloud.google.com/python/docs/reference/secretmanager/latest/google.cloud.secretmanager_v1.services.secret_manager_service.SecretManagerServiceClient#google_cloud_secretmanager_v1_services_secret_manager_service_SecretManagerServiceClient_access_secret_version

        :param project_id: Required. ID of the GCP project that owns the job.
            If set to ``None`` or missing, the default project_id from the GCP connection is used.
        :param secret_id: Required. ID of the secret to access.
        :param secret_version: Optional. Version of the secret to access. Default: latest.
        :param retry: Optional. Designation of what errors, if any, should be retried.
        :param timeout: Optional. The timeout for this request.
        :param metadata: Optional. Strings which should be sent along with the request as metadata.
        :return: Access secret version response object.
        """
        response = self.client.access_secret_version(
            request={
                "name": self.client.secret_version_path(project_id, secret_id, secret_version),
            },
            retry=retry,
            timeout=timeout,
            metadata=metadata,
        )
        self.log.info("Secret version accessed: %s", response.name)
        return response

    @GoogleBaseHook.fallback_to_default_project_id
    def delete_secret(
        self,
        project_id: str,
        secret_id: str,
        retry: Retry | _MethodDefault = DEFAULT,
        timeout: float | None = None,
        metadata: Sequence[tuple[str, str]] = (),
    ) -> None:
        """
        Delete a secret.

        .. seealso::
            For more details see API documentation:
            https://cloud.google.com/python/docs/reference/secretmanager/latest/google.cloud.secretmanager_v1.services.secret_manager_service.SecretManagerServiceClient#google_cloud_secretmanager_v1_services_secret_manager_service_SecretManagerServiceClient_delete_secret

        :param project_id: Required. ID of the GCP project that owns the job.
            If set to ``None`` or missing, the default project_id from the GCP connection is used.
        :param secret_id: Required. ID of the secret to delete.
        :param retry: Optional. Designation of what errors, if any, should be retried.
        :param timeout: Optional. The timeout for this request.
        :param metadata: Optional. Strings which should be sent along with the request as metadata.
        :return: Access secret version response object.
        """
        name = self.client.secret_path(project_id, secret_id)
        self.client.delete_secret(
            request={"name": name},
            retry=retry,
            timeout=timeout,
            metadata=metadata,
        )
        self.log.info("Secret deleted: %s", name)
        return None
