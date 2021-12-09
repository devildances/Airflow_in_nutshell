## How to Start

- Install Virtual Machine on our local (e.g. VirtualBox)
- Download Linux distribution (Ubuntu) that will be running in VirtualBox
- Start the VM, open our web browser and go to localhost:8080 to go through the Airflow UI
- Access the VM in SSH and connect VS Code through it
    - Open our terminal and type ```bash
    ssh -p 2222 airflow@localhost
    ```
    - Type `yes` if it asks for connecting
    - Then we need to enter the password `airflow`
    - At this point we're inside the VM connected through the user ***airflow***
    - Hit Control+D to exit the VM
- set up Visual Studio Code to edit files/folders in the VM
    - Open VS Code
    - Click on "Extensions"
    - In the search bar on the top, look for "remote ssh" and Install it
    - Once the plugin is installed, open it by hitting
        - Cmd-P (on Mac)
        - F1 (on Windows)
    - Type `>remote-ssh`
    - Then hit enter, and select "Add New SSH host..."
    - Enter the following command ```bash ssh -p 2222 airflow@localhost``` and hit enter
    - Select the first proposition for the SSH config file
    - Now the connection has been added, open the plugin again
        - Cmd-P (on Mac)
        - F1 (on Windows)
    - Type `>remote-ssh` Then choose "localhost" by hitting enter
    - A new Visual Studio Code window opens, type the password `airflow`
    - And **WE ARE CONNECTED!**