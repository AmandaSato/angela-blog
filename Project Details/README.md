# Git: version control

Terminal
: mkdir Story
(Working Directory)

: cd Story
:~/Story$ touch chapter1.txt
:~/Story$ open chapter1.txt
:~/Story$ git init
:~/Story$ ls -a
:~/Story$ ls 
:~/Story$ git status
Untracked Files in RED (working directory)

:~/Story$ git add chapter1.txt
:~/Story$ git status
Files ready to be commited in GREEN (Staging area)

:~/Story$ git commit -m "Complete Chapter 1"
Commit the files.
(Messages usually written in the "present tense".)

:~/Story$ git log
See the commits you've made.

:~/Story$ touch chapter2.txt
:~/Story$ touch chapter3.txt
:~/Story$ git add .
Will send all Untracked Files in the working directory to Staging area.

:~/Story$ git commit -m "Complete Chapter 2 and 3"

[Suppose you edited Chapter 3, but fell asleep on the keyboard, wrote a bunch of nonsense and saved the file. ]
[The new version of Chapter 3 is in the Working directory, not yet on Staging nor Commited.]

:~/Story$ git diff chapter3.txt
Will show what is different between the current version and the last version commited.

:~/Story$ git checkout chapter3.txt
Will roll back the file to it's last version commited.

# Githhub
To add our local repository to a remote repository (Github), we first create a new repository on Github and copy the URL.

:~/Story$ git add remote origin repository_URL_here
We added the remote repository

:~/Story$ git push -u origin master
We push our local repository to the main(master) branch of the remote repository.
