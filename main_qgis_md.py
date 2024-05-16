import pandas as pd
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from qgis.core import *
from qgis.gui import QgsMapCanvas, QgsVertexMarker, QgsMapToolEmitPoint

# Initialize the QGIS application
QgsApplication.setPrefixPath("C:/Users/alvirownok/pyQGIS/apps/qgis", True)
qgs = QgsApplication([], True)
qgs.initQgis()

# Create a QApplication instance
app = QApplication([])

# Main window setup
window = QMainWindow()
window.setWindowTitle('Madrid Map Viewer')
window.resize(800, 600)

# Central widget and layout
central_widget = QWidget()
window.setCentralWidget(central_widget)
layout = QVBoxLayout(central_widget)

# Create a QGIS map canvas and set properties
canvas = QgsMapCanvas()
canvas.setCanvasColor(Qt.white)
canvas.enableAntiAliasing(True)
canvas.setWheelFactor(2)

# Load the QGIS project file
project_path = "C:/Users/alvirownok/Downloads/QGIS for python/Madrid Spain gpkg files/Madrid_map.qgz"
project = QgsProject.instance()
project.read(project_path)
print("Project loaded successfully:", project.fileName())

# Load the additional GeoPackage layer
gpkg_path = "C:/Users/alvirownok/Downloads/QGIS for python/Madrid Spain gpkg files/Madrid_Boundary.gpkg"
gpkg_layer = QgsVectorLayer(gpkg_path, "Confini Bacoli", "ogr")
if not gpkg_layer.isValid():
    print("Failed to open GeoPackage file!")
else:
    print(f"Loaded GeoPackage layer: {gpkg_layer.name()}")
    project.addMapLayer(gpkg_layer)

    # Set a simple fill symbol with only an outline for the boundary
    symbol = QgsFillSymbol.createSimple({
        'color': 'rgba(0, 0, 0, 0)',  # Fully transparent fill
        'outline_color': 'blue',
        'outline_style': 'solid',
        'outline_width': '0.5'
    })
    gpkg_layer.setRenderer(QgsSingleSymbolRenderer(symbol))

# Set the project CRS
target_crs = QgsCoordinateReferenceSystem("EPSG:3857")
project.setCrs(target_crs)

# Transform only vector layers to EPSG:3857 if needed
transform_context = QgsProject.instance().transformContext()
for layer in project.mapLayers().values():
    if isinstance(layer, QgsVectorLayer) and layer.crs() != target_crs:
        with edit(layer):
            for feature in layer.getFeatures():
                geom = feature.geometry()
                geom.transform(QgsCoordinateTransform(layer.crs(), target_crs, transform_context))
                layer.changeGeometry(feature.id(), geom)

# Refresh the map canvas to the extents of all visible layers
all_layers = list(project.mapLayers().values())
extent = QgsRectangle()
extent.setMinimal()
for layer in all_layers:
    if layer.isValid():
        extent.combineExtentWith(layer.extent())

canvas.setExtent(extent)
canvas.setLayers(all_layers)

# Create an empty DataFrame to store points with columns for coordinates and boundary status
points_df = pd.DataFrame(columns=['X', 'Y', 'Within_Boundary'])

def add_point(point, button):
    global points_df  # Reference the global DataFrame
    pointXY = QgsPointXY(point.x(), point.y())
    within_boundary = False

    # Check containment within the GeoPackage layer
    for feature in gpkg_layer.getFeatures():
        if feature.geometry().contains(pointXY):
            within_boundary = True
            break

    # Create a new DataFrame for the current point
    new_point = pd.DataFrame({'X': [point.x()], 'Y': [point.y()], 'Within_Boundary': [within_boundary]})

    # Append the new point DataFrame to the existing DataFrame
    points_df = pd.concat([points_df, new_point], ignore_index=True)

    # Save the updated DataFrame to a CSV file
    points_df.to_csv('C:/Users/alvirownok/Downloads/QGIS for python/Madrid Spain gpkg files/clicked_points.csv', index=True)

    marker = QgsVertexMarker(canvas)
    marker.setColor(QColor(255, 0, 0))
    marker.setCenter(pointXY)
    marker.setIconType(QgsVertexMarker.ICON_BOX)
    marker.setIconSize(5)
    marker.setPenWidth(2)

# Set the map tool for clicking on the map
map_tool = QgsMapToolEmitPoint(canvas)
map_tool.canvasClicked.connect(add_point)
canvas.setMapTool(map_tool)

# Layout setup and show window
layout.addWidget(canvas)
window.show()

# Start the application loop
app.exec_()

# Clean up on close
qgs.exitQgis()
