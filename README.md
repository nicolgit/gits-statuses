# Welcome to gits-statuses
in this repo you can fine a powershell and a corresponding sh scripts that once executed into the root directory where you have all you local repos
gives you a table in output that shows repo URL, pull number, push number, commit nunmber, files changed, in a similar way on-my-posh provides on the
prompt, but here you have a massive view of all your repos.

# hot to use it

clone the repo in the same folder you have all your repos

```
git clone https://github.com/nicolgit/gits-statuses  
```

the type:

```
# Basic usage - scan current directory
.\run.ps1

# Detailed view with full remote URLs
.\run.ps1 -Detailed

# Scan a specific directory
.\run.ps1 -Path "C:\MyProjects"

# Show help
.\run.ps1 -Help
```
