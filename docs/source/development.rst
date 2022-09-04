**************
Development
**************

Pre-commit actions
######################

Before each commit developer should run

.. code-block:: bash

    make fix

This will reformat code to not be longer than 100 symbols on the line and other things that ``black`` requres. This will also resort imports and regenerate schemas for YAML configuration files.

.. code-block:: bash

    make check

This will run style checks, typing checks and all of the unittests.


Miscellaneous
#########################

.. code-block:: bash

    make build-*

Depending on the glob this will build docs or the project itself. See `Makefile <https://github.com/Kraysent/OMTool/blob/main/Makefile>`__ for specifics. 
