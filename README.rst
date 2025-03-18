======
remopy
======


Python package for remotely executing python functions during runtime



============
Installation
============


To install remopy, run this command in your terminal:

.. code-block:: console

    pip install git+https://github.com/surajgoel5/remopy.git

============
Usage
============

Server:


.. code-block:: console

    server = Server()
	server.run()



Client:


.. code-block:: py

    def fn(x):
		import numpy as np
		return np.array(x**2)
	client = Client("192.168.0.10")
	res = client.submit_job(fn,5)

=======
Credits
=======

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
