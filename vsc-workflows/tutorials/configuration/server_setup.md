# Workflows - Setting up the server

This text is designed to help someone set up a `fireworks` server and start using the workflows in the `vsc-workflows` package. In principle, it's also possible to just follow the tutorials on the [Fireworks website](https://materialsproject.github.io/fireworks/), but this will be a more succinct but detailed version, which stays focused on how to set up a free server using mongoDB Atlas.

## mongoDB Atlas

Before you can start using `fireworks` to start managing your workflows, you need to set up a mongoDB server that can store the details of your workflows. Although it is possible to install and run your own mongoDB server, it's easier to set up a mongoDB server using mongoDB Atlas, and use this as a database for your initial workflows. 

First go the the [mongoDB Atlas website](https://www.mongodb.com/cloud/atlas) and set up an account. Next, create a new project using the context dropdown menu on the top left and clicking on 'New Project'. Give it a suitable name (e.g. Workflow Tutorial). In the next page it is possible to add other members who can collaborate on the project. However, for this tutorial, just skip that and press "Create Project".

Once the project is set up, it's time to create a cluster, by pressing the "Build a Cluster" button in the center of the screen. We'll be using one of the (free) started clusters, so press the "Create Cluster" right below where it says FREE. Next, let's go over the various click-down menu's available on the cluster creation screen:

* __Cloud Provider & Region__: Here you can choose the location of the server, as well as the service that provides the Cloud storage. Choose whatever region and provider you prefer. For Belgian users, I'd recommend the Google Cloud Platform, because they a free tier available in Belgium. 

* __Cluster Tier__: For the cluster tier, choose 'M0 Sandbox'. This is the only tier that is free of charge, and should be selected by default.
* __Additional Settings__: As no addition settings can be configured for the M0 tier, you can safely ignore this tab.
* __Cluster Name__: Pretty self-explanatory. Once you've given your cluster a suitable name, click on 'Create Cluster' to continue.

> Setting up the cluster takes a little while. This is the perfect time for some [covfefe](https://www.amazon.com/Covfefe-Mug-11oz-Presidential-Alternative/dp/B072Q1B52J).

Once the cluster is set up, you need to set up the Admin user, and whitelist all IP's to be able to connect to the cluster. To do this, click on 'Database Acess'  in the menu on the left. Next, click on the green 'Add New User' button on the right. For the username, just type in `admin`, then choose a password that is easy to remember. Under 'User Privileges', select 'Atlas admin'. Then click on 'Add User'. 

To whitelist all IP's, first click on 'Network Access' in the menu on the left. Click on the green 'Add IP Adress' button on the right, and click on 'Allow Access From Anywhere'. You can see that the 'Whitelist Entry' will be set to `0.0.0.0/0`, which basically tells MongoDB that any IP address can have access to the database. Click on 'Confirm' to add the whitelist entry. 

You're all set! Your MongoDB Atlas Cluster should now be properly configured to start running workflows. The next step is to set up a `launchpad.yaml` file and try connecting to the cluster.

## Setting up the launchpad

Fireworks relies on `.yaml` files for storing the details of your mongoDB server. This file should have the following content for a mongo DB Atlas server:

```
host: "<server URL>"
name: fireworks
username: admin
password: <password>
port: 27017
ssl: true
authsource: admin
```

First, copy that contect into a new file called `my_launchpad.yaml`. Next, you still have to insert your `<server URL>` and `<password>`. The password is **not** the password of your mongoDB account, but rather the password you set for the admin user, after setting up the Cluster.

> Note that the `name` of the server also does not have to correspond to the Cluster name you gave earlier. The `name` specified in the `my_launchpad.yaml` file is the name of the collection you will be storing the workflows in. One cluster can have multiple collections. We'll come back to this once we've connected to the server.

For finding the correct `<server URL>`, follow the following steps:

1. Go back to your new cluster . using the "Clusters" button in the menu on the left.
2. Click on CONNECT just below the cluster name.
3. Choose "Connect with the Mongo Shell".
4. Copy everything between the quotes behind the mongo command under "3 - Run your connection string in your command line".
5. Substitute `<server URL>` in `my_launchpad.yaml` by the URL you just copied.

When you're done, the `my_launchpad.yaml` file should look something like this:

```
host: "mongodb+srv://test-cdfdv.gcp.mongodb.net/test"
name: fireworks
username: admin
password: tutorial
port: 27017
ssl: true
authsource: admin
```

## Connecting to the server

Now that you've set up the `my_launchpad.yaml` file, it's time to try and connect to the server using the Fireworks `lpad` command. After you've made sure the python environment in which `fireworks` is installed is active, use the following command to reset the server:

```
lpad -l my_launchpad.yaml reset
```

When asked if you are sure, answer with `Y`. If everything is working as it should, you now get something like the following output:

```
Are you sure? This will RESET 0 workflows and all data. (Y/N)Y
2020-01-16 19:39:04,268 INFO Performing db tune-up
2020-01-16 19:39:08,179 INFO LaunchPad was RESET.
```

The server is now up and running, and ready to receive workflows! Note that if you go back to your Cluster, and click on COLLECTIONS, there now is the `fireworks` collection. This name was taken from the `my_launchpad.yaml` file. Hence, you can have multiple launchpad files that use the same Cluster, but simply have a different name for the collection.