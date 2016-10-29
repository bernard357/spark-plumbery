# Plumby, a chat assistant for smart Ops

Plumby is your chat assistant for the preparation and the delivery of amazing demonstrations related to cloud orchestration.
For example, ask plumby to deploy a Hadoop cluster, and in response you will get web links to access the ready-to-use HDFS and YARN consoles created for you. Or pick-up any other template from [the plumbery library](http://github.com/bernard357/plumbery-contrib),
such as [the Puppet demonstration](http://github.com/bernard357/plumbery-contrib/fittings/devops/puppet).

Plumby is a software robot (a bot) that relies on Cisco Spark for its main user interface. In the backgound, plumby interacts with the CloudControl API from Dimension Data to deploy, refresh and kill resources on the Managed Cloud Platform.

Plumby is a concrete experimentation on smart Ops, and implements following innovative features:
- user-centric interface - chat box is available from the device of Ops choice, be it a mobile, a tablet or even a desktop computer
- service industrialisation - plumby exposes a standard library of templates that can be consumed on demand
- social-based access control - invite or remove participants to manage the crowd of enabled Ops persons
- contextual delivery - watch and review activities of other Ops, jump in and read what other Ops did before

## Why do you need a chat assistant for your infrastructure?

Let say that you and your team need a working Hadoop cluster to support a demanding application software developer.
With the combination of Cisco Spark, plumby and the Managed Cloud Platform you can arrange this in less than 30 minutes.

1. Create a new Cisco Spark room for your project and invite the other members of the team. From there you can connect easily and share information across the full team.

2. Add plumby to the new room so that it can receive and process commands submitted there.

3. Select the `analytics/hadoop-cluster` template and ask plumby to deploy it.

    """
    Plumby list
    Plumby list analytics
    Plumby use analytics/hadoop-cluster
    Plumby deploy
    """

4. On completion, use information displayed in the chat room to check the behaviour of the cluster.

5. Interact with the software developer and provide him with access to the cluster. This can be done over Cisco Spark or any other communication mean. To retrieve information on the template that has been deployed just ask plumby.

    """
    Plumby information
    """

6. The software developer would perform some tests using the cluster and other components, as automatically as possible.

7. At some point, you go back to the Cisco Spark room of this project and just kill the Hadoop cluster

    """
    Plumby dispose
    """

## How do I interact with plumby?

Plumby analyses commands sent to it, and responds accordingly. At any point in time, use `help` and get a list of common useful commands.

Click in the chat box and type `@plumby` then click or tap on the Plumby label displayed above. Now Cisco Spark knows who you are talking to. Press the space bar and type the rest of the command. The bot will respond to you by appending one or several updates in the room.

![chat](docs/chat.png)

## What can plumby really do?

Plumby has absolutely zero artificial intelligence, so do not expect too much from it. Please type commands carefully.

Common plumby commands:

**`Plumby help`** -- the only command to remember, really

**`Plumby list`** -- get a list of available categories of template

**`Plumby list <category>`** -- get a list of available templates in this category

**`Plumby use <category>/<template>`** -- mention to Plumby that subsequent commands will apply to this template

**`Plumby deploy`** -- deploy the template on the Managed Cloud Platform

**`Plumby information`** -- display information available from the template, e.g., how to access deployed nodes

**`Plumby dispose`** -- destroy all resources from the Managed Cloud Platform that were coming from the template

**`Plumby version`** -- display the version of Plumby

## What do you need to run plumby?

* a token for your bot, provided by [Cisco Spark for Developers](https://developer.ciscospark.com/index.html)
* credentials to consume resources from the [Managed Cloud Platform](https://www.dimensiondata.com) from Dimension Data. If you are a Dimension Data employee, join on of the regional cloud teams to benefit from demonstration credentials
* some instructions and goodwill :-)

