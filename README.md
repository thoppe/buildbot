In-progress experiment implementing flows as a graph database.

The results of `demo.py` should look something like:

![](example_images/Screenshot.png)

Right now the interface looks something like:


Create a new graph connection

    gdb = enchanced_GraphDatabase(**neo4j_login)

Delete everything in the old graph. WARNING: this is really a hard reset and will wipe any existing neo4j database. It's useful here for testing purposes only.

    gdb.hard_reset()

Define some flows:

    f1 = gdb.new_flow(description = "Install neo4j-rest-client")
    f2 = gdb.new_flow(description = "Install pip")
    f3 = gdb.new_flow(description = "sudo apt-get install pip")
    f4 = gdb.new_flow(description = "pip install neo4jrestclient")

Assign the ddependencies.

    f1.relationships.create("depends", f2)
    f2.relationships.create("depends", f3)
    f1.relationships.create("depends", f4)

Add some validation steps:

    v = gdb.new_validation(
        command="pip --version",
        success="pip 7.0.3 ...",
        failure="command not found",
        )

    f2.relationships.create("validator", v)


    v = gdb.new_validation(
        command='python -c "import neo4jrestclientx"',
        success="",
        failure="ImportError: No module named neo4jrestclientx",
        )

    v.relationships.create("validator", f1)
