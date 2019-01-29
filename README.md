# Electroencephalogram-Project
This project is based around the construction and modifcation of an instructables DIY electroencephalogram aimed at providing communication via neural firing patterns using current AI strategies. The foundation of this project lies at https://www.instructables.com/id/DIY-EEG-and-ECG-Circuit/. Here you will find every aspect as to how to create the EEG yourself, and will help with understanding every aspect of the foundation of this project as well.

## Getting started
1. Download Processing 3 at https://processing.org/download/
2. Clone the repository in your command line and change your directory to the repository
```
git clone https://github.com/cwnicoletti/Electroencephalogram-Project/
cd Electroenceophalogram-Project
```
3. Open Processing
4. File > Open... > *EEG_main.pde*
### If attempting to open EEG_main_python.pyde
4. In the upper-right-hand corner of the Processing IDE window press "Java"
5. Click "Add Mode..."
6. Search in the Modes tab "python"
7. Install "Python Mode for Processing 3"
8. You may now go to File > Open... > *EEG_main_python_pde.pyde*

## Contributions
All contributions should be referenced to the [CONTRIBUTIONS](https://github.com/cwnicoletti/Electroencephalogram-Project/blob/master/CONTRIBUTING.md) file before making a pull request.

## Libraries used
* [Serial](https://processing.org/reference/libraries/serial/index.html)
* [Minim](http://code.compartmental.net/minim/)

## Known Bugs
Currently there is a bug with the python version of this code. The minim library seems to be requiring more than 1 parameter for its fft function calls, as opposed to the Java version, where it only requires 1. There seems to be little to no documentation on the python version of the minim library so its unknown as to what this second parameter requires (another reason why we are changing libraries and IDEs).

## Licensing
The content of this repository is licensed under the terms specified in the [LICENSE](https://github.com/cwnicoletti/Electroencephalogram-Project/blob/master/LICENSE) file.
