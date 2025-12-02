Examples
========

.. contents:: Table of Contents
   :local:
   :depth: 2

1. Basic Configuration
----------------------

This example demonstrates the simplest usage of ``classconfig`` with basic types.

.. code-block:: python

    from classconfig import ConfigurableMixin, ConfigurableValue, Config

    class ServerConfig(ConfigurableMixin):
        host: str = ConfigurableValue(desc="Host address", user_default="localhost")
        port: int = ConfigurableValue(desc="Port number", user_default=8080)
        debug: bool = ConfigurableValue(desc="Debug mode", user_default=False)

    # Generate config
    Config(ServerConfig).save("server_config.yaml")

    # Load config
    # loaded_config = Config(ServerConfig).load("server_config.yaml")
    # server = ConfigurableFactory(ServerConfig).create(loaded_config)

2. Nested Configuration
-----------------------

You can nest configurable objects using ``ConfigurableFactory``.

.. code-block:: python

    from classconfig import ConfigurableMixin, ConfigurableValue, ConfigurableFactory

    class DatabaseConfig(ConfigurableMixin):
        host: str = ConfigurableValue(desc="DB Host")
        port: int = ConfigurableValue(desc="DB Port", user_default=5432)

    class AppConfig(ConfigurableMixin):
        name: str = ConfigurableValue(desc="App Name")
        database: DatabaseConfig = ConfigurableFactory(DatabaseConfig, desc="Database Settings")

3. Polymorphism with Subclass Factory
-------------------------------------

Use ``ConfigurableSubclassFactory`` to allow selecting a specific subclass implementation via configuration.

.. code-block:: python

    from classconfig import ConfigurableMixin, ConfigurableValue, ConfigurableSubclassFactory
    from abc import ABC, abstractmethod

    class Storage(ConfigurableMixin, ABC):
        @abstractmethod
        def save(self, data):
            pass

    class DiskStorage(Storage):
        path: str = ConfigurableValue(desc="Storage path")
        def save(self, data): print(f"Saving to disk at {self.path}")

    class S3Storage(Storage):
        bucket: str = ConfigurableValue(desc="S3 Bucket")
        def save(self, data): print(f"Saving to S3 bucket {self.bucket}")

    class Service(ConfigurableMixin):
        storage: Storage = ConfigurableSubclassFactory(Storage, desc="Storage backend")

    # In YAML, you specify the class name:
    # storage:
    #   cls: S3Storage
    #   config:
    #     bucket: my-bucket

4. List of Polymorphic Objects
------------------------------

Use ``ListOfConfigurableSubclassFactoryAttributes`` to configure a list of objects where each can be a different subclass.

.. code-block:: python

    from classconfig import ConfigurableMixin, ListOfConfigurableSubclassFactoryAttributes, ConfigurableSubclassFactory
    # Assuming Storage, DiskStorage, S3Storage from Example 3

    class BackupService(ConfigurableMixin):
        targets: list[Storage] = ListOfConfigurableSubclassFactoryAttributes(
            ConfigurableSubclassFactory(Storage),
            desc="List of backup targets"
        )

    # In YAML:
    # targets:
    #   - cls: DiskStorage
    #     config:
    #       path: /backup
    #   - cls: S3Storage
    #     config:
    #       bucket: backup-bucket

5. Dataclasses
--------------

You can use Python dataclasses with ``ConfigurableDataclassMixin``.

.. code-block:: python

    from dataclasses import dataclass, field
    from classconfig.classes import ConfigurableDataclassMixin

    @dataclass
    class UserConfig(ConfigurableDataclassMixin):
        username: str = field(metadata={"desc": "Username"})
        age: int = field(default=18, metadata={"desc": "Age"})

6. Validation
-------------

Ensure configuration values meet specific criteria using validators.

.. code-block:: python

    from classconfig import ConfigurableMixin, ConfigurableValue
    from classconfig.validators import MinValueIntegerValidator, StringValidator

    class RetryConfig(ConfigurableMixin):
        count: int = ConfigurableValue(
            desc="Retry count",
            validator=MinValueIntegerValidator(0)
        )
        strategy: str = ConfigurableValue(
            desc="Retry strategy",
            validator=StringValidator()
        )

7. Transformation (Enums)
-------------------------

Automatically convert string inputs to Enum members.

.. code-block:: python

    from classconfig import ConfigurableMixin, ConfigurableValue
    from classconfig.transforms import EnumTransformer
    from enum import Enum

    class Color(Enum):
        RED = "RED"
        GREEN = "GREEN"
        BLUE = "BLUE"

    class ThemeConfig(ConfigurableMixin):
        primary_color: Color = ConfigurableValue(
            desc="Primary color",
            transform=EnumTransformer(Color)
        )

8. Relative Paths
-----------------

Resolve paths relative to the configuration file location.

.. code-block:: python

    from classconfig import ConfigurableMixin, ConfigurableValue
    from classconfig.transforms import RelativePathTransformer

    class FileConfig(ConfigurableMixin):
        # Path will be resolved relative to the config file's directory
        input_file: str = ConfigurableValue(
            desc="Input file path",
            transform=RelativePathTransformer()
        )

9. Delayed Initialization
-------------------------

Delay the creation of objects until needed.

.. code-block:: python

    from classconfig import ConfigurableMixin, ConfigurableFactory

    class HeavyResource(ConfigurableMixin):
        def __init__(self):
            print("Heavy resource initialized")

    class App(ConfigurableMixin):
        # Resource won't be created immediately upon config loading
        resource = ConfigurableFactory(HeavyResource, delay_init=True)

    # When loaded:
    # app = ...
    # resource_factory = app.resource
    # resource_instance = resource_factory.create()

10. Inheritance
---------------

Configurable classes can inherit from other configurable classes.

.. code-block:: python

    from classconfig import ConfigurableMixin, ConfigurableValue

    class BaseConfig(ConfigurableMixin):
        name: str = ConfigurableValue(desc="Name")

    class ExtendedConfig(BaseConfig):
        # Inherits 'name' from BaseConfig
        version: str = ConfigurableValue(desc="Version")

    # ExtendedConfig will have both 'name' and 'version' configurable attributes.

11. Omit Attributes in Factory
------------------------------

You can exclude specific attributes from being configurable when using ``ConfigurableFactory``.

.. code-block:: python

    from classconfig import ConfigurableMixin, ConfigurableValue, ConfigurableFactory

    class InternalConfig(ConfigurableMixin):
        public_param: str = ConfigurableValue(desc="Public parameter")
        secret_param: str = ConfigurableValue(desc="Secret parameter")

    class AppConfig(ConfigurableMixin):
        # 'secret_param' will not be exposed in the configuration file for 'internal'
        internal: InternalConfig = ConfigurableFactory(
            InternalConfig,
            desc="Internal settings",
            omit={"secret_param": {}}
        )

12. Overriding User Defaults
----------------------------

You can override the default values of the nested class when defining the factory.

.. code-block:: python

    from classconfig import ConfigurableMixin, ConfigurableValue, ConfigurableFactory

    class Server(ConfigurableMixin):
        port: int = ConfigurableValue(desc="Port", user_default=8080)

    class AppConfig(ConfigurableMixin):
        # Override default port to 9090 for this specific usage
        server: Server = ConfigurableFactory(
            Server,
            desc="Server settings",
            file_override_user_defaults={"port": 9090}
        )

13. Creatable Mixin
-------------------

``CreatableMixin`` allows you to create an instance directly from a configuration dictionary or file, without explicitly using ``ConfigurableFactory``.

.. code-block:: python

    from classconfig import ConfigurableMixin, ConfigurableValue, CreatableMixin

    class MyService(ConfigurableMixin, CreatableMixin):
        name: str = ConfigurableValue(desc="Service Name")

    # Create directly from dict
    service = MyService.create({"name": "My Service"})
    print(service.name)

    # Create directly from file
    # service = MyService.create("config.yaml")
