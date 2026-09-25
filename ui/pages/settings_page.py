from __future__ import annotations
from pathlib import Path
from sqlalchemy import select
from core.config import BASE_DIR
from db.engine import SessionLocal
from models.settings import Settings
from PySide6.QtWidgets import QFileDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QCheckBox, QComboBox, QVBoxLayout, QWidget
from services.backup_service import backup_database, restore_database
class SettingsPage(QWidget):
    def __init__(self) -> None:
        super().__init__(); layout=QVBoxLayout(self); title=QLabel("Settings"); title.setObjectName("page_title"); layout.addWidget(title); form=QFormLayout(); self.business=QLineEdit(); self.owner=QLineEdit(); self.phone=QLineEdit(); self.email=QLineEdit(); self.address=QLineEdit(); self.vat_enabled=QCheckBox("VAT enabled"); self.vat_rate=QLineEdit(); self.theme=QComboBox(); self.theme.addItems(["light","dark","system"]); self.font_size=QComboBox(); self.font_size.addItems(["small","normal","large"])
        for label,widget in [("Business Name",self.business),("Owner Name",self.owner),("Phone",self.phone),("Email",self.email),("Address",self.address),("VAT Rate (%)",self.vat_rate),("Theme",self.theme),("Font Size",self.font_size)]: form.addRow(label,widget)
        form.addRow("Tax",self.vat_enabled); layout.addLayout(form); save=QPushButton("Save Settings"); save.clicked.connect(self.save); layout.addWidget(save); actions=QHBoxLayout(); b=QPushButton("Backup Database"); b.clicked.connect(self.backup); r=QPushButton("Restore Database"); r.clicked.connect(self.restore); actions.addWidget(b); actions.addWidget(r); layout.addLayout(actions); layout.addStretch(); self.load()
    def load(self):
        session=SessionLocal()
        try:
            settings=session.scalar(select(Settings).limit(1))
            if settings is None: settings=Settings(); session.add(settings); session.commit()
            self.business.setText(settings.business_name); self.owner.setText(settings.owner_name or ""); self.phone.setText(settings.phone or ""); self.email.setText(settings.email or ""); self.address.setText(settings.address or ""); self.vat_enabled.setChecked(settings.vat_enabled); self.vat_rate.setText(str(settings.vat_rate)); self.theme.setCurrentText(settings.theme); self.font_size.setCurrentText(settings.font_size)
        finally: session.close()
    def save(self):
        session=SessionLocal()
        try:
            s=session.scalar(select(Settings).limit(1)) or Settings(); session.add(s); s.business_name=self.business.text().strip() or "VEYRA Shop"; s.owner_name=self.owner.text().strip() or None; s.phone=self.phone.text().strip() or None; s.email=self.email.text().strip() or None; s.address=self.address.text().strip() or None; s.vat_enabled=self.vat_enabled.isChecked(); s.vat_rate=float(self.vat_rate.text() or 0); s.theme=self.theme.currentText(); s.font_size=self.font_size.currentText(); session.commit(); QMessageBox.information(self,"Settings","Settings saved.")
        except Exception as exc: session.rollback(); QMessageBox.critical(self,"Settings Error",str(exc))
        finally: session.close()
    def backup(self):
        try: QMessageBox.information(self,"Backup Created",str(backup_database()))
        except Exception as exc: QMessageBox.critical(self,"Backup Error",str(exc))
    def restore(self):
        path,_=QFileDialog.getOpenFileName(self,"Select Backup","", "SQLite Database (*.db *.sqlite)")
        if path:
            try: restore_database(path); QMessageBox.information(self,"Restore Complete","Restart VEYRA to reload the restored database.")
            except Exception as exc: QMessageBox.critical(self,"Restore Error",str(exc))
