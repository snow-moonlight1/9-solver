# widgets.py
from PyQt6.QtWidgets import QAbstractButton
from PyQt6.QtCore import (Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, 
                          QSize, QRectF, QVariant, pyqtProperty) # <--- Use pyqtProperty directly
from PyQt6.QtGui import QPainter, QBrush, QColor, QPaintEvent, QMouseEvent, QPen, QPainterPath

class CustomSwitch(QAbstractButton):

    # NOTIFY signal for the Qt property
    sliderOffsetAnimChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)

        self._height = 22 
        self._slider_diameter = self._height - 4
        self._track_radius = self._height / 2
        self._track_width = self._height * 1.8

        self._bg_color_off = QColor("#bdc3c7") 
        self._bg_color_on = QColor("#a4c7f4")  
        self._slider_color_off = QColor("#ffffff") 
        self._slider_color_on = QColor("#4a90e2")  

        self._internal_slider_offset = 1.0 if self.isChecked() else 0.0

        # QPropertyAnimation targets the Qt property "sliderOffsetAnim"
        self.animation = QPropertyAnimation(self, b"sliderOffsetAnim") 
        self.animation.setDuration(300) 
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self.toggled.connect(self._trigger_animation_on_toggle)

    # --- Getter for the Qt property ---
    def _read_slider_offset_anim(self):
        # print(f"READ sliderOffsetAnim: {self._internal_slider_offset}")
        return self._internal_slider_offset

    # --- Setter for the Qt property ---
    def _write_slider_offset_anim(self, value: float): # Explicitly type hint value
        # print(f"WRITE sliderOffsetAnim: {value}")
        if abs(self._internal_slider_offset - value) > 0.001: 
            self._internal_slider_offset = value
            self.update() # Schedule repaint
            self.sliderOffsetAnimChanged.emit() # Emit notify signal

    # --- Declare sliderOffsetAnim as a Qt property ---
    # The type is float, getter is _read_slider_offset_anim, 
    # setter is _write_slider_offset_anim, and notify signal is sliderOffsetAnimChanged.
    sliderOffsetAnim = pyqtProperty(float, 
                                   fget=_read_slider_offset_anim, 
                                   fset=_write_slider_offset_anim, 
                                   notify=sliderOffsetAnimChanged)

    def _trigger_animation_on_toggle(self, checked: bool): # Explicitly type hint checked
        print(f"--- _trigger_animation_on_toggle ---")
        print(f"  Signal 'toggled' received with new checked state: {checked}")
        print(f"  Current isChecked() before animation setup: {self.isChecked()}")
        
        self.animation.stop() 
        
        # Access the Qt property to get its current value for the animation start
        start_offset = self.sliderOffsetAnim  
        end_offset = 1.0 if checked else 0.0      

        print(f"  Calculated animation start_offset (current visual): {start_offset}")
        print(f"  Calculated animation end_offset (target visual): {end_offset}")

        if abs(start_offset - end_offset) < 0.01: 
            if abs(self._internal_slider_offset - end_offset) > 0.001 : # Check internal state too
                 self.sliderOffsetAnim = end_offset # Use property to set, ensuring notify if changed
            print(f"  Animation SKIPPED: Slider already visually at target for checked={checked}. Offset: {self._internal_slider_offset}")
            return

        self.animation.setStartValue(start_offset) 
        self.animation.setEndValue(end_offset)   
        
        print(f"  Starting animation for property: '{self.animation.propertyName().data().decode()}' from {start_offset} to {end_offset}")
        self.animation.start()
        print(f"  Animation state after start(): {self.animation.state()}")

    def setChecked(self, checked: bool): # Explicitly type hint checked
        was_checked = self.isChecked()
        # print(f"setChecked({checked}) called. was_checked: {was_checked}, current offset: {self._internal_slider_offset}")
        super().setChecked(checked)

        if was_checked == checked: # If state didn't change (e.g. setChecked(True) when already True)
            target_offset = 1.0 if checked else 0.0
            # Ensure visual consistency if animation is not running
            if abs(self._internal_slider_offset - target_offset) > 0.01: 
                if not (hasattr(self, 'animation') and self.animation.state() == QPropertyAnimation.State.Running):
                    # print(f"  setChecked: State unchanged ({checked}), but visuals mismatch. Correcting offset to {target_offset}.")
                    self.sliderOffsetAnim = target_offset # Use property setter
        # If state *did* change, toggled() -> _trigger_animation_on_toggle will handle animation.

    def paintEvent(self, event: QPaintEvent):
        # print(f"Paint event, _internal_slider_offset: {self._internal_slider_offset}")
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen) 

        track_rect = QRectF(0, 0, self._track_width, self._height)
        
        current_bg_color = QColor()
        r_off, g_off, b_off, _ = self._bg_color_off.getRgbF() 
        r_on, g_on, b_on, _ = self._bg_color_on.getRgbF()
        
        interp_r = r_off + (r_on - r_off) * self._internal_slider_offset 
        interp_g = g_off + (g_on - g_off) * self._internal_slider_offset
        interp_b = b_off + (b_on - b_off) * self._internal_slider_offset
        current_bg_color.setRgbF(interp_r, interp_g, interp_b)

        painter.setBrush(QBrush(current_bg_color))
        painter.drawRoundedRect(track_rect, self._track_radius, self._track_radius)

        slider_y_pos = (self._height - self._slider_diameter) / 2
        slider_min_x = 2  
        slider_max_x = self._track_width - self._slider_diameter - 2 

        current_slider_x_pos = slider_min_x + (slider_max_x - slider_min_x) * self._internal_slider_offset 
        slider_rect = QRectF(current_slider_x_pos, slider_y_pos, self._slider_diameter, self._slider_diameter)

        current_slider_color = QColor()
        sr_off, sg_off, sb_off, _ = self._slider_color_off.getRgbF()
        sr_on, sg_on, sb_on, _ = self._slider_color_on.getRgbF()

        interp_sr = sr_off + (sr_on - sr_off) * self._internal_slider_offset 
        interp_sg = sg_off + (sg_on - sg_off) * self._internal_slider_offset
        interp_sb = sb_off + (sb_on - sb_off) * self._internal_slider_offset
        current_slider_color.setRgbF(interp_sr, interp_sg, interp_sb)
        
        shadow_offset_val = 1 
        shadow_color_val = QColor(0, 0, 0, 40) 
        simulated_shadow_rect = QRectF(slider_rect)
        simulated_shadow_rect.translate(shadow_offset_val, shadow_offset_val)
        painter.setBrush(QBrush(shadow_color_val))
        painter.drawEllipse(simulated_shadow_rect) 

        painter.setBrush(QBrush(current_slider_color)) 
        painter.drawEllipse(slider_rect)

    def sizeHint(self):
        return QSize(int(self._track_width), self._height)

    def minimumSizeHint(self):
        return self.sizeHint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            # Let QAbstractButton handle toggling and emitting 'toggled'
            super().mouseReleaseEvent(event) 
        else:
            super().mouseReleaseEvent(event)
