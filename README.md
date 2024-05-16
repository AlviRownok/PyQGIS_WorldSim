# Python-for-QGIS-3.36.2

Welcome to the Python-for-QGIS-3.36.2 repository! This repository is dedicated to providing a step-by-step guide and code for setting up a custom Python environment that leverages the programmatic capabilities of QGIS 3.36.2 on a local system.

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.10 or newer. I am using Python 3.12.3 64-bit
- QGIS 3.36.2 (install in a specific new directory of your choice so that you can acccess the installed folder for paths that will be required .env and settings.json.
- pip (Python package installer)

This guide assumes you have basic knowledge of Python programming and familiarity with geographic information systems (GIS).

## Installation

To set up your environment to use QGIS 3.36.2 with Python, follow these steps:

1. **Install QGIS**: Make sure QGIS 3.36.2 is installed on your system. You can download it from the [https://qgis.org](https://www.qgis.org/en/site/).

2. **Clone the Repository**:
   ```bash
   git clone https://github.com/AlviRownok/Python-for-QGIS-3.36.2.git
   cd Python-for-QGIS-3.36.2

3. **Setting up Environment**
   - Open the .env file using your preferred IDE. I recommend Visual Studio. And you will see the following locations.
     
## Configuration

To properly set up your local environment for using Python with QGIS 3.36.2, you need to configure some environment variables. Here are the necessary settings:

```plaintext
PYTHONHOME=C:\Users\alvirownok\pyQGIS\apps\Python312
PYTHONPATH=C:\Users\alvirownok\pyQGIS\apps\qgis\python;C:\Users\alvirownok\pyQGIS\apps\qgis\python\plugins;C:\Users\alvirownok\pyQGIS\apps\Python312\Lib\site-packages;C:\Users\alvirownok\pyQGIS\apps\Qt5\plugins;C:\Users\alvirownok\pyQGIS\apps\gdal\share\gdal;C:\Users\alvirownok\pyQGIS\apps\Qt5\bin
PATH=%PATH%;C:\Users\alvirownok\pyQGIS\apps\Qt5\bin;C:\Users\alvirownok\pyQGIS\apps\Python312\Scripts;C:\Users\alvirownok\pyQGIS\bin
```

   - Update these paths with the actual paths that you have in your system inside the folder in which you have installed QGIS 3.36.2.

4. **Setting up Workspace**
   - Open the settings.json file using Visual Studio.

## Configuring Visual Studio Code Workspace

For those using Visual Studio Code (VS Code) as their IDE, you can optimize your setup for working with Python and QGIS by configuring the following settings. Add these settings to your `settings.json` file in VS Code:

```json
{
    "workbench.colorTheme": "Default Light Modern",
    "git.autofetch": true,
    "workbench.colorCustomizations": {},
    "python.defaultInterpreterPath": "C:\\Users\\alvirownok\\pyQGIS\\apps\\Python312\\python.exe",
    "terminal.integrated.env.windows": {
        "PYTHONHOME": "C:\\Users\\alvirownok\\pyQGIS\\apps\\Python312",
        "PYTHONPATH": "C:\\Users\\alvirownok\\pyQGIS\\apps\\qgis\\python;C:\\Users\\alvirownok\\pyQGIS\\apps\\qgis\\python\\plugins;C:\\Users\\alvirownok\\pyQGIS\\apps\\Python312\\Lib\\site-packages;C:\\Users\\alvirownok\\pyQGIS\\apps\\Qt5\\plugins;C:\\Users\\alvirownok\\pyQGIS\\apps\\gdal\\share\\gdal;C:\\Users\\alvirownok\\pyQGIS\\apps\\Qt5\\bin",
        "PATH": "${env:PATH};C:\\Users\\alvirownok\\pyQGIS\\apps\\Qt5\\bin;C:\\Users\\alvirownok\\pyQGIS\\apps\\Python312\\Scripts;C:\\Users\\alvirownok\\pyQGIS\\bin"
    }    
}
```

- Update the paths with the actual paths that you have in your system inside the folder in which you have installed QGIS 3.36.2.

5. **Play with the main_qgis_md.py**
   - Now run the main program. Check if all the libraries in the script are detected by your python kernel in Visual Studio.

## Contributing
Contributions to this project are welcome! Please refer to `CONTRIBUTING.md` for more details on how to submit pull requests, report issues, or make suggestions for improvements.

## License
This project is licensed under the Apache License 2.0 - see the `LICENSE.md` file for details.

## Help
If you encounter any problems or have questions, feel free to open an issue on this repository or contact Alvi Rownok at alvi2241998@gmail.com.
