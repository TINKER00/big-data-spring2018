# Beginning of Class Checklist

## Commit changes to your fork

Using Terminal or Git Bash, change into the directory that contains the local copy of your forked repository.

```sh
cd path/to/my/big-data-spring2018
```

Before you fetch, you need to check if any files have changed because you will need to commit these files before you can fetch changes to the class repo from Github.

```sh
git status
```

If you have not changed any files, or you have already committed your changes to your own forked repository, you will get a message informing you that everything is up to date.

If Git tells you you have modified files in the step above, you need to stage and commit those changes to your personal fork, then push them.

```sh
# Tell git which files need to be committed to your repository.
git add changed_file.md
# Or, if you want to add all of your changes at once...
git add .

# Commit the changed files locally to your personal fork.
# Remember to include a descriptive commit message!
git commit –m ‘my commit message’

# Push the changes to Github.
git push origin master
```

It's a `push`! `origin` is your forked remote repository and `master` is the branch we are pushing.

## Fetch and merge

```sh
# Check out your fork's master branch.
git checkout master
# Fetch changes.
git fetch class
# Marge master branch of class repo into our current branch (`master`)
git merge class/master
```

You should now have any changes made by the teaching staff merged with your forked repository!

## Activate your virtual environment

You need to activate your virtual environment to access all of the python libraries we've installed! As a reminder, you do this as follows:

```sh
# On Mac or Linux...
. ~/.venvs/bdvs/bin/activate
# On Windows...
. ~/.venvs/bdvs/Scripts/activate
```
