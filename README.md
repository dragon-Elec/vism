# vism
Vi Software Manager for Linux, helps to install 3rd party software that was not packaged specially for your distribution (supports only local installations so far)

To install run:
```bash
python3 install.py
```

To install software using VISM, chdir to root of program and run:
```bash
sudo vism setup
```
Note: when you will be asked about software name, write human-readable name, for example: "Hello World Program" isntead of "helloworld_program"

To list installed software, run:
```bash
vism list
```

To remove installed software, run:
```bash
sudo vism remove "Software Name"
```
