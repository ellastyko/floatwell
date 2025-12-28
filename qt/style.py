class StyleManager:
    _styles = {
        "QTabBar": """
            /* Ваши текущие стили для QTabBar */
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5A5A5A, stop:1 #3A3A3A);
                color: white;
                padding: 6px 12px;
                border: 1px solid #444;
                border-bottom: none;
                border-radius: 4px 4px 0 0;
                margin-right: 4px;
            }
            
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,stop:0 #6A6A6A, stop:1 #4A4A4A);
                border-bottom: 1px solid #6A6A6A;
            }
            
            QTabBar::tab:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #707070, stop:1 #505050);
            }
        """,
        
        "QPushButton": """
            /* Адаптированные стили для обычных кнопок */
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5A5A5A, stop:1 #3A3A3A);
                color: white;
                padding: 6px 12px;
                border: 1px solid #444;
                border-radius: 4px;
                margin: 2px;
            }
            
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4A4A4A, stop:1 #2A2A2A);
                padding: 6px 12px 5px 13px; /* Эффект нажатия */
            }
            
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #707070, stop:1 #505050);
            }
            
            QPushButton:disabled {
                background: #3A3A3A;
                color: #777;
                border: 1px solid #333;
            }
            
            QPushButton:checked {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6A6A6A, stop:1 #4A4A4A);
                border: 1px solid #555;
            }
        """,
        "QComboBox": """
            /* Основной стиль ComboBox */
            QComboBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5A5A5A, stop:1 #3A3A3A);
                color: white;
                padding: 6px 12px 6px 8px;
                border: 1px solid #444;
                border-radius: 4px;
                min-width: 100px;
                selection-background-color: #505050;
            }
            
            /* Стиль выпадающего списка */
            QComboBox QAbstractItemView {
                background: #3A3A3A;
                color: white;
                border: 1px solid #444;
                selection-background-color: #505050;
                outline: none;
            }
            
            /* Стрелка выпадающего списка */
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #444;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            
            QComboBox::down-arrow {
                image: url(:/icons/down_arrow.png);
                width: 10px;
                height: 10px;
            }
            
            /* Состояния */
            QComboBox:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #707070, stop:1 #505050);
            }
            
            QComboBox:on { /* когда открыт список */
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6A6A6A, stop:1 #4A4A4A);
            }
            
            QComboBox:disabled {
                background: #3A3A3A;
                color: #777;
                border: 1px solid #333;
            }
            
            /* Стиль для компоновки с Label слева */
            QComboBox.with-label {
                padding-left: 5px;
                border-top-left-radius: 0;
                border-bottom-left-radius: 0;
                margin-left: 0;
            }
        """,
        
        "ComboLabel": """
            /* Стиль для Label рядом с ComboBox */
            QLabel.combo-label {
                color: white;
                padding: 6px 8px 6px 12px;
                border-right: none;
                border-radius: 4px 0 0 4px;
                margin-right: 0;
            }
        """,

        "QDockWidget": """
            QDockWidget {
                background-color: #212327;
                color: #f8faff;
                titlebar-close-icon: url(none.png);
                titlebar-normal-icon: url(none.png);
            }
        """,

        "QToolBox": """
            QToolBox {
                background-color: #212327;
            }
            QToolBox::tab {
                background: #505055;
                color: #f8faff;
                border: 1px solid #606065;
                border-radius: 3px;
                margin-top: 2px;
            }
            QToolBox::tab:selected {
            }
        """,

        "QTable": """
                /* ===== TABLE ===== */
                QTableWidget {
                    background-color: #1e1e1e;
                    color: #d4d4d4;
                    border: 1px solid #2a2a2a;
                    gridline-color: #2a2a2a;
                    selection-background-color: #264f78; /* fallback */
                    selection-color: #ffffff;
                }

                QTableWidget::item {
                    padding: 6px;
                    border: none;
                }

                QTableWidget::item:selected {
                    background-color: #264f78;
                    color: #ffffff;
                }

                QTableWidget::item:hover {
                    background-color: #2a2d2e;
                }

                /* ===== HEADER ===== */
                QHeaderView::section {
                    background-color: #252526;
                    color: #d4d4d4;
                    padding: 6px;
                    font-weight: 600;
                    border: none;
                    border-right: 1px solid #2a2a2a;
                    border-bottom: 1px solid #2a2a2a;
                }

                QHeaderView::section:hover {
                    background-color: #2d2d2d;
                }

                /* ===== CORNER BUTTON ===== */
                QTableCornerButton::section {
                    background-color: #252526;
                    border: none;
                    border-right: 1px solid #2a2a2a;
                    border-bottom: 1px solid #2a2a2a;
                }

                /* ===== SCROLLBAR (optional, but fits theme) ===== */
                QScrollBar:vertical {
                    background: #1e1e1e;
                    width: 10px;
                    margin: 0;
                }

                QScrollBar::handle:vertical {
                    background: #3a3a3a;
                    min-height: 20px;
                    border-radius: 4px;
                }

                QScrollBar::handle:vertical:hover {
                    background: #4a4a4a;
                }

                QScrollBar::add-line:vertical,
                QScrollBar::sub-line:vertical {
                    height: 0;
                }

                QScrollBar::add-page:vertical,
                QScrollBar::sub-page:vertical {
                    background: none;
                }
        """,
        "QLogWidget": """
            LogWidget {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #444;
                selection-background-color: #264f78;
            }

            QScrollBar:vertical {
                    background: #1e1e1e;
                    width: 10px;
                    margin: 0;
            }

            QScrollBar::handle:vertical {
                background: #3a3a3a;
                min-height: 20px;
                border-radius: 4px;
            }

            QScrollBar::handle:vertical:hover {
                background: #4a4a4a;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }
        """,
        "QMenu": """
            QMenu {
                background-color: #2B2B2B;
                color: #EEE;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 6px 0;
            }

            QMenu::item {
                padding: 6px 28px 6px 24px;
                margin: 0;
            }

            QMenu::item:selected {
                background-color: #505050;
            }

            QMenu::item:disabled {
                color: #777;
            }

            QMenu::separator {
                height: 1px;
                background: #444;
                margin: 6px 0;
            }
        """
    }
    
    @classmethod
    def get_style(cls, style_name):
        return cls._styles.get(style_name, "")