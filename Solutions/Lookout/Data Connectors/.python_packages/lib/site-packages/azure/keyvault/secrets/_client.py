# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from functools import partial
from azure.core.tracing.decorator import distributed_trace

from ._models import KeyVaultSecret, DeletedSecret, SecretProperties
from ._shared import KeyVaultClientBase
from ._shared.exceptions import error_map as _error_map
from ._shared._polling import DeleteRecoverPollingMethod, KeyVaultOperationPoller

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any, Dict, Optional
    from datetime import datetime
    from azure.core.paging import ItemPaged


class SecretClient(KeyVaultClientBase):
    """A high-level interface for managing a vault's secrets.

    :param str vault_url: URL of the vault the client will access. This is also called the vault's "DNS Name".
    :param credential: An object which can provide an access token for the vault, such as a credential from
        :mod:`azure.identity`
    :keyword api_version: version of the Key Vault API to use. Defaults to the most recent.
    :paramtype api_version: ~azure.keyvault.secrets.ApiVersion
    :keyword transport: transport to use. Defaults to :class:`~azure.core.pipeline.transport.RequestsTransport`.
    :paramtype transport: ~azure.core.pipeline.transport.HttpTransport

    Example:
        .. literalinclude:: ../tests/test_samples_secrets.py
            :start-after: [START create_secret_client]
            :end-before: [END create_secret_client]
            :language: python
            :caption: Create a new ``SecretClient``
            :dedent: 4
    """

    # pylint:disable=protected-access

    @distributed_trace
    def get_secret(self, name, version=None, **kwargs):
        # type: (str, str, **Any) -> KeyVaultSecret
        """Get a secret. Requires the secrets/get permission.

        :param str name: The name of the secret
        :param str version: (optional) Version of the secret to get. If unspecified, gets the latest version.
        :rtype: ~azure.keyvault.secrets.KeyVaultSecret
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the secret doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START get_secret]
                :end-before: [END get_secret]
                :language: python
                :caption: Get a secret
                :dedent: 8
        """
        bundle = self._client.get_secret(
            vault_base_url=self._vault_url,
            secret_name=name,
            secret_version=version or "",
            error_map=_error_map,
            **kwargs
        )
        return KeyVaultSecret._from_secret_bundle(bundle)

    @distributed_trace
    def set_secret(self, name, value, **kwargs):
        # type: (str, str, **Any) -> KeyVaultSecret
        """Set a secret value. If `name` is in use, create a new version of the secret. If not, create a new secret.

        Requires secrets/set permission.

        :param str name: The name of the secret
        :param str value: The value of the secret
        :keyword bool enabled: Whether the secret is enabled for use.
        :keyword tags: Application specific metadata in the form of key-value pairs.
        :paramtype tags: dict[str, str]
        :keyword str content_type: An arbitrary string indicating the type of the secret, e.g. 'password'
        :keyword ~datetime.datetime not_before: Not before date of the secret in UTC
        :keyword ~datetime.datetime expires_on: Expiry date of the secret in UTC
        :rtype: ~azure.keyvault.secrets.KeyVaultSecret
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START set_secret]
                :end-before: [END set_secret]
                :language: python
                :caption: Set a secret's value
                :dedent: 8

        """
        enabled = kwargs.pop("enabled", None)
        not_before = kwargs.pop("not_before", None)
        expires_on = kwargs.pop("expires_on", None)
        content_type = kwargs.pop("content_type", None)
        if enabled is not None or not_before is not None or expires_on is not None:
            attributes = self._models.SecretAttributes(
                enabled=enabled, not_before=not_before, expires=expires_on
            )
        else:
            attributes = None

        parameters = self._models.SecretSetParameters(
            value=value,
            tags=kwargs.pop("tags", None),
            content_type=content_type,
            secret_attributes=attributes
        )

        bundle = self._client.set_secret(
            vault_base_url=self.vault_url,
            secret_name=name,
            parameters=parameters,
            error_map=_error_map,
            **kwargs
        )
        return KeyVaultSecret._from_secret_bundle(bundle)

    @distributed_trace
    def update_secret_properties(self, name, version=None, **kwargs):
        # type: (str, Optional[str], **Any) -> SecretProperties
        """Update properties of a secret other than its value. Requires secrets/set permission.

        This method updates properties of the secret, such as whether it's enabled, but can't change the secret's
        value. Use :func:`set_secret` to change the secret's value.

        :param str name: Name of the secret
        :param str version: (optional) Version of the secret to update. If unspecified, the latest version is updated.
        :keyword bool enabled: Whether the secret is enabled for use.
        :keyword tags: Application specific metadata in the form of key-value pairs.
        :paramtype tags: dict[str, str]
        :keyword str content_type: An arbitrary string indicating the type of the secret, e.g. 'password'
        :keyword ~datetime.datetime not_before: Not before date of the secret in UTC
        :keyword ~datetime.datetime expires_on: Expiry date of the secret in UTC
        :rtype: ~azure.keyvault.secrets.SecretProperties
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the secret doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START update_secret]
                :end-before: [END update_secret]
                :language: python
                :caption: Update a secret's attributes
                :dedent: 8

        """
        enabled = kwargs.pop("enabled", None)
        not_before = kwargs.pop("not_before", None)
        expires_on = kwargs.pop("expires_on", None)
        content_type = kwargs.pop("content_type", None)
        if enabled is not None or not_before is not None or expires_on is not None:
            attributes = self._models.SecretAttributes(
                enabled=enabled, not_before=not_before, expires=expires_on
            )
        else:
            attributes = None

        parameters = self._models.SecretUpdateParameters(
            content_type=content_type,
            secret_attributes=attributes,
            tags=kwargs.pop("tags", None)
        )

        bundle = self._client.update_secret(
            self.vault_url,
            name,
            secret_version=version or "",
            parameters=parameters,
            error_map=_error_map,
            **kwargs
        )
        return SecretProperties._from_secret_bundle(bundle)  # pylint: disable=protected-access

    @distributed_trace
    def list_properties_of_secrets(self, **kwargs):
        # type: (**Any) -> ItemPaged[SecretProperties]
        """List identifiers and attributes of all secrets in the vault. Requires secrets/list permission.

        List items don't include secret values. Use :func:`get_secret` to get a secret's value.

        :returns: An iterator of secrets, excluding their values
        :rtype: ~azure.core.paging.ItemPaged[~azure.keyvault.secrets.SecretProperties]

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START list_secrets]
                :end-before: [END list_secrets]
                :language: python
                :caption: List all secrets
                :dedent: 8

        """
        return self._client.get_secrets(
            self._vault_url,
            maxresults=kwargs.pop("max_page_size", None),
            cls=lambda objs: [SecretProperties._from_secret_item(x) for x in objs],
            error_map=_error_map,
            **kwargs
        )

    @distributed_trace
    def list_properties_of_secret_versions(self, name, **kwargs):
        # type: (str, **Any) -> ItemPaged[SecretProperties]
        """List properties of all versions of a secret, excluding their values. Requires secrets/list permission.

        List items don't include secret values. Use :func:`get_secret` to get a secret's value.

        :param str name: Name of the secret
        :returns: An iterator of secrets, excluding their values
        :rtype: ~azure.core.paging.ItemPaged[~azure.keyvault.secrets.SecretProperties]

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START list_properties_of_secret_versions]
                :end-before: [END list_properties_of_secret_versions]
                :language: python
                :caption: List all versions of a secret
                :dedent: 8

        """
        return self._client.get_secret_versions(
            self._vault_url,
            name,
            maxresults=kwargs.pop("max_page_size", None),
            cls=lambda objs: [SecretProperties._from_secret_item(x) for x in objs],
            error_map=_error_map,
            **kwargs
        )

    @distributed_trace
    def backup_secret(self, name, **kwargs):
        # type: (str, **Any) -> bytes
        """Back up a secret in a protected form useable only by Azure Key Vault. Requires secrets/backup permission.

        :param str name: Name of the secret to back up
        :rtype: bytes
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the secret doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START backup_secret]
                :end-before: [END backup_secret]
                :language: python
                :caption: Back up a secret
                :dedent: 8

        """
        backup_result = self._client.backup_secret(self.vault_url, name, error_map=_error_map, **kwargs)
        return backup_result.value

    @distributed_trace
    def restore_secret_backup(self, backup, **kwargs):
        # type: (bytes, **Any) -> SecretProperties
        """Restore a backed up secret. Requires the secrets/restore permission.

        :param bytes backup: A secret backup as returned by :func:`backup_secret`
        :returns: The restored secret
        :rtype: ~azure.keyvault.secrets.SecretProperties
        :raises:
            :class:`~azure.core.exceptions.ResourceExistsError` if the secret's name is already in use,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START restore_secret_backup]
                :end-before: [END restore_secret_backup]
                :language: python
                :caption: Restore a backed up secret
                :dedent: 8

        """
        bundle = self._client.restore_secret(
            self.vault_url,
            parameters=self._models.SecretRestoreParameters(secret_bundle_backup=backup),
            error_map=_error_map,
            **kwargs
        )
        return SecretProperties._from_secret_bundle(bundle)

    @distributed_trace
    def begin_delete_secret(self, name, **kwargs):
        # type: (str, **Any) -> DeletedSecret
        """Delete all versions of a secret. Requires secrets/delete permission.

        When this method returns Key Vault has begun deleting the secret. Deletion may take several seconds in a vault
        with soft-delete enabled. This method therefore returns a poller enabling you to wait for deletion to complete.

        :param str name: Name of the secret to delete.
        :returns: A poller for the delete operation. The poller's `result` method returns the
         :class:`~azure.keyvault.secrets.DeletedSecret` without waiting for deletion to complete. If the vault has
         soft-delete enabled and you want to permanently delete the secret with :func:`purge_deleted_secret`, call the
         poller's `wait` method first. It will block until the deletion is complete. The `wait` method requires
         secrets/get permission.
        :rtype: ~azure.core.polling.LROPoller[~azure.keyvault.secrets.DeletedSecret]
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the secret doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START delete_secret]
                :end-before: [END delete_secret]
                :language: python
                :caption: Delete a secret
                :dedent: 8

        """
        polling_interval = kwargs.pop("_polling_interval", None)
        if polling_interval is None:
            polling_interval = 2
        deleted_secret = DeletedSecret._from_deleted_secret_bundle(
            self._client.delete_secret(self.vault_url, name, error_map=_error_map, **kwargs)
        )

        command = partial(self.get_deleted_secret, name=name, **kwargs)
        polling_method = DeleteRecoverPollingMethod(
            # no recovery ID means soft-delete is disabled, in which case we initialize the poller as finished
            finished=deleted_secret.recovery_id is None,
            command=command,
            final_resource=deleted_secret,
            interval=polling_interval,
        )
        return KeyVaultOperationPoller(polling_method)

    @distributed_trace
    def get_deleted_secret(self, name, **kwargs):
        # type: (str, **Any) -> DeletedSecret
        """Get a deleted secret. Possible only in vaults with soft-delete enabled. Requires secrets/get permission.

        :param str name: Name of the deleted secret
        :rtype: ~azure.keyvault.secrets.DeletedSecret
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the deleted secret doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START get_deleted_secret]
                :end-before: [END get_deleted_secret]
                :language: python
                :caption: Get a deleted secret
                :dedent: 8

        """
        bundle = self._client.get_deleted_secret(self.vault_url, name, error_map=_error_map, **kwargs)
        return DeletedSecret._from_deleted_secret_bundle(bundle)

    @distributed_trace
    def list_deleted_secrets(self, **kwargs):
        # type: (**Any) -> ItemPaged[DeletedSecret]
        """Lists all deleted secrets. Possible only in vaults with soft-delete enabled.

        Requires secrets/list permission.

        :returns: An iterator of deleted secrets, excluding their values
        :rtype: ~azure.core.paging.ItemPaged[~azure.keyvault.secrets.DeletedSecret]

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START list_deleted_secrets]
                :end-before: [END list_deleted_secrets]
                :language: python
                :caption: List deleted secrets
                :dedent: 8

        """
        return self._client.get_deleted_secrets(
            self._vault_url,
            maxresults=kwargs.pop("max_page_size", None),
            cls=lambda objs: [DeletedSecret._from_deleted_secret_item(x) for x in objs],
            error_map=_error_map,
            **kwargs
        )

    @distributed_trace
    def purge_deleted_secret(self, name, **kwargs):
        # type: (str, **Any) -> None
        """Permanently deletes a deleted secret. Possible only in vaults with soft-delete enabled.

        Performs an irreversible deletion of the specified secret, without
        possibility for recovery. The operation is not available if the
        :py:attr:`~azure.keyvault.secrets.SecretProperties.recovery_level` does not specify 'Purgeable'.
        This method is only necessary for purging a secret before its
        :py:attr:`~azure.keyvault.secrets.DeletedSecret.scheduled_purge_date`.

        Requires secrets/purge permission.

        :param str name: Name of the secret to purge
        :returns: None
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. code-block:: python

                # if the vault has soft-delete enabled, purge permanently deletes the secret
                # (with soft-delete disabled, begin_delete_secret is permanent)
                secret_client.purge_deleted_secret("secret-name")

        """
        self._client.purge_deleted_secret(self.vault_url, name, error_map=_error_map, **kwargs)

    @distributed_trace
    def begin_recover_deleted_secret(self, name, **kwargs):
        # type: (str, **Any) -> SecretProperties
        """Recover a deleted secret to its latest version. Possible only in a vault with soft-delete enabled.

        If the vault does not have soft-delete enabled, :func:`begin_delete_secret` is permanent, and this method will
        return an error. Attempting to recover a non-deleted secret will also return an error.

        When this method returns Key Vault has begun recovering the secret. Recovery may take several seconds. This
        method therefore returns a poller enabling you to wait for recovery to complete. Waiting is only necessary when
        you want to use the recovered secret in another operation immediately.

        Requires the secrets/recover permission.

        :param str name: Name of the deleted secret to recover
        :returns: A poller for the recovery operation. The poller's `result` method returns the recovered
         :class:`~azure.keyvault.secrets.Secret` without waiting for recovery to complete. If you want to use the
         recovered secret immediately, call the poller's `wait` method, which blocks until the secret is ready to use.
         The `wait` method requires secrets/get permission.
        :rtype: ~azure.core.polling.LROPoller[~azure.keyvault.secrets.SecretProperties]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START recover_deleted_secret]
                :end-before: [END recover_deleted_secret]
                :language: python
                :caption: Recover a deleted secret
                :dedent: 8

        """
        polling_interval = kwargs.pop("_polling_interval", None)
        if polling_interval is None:
            polling_interval = 2
        recovered_secret = SecretProperties._from_secret_bundle(
            self._client.recover_deleted_secret(self.vault_url, name, error_map=_error_map, **kwargs)
        )

        command = partial(self.get_secret, name=name, **kwargs)
        polling_method = DeleteRecoverPollingMethod(
            finished=False, command=command, final_resource=recovered_secret, interval=polling_interval,
        )
        return KeyVaultOperationPoller(polling_method)
