# actions_101
How works the actions on Github, a first sight

This repo has as main goal to show how works the actions on Github, a first sight. It's not intended to be used in production, but to be used as a learning tool.
I've been using GitHub for some time now, but I've never had the opportunity to use the actions. So, I decided to create this repo to learn how to use it.

## What is GitHub Actions?
GitHub Actions is a continuous integration and continuous delivery (CI/CD) platform that allows you to automate your build, test, and deployment pipeline. You can create workflows that build and test every pull request to your repository, or deploy merged pull requests to production.
Take it from: https://docs.github.com/en/actions/learn-github-actions/understanding-github-actions#overview

## The components of GitHub Actions
You can configure a GitHub Actions workflow to be triggered when an event occurs in your repository, such as a pull request being opened or an issue being created. Your workflow contains one or more jobs which can run in sequential order or in parallel.

Event --------> Runner 1                ----->  Runner 2
                Job 1                           Job 2
                  Step 1: Run action              Step 1: Run action
                  Step 2: Run script              Step 2: Run script
                  Step 3: Run script              Step 3: Run script
                  Step 4: Run script

### Workflows
A workflow is a configurable automated process that will run one or more jobs. Workflows are defined by a YAML file checked in to your repository and will run when triggered by an event in your repository, or they can be triggered manually, or at a defined schedule.            

Workflows are defined in the .github/workflows directory in a repository, and a repository can have multiple workflows, each of which can perform a different set of tasks. 

Note: YAML is a human-readable data serialization standard that can be used in conjunction with all programming languages and is often used to write configuration files.

### Events
An event is a specific activity in a repository that triggers a workflow run. For example, activity can originate from GitHub when someone creates a pull request, opens an issue, or pushes a commit to a repository.
List of events: https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows

### Jobs
A job is a set of steps in a workflow that is executed on the same runner. Each step is either a shell script that will be executed, or an action that will be run.  Steps are executed in order and are dependent on each other. Since each step is executed on the same runner, you can share data from one step to another. 

### Actions
An action is a custom application for the GitHub Actions platform that performs a complex but frequently repeated task. Use an action to help reduce the amount of repetitive code that you write in your workflow files. 

### Runners
A runner is a server that runs your workflows when they're triggered. Each runner can run a single job at a time. GitHub provides Ubuntu Linux, Microsoft Windows, and macOS runners to run your workflows; each workflow run executes in a fresh, newly-provisioned virtual machine. GitHub also offers larger runners, which are available in larger configurations.

### Variables
Variables provide a way to store and reuse non-sensitive configuration information. You can store any configuration data such as compiler flags, usernames, or server names as variables. Variables are interpolated on the runner machine that runs your workflow, also we can find a environment variables .
List of environment variables: https://docs.github.com/en/actions/learn-github-actions/variables#default-environment-variables


