from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from qgis.core import *
from qgis.gui import QgsMapCanvas

# Initialize the QGIS application
QgsApplication.setPrefixPath("C:/Users/alvirownok/pyQGIS/apps/qgis", True)
qgs = QgsApplication([], True)  # True to enable GUI
qgs.initQgis()

# Create a QApplication instance
app = QApplication([])

# Main window setup
window = QMainWindow()
window.setWindowTitle('PyQGIS Map Viewer')
window.resize(800, 600)

# Central widget and layout
central_widget = QWidget()
window.setCentralWidget(central_widget)
layout = QVBoxLayout(central_widget)

# Create a QGIS map canvas and set properties
canvas = QgsMapCanvas()
canvas.setCanvasColor(Qt.white)
canvas.enableAntiAliasing(True)
canvas.setExtent(QgsRectangle(-180, -90, 180, 90))
canvas.setWheelFactor(2)

# Load a GeoPackage layer
gpkg_path = "C:/Users/alvirownok/Downloads/QGIS for python/boundary_file.gpkg"
layer = QgsVectorLayer(gpkg_path, "boundary layer", "ogr")
if not layer.isValid():
    print("Failed to open GeoPackage file!")
else:
    print(f"Loaded layer: {layer.name()}")

# Add the layer to the map and refresh
QgsProject.instance().addMapLayer(layer)
canvas.setLayers([layer])

# Load a QGIS project
project_path = "C:/Users/alvirownok/Downloads/QGIS for python/exported map.qgz"
project = QgsProject.instance()
project.read(project_path)

# If the project has layers, set them on the canvas
if project.mapLayers():
    canvas.setLayers(list(project.mapLayers().values()))

layout.addWidget(canvas)  # Add the canvas to the layout

# Show the window
window.show()

# Start the application loop
app.exec_()

# When the application is closed, clean up
qgs.exitQgis()
