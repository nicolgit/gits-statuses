TODO: 
- `run.ps1` gets modularized for deployment to the PowerShell Gallery 
Idea of what this project sub-folder would look like:
```bash
  ├── powershell-module/                # PowerShell module deployment
  │   ├── README.md                     # PowerShell-specific README
  │   ├── gits-statuses.psd1            # PowerShell module manifest
  │   ├── gits-statuses.psm1            # PowerShell module file
  │   ├── public/                       # Public functions
  │   │   └── get-gitstatus.ps1
  │   ├── private/                      # Private functions
  │   │   ├── get-gitrepository.ps1
  │   │   └── format-git-table.ps1
  │   └── tests/                        # PowerShell tests
  │       └── gits-statuses.tests.ps1
```