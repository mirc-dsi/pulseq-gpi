# Pulseq-GPI 0.1
Python 3.6 based implementation of [Pulseq](http://pulseq.github.io) in [GPI Lab](http://gpilab.com).

- Tested on **macOS Sierra 10.12.1**
- Software: **PyCharm 2017.2.4**, **GPI 1.0.0-rc**
- PyCharm 2017.2.4 SHA1: `0a119a7d305f50efedb65589d77a46a36536bf0b`
- GPI 1.0.0-rc SHA1: `5fa5c62d0698d076052be59b07ec9cf4c434a50c`
- TOPPEv2 SHA1: `6fe3277fe84d76f2b1816d804fb1cf39c2eb2e86`
- Libraries: **Numpy 1.13.3**, **Matplotlib 2.0.2**, **h5py 2.7.1**


---
## TABLE OF CONTENTS
1. Setting up
    1. Note
    2. Installing *pulseq-gpi*
    3. Installing GPI (optional)
    4. Installing pre-requisite libraries (optional)
2. Getting startedP∏
3. Developing for *pulseq-gpi*
    1. Node documentation
    2. Contributing
---
## 1. SETTNG UP
- The *pulseq-gpi* library contains code to either design pulse sequences in GPI or program pulse sequences in Python
- To program pulse sequences in Python, step 2 of this section can be skipped but step 4 is required
- To design pulse sequences in GPI, step 4 of this section can be skipped

### 1. Note
- If not already familiar with *Pulseq*, it is strongly recommended to learn the design spec. The [whitepaper](https://www.ncbi.nlm.nih.gov/pubmed/27271292) and the [official website](http://pulseq.github.io/) are the best resources to get started
- Similarly, if not already familiar with GPI, it is strongly recommended to go through the official [documentation](http://docs.gpilab.com/en/develop/intro.html)

### 2. Installing the *pulseq-gpi* library
This section lists instructions to install *pulseq-gpi*.

1. Clone the [repo](https://github.com/sravan953/pulseq-gpi) by downloading the zip file and extracting it:
![Clone the repo](readme_files/clone.png?raw=true "Clone the repo")

2. Open GPI

3. Click on *Config* > *Generate User Library*. This generates a *gpi* folder in the current user's home directory

4. Place the *mr_gpi* and *mr_nodes* folders from the extracted *pulseq-gpi* folder inside this auto-generated folder. On Mac - */Users/[user-name]/gpi/[user-name]/*

5. In GPI Lab, click on *Config* > *Scan for new nodes*

That's it! Now, the *pulseq-gpi Nodes* should show up when you right-click anywhere on the canvas.

### 3. Installing GPI (optional)
This section lists instructions to install the GPI software.

1. Download v1 beta from - http://gpilab.com/downloads/
2. Install:
![Install GPI](readme_files/install_gpi.png?raw=true "Install GPI")

### 4. Installing prerequisite libraries (optional)
To program pulse sequences in Python, *pulseq-gpi* requires the following libraries:
- [numpy](http://www.numpy.org/)
- [Matplotlib](https://matplotlib.org/)
- [hdf5](http://www.h5py.org/)

The official websites have resources on installing the respective libraries (usually, using *pip*). Listed below are instructions for installing the same libraries on PyCharm:

1. Open PyCharm

2. *Configure* > *Preferences*:
![Open Preferences](readme_files/pycharm_1.png?raw=true "Open Preferences")

3. Click *Project Intepreter* in the left pane

4. Click the *+* to add new libraries:
![Click +](readme_files/pycharm_2.png?raw=true "Click +")

5. Search for the prerequisite libraries and install
---
## 2. GETTING STARTED
This section lists instructions to get started. There are two ways to design pulse sequences using the *pulseq-gpi* library. Sequences can either be programmed in Python or designed using GPI *Nodes*. Programming pulse sequences in Python allows for more flexibility in design, while designing sequences using *Nodes* in GPI trades flexibility for ease of use.

### Example networks and scripts
The *pulseq-gpi* library comes bundled with example GPI networks and Python scripts for the following pulse sequences: Gradient Recalled Echo, Spin Echo and Spin Echo-EPI.

- The GPI networks and Python scripts are runnable out-of-the-box, configured to display plots for a single TR
- The Python scripts are not executable without the prerequisite libraries installed.

To run a GPI network, simply drag and drop the network onto the GPI canvas. Then, open the `ConfigSeq` *Node* by right-clicking and click on *Compute Events*. Finally, open the `GenSeq` *Node* by right-clicking and click on *Compute Events* to construct the pulse sequence. The plots are viewable in the `Matplotlib` *Node*.

#### Writing code
While *pulseq-gpi* is a translation of the original *Pulseq* specification for Matlab, the code has been modified to suit the Pythonic style of programming. This includes slightly modifying method and variable names. The code documentation contains all the details.

#### Using GPI
1. Open GPI
2. Right click anywhere on the canvas > *Load network* > */path/to/pulseq-gpi/Networks/* > select any network
3. Configure the pulse sequence values by right clicking the `ConfigSeq` and `AddBlock` *Nodes*. Each `Event` mandatorily needs a unique name. Each *Node* also mandatorily needs a unique name
5. From left to right, click `Compute Events` in each *Node*
6. Right click the `GenSeq` *Node*. Here you will see a list of the *Nodes* you have defined in your canvas. Enter the unique *Node* names in the order in which you want the `Events` to be played out. *Node* names are separated by a comma (,)
7. Click on `ComputeEvents` once you are done. Make sure the `GenSeq` *Node's* output connectors are linked to the input connectors of the `Matplotlib` *Node*
6. Right click on the `Matplotlib` *Node* to view plots
---
## 3. DEVELOPING FOR *pulseq-gpi*
Fork & PR if the code can be improved in any way!

### *Node* documentation
Every *Node* has documentation text included in the code. The documentation lists the parameters handled and the values returned by the *Node*, along with a brief description of the functioning.

The folder structure of the project is as follows (.py files are not listed):

**pulseq-gpi:**
- `mr_gpi`: Contains code that is a direct translation of the *Pulseq* specification for Matlab
- - `pulseq2jemris`: Not included in the original *Pulseq* design. Contains code that lets *pulseq-gpi* play nicely with *[Jemris](http://www.jemris.org/)*
- - `Sequence`: Included in the original *Pulseq* design
- `mr_nodes`: Custom *Nodes* that leverage `mr_gpi` methods a provide a graphical interface in GPI
- **Networks**: Contains example network files for the following pulse sequences: Gradient Recalled Echo, Spin Echo and Spin Echo-EPI
- **Scripts**: Contains sample scripts to design: Gradient Recalled Echo, Spin Echo and Spin Echo-EPI
- **LICENSE**
- **README**: This file

If there is any *Node* that is missing or having incomplete documentation, raise an issue on this repo.
