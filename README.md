## How to use? ##

Checkout this project using the command line, then it is recommended
to set up a virtual environment, and activate it.

For example, if you're using a Windows system this looks like this:
```shell
python -m venv venv
venv\Scripts\activate.bat
```

Next install dependencies, there is only the pyved engine here:
```shell
pip install pyved-engine
```

Finally you can test games by using the pyved-engine launcher. As follows:
```shell
pyv-cli play ChessBundle
```
It's important to understand that games made with the pyved-engine are
somehow "bundled" so it becomes possible to convert them to browser games.
Do no try to bundle games manually as unexpected (and hard to find) bugs may
appear.

In order to create a new bundle you can simply use the command:
```shell
pyv-cli init MyUniqueGame
```
To learn more about the pyved-engine, please refer to:
[the Pyved-engine repository](https://github.com/gaudiatech/pyved-engine/)
