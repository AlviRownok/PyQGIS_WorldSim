import sys  # Importing the sys module for system-specific parameters and functions
import os  # Importing the os module for operating system dependent functionality
import pandas as pd  # Importing pandas for data manipulation and analysis
from PyQt5.QtCore import Qt  # Importing Qt constants from PyQt5
from PyQt5.QtGui import QColor, QCursor  # Importing QColor and QCursor classes from PyQt5
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QPushButton, QLineEdit, QFormLayout, QColorDialog  # Importing various PyQt5 widgets
from qgis.core import *  # Importing all from QGIS core module
from qgis.gui import QgsMapCanvas, QgsVertexMarker, QgsMapToolEmitPoint, QgsMapTool  # Importing QGIS GUI components

# Class for handling map click events
class ClickTool(QgsMapToolEmitPoint):
    def __init__(self, canvas, callback):
        QgsMapToolEmitPoint.__init__(self, canvas)  # Initialize the base class
        self.canvas = canvas  # Set the canvas
        self.callback = callback  # Set the callback function

    def canvasPressEvent(self, e):
        point = self.toMapCoordinates(e.pos())  # Convert click position to map coordinates
        self.callback(point)  # Call the callback function with the point

    def activate(self):
        self.canvas.setCursor(QCursor(Qt.CrossCursor))  # Set cursor to cross when the tool is active

# Main window class for the application
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()  # Initialize the base class
        self.setWindowTitle('Map Viewer')  # Set the window title
        self.resize(1200, 600)  # Set the window size
        central_widget = QWidget()  # Create a central widget
        self.setCentralWidget(central_widget)  # Set the central widget
        self.layout = QHBoxLayout(central_widget)  # Create a horizontal layout for the central widget

        # Left side: input fields
        self.form_widget = QWidget()  # Create a widget for the form
        self.form_layout = QFormLayout(self.form_widget)  # Create a form layout for the form widget

        self.prefix_path_edit = QLineEdit()  # Create a QLineEdit for the prefix path
        self.project_path_edit = QLineEdit()  # Create a QLineEdit for the project path
        self.gpkg_paths = []  # List to store multiple GPKG paths
        self.gpkg_colors = []  # List to store colors for each GPKG path
        self.points_csv_path_edit = QLineEdit()  # Create a QLineEdit for the points CSV path
        self.window_title_edit = QLineEdit()  # Create a QLineEdit for the window title

        prefix_path_button = QPushButton('Browse')  # Create a button to browse for the prefix path
        prefix_path_button.clicked.connect(lambda: self.browse_directory(self.prefix_path_edit))  # Connect button click to browse_directory method

        project_path_button = QPushButton('Browse')  # Create a button to browse for the project path
        project_path_button.clicked.connect(lambda: self.browse_file(self.project_path_edit))  # Connect button click to browse_file method

        add_gpkg_button = QPushButton('Add GeoPackage')  # Create a button to add GeoPackage files
        add_gpkg_button.clicked.connect(self.browse_gpkg_files)  # Connect button click to browse_gpkg_files method

        points_csv_path_button = QPushButton('Browse')  # Create a button to browse for the points CSV path
        points_csv_path_button.clicked.connect(lambda: self.browse_file(self.points_csv_path_edit))  # Connect button click to browse_file method

        self.form_layout.addRow('QGIS Prefix Path:', self.prefix_path_edit)  # Add prefix path QLineEdit to the form layout
        self.form_layout.addRow('', prefix_path_button)  # Add prefix path browse button to the form layout
        self.form_layout.addRow('QGIS Project Path:', self.project_path_edit)  # Add project path QLineEdit to the form layout
        self.form_layout.addRow('', project_path_button)  # Add project path browse button to the form layout
        self.form_layout.addRow('GeoPackage Paths:', add_gpkg_button)  # Add add GeoPackage button to the form layout
        self.form_layout.addRow('CSV Input Path:', self.points_csv_path_edit)  # Add points CSV path QLineEdit to the form layout
        self.form_layout.addRow('', points_csv_path_button)  # Add points CSV path browse button to the form layout
        self.form_layout.addRow('Window Title:', self.window_title_edit)  # Add window title QLineEdit to the form layout

        set_paths_button = QPushButton('Set Paths and Start')  # Create a button to set paths and start the application
        set_paths_button.clicked.connect(self.set_paths)  # Connect button click to set_paths method
        self.form_layout.addRow('', set_paths_button)  # Add set paths button to the form layout

        self.layout.addWidget(self.form_widget)  # Add the form widget to the main layout

        # Right side: map canvas
        self.canvas = QgsMapCanvas()  # Create a map canvas
        self.canvas.setCanvasColor(Qt.white)  # Set the canvas color to white
        self.canvas.enableAntiAliasing(True)  # Enable anti-aliasing
        self.canvas.setWheelFactor(2)  # Set the wheel zoom factor

        self.canvas_widget = QWidget()  # Create a widget for the canvas
        self.canvas_layout = QVBoxLayout(self.canvas_widget)  # Create a vertical layout for the canvas widget
        self.canvas_layout.addWidget(self.canvas)  # Add the canvas to the canvas layout
        self.layout.addWidget(self.canvas_widget)  # Add the canvas widget to the main layout

        self.points_df = pd.DataFrame(columns=['X', 'Y', 'Within_Boundary'])  # Initialize a DataFrame to store points

    def browse_directory(self, line_edit):
        dir_path = QFileDialog.getExistingDirectory()  # Open a directory dialog
        if dir_path:
            line_edit.setText(dir_path)  # Set the selected directory path to the QLineEdit

    def browse_file(self, line_edit):
        file_path, _ = QFileDialog.getOpenFileName()  # Open a file dialog
        if file_path:
            line_edit.setText(file_path)  # Set the selected file path to the QLineEdit

    def browse_gpkg_files(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select GeoPackage File", "", "GeoPackage Files (*.gpkg)")  # Open a file dialog for GeoPackage files
        if file_path:
            color = QColorDialog.getColor()  # Open a color dialog
            if color.isValid():
                self.gpkg_paths.append(file_path)  # Add the selected file path to the list of GeoPackage paths
                self.gpkg_colors.append(color)  # Add the selected color to the list of GeoPackage colors
                self.form_layout.addRow(f'GeoPackage Path {len(self.gpkg_paths)}:', QLineEdit(file_path))  # Add the GeoPackage path QLineEdit to the form layout
                color_button = QPushButton('Color')  # Create a button to display the selected color
                color_button.setStyleSheet(f'background-color: {color.name()}')  # Set the button background color
                self.form_layout.addRow(f'Color {len(self.gpkg_paths)}:', color_button)  # Add the color button to the form layout

    def set_paths(self):
        prefix_path = self.prefix_path_edit.text()  # Get the prefix path from the QLineEdit
        project_path = self.project_path_edit.text()  # Get the project path from the QLineEdit
        points_csv_path = self.points_csv_path_edit.text()  # Get the points CSV path from the QLineEdit
        window_title = self.window_title_edit.text()  # Get the window title from the QLineEdit

        # Initialize the QGIS application
        QgsApplication.setPrefixPath(prefix_path, True)  # Set the QGIS prefix path
        self.qgs = QgsApplication([], True)  # Create a QGIS application
        self.qgs.initQgis()  # Initialize QGIS

        # Set the window title
        self.setWindowTitle(window_title)  # Set the window title

        # Load the QGIS project file
        self.project = QgsProject.instance()  # Get the QGIS project instance
        self.project.read(project_path)  # Read the project file
        print("Project loaded successfully:", self.project.fileName())  # Print a success message

        # Get the project's CRS
        project_crs = self.project.crs()  # Get the project's CRS

        # Load the GeoPackage layers in order
        self.gpkg_layers = []  # Initialize a list to store GeoPackage layers
        for i, gpkg_path in enumerate(self.gpkg_paths):
            if not os.path.exists(gpkg_path):
                print(f"GeoPackage file does not exist: {gpkg_path}")  # Print an error message if the file does not exist
                continue

            gpkg_layer = QgsVectorLayer(gpkg_path, f"GeoPackage Layer {len(self.gpkg_layers) + 1}", "ogr")  # Load the GeoPackage layer
            if not gpkg_layer.isValid():
                print(f"Failed to open GeoPackage file: {gpkg_path}")  # Print an error message if the layer is invalid
            else:
                print(f"Loaded GeoPackage layer: {gpkg_layer.name()}")  # Print a success message
                self.project.addMapLayer(gpkg_layer)  # Add the layer to the project
                self.gpkg_layers.append(gpkg_layer)  # Add the layer to the list of GeoPackage layers

                # Assign a unique color to each layer
                color = self.gpkg_colors[i]  # Get the color for the current layer
                symbol = QgsFillSymbol.createSimple({
                    'color': 'rgba(0, 0, 0, 0)',  # Fully transparent fill
                    'outline_color': color.name(),  # Set the outline color
                    'outline_style': 'solid',  # Set the outline style
                    'outline_width': '0.5'  # Set the outline width
                })
                gpkg_layer.setRenderer(QgsSingleSymbolRenderer(symbol))  # Set the renderer for the layer

                # Ensure the GeoPackage layer's CRS matches the project's CRS
                if gpkg_layer.crs() != project_crs:
                    original_crs = gpkg_layer.crs()  # Get the original CRS of the layer
                    transform = QgsCoordinateTransform(original_crs, project_crs, QgsProject.instance().transformContext())  # Create a coordinate transform
                    with edit(gpkg_layer):
                        for feature in gpkg_layer.getFeatures():
                            geom = feature.geometry()  # Get the geometry of the feature
                            geom.transform(transform)  # Transform the geometry
                            gpkg_layer.changeGeometry(feature.id(), geom)  # Update the feature geometry

        # Refresh the map canvas to the extents of all visible layers
        all_layers = list(self.project.mapLayers().values())  # Get all layers in the project
        extent = QgsRectangle()  # Create a new extent
        extent.setMinimal()  # Set the extent to minimal
        for layer in all_layers:
            if layer.isValid():
                extent.combineExtentWith(layer.extent())  # Combine the extent with the layer's extent

        self.canvas.setExtent(extent)  # Set the canvas extent
        self.canvas.setLayers(all_layers)  # Set the layers for the canvas

        # Read and plot points from CSV
        self.read_and_plot_points(points_csv_path)  # Read and plot points from the CSV file

        # Set the map tool for clicking on the map
        self.click_tool = ClickTool(self.canvas, self.add_point)  # Create a click tool
        self.canvas.setMapTool(self.click_tool)  # Set the map tool for the canvas
        print("Map tool set for clicking")  # Print a success message

    def read_and_plot_points(self, csv_path):
        try:
            points_df = pd.read_csv(csv_path)  # Read points from the CSV file
            for _, row in points_df.iterrows():
                pointXY = QgsPointXY(row['X'], row['Y'])  # Create a QgsPointXY from the CSV data
                marker = QgsVertexMarker(self.canvas)  # Create a vertex marker
                marker.setColor(QColor(255, 0, 0))  # Set the marker color to red
                marker.setCenter(pointXY)  # Set the marker position
                marker.setIconType(QgsVertexMarker.ICON_BOX)  # Set the marker icon type
                marker.setIconSize(5)  # Set the marker size
                marker.setPenWidth(2)  # Set the marker pen width
                print(f"Plotted point: {row['X']}, {row['Y']}, Within Boundary: {row['Within_Boundary']}")  # Print the plotted point details
        except Exception as e:
            print(f"Error reading CSV file: {e}")  # Print an error message if reading the CSV fails

    def add_point(self, point):
        print("Point clicked:", point)  # Print the clicked point
        pointXY = QgsPointXY(point.x(), point.y())  # Create a QgsPointXY from the clicked point
        within_boundary = False

        # Check containment within the GeoPackage layers
        for gpkg_layer in self.gpkg_layers:
            for feature in gpkg_layer.getFeatures():
                if feature.geometry().contains(pointXY):  # Check if the point is within the feature geometry
                    within_boundary = True
                    break

        # Create a new DataFrame for the current point
        new_point = pd.DataFrame({'X': [point.x()], 'Y': [point.y()], 'Within_Boundary': [within_boundary]})  # Create a DataFrame for the new point

        # Read the existing points from the CSV file
        try:
            existing_points_df = pd.read_csv(self.points_csv_path_edit.text())  # Read the existing points from the CSV file
        except FileNotFoundError:
            existing_points_df = pd.DataFrame(columns=['X', 'Y', 'Within_Boundary'])  # Create an empty DataFrame if the file does not exist

        # Append the new point DataFrame to the existing DataFrame
        updated_points_df = pd.concat([existing_points_df, new_point], ignore_index=True)  # Append the new point to the existing points

        # Save the updated DataFrame to a CSV file
        updated_points_df.to_csv(self.points_csv_path_edit.text(), index=False)  # Save the updated points to the CSV file
        print("Point added and saved:", new_point)  # Print a success message

        marker = QgsVertexMarker(self.canvas)  # Create a vertex marker
        marker.setColor(QColor(255, 0, 0))  # Set the marker color to red
        marker.setCenter(pointXY)  # Set the marker position
        marker.setIconType(QgsVertexMarker.ICON_BOX)  # Set the marker icon type
        marker.setIconSize(5)  # Set the marker size
        marker.setPenWidth(2)  # Set the marker pen width

    def closeEvent(self, event):
        self.qgs.exitQgis()  # Exit QGIS when the application is closed
        QApplication.quit()  # Ensure the PyQt application also exits
        event.accept()  # Accept the close event

if __name__ == '__main__':
    app = QApplication(sys.argv)  # Create a QApplication
    window = MainWindow()  # Create the main window
    window.show()  # Show the main window
    sys.exit(app.exec_())  # Execute the application
