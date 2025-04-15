from PyQt5.QtWidgets import QWidget
from PyQt5 import uic
import cv2
from PyQt5 import QtWidgets, QtGui, QtCore
import numpy as np
#this file should make the elements in the "pickup_tabWidget" functional

import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget, QSlider, QLineEdit, QHBoxLayout, QPushButton, QRadioButton, QMessageBox, QFileDialog, QTabWidget, QLabel, QComboBox, QCheckBox,QSizePolicy
from PyQt5 import uic, QtWidgets
import serial.tools.list_ports
import time
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPainter, QBrush, QPen
from PyQt5 import QtTest

import argparse
import json
import os
import time
import cv2
import numpy as np
# start by importing the necessary packages
import matplotlib.pyplot as plt
import json
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QPixmap, QImage
import pyautogui


class PickupTab(QWidget):
    def __init__(self, image_frame_manager, settings_tab):
        super().__init__()
        uic.loadUi("pickup_tab.ui", self)
        self.image_frame_manager = image_frame_manager
        self.settings_tab=settings_tab
        self.binary_mask = None
        self.binary_mask_image = None #once the segment btn is pressed this will be generated

        self.settings_tab.get_temperature() # this will use the device initialized in the settings tab
        #note: you can put "if self.settings_tab.temperature_controller:" do avoid crashing if the user forgets to initialize the device
        #self.settings_tab.set_temperature(-10)

        #self.pick_btn = self.findChild(QPushButton, "select_target_pick_btn")
        #why do I need to this and rename my button? I can just use clicked ethod on it directly, right?

        self.select_target_pick_btn.clicked.connect(self.segment_target)
        #self.start_pickup_btn.clicked.connect(self.start_pickup_sequence)

    def show_pixmap(self,image):
                # Convert to QImage and show in QLabel
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_img = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)

        # Optional: scale it to fit the QLabel
        pixmap = pixmap.scaled(self.image_pick.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_pick.setPixmap(pixmap)
        self.image_pick.show()

    def segment_target(self):
        start = time.time()
        segmented_image, binary_mask=self.image_frame_manager.run_sam()
        self.segmentation_overlay = segmented_image
        self.binary_mask = binary_mask
        self.binary_mask_image = cv2.cvtColor(binary_mask, cv2.COLOR_GRAY2RGB)
        self.show_pixmap(self.binary_mask_image)
        end = time.time()
        length = end - start
        print("It took", length, "seconds!")
        return


    def get_avg_color(self, image, mask):
        masked_pixels = image[mask > 0]
        blurred = cv2.blur(masked_pixels.astype(np.float32), (1, 1))
        return np.mean(blurred, axis=0)

    def is_color_changed(self, color_a, color_b, threshold=20.0):
        return np.linalg.norm(np.array(color_a) - np.array(color_b)) > threshold

    def get_edge_and_corner_regions(self, image, edge_width=20, corner_depth=30):
        h, w, _ = image.shape
        regions = []

        regions.append(image[0:edge_width, :, :])         # Top
        regions.append(image[-edge_width:, :, :])         # Bottom
        regions.append(image[:, 0:edge_width, :])         # Left
        regions.append(image[:, -edge_width:, :])         # Right

        mask = np.tri(corner_depth, corner_depth, dtype=bool)
        tri = image[0:corner_depth, 0:corner_depth, :]
        regions.append(tri[mask])

        mask = np.fliplr(np.tri(corner_depth, corner_depth, dtype=bool))
        tri = image[0:corner_depth, -corner_depth:, :]
        regions.append(tri[mask])

        tri = image[-corner_depth:, 0:corner_depth, :]
        regions.append(np.flipud(tri)[mask])

        mask = np.tri(corner_depth, corner_depth, dtype=bool)
        tri = image[-corner_depth:, -corner_depth:, :]
        regions.append(np.flipud(tri)[mask])

        all_pixels = np.concatenate(regions, axis=0)
        return all_pixels

    # def start_pickup_sequence(self):
    #     print("🚀 Starting pickup sequence...")

    #     speed1, speed2, speed3 = -2, -0.5, -0.1
    #     speed4, speed5, speed6 = 2, 0.5, 0.1
    #     distance1, distance2 = 300,400 
    #     temperature1, temperature2 = 130, 10
    #     threshold = 20.0

    #     image = self.image_frame_manager.get_screenshot()
    #     color1 = self.get_avg_color(image, self.binary_mask)
    #     print(f"🎯 color1 saved: {color1}")

    #     print(f"⬇️ Moving down to {distance1} with speed {speed1}")
    #     self.settings_tab_instance.move_z(speed1)
    #     time.sleep(1)

    #     print(f"👁 Monitoring edges/corners (width=50, corner=80)...")
    #     baseline_pixels = self.get_edge_and_corner_regions(image)
    #     baseline_color = np.mean(baseline_pixels, axis=0)

    #     while True:
    #         current_image = self.get_image_from_frame()
    #         edge_pixels = self.get_edge_and_corner_regions(current_image)
    #         current_color = np.mean(edge_pixels, axis=0)

    #         if self.is_color_changed(baseline_color, current_color, threshold=threshold):
    #             print("🔄 Detected edge/corner color change!")
    #             break
    #         self.settings_tab_instance.move_z(speed2)
    #         time.sleep(0.5)

    #     print(f"⬇️ Slowing down to {speed3}, watching segment region...")
    #     while True:
    #         image = self.get_image_from_frame()
    #         color_now = self.get_avg_color(image, mask)
    #         if self.is_color_changed(color1, color_now, threshold=threshold):
    #             color2 = color_now
    #             print(f"🎨 color2 saved: {color2}")
    #             break
    #         self.settings_tab_instance.move_z(speed3)
    #         time.sleep(0.5)

    #     self.settings_tab_instance.set_temperature(temperature1)
    #     while self.settings_tab_instance.get_temperature() < temperature1:
    #         time.sleep(0.5)
    #     print("⏱ Holding temperature for 3 minutes...")
    #     time.sleep(3 * 60)

    #     self.settings_tab_instance.set_temperature(temperature2)
    #     while self.settings_tab_instance.get_temperature() < temperature2:
    #         time.sleep(0.5)

    #     print(f"⬆️ Moving up with speed {speed4}, watching segment...")
    #     color3 = None
    #     while True:
    #         image = self.get_image_from_frame()
    #         color_now = self.get_avg_color(image, mask)
    #         if self.is_color_changed(color2, color_now, threshold=threshold):
    #             color3 = color_now
    #             print(f"🎨 color3 saved: {color3}")
    #             break
    #         self.settings_tab_instance.move_z(speed4)
    #         time.sleep(0.5)

    #     print(f"⬆️ Speed {speed5}, watching full frame for change...")
    #     while True:
    #         image = self.get_image_from_frame()
    #         avg_now = np.mean(image, axis=(0, 1))
    #         if self.is_color_changed(color3, avg_now, threshold=threshold):
    #             print("🌈 Full frame color changed.")
    #             break
    #         self.settings_tab_instance.move_z(speed5)
    #         time.sleep(0.5)

    #     print(f"🔼 Final lift to {distance2} with speed {speed6}...")
    #     self.settings_tab_instance.move_z(speed6)
    #     time.sleep(1)

    #     if not self.is_color_changed(color1, color3, threshold=threshold):
    #         print("❌ Pickup failed (color1 ≈ color3)")
    #     else:
    #         print("✅ Pickup successful!")
