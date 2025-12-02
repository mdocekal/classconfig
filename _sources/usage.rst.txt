Usage
=====

.. contents:: Table of Contents
   :local:
   :depth: 2

Installation
------------

You can install it using pip:

.. code-block:: bash

    pip install classconfig

Basic Usage
-----------

The core of ``classconfig`` is the ``ConfigurableMixin`` class and ``ConfigurableValue``/``ConfigurableFactory`` descriptors.

Here is a simple example:

.. code-block:: python

    from classconfig import ConfigurableMixin, ConfigurableValue, Config

    class MyConfig(ConfigurableMixin):
        host: str = ConfigurableValue(desc="Host address", user_default="localhost")
        port: int = ConfigurableValue(desc="Port number", user_default=8080)

    # Create an instance with default values
    config = MyConfig()
    print(f"Host: {config.host}, Port: {config.port}")
    # Output: Host: localhost, Port: 8080

    # Create an instance with custom values
    config = MyConfig(host="127.0.0.1", port=9090)
    print(f"Host: {config.host}, Port: {config.port}")
    # Output: Host: 127.0.0.1, Port: 9090

Configuration Files
-------------------

Generating Configuration
^^^^^^^^^^^^^^^^^^^^^^^^

You can easily generate a YAML configuration file from your class definition:

.. code-block:: python

    from classconfig import Config

    # Generate YAML config
    Config(MyConfig).save("config.yaml")

The generated ``config.yaml`` will look like this:

.. code-block:: yaml

    host: localhost  # Host address
    port: 8080  # Port number

Loading Configuration
^^^^^^^^^^^^^^^^^^^^^

You can load the configuration back into your class:

.. code-block:: python

    from classconfig import Config, ConfigurableFactory

    # Load config
    loaded_config = Config(MyConfig).load("config.yaml")
    
    # Create instance
    my_obj = ConfigurableFactory(MyConfig).create(loaded_config)
    print(f"Host: {my_obj.host}, Port: {my_obj.port}")

Dataclasses
-----------

``classconfig`` also supports Python dataclasses via ``ConfigurableDataclassMixin``.

.. code-block:: python

    from dataclasses import dataclass, field
    from classconfig.classes import ConfigurableDataclassMixin

    @dataclass
    class ServerConfig(ConfigurableDataclassMixin):
        host: str = field(default="localhost", metadata={"desc": "Host address"})
        port: int = field(default=8080, metadata={"desc": "Port number"})

    # Usage is similar to ConfigurableMixin
    config = ServerConfig()
    print(config.host)

Advanced Features
-----------------

Configurable Attributes
^^^^^^^^^^^^^^^^^^^^^^^

``classconfig`` provides several descriptors to define configurable attributes:

*   **ConfigurableValue**: For simple values (int, str, float, bool, etc.).
*   **ConfigurableFactory**: For nested configurable objects.
*   **ConfigurableSubclassFactory**: For selecting and configuring a subclass of a given parent class.
*   **ListOfConfigurableSubclassFactoryAttributes**: For a list of configurable objects (subclasses).

Mixins
^^^^^^

*   **ConfigurableMixin**: The base mixin for standard classes.
*   **ConfigurableDataclassMixin**: The mixin for dataclasses.

Validators
^^^^^^^^^^

Validators ensure that the configuration values meet specific criteria. They are callables that take a value and return ``True`` or raise an exception.

Available validators in ``classconfig.validators``:

*   **TypeValidator**: Checks if value is of specific type.
*   **IntegerValidator**, **FloatValidator**, **StringValidator**, **BoolValidator**: Type-specific validators.
*   **MinValueIntegerValidator**, **MinValueFloatValidator**: Checks minimum value.
*   **ValueInIntervalIntegerValidator**: Checks if value is within an interval.
*   **AllValidator**: Combines multiple validators (AND logic).
*   **AnyValidator**: Combines multiple validators (OR logic).

Transformers
^^^^^^^^^^^^

Transformers modify the input value before validation.

Available transformers in ``classconfig.transforms``:

*   **TryTransforms**: Tries multiple transformers in order.
*   **RelativePathTransformer**: Resolves relative paths.
*   **CPUWorkersTransformer**: Handles CPU count (e.g., -1 for all cores).
*   **EnumTransformer**: Converts string to Enum member.
*   **SubclassTransformer**: Converts string to class type.
*   **TransformIfNotNone**: Applies transformer only if value is not None.

Comprehensive Example
---------------------

Let's put it all together with an example using ``ConfigurableSubclassFactory``, validators, and transformers.

.. code-block:: python

    from classconfig import (
        ConfigurableMixin, ConfigurableValue, ConfigurableSubclassFactory,
        ListOfConfigurableSubclassFactoryAttributes, Config, ConfigurableFactory
    )
    from classconfig.validators import MinValueIntegerValidator
    from classconfig.transforms import EnumTransformer
    from enum import Enum
    from abc import ABC, abstractmethod

    # 1. Define an Enum and a Transformer for it
    class LogLevel(Enum):
        INFO = "INFO"
        DEBUG = "DEBUG"
        ERROR = "ERROR"

    # 2. Define an abstract base class for plugins
    class Plugin(ConfigurableMixin, ABC):
        @abstractmethod
        def run(self):
            pass

    # 3. Define concrete plugins
    class FilePlugin(Plugin):
        path: str = ConfigurableValue(desc="Path to log file")
        
        def run(self):
            print(f"Logging to file: {self.path}")

    class ConsolePlugin(Plugin):
        prefix: str = ConfigurableValue(desc="Log prefix", user_default="[LOG]")
        
        def run(self):
            print(f"{self.prefix} Logging to console")

    # 4. Define the main application configuration
    class AppConfig(ConfigurableMixin):
        # Simple value with validator and transformer
        log_level: LogLevel = ConfigurableValue(
            desc="Logging level",
            user_default="INFO",
            transform=EnumTransformer(LogLevel)
        )
        
        # Value with validator
        max_retries: int = ConfigurableValue(
            desc="Maximum retries",
            user_default=3,
            validator=MinValueIntegerValidator(0)
        )

        # Subclass factory: allows choosing between FilePlugin and ConsolePlugin
        primary_plugin: Plugin = ConfigurableSubclassFactory(
            parent_cls_type=Plugin,
            desc="Primary plugin to use",
            user_default=ConsolePlugin
        )

        # List of subclass factories
        extra_plugins: list[Plugin] = ListOfConfigurableSubclassFactoryAttributes(
            ConfigurableSubclassFactory(Plugin),
            desc="List of additional plugins",
            user_defaults=[ConsolePlugin]
        )

    # --- Usage ---

    # Generate config file
    Config(AppConfig).save("advanced_config.yaml")

    # The generated YAML will look like this:
    # log_level: INFO # Logging level
    # max_retries: 3 # Maximum retries
    # primary_plugin: # Primary plugin to use
    #   cls: ConsolePlugin # name of class that is subclass of Plugin
    #   config: # configuration for defined class
    #     prefix: [LOG] # Log prefix
    # extra_plugins: # List of additional plugins
    # - cls: ConsolePlugin # name of class that is subclass of Plugin
    #   config: # configuration for defined class
    #     prefix: [LOG] # Log prefix

    # Load config (assuming we modified it to use FilePlugin for primary)
    # Let's simulate loading a modified config dict
    config_data = {
        "log_level": "DEBUG",
        "max_retries": 5,
        "primary_plugin": {
            "cls": "FilePlugin",
            "config": {"path": "/var/log/app.log"}
        },
        "extra_plugins": []
    }
    
    # In real usage: loaded_config = Config(AppConfig).load("advanced_config.yaml")
    # Here we mock the loading for demonstration
    from classconfig import LoadedConfig
    loaded_config = Config(AppConfig).trans_and_val(config_data, None)

    app_config = ConfigurableFactory(AppConfig).create(loaded_config)

    print(f"Log Level: {app_config.log_level}")
    print(f"Max Retries: {app_config.max_retries}")
    print(f"Primary Plugin Type: {type(app_config.primary_plugin)}")
    if isinstance(app_config.primary_plugin, FilePlugin):
        print(f"Primary Plugin Path: {app_config.primary_plugin.path}")

    # Output:
    # Log Level: LogLevel.DEBUG
    # Max Retries: 5
    # Primary Plugin Type: <class '__main__.FilePlugin'>
    # Primary Plugin Path: /var/log/app.log

Why YAML?
---------

YAML is a human-readable data serialization language. It is easy to read and write. It is also easy to parse and
generate.

It supports hierarchical data structures, which are very useful when you need to represent configuration
of a class that has other configurable classes as members.

It supports comments, unlike e.g. json, which is also a big advantage.
