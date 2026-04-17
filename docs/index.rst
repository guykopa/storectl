storectl
========

CLI tool for monitoring, diagnosing, and managing a distributed object storage cluster on Kubernetes.

Overview
--------

storectl uses Hexagonal Architecture (Ports & Adapters).
The domain layer contains pure business logic with no infrastructure dependencies.
Adapters implement ports to interact with kubectl, /proc, and journalctl.

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   modules/modules
