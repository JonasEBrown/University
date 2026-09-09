# Requirements

You will need `Python 3.12` or above to run this code.

Make sure you run 
```shell
python3 -m pip install idx2numpy==1.2.3 ImageIO==2.37.3 imageio-ffmpeg==0.6.0 kagglehub matplotlib==3.10.8 numpy==2.4.3 pandas==3.0.1 pillow==12.1.1 tqdm==4.67.3"
```
You may need to set up an environment first
```shell
python3 -m venv venv
\venv\Scripts\activate
```
or for linux
```shell
sudo apt update -y && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv -y
python3 -m venv ~/.venvs/venv
source ~/.venvs/venv/bin/activate
```
then try running the above command again.

# Usage

Either run
```shell
python3 main.py [program] [kwargs]
```
where program and kwargs are the same as below. This will run the program with the given arguments.
Now, without any arguments
```shell
python3 main.py

Please type "mnist", "plots", or "batch": ... 
```

Select what program to run:
- **mnist**: opens the digit drawing app.
- **plots**: displays plots for specific parameter values entered in either WCParameters or manually in the console along side the program name e.g. "plots tau_E=3".
- **batch**: runs a batch of numbers through the classifier and outputs a plot.

```shell
Please type "mnist", "plots", or "batch": plots tau_E=3.0
```
This will run the **plots** program with the argument tau_E=3.0.
This can be done for any parameter from WCParameters.

There are other options for the programs that you are welcome to look at, but they are mostly for the implementation of the `ray` package and clusterisation.
Please note that ray requires `Python 3.12` and a more recent version will not work!
To install `ray` you need to run
```shell
python3 -m pip install ray[default]
```