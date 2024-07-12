import sys
import pandas as pd
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QCursor
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QPushButton, QLineEdit, QFormLayout
from qgis.core import *
from qgis.gui import QgsMapCanvas, QgsVertexMarker, QgsMapToolEmitPoint, QgsMapTool

class ClickTool(QgsMapToolEmitPoint):
    def __init__(self, canvas, callback):
        QgsMapToolEmitPoint.__init__(self, canvas)
        self.canvas = canvas
        self.callback = callback

    def canvasPressEvent(self, e):
        point = self.toMapCoordinates(e.pos())
        self.callback(point)

    def activate(self):
        self.canvas.setCursor(QCursor(Qt.CrossCursor))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Map Viewer')
        self.resize(1200, 600)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QHBoxLayout(central_widget)

        # Left side: input fields
        self.form_widget = QWidget()
        self.form_layout = QFormLayout(self.form_widget)

        self.prefix_path_edit = QLineEdit()
        self.project_path_edit = QLineEdit()
        self.gpkg_path_edit = QLineEdit()
        self.points_csv_path_edit = QLineEdit()
        self.window_title_edit = QLineEdit()

        prefix_path_button = QPushButton('Browse')
        prefix_path_button.clicked.connect(lambda: self.browse_directory(self.prefix_path_edit))

        project_path_button = QPushButton('Browse')
        project_path_button.clicked.connect(lambda: self.browse_file(self.project_path_edit))

        gpkg_path_button = QPushButton('Browse')
        gpkg_path_button.clicked.connect(lambda: self.browse_file(self.gpkg_path_edit))

        points_csv_path_button = QPushButton('Browse')
        points_csv_path_button.clicked.connect(lambda: self.browse_file(self.points_csv_path_edit))

        self.form_layout.addRow('QGIS Prefix Path:', self.prefix_path_edit)
        self.form_layout.addRow('', prefix_path_button)
        self.form_layout.addRow('QGIS Project Path:', self.project_path_edit)
        self.form_layout.addRow('', project_path_button)
        self.form_layout.addRow('GeoPackage Path:', self.gpkg_path_edit)
        self.form_layout.addRow('', gpkg_path_button)
        self.form_layout.addRow('CSV Output Path:', self.points_csv_path_edit)
        self.form_layout.addRow('', points_csv_path_button)
        self.form_layout.addRow('Window Title:', self.window_title_edit)

        set_paths_button = QPushButton('Set Paths and Start')
        set_paths_button.clicked.connect(self.set_paths)
        self.form_layout.addRow('', set_paths_button)

        self.layout.addWidget(self.form_widget)

        # Right side: map canvas
        self.canvas = QgsMapCanvas()
        self.canvas.setCanvasColor(Qt.white)
        self.canvas.enableAntiAliasing(True)
        self.canvas.setWheelFactor(2)

        self.canvas_widget = QWidget()
        self.canvas_layout = QVBoxLayout(self.canvas_widget)
        self.canvas_layout.addWidget(self.canvas)
        self.layout.addWidget(self.canvas_widget)

        self.points_df = pd.DataFrame(columns=['X', 'Y', 'Within_Boundary'])

    def browse_directory(self, line_edit):
        dir_path = QFileDialog.getExistingDirectory()
        if dir_path:
            line_edit.setText(dir_path)

    def browse_file(self, line_edit):
        file_path, _ = QFileDialog.getOpenFileName()
        if file_path:
            line_edit.setText(file_path)

    def set_paths(self):
        prefix_path = self.prefix_path_edit.text()
        project_path = self.project_path_edit.text()
        gpkg_path = self.gpkg_path_edit.text()
        points_csv_path = self.points_csv_path_edit.text()
        window_title = self.window_title_edit.text()

        # Initialize the QGIS application
        QgsApplication.setPrefixPath(prefix_path, True)
        self.qgs = QgsApplication([], True)
        self.qgs.initQgis()

        # Set the window title
        self.setWindowTitle(window_title)

        # Load the QGIS project file
        self.project = QgsProject.instance()
        self.project.read(project_path)
        print("Project loaded successfully:", self.project.fileName())

        # Set the project CRS
        target_crs = QgsCoordinateReferenceSystem("EPSG:3857")
        self.project.setCrs(target_crs)

        # Load the additional GeoPackage layer
        self.gpkg_layer = QgsVectorLayer(gpkg_path, "Confini Bacoli", "ogr")
        if not self.gpkg_layer.isValid():
            print("Failed to open GeoPackage file!")
        else:
            print(f"Loaded GeoPackage layer: {self.gpkg_layer.name()}")
            self.project.addMapLayer(self.gpkg_layer)

            # Set a simple fill symbol with only an outline for the boundary
            symbol = QgsFillSymbol.createSimple({
                'color': 'rgba(0, 0, 0, 0)',  # Fully transparent fill
                'outline_color': 'blue',
                'outline_style': 'solid',
                'outline_width': '0.5'
            })
            self.gpkg_layer.setRenderer(QgsSingleSymbolRenderer(symbol))

            # Ensure the GeoPackage layer's CRS matches the project's CRS
            if self.gpkg_layer.crs() != target_crs:
                original_crs = self.gpkg_layer.crs()
                transform = QgsCoordinateTransform(original_crs, target_crs, QgsProject.instance().transformContext())
                self.gpkg_layer.setCrs(target_crs)
                with edit(self.gpkg_layer):
                    for feature in self.gpkg_layer.getFeatures():
                        geom = feature.geometry()
                        geom.transform(transform)
                        self.gpkg_layer.changeGeometry(feature.id(), geom)

        # Transform only vector layers to EPSG:3857 if needed
        transform_context = QgsProject.instance().transformContext()
        for layer in self.project.mapLayers().values():
            if isinstance(layer, QgsVectorLayer) and layer.crs() != target_crs:
                original_crs = layer.crs()
                transform = QgsCoordinateTransform(original_crs, target_crs, transform_context)
                with edit(layer):
                    for feature in layer.getFeatures():
                        geom = feature.geometry()
                        geom.transform(transform)
                        layer.changeGeometry(feature.id(), geom)

        # Refresh the map canvas to the extents of all visible layers
        all_layers = list(self.project.mapLayers().values())
        extent = QgsRectangle()
        extent.setMinimal()
        for layer in all_layers:
            if layer.isValid():
                extent.combineExtentWith(layer.extent())

        self.canvas.setExtent(extent)
        self.canvas.setLayers(all_layers)

        # Set the map tool for clicking on the map
        self.click_tool = ClickTool(self.canvas, self.add_point)
        self.canvas.setMapTool(self.click_tool)
        print("Map tool set for clicking")

    def add_point(self, point):
        print("Point clicked:", point)
        pointXY = QgsPointXY(point.x(), point.y())
        within_boundary = False

        # Check containment within the GeoPackage layer
        for feature in self.gpkg_layer.getFeatures():
            if feature.geometry().contains(pointXY):
                within_boundary = True
                break

        # Create a new DataFrame for the current point
        new_point = pd.DataFrame({'X': [point.x()], 'Y': [point.y()], 'Within_Boundary': [within_boundary]})

        # Append the new point DataFrame to the existing DataFrame
        self.points_df = pd.concat([self.points_df, new_point], ignore_index=True)

        # Save the updated DataFrame to a CSV file
        self.points_df.to_csv(self.points_csv_path_edit.text(), index=True)
        print("Point added and saved:", new_point)

        marker = QgsVertexMarker(self.canvas)
        marker.setColor(QColor(255, 0, 0))
        marker.setCenter(pointXY)
        marker.setIconType(QgsVertexMarker.ICON_BOX)
        marker.setIconSize(5)
        marker.setPenWidth(2)

    def closeEvent(self, event):
        self.qgs.exitQgis()
        QApplication.quit()  # Ensure the PyQt application also exits
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
