#   PASTA-ELN and all its sub-parts are covered by the MIT license.
#  #
#   Copyright (c) 2023
#  #
#   Author: Jithu Murugan
#   Filename: test_ontology_configuration_extended.py
#  #
#   You should have received a copy of the license with this file. Please refer the license file for more information.

from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QCheckBox
from pytestqt.qtbot import QtBot

from pasta_eln.GUI.ontology_configuration.lookup_iri_action import LookupIriAction
from pasta_eln.GUI.ontology_configuration.ontology_configuration_extended import OntologyConfigurationForm
from pasta_eln.GUI.ontology_configuration.utility_functions import adapt_type, get_types_for_display
from tests.app_tests.common.fixtures import attachments_column_names, ontology_doc_mock, ontology_editor_gui, \
  pasta_db_mock, props_column_names


class TestOntologyConfigurationExtended(object):

  def test_component_launch_should_display_all_ui_elements(self,
                                                           pasta_db_mock: pasta_db_mock,
                                                           # Added to import fixture by other tests
                                                           ontology_editor_gui: tuple[
                                                             QApplication,
                                                             QtWidgets.QDialog,
                                                             OntologyConfigurationForm,
                                                             QtBot]):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    assert ui_form.headerLabel is not None, "Header not loaded!"
    assert ui_form.typeLabel is not None, "Data type label not loaded!"
    assert ui_form.saveOntologyPushButton is not None, "Save button not loaded!"
    assert ui_form.helpPushButton is not None, "Help button not loaded!"
    assert ui_form.typePropsTableView is not None, "Properties table view not loaded!"
    assert ui_form.typeAttachmentsTableView is not None, "Type table view not loaded!"
    assert ui_form.addAttachmentPushButton is not None, "Add attachment button not loaded!"
    assert ui_form.addTypePushButton is not None, "Add type button not loaded!"
    assert ui_form.addPropsRowPushButton is not None, "Add property row button not loaded!"
    assert ui_form.addPropsCategoryPushButton is not None, "Add property category button not loaded!"
    assert ui_form.cancelPushButton is not None, "Cancel button not loaded!"
    assert ui_form.typeLabelLineEdit is not None, "Data type line edit not loaded!"
    assert ui_form.typeIriLineEdit is not None, "Data type IRI line edit not loaded!"
    assert ui_form.addPropsCategoryLineEdit is not None, "Property category line edit not loaded!"
    assert ui_form.typeComboBox is not None, "Data type combo box not loaded!"
    assert ui_form.propsCategoryComboBox is not None, "Property category combo box not loaded!"

  def test_component_launch_should_load_ontology_data(self,
                                                      ontology_editor_gui: tuple[
                                                        QApplication,
                                                        QtWidgets.QDialog,
                                                        OntologyConfigurationForm,
                                                        QtBot],
                                                      ontology_doc_mock: ontology_doc_mock,
                                                      props_column_names: props_column_names,
                                                      attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    assert ([ui_form.typeComboBox.itemText(i) for i in range(ui_form.typeComboBox.count())]
            == get_types_for_display(ontology_doc_mock.types_list())), "Type combo box not loaded!"
    assert (adapt_type(ui_form.typeComboBox.currentText())
            == ontology_doc_mock.types_list()[0]), "Type combo box should be selected to first item"
    selected_type = ontology_doc_mock.types()[adapt_type(ui_form.typeComboBox.currentText())]
    assert (ui_form.typeLabelLineEdit.text() ==
            selected_type["label"]), "Data type label line edit not loaded!"
    assert (ui_form.typeIriLineEdit.text() ==
            selected_type["IRI"]), "Data type IRI line edit not loaded!"

    categories = list(selected_type["prop"].keys())
    assert ([ui_form.propsCategoryComboBox.itemText(i) for i in range(ui_form.propsCategoryComboBox.count())]
            == categories), "propsCategoryComboBox combo box not loaded!"
    assert (ui_form.propsCategoryComboBox.currentText()
            == categories[0]), "propsCategoryComboBox should be selected to first item"
    self.check_table_contents(attachments_column_names, props_column_names, selected_type, ui_form)

  @staticmethod
  def check_table_view_model(model, column_names, data_selected):
    for row in range(model.rowCount()):
      data = data_selected[row]
      for column in range(model.columnCount() - 2):
        index = model.index(row, column)
        if column_names[column] in data:
          cell_data = data[column_names[column]]
          assert (model.data(index, Qt.DisplayRole)
                  == ','.join(cell_data) if isinstance(cell_data, list) else cell_data), \
            f"{column_names[column]} not loaded!"
        else:
          assert model.data(index, Qt.DisplayRole) is None, f"{column_names[column]} should be None!"

  def check_table_contents(self, attachments_column_names, props_column_names, selected_type, ui_form):
    categories = list(selected_type["prop"].keys())
    # Assert if the properties are loaded in the table view
    model = ui_form.typePropsTableView.model()
    self.check_table_view_model(model, props_column_names, selected_type["prop"][categories[0]])
    # Assert if the attachments are loaded in the table view
    model = ui_form.typeAttachmentsTableView.model()
    self.check_table_view_model(model, attachments_column_names, selected_type["attachments"])

  def test_component_add_new_type_with_loaded_ontology_should_display_create_new_type_window(self,
                                                                                             ontology_editor_gui: tuple[
                                                                                               QApplication,
                                                                                               QtWidgets.QDialog,
                                                                                               OntologyConfigurationForm,
                                                                                               QtBot],
                                                                                             ontology_doc_mock: ontology_doc_mock):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog should not be shown!"
    qtbot.mouseClick(ui_form.addTypePushButton, Qt.LeftButton)
    assert ui_form.create_type_dialog.buttonBox.isVisible() is True, "Create new type dialog not shown!"

  def test_component_delete_new_type_without_ontology_loaded_should_show_error_message(self,
                                                                                       ontology_editor_gui: tuple[
                                                                                         QApplication,
                                                                                         QtWidgets.QDialog,
                                                                                         OntologyConfigurationForm,
                                                                                         QtBot],
                                                                                       ontology_doc_mock: ontology_doc_mock,
                                                                                       mocker):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    mock_show_message = mocker.patch(
      "pasta_eln.GUI.ontology_configuration.ontology_configuration_extended.show_message")
    mocker.patch.object(ui_form, "ontology_loaded", False)
    # Select a non-structural type in the type combo box, in-order to enable delete button
    ui_form.typeComboBox.setCurrentText("measurement")
    assert ui_form.typeComboBox.currentText() == "measurement", "Data type combo box should be selected to measurement"
    qtbot.mouseClick(ui_form.deleteTypePushButton, Qt.LeftButton)
    mock_show_message.assert_called_once_with("Load the ontology data first....")
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog should not be shown!"

  def test_component_delete_selected_type_with_loaded_ontology_should_delete_and_update_ui(self,
                                                                                           ontology_editor_gui:
                                                                                           tuple[
                                                                                             QApplication,
                                                                                             QtWidgets.QDialog,
                                                                                             OntologyConfigurationForm,
                                                                                             QtBot],
                                                                                           ontology_doc_mock: ontology_doc_mock,
                                                                                           props_column_names: props_column_names,
                                                                                           attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog should not be shown!"
    # Select a non-structural type in the type combo box, in order to enable the "delete" button
    ui_form.typeComboBox.setCurrentText("measurement")
    assert ui_form.typeComboBox.currentText() == "measurement", "Data type combo box should be selected to measurement"
    current_selected_type = ui_form.typeComboBox.currentText()
    previous_types_count = ui_form.typeComboBox.count()
    qtbot.mouseClick(ui_form.deleteTypePushButton, Qt.LeftButton)
    assert (current_selected_type not in [ui_form.typeComboBox.itemText(i)
                                          for i in range(ui_form.typeComboBox.count())]), \
      f"Deleted type:{current_selected_type} should not exist in combo list!"
    assert (previous_types_count - 1 == ui_form.typeComboBox.count()), \
      f"Combo list should have {previous_types_count - 1} items!"
    assert adapt_type(ui_form.typeComboBox.currentText()) == ontology_doc_mock.types_list()[0], \
      "Type combo box should be selected to first structural item"
    selected_type = ontology_doc_mock.types()[adapt_type(ui_form.typeComboBox.currentText())]
    assert ui_form.typeLabelLineEdit.text() == selected_type["label"], \
      "Type label line edit should be selected to first structural item"
    assert ui_form.typeIriLineEdit.text() == selected_type["IRI"], \
      "Type label line edit should be selected to first structural item"
    assert ui_form.propsCategoryComboBox.currentText() == list(selected_type["prop"].keys())[0], \
      "Type label line edit should be selected to first structural item"
    self.check_table_contents(attachments_column_names, props_column_names, selected_type, ui_form)

  def test_component_add_new_type_button_click_should_display_create_new_type_window(self,
                                                                                     ontology_editor_gui:
                                                                                     tuple[
                                                                                       QApplication,
                                                                                       QtWidgets.QDialog,
                                                                                       OntologyConfigurationForm,
                                                                                       QtBot],
                                                                                     ontology_doc_mock: ontology_doc_mock,
                                                                                     props_column_names: props_column_names,
                                                                                     attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog should not be shown!"
    qtbot.mouseClick(ui_form.addTypePushButton, Qt.LeftButton)
    with qtbot.waitExposed(ui_form.create_type_dialog.instance, timeout=500):
      assert ui_form.create_type_dialog.instance.isVisible() is True, "Create new type dialog should be shown!"
      assert ui_form.create_type_dialog.buttonBox.isVisible() is True, "Create new type dialog not shown!"

  def test_component_create_new_type_structural_type_should_add_new_type_with_label(self,
                                                                                    ontology_editor_gui:
                                                                                    tuple[
                                                                                      QApplication,
                                                                                      QtWidgets.QDialog,
                                                                                      OntologyConfigurationForm,
                                                                                      QtBot],
                                                                                    ontology_doc_mock: ontology_doc_mock,
                                                                                    props_column_names: props_column_names,
                                                                                    attachments_column_names: attachments_column_names):

    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog button box should not be shown!"
    qtbot.mouseClick(ui_form.addTypePushButton, Qt.LeftButton)
    with qtbot.waitExposed(ui_form.create_type_dialog.instance, timeout=200):
      assert ui_form.create_type_dialog.instance.isVisible() is True, "Create new type dialog should be shown!"
      assert ui_form.create_type_dialog.buttonBox.isVisible() is True, "Create new type dialog button box should be shown!"
      ui_form.create_type_dialog.structuralLevelCheckBox.setChecked(True)
      ui_form.create_type_dialog.labelLineEdit.setText("test")
      assert ui_form.create_type_dialog.titleLineEdit.text() == ui_form.create_type_dialog.next_struct_level.replace(
        'x', 'Structure level '), "title should be set to 'Structure level 3'"
    qtbot.mouseClick(ui_form.create_type_dialog.buttonBox.button(ui_form.create_type_dialog.buttonBox.Ok),
                     Qt.LeftButton)
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    assert ui_form.typeComboBox.currentText() == "Structure level 3", "Data type combo box should be newly added structural item"
    assert ui_form.typeLabelLineEdit.text() == "test", "Data type label should be newly added label"

  def test_component_create_new_type_normal_type_should_add_new_type_with_label(self,
                                                                                ontology_editor_gui:
                                                                                tuple[
                                                                                  QApplication,
                                                                                  QtWidgets.QDialog,
                                                                                  OntologyConfigurationForm,
                                                                                  QtBot],
                                                                                ontology_doc_mock: ontology_doc_mock,
                                                                                props_column_names: props_column_names,
                                                                                attachments_column_names: attachments_column_names):

    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog button box should not be shown!"
    qtbot.mouseClick(ui_form.addTypePushButton, Qt.LeftButton)
    with qtbot.waitExposed(ui_form.create_type_dialog.instance, timeout=200):
      assert ui_form.create_type_dialog.instance.isVisible() is True, "Create new type dialog should be shown!"
      assert ui_form.create_type_dialog.buttonBox.isVisible() is True, "Create new type dialog button box should be shown!"
      assert ui_form.create_type_dialog.structuralLevelCheckBox.isChecked() is False, "structuralLevelCheckBox should be unchecked"
      ui_form.create_type_dialog.titleLineEdit.setText("title")
      ui_form.create_type_dialog.labelLineEdit.setText("label")
    qtbot.mouseClick(ui_form.create_type_dialog.buttonBox.button(ui_form.create_type_dialog.buttonBox.Ok),
                     Qt.LeftButton)
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    assert ui_form.typeComboBox.currentText() == "title", "Data type combo box should be newly added type title"
    assert ui_form.typeLabelLineEdit.text() == "label", "Data type combo box should be newly added type label"

  def test_component_create_new_type_normal_type_with_empty_title_should_warn_user(self,
                                                                                   mocker,
                                                                                   ontology_editor_gui:
                                                                                   tuple[
                                                                                     QApplication,
                                                                                     QtWidgets.QDialog,
                                                                                     OntologyConfigurationForm,
                                                                                     QtBot],
                                                                                   ontology_doc_mock: ontology_doc_mock,
                                                                                   props_column_names: props_column_names,
                                                                                   attachments_column_names: attachments_column_names):

    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    mocker.patch.object(ui_form.logger, 'warning')

    # Checking with empty title
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog button box should not be shown!"
    qtbot.mouseClick(ui_form.addTypePushButton, Qt.LeftButton)
    with qtbot.waitExposed(ui_form.create_type_dialog.instance, timeout=200):
      assert ui_form.create_type_dialog.instance.isVisible() is True, "Create new type dialog should be shown!"
      assert ui_form.create_type_dialog.buttonBox.isVisible() is True, "Create new type dialog button box should be shown!"
      assert ui_form.create_type_dialog.structuralLevelCheckBox.isChecked() is False, "structuralLevelCheckBox should be unchecked"
      ui_form.create_type_dialog.titleLineEdit.setText("")
      ui_form.create_type_dialog.labelLineEdit.setText("label")
    qtbot.mouseClick(ui_form.create_type_dialog.buttonBox.button(ui_form.create_type_dialog.buttonBox.Ok),
                     Qt.LeftButton)
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    ui_form.logger.warning.assert_called_once_with("Enter non-null/valid title!!.....")
    ui_form.message_box.setText.assert_called_once_with('Enter non-null/valid title!!.....')
    ui_form.message_box.exec.assert_called_once_with()
    assert ui_form.typeComboBox.currentText() != "", "Data type combo box should not be empty title"
    assert ui_form.typeLabelLineEdit.text() != "label", "Data type combo box should not be newly added type label"

    # Checking with None title
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog button box should not be shown!"
    qtbot.mouseClick(ui_form.addTypePushButton, Qt.LeftButton)
    with qtbot.waitExposed(ui_form.create_type_dialog.instance, timeout=200):
      assert ui_form.create_type_dialog.instance.isVisible() is True, "Create new type dialog should be shown!"
      assert ui_form.create_type_dialog.buttonBox.isVisible() is True, "Create new type dialog button box should be shown!"
      assert ui_form.create_type_dialog.structuralLevelCheckBox.isChecked() is False, "structuralLevelCheckBox should be unchecked"
      ui_form.create_type_dialog.titleLineEdit.setText(None)
      ui_form.create_type_dialog.labelLineEdit.setText("label")
    qtbot.mouseClick(ui_form.create_type_dialog.buttonBox.button(ui_form.create_type_dialog.buttonBox.Ok),
                     Qt.LeftButton)
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    ui_form.logger.warning.assert_has_calls([
      mocker.call("Enter non-null/valid title!!....."),
      mocker.call("Enter non-null/valid title!!.....")])
    ui_form.message_box.setText.assert_has_calls([
      mocker.call("Enter non-null/valid title!!....."),
      mocker.call("Enter non-null/valid title!!.....")])
    ui_form.message_box.exec.assert_has_calls([
      mocker.call(),
      mocker.call()])
    assert ui_form.typeComboBox.currentText() != None, "Data type combo box should not be None"
    assert ui_form.typeLabelLineEdit.text() != "label", "Data type combo box should not be newly added type label"

  def test_component_create_new_type_reject_should_not_add_new_type_with_label(self,
                                                                               ontology_editor_gui:
                                                                               tuple[
                                                                                 QApplication,
                                                                                 QtWidgets.QDialog,
                                                                                 OntologyConfigurationForm,
                                                                                 QtBot],
                                                                               ontology_doc_mock: ontology_doc_mock,
                                                                               props_column_names: props_column_names,
                                                                               attachments_column_names: attachments_column_names):

    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog button box should not be shown!"
    qtbot.mouseClick(ui_form.addTypePushButton, Qt.LeftButton)
    with qtbot.waitExposed(ui_form.create_type_dialog.instance, timeout=200):
      assert ui_form.create_type_dialog.instance.isVisible() is True, "Create new type dialog should be shown!"
      assert ui_form.create_type_dialog.buttonBox.isVisible() is True, "Create new type dialog button box should be shown!"
      assert ui_form.create_type_dialog.structuralLevelCheckBox.isChecked() is False, "structuralLevelCheckBox should be unchecked"
      ui_form.create_type_dialog.titleLineEdit.setText("title")
      ui_form.create_type_dialog.labelLineEdit.setText("label")
    qtbot.mouseClick(ui_form.create_type_dialog.buttonBox.button(ui_form.create_type_dialog.buttonBox.Cancel),
                     Qt.LeftButton)
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    assert ui_form.typeComboBox.currentText() != "title", "Data type combo box should not be newly added type title"
    assert ui_form.typeLabelLineEdit.text() != "label", "Data type combo box should not be newly added type label"

  def test_component_cancel_button_click_after_delete_category_should_not_modify_ontology_document_data(self,
                                                                                                        ontology_editor_gui:
                                                                                                        tuple[
                                                                                                          QApplication,
                                                                                                          QtWidgets.QDialog,
                                                                                                          OntologyConfigurationForm,
                                                                                                          QtBot],
                                                                                                        ontology_doc_mock: ontology_doc_mock,
                                                                                                        props_column_names: props_column_names,
                                                                                                        attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog should not be shown!"
    current_selected_type_category = ui_form.propsCategoryComboBox.currentText()
    previous_types_category_count = ui_form.propsCategoryComboBox.count()
    qtbot.mouseClick(ui_form.deletePropsCategoryPushButton, Qt.LeftButton)
    assert (current_selected_type_category not in [ui_form.propsCategoryComboBox.itemText(i)
                                                   for i in range(ui_form.propsCategoryComboBox.count())]), \
      f"Deleted category: {current_selected_type_category} should not exist in combo list!"
    assert (previous_types_category_count - 1 == ui_form.propsCategoryComboBox.count()), \
      f"Combo list should have {previous_types_category_count - 1} items!"
    qtbot.mouseClick(ui_form.cancelPushButton, Qt.LeftButton)
    assert ontology_doc_mock.types() != ui_form.ontology_types, "Ontology document should not be modified!"

  def test_component_delete_type_after_creation_of_new_structural_type_should_succeed(self,
                                                                                      ontology_editor_gui:
                                                                                      tuple[
                                                                                        QApplication,
                                                                                        QtWidgets.QDialog,
                                                                                        OntologyConfigurationForm,
                                                                                        QtBot],
                                                                                      ontology_doc_mock: ontology_doc_mock,
                                                                                      props_column_names: props_column_names,
                                                                                      attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog button box should not be shown!"
    qtbot.mouseClick(ui_form.addTypePushButton, Qt.LeftButton)
    with qtbot.waitExposed(ui_form.create_type_dialog.instance, timeout=200):
      assert ui_form.create_type_dialog.instance.isVisible() is True, "Create new type dialog should be shown!"
      assert ui_form.create_type_dialog.buttonBox.isVisible() is True, "Create new type dialog button box should be shown!"
      ui_form.create_type_dialog.structuralLevelCheckBox.setChecked(True)
      ui_form.create_type_dialog.labelLineEdit.setText("test")
      assert ui_form.create_type_dialog.titleLineEdit.text() == ui_form.create_type_dialog.next_struct_level.replace(
        'x', 'Structure level '), "title should be set to 'Structure level 3'"
    qtbot.mouseClick(ui_form.create_type_dialog.buttonBox.button(ui_form.create_type_dialog.buttonBox.Ok),
                     Qt.LeftButton)
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    assert ui_form.typeComboBox.currentText() == "Structure level 3", "Data type combo box should be newly added structural item"
    assert ui_form.typeLabelLineEdit.text() == "test", "Data type label should be newly added label"
    current_selected_type = ui_form.typeComboBox.currentText()
    previous_types_count = ui_form.typeComboBox.count()
    qtbot.mouseClick(ui_form.deleteTypePushButton, Qt.LeftButton)
    assert (current_selected_type not in [ui_form.typeComboBox.itemText(i)
                                          for i in range(ui_form.typeComboBox.count())]), \
      f"Deleted type:{current_selected_type} should not exist in combo list!"
    assert (previous_types_count - 1 == ui_form.typeComboBox.count()), \
      f"Combo list should have {previous_types_count - 1} items!"
    assert adapt_type(ui_form.typeComboBox.currentText()) == ontology_doc_mock.types_list()[0], \
      "Type combo box should be selected to first structural item"
    selected_type = ontology_doc_mock.types()[adapt_type(ui_form.typeComboBox.currentText())]
    assert ui_form.typeLabelLineEdit.text() == selected_type["label"], \
      "Type label line edit should be selected to first structural item"
    assert ui_form.typeIriLineEdit.text() == selected_type["IRI"], \
      "Type label line edit should be selected to first structural item"
    assert ui_form.propsCategoryComboBox.currentText() == list(selected_type["prop"].keys())[0], \
      "Type label line edit should be selected to first structural item"
    self.check_table_contents(attachments_column_names, props_column_names, selected_type, ui_form)

  def test_component_save_button_click_after_delete_category_should_modify_ontology_document_data(self,
                                                                                                  mocker,
                                                                                                  ontology_editor_gui:
                                                                                                  tuple[
                                                                                                    QApplication,
                                                                                                    QtWidgets.QDialog,
                                                                                                    OntologyConfigurationForm,
                                                                                                    QtBot],
                                                                                                  ontology_doc_mock: ontology_doc_mock,
                                                                                                  props_column_names: props_column_names,
                                                                                                  attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog should not be shown!"
    mock_show_message = mocker.patch(
      "pasta_eln.GUI.ontology_configuration.ontology_configuration_extended.show_message")
    current_selected_type_category = ui_form.propsCategoryComboBox.currentText()
    previous_types_category_count = ui_form.propsCategoryComboBox.count()
    qtbot.mouseClick(ui_form.deletePropsCategoryPushButton, Qt.LeftButton)
    assert (current_selected_type_category not in [ui_form.propsCategoryComboBox.itemText(i)
                                                   for i in range(ui_form.propsCategoryComboBox.count())]), \
      f"Deleted category: {current_selected_type_category} should not exist in combo list!"
    assert (previous_types_category_count - 1 == ui_form.propsCategoryComboBox.count()), \
      f"Combo list should have {previous_types_category_count - 1} items!"
    qtbot.mouseClick(ui_form.saveOntologyPushButton, Qt.LeftButton)
    assert ontology_doc_mock.types() == ui_form.ontology_types, "Ontology document should be modified!"
    mock_show_message.assert_called_once_with("Ontology data saved successfully..")

  def test_component_iri_lookup_button_click_should_show_ontology_lookup_dialog_and_set_iris_on_accept(self,
                                                                                                       ontology_editor_gui:
                                                                                                       tuple[
                                                                                                         QApplication,
                                                                                                         QtWidgets.QDialog,
                                                                                                         OntologyConfigurationForm,
                                                                                                         QtBot],
                                                                                                       ontology_doc_mock: ontology_doc_mock,
                                                                                                       props_column_names: props_column_names,
                                                                                                       attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    assert ui_form.typeIriLineEdit.text() == 'http://url.com', "typeIriLineEdit should be default test value"
    iri_lookup_action = None
    for act in ui_form.typeIriLineEdit.actions():
      if isinstance(act, LookupIriAction):
        iri_lookup_action = act
        act.trigger()
    lookup_dialog = iri_lookup_action.terminology_lookup_dialog
    assert lookup_dialog.selected_iris == [], "Selected IRIs should be empty"
    with qtbot.waitExposed(lookup_dialog.instance, timeout=500):
      assert lookup_dialog.instance.isVisible() is True, "Ontology lookup dialog should be visible"
      assert lookup_dialog.terminologyLineEdit.text() == "Projects", "Search term should be 'Projects'"
      assert lookup_dialog.errorConsoleTextEdit.isVisible() is False, "Error console should not be visible"
      assert lookup_dialog.scrollAreaWidgetContents.isVisible() is True, "Scroll area should be visible"
      assert lookup_dialog.scrollAreaContentsVerticalLayout.count() == 0, "Scroll area should be empty"
      qtbot.mouseClick(lookup_dialog.terminologySearchPushButton, Qt.LeftButton)
      assert lookup_dialog.scrollAreaContentsVerticalLayout.count() == 11, "Scroll area should be populated with 11 items"
      for pos in range(lookup_dialog.scrollAreaContentsVerticalLayout.count()):
        check_box = lookup_dialog.scrollAreaContentsVerticalLayout.itemAt(pos).widget().findChildren(QCheckBox)[0]
        assert check_box is not None and check_box.isChecked() is False, "Checkbox should not be checked"
        check_box.setChecked(True)
        assert check_box.isChecked() is True, "Checkbox should be checked"
    qtbot.mouseClick(lookup_dialog.buttonBox.button(lookup_dialog.buttonBox.Ok), Qt.LeftButton)
    assert lookup_dialog.instance.isVisible() is False, "Ontology lookup dialog should be accepted and closed"
    assert len(lookup_dialog.selected_iris) == 11, "IRIs should be set"
    assert ui_form.typeIriLineEdit.text() == " ".join(
      lookup_dialog.selected_iris), "typeIriLineEdit should contain all selected IRIs"

  def test_component_iri_lookup_button_click_should_show_ontology_lookup_dialog_and_should_not_set_iris_on_cancel(self,
                                                                                                                  ontology_editor_gui:
                                                                                                                  tuple[
                                                                                                                    QApplication,
                                                                                                                    QtWidgets.QDialog,
                                                                                                                    OntologyConfigurationForm,
                                                                                                                    QtBot],
                                                                                                                  ontology_doc_mock: ontology_doc_mock,
                                                                                                                  props_column_names: props_column_names,
                                                                                                                  attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    assert ui_form.typeIriLineEdit.text() == 'http://url.com', "typeIriLineEdit should be default test value"
    iri_lookup_action = None
    for act in ui_form.typeIriLineEdit.actions():
      if isinstance(act, LookupIriAction):
        iri_lookup_action = act
        act.trigger()
    lookup_dialog = iri_lookup_action.terminology_lookup_dialog
    assert lookup_dialog.selected_iris == [], "Selected IRIs should be empty"
    with qtbot.waitExposed(lookup_dialog.instance, timeout=500):
      assert lookup_dialog.instance.isVisible() is True, "Ontology lookup dialog should be visible"
      assert lookup_dialog.terminologyLineEdit.text() == "Projects", "Search term should be 'Projects'"
      assert lookup_dialog.errorConsoleTextEdit.isVisible() is False, "Error console should not be visible"
      assert lookup_dialog.scrollAreaWidgetContents.isVisible() is True, "Scroll area should be visible"
      assert lookup_dialog.scrollAreaContentsVerticalLayout.count() == 0, "Scroll area should be empty"
      qtbot.mouseClick(lookup_dialog.terminologySearchPushButton, Qt.LeftButton)
      assert lookup_dialog.scrollAreaContentsVerticalLayout.count() == 11, "Scroll area should be populated with 11 items"
      for pos in range(lookup_dialog.scrollAreaContentsVerticalLayout.count()):
        check_box = lookup_dialog.scrollAreaContentsVerticalLayout.itemAt(pos).widget().findChildren(QCheckBox)[0]
        assert check_box is not None and check_box.isChecked() is False, "Checkbox should not be checked"
        check_box.setChecked(True)
        assert check_box.isChecked() is True, "Checkbox should be checked"
    qtbot.mouseClick(lookup_dialog.buttonBox.button(lookup_dialog.buttonBox.Cancel), Qt.LeftButton)
    assert lookup_dialog.instance.isVisible() is False, "Ontology lookup dialog should be cancelled and closed"
    assert lookup_dialog.selected_iris == [], "IRIs should not be set"
    assert ui_form.typeIriLineEdit.text() == 'http://url.com', "typeIriLineEdit should be default test value after the cancellation"

  def test_delete_type_button_must_be_disabled_for_every_structural_level_except_the_last(self,
                                                                                          ontology_editor_gui:
                                                                                          tuple[
                                                                                            QApplication,
                                                                                            QtWidgets.QDialog,
                                                                                            OntologyConfigurationForm,
                                                                                            QtBot],
                                                                                          ontology_doc_mock: ontology_doc_mock,
                                                                                          props_column_names: props_column_names,
                                                                                          attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    assert ui_form.typeComboBox.currentText() == "Structure level 0", "Initial loaded type must be 'Structure level 0'"
    assert ui_form.deleteTypePushButton.isEnabled() is False, "Delete type button must be disabled for 'Structure level 0'"
    loaded_types = []
    for i in range(ui_form.typeComboBox.count()):
      loaded_types.append(ui_form.typeComboBox.itemText(i))
    enabled_structural_type = max(filter(lambda k: 'Structure level' in k, loaded_types))
    ui_form.typeComboBox.setCurrentText(enabled_structural_type)
    assert ui_form.deleteTypePushButton.isEnabled() is True, f"Delete type button must be enabled for only enabled structural type: '{enabled_structural_type}'"
    loaded_types.remove(enabled_structural_type)
    for loaded_type in loaded_types:
      ui_form.typeComboBox.setCurrentText(loaded_type)
      if "Structure level" in loaded_type:
        assert ui_form.deleteTypePushButton.isEnabled() is False, f"Delete type button must be disabled for '{loaded_type}'"
      else:
        assert ui_form.deleteTypePushButton.isEnabled() is True, "Delete type button must be enabled for normal types"

    # Add a new structural type and check if the delete button is disabled for the previously enabled type
    qtbot.mouseClick(ui_form.addTypePushButton, Qt.LeftButton)
    with qtbot.waitExposed(ui_form.create_type_dialog.instance, timeout=200):
      ui_form.create_type_dialog.structuralLevelCheckBox.setChecked(True)
      ui_form.create_type_dialog.labelLineEdit.setText("test")
    qtbot.mouseClick(ui_form.create_type_dialog.buttonBox.button(ui_form.create_type_dialog.buttonBox.Ok),
                     Qt.LeftButton)
    ui_form.typeComboBox.setCurrentText(enabled_structural_type)
    assert ui_form.deleteTypePushButton.isEnabled() is False, f"Delete type button must be disabled for only previously enabled structural type: '{enabled_structural_type}'"

    # Reload the types and check after the addition of new type and check if the delete button is enabled/disabled
    loaded_types.clear()
    for i in range(ui_form.typeComboBox.count()):
      loaded_types.append(ui_form.typeComboBox.itemText(i))
    enabled_structural_type = max(filter(lambda k: 'Structure level' in k, loaded_types))
    ui_form.typeComboBox.setCurrentText(enabled_structural_type)
    assert ui_form.deleteTypePushButton.isEnabled() is True, f"Delete type button must be enabled for only enabled structural type: '{enabled_structural_type}'"
    loaded_types.remove(enabled_structural_type)
    for loaded_type in loaded_types:
      ui_form.typeComboBox.setCurrentText(loaded_type)
      if "Structure level" in loaded_type:
        assert ui_form.deleteTypePushButton.isEnabled() is False, f"Delete type button must be disabled for '{loaded_type}'"
      else:
        assert ui_form.deleteTypePushButton.isEnabled() is True, "Delete type button must be enabled for normal types"

    # Add a normal type and check if the delete button is disabled correctly for the structural types
    qtbot.mouseClick(ui_form.addTypePushButton, Qt.LeftButton)
    with qtbot.waitExposed(ui_form.create_type_dialog.instance, timeout=200):
      ui_form.create_type_dialog.titleLineEdit.setText("new type")
      ui_form.create_type_dialog.labelLineEdit.setText("test")
    qtbot.mouseClick(ui_form.create_type_dialog.buttonBox.button(ui_form.create_type_dialog.buttonBox.Ok),
                     Qt.LeftButton)

    # Reload the types and check after the addition of new type and check if the delete button is enabled/disabled
    loaded_types.clear()
    for i in range(ui_form.typeComboBox.count()):
      loaded_types.append(ui_form.typeComboBox.itemText(i))
    enabled_structural_type = max(filter(lambda k: 'Structure level' in k, loaded_types))
    ui_form.typeComboBox.setCurrentText(enabled_structural_type)
    assert ui_form.deleteTypePushButton.isEnabled() is True, f"Delete type button must be enabled for only enabled structural type: '{enabled_structural_type}'"
    loaded_types.remove(enabled_structural_type)
    for loaded_type in loaded_types:
      ui_form.typeComboBox.setCurrentText(loaded_type)
      if "Structure level" in loaded_type:
        assert ui_form.deleteTypePushButton.isEnabled() is False, f"Delete type button must be disabled for '{loaded_type}'"
      else:
        assert ui_form.deleteTypePushButton.isEnabled() is True, "Delete type button must be enabled for normal types'"

  def test_delete_of_structural_type_possible_from_xn_to_x1_must_succeed_and_x0_delete_disabled(self,
                                                                                                ontology_editor_gui:
                                                                                                tuple[
                                                                                                  QApplication,
                                                                                                  QtWidgets.QDialog,
                                                                                                  OntologyConfigurationForm,
                                                                                                  QtBot],
                                                                                                ontology_doc_mock: ontology_doc_mock,
                                                                                                props_column_names: props_column_names,
                                                                                                attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    assert ui_form.typeComboBox.currentText() == "Structure level 0", "Initial loaded type must be 'Structure level 0'"
    assert ui_form.deleteTypePushButton.isEnabled() is False, "Delete type button must be disabled for 'Structure level 0'"
    # Add 5 structural types
    for i in range(5):
      qtbot.mouseClick(ui_form.addTypePushButton, Qt.LeftButton)
      with qtbot.waitExposed(ui_form.create_type_dialog.instance, timeout=200):
        ui_form.create_type_dialog.structuralLevelCheckBox.setChecked(True)
        ui_form.create_type_dialog.labelLineEdit.setText("test")
      qtbot.mouseClick(ui_form.create_type_dialog.buttonBox.button(ui_form.create_type_dialog.buttonBox.Ok),
                       Qt.LeftButton)

    # Read the loaded types
    loaded_types = []
    for i in range(ui_form.typeComboBox.count()):
      loaded_types.append(ui_form.typeComboBox.itemText(i))

    # Delete the normal types from UI
    normal_types = list(filter(lambda k: 'Structure level' not in k, loaded_types))
    for normal_type in normal_types:
      ui_form.typeComboBox.setCurrentText(normal_type)
      assert ui_form.deleteTypePushButton.isEnabled() is True, f"Delete type button must be enabled for only enabled structural type: '{normal_type}'"
      qtbot.mouseClick(ui_form.deleteTypePushButton, Qt.LeftButton)
      for i in range(ui_form.typeComboBox.count()):
        assert ui_form.typeComboBox.itemText(
          i) != normal_type, f"Deleted type:{normal_type} should not exist in combo list!"
      loaded_types.remove(normal_type)

    # Delete the structural types from UI
    structural_types = list(filter(lambda k: 'Structure level' in k, loaded_types))
    structural_types.sort()
    assert structural_types == loaded_types, "All normal types must be deleted from UI, hence only structural types are left!"
    for i in range(len(structural_types)):
      enabled_structural_type = max(structural_types)
      if enabled_structural_type == 'Structure level 0':
        break
      for structural_type in list(structural_types):
        if structural_type == enabled_structural_type:
          ui_form.typeComboBox.setCurrentText(structural_type)
          assert ui_form.deleteTypePushButton.isEnabled() is True, f"Delete type button must be enabled for only enabled structural type: '{structural_type}'"
          qtbot.mouseClick(ui_form.deleteTypePushButton, Qt.LeftButton)
          for j in range(ui_form.typeComboBox.count()):
            assert ui_form.typeComboBox.itemText(
              j) != structural_type, f"Deleted type:{structural_type} should not exist in combo list!"
          structural_types.remove(structural_type)
          loaded_types.remove(structural_type)
        else:
          ui_form.typeComboBox.setCurrentText(structural_type)
          assert ui_form.deleteTypePushButton.isEnabled() is False, f"Delete type button must be disabled for '{structural_type}'"
    assert structural_types == loaded_types == [
      "Structure level 0"], "All structural types must be deleted from UI except 'Structure level 0'"
