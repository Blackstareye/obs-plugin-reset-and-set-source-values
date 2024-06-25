import obspython as obs
from UiProvider import UiProvider
from pathlib import Path


print("Hello world!")

def script_tick(seconds):
    pass

# Called at script unload
def script_unload():
  pass

# Called before data settings are saved
def script_save(settings):
  pass

# Callback for the hotkey
def on_shake_hotkey(pressed):
  pass



# Called to set default values of data settings
def script_defaults(settings):
    pass

# Identifier of the hotkey set by OBS
hotkey_id = obs.OBS_INVALID_HOTKEY_ID
# Called at script load
def script_load(settings):
    pass


# TODO could be elaborated to add "set values" and set them after reset.
# Description displayed in the Scripts dialog window
def script_description():
  return """<center><h2>OBS Camera Reset Button</h2></center>
            <p> Reset the Camera and trigger two commands. Go to <em>Settings
            </em> then <em>Hotkeys</em> to select the key combination.</p><p>Check the <a href=
            "https://github.com/obsproject/obs-studio/wiki/Scripting-Tutorial-Source-Shake.md">
            Source Shake Scripting Tutorial</a> on the OBS Wiki for more information.</p>"""




# Called to display the properties GUI
def script_properties():
  props = obs.obs_properties_create()
  #obs.obs_properties_add_text(props, "source_name", "Source name", obs.OBS_TEXT_DEFAULT)
  # Drop-down list of sources
  list_property = obs.obs_properties_add_list(props, "source_name", "Source name",
              obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
  # Button to refresh the drop-down list
  obs.obs_properties_add_button(props, "button", "Refresh list of sources",
    lambda props,prop: True if fillSourceList(list_property) else True)
  fillSourceList(list_property)

  p = Path(__file__).absolute()  # current script path
  pstr : str  = p.parent.as_posix()
  path = obs.obs_properties_add_path(props, "path_to_setting_file", "Path to the setting file", obs.OBS_PATH_FILE, "json", pstr )
  # TODO modified hook
  obs.obs_properties_add_text(props, "fileInfo", "Displays the File Content", obs.OBS_TEXT_INFO | obs.OBS_TEXT_MULTILINE)

  # callbacks
#   obs.obs_property_set_modified_callback(path, on_path_update)
  return props


def fillSourceList(list_property):
    # Fills the given list property object with the names of all sources plus an empty one
    sources = obs.obs_enum_sources()
    obs.obs_property_list_clear(list_property)
    obs.obs_property_list_add_string(list_property, "", "")
    for source in sources:
        name = obs.obs_source_get_name(source)
        obs.obs_property_list_add_string(list_property, name, name)
    obs.source_list_release(sources)


def on_path_update(props, prop, settings):
  return True
  #TODO mit dem hier müsste ich evtl eine modified list hinbekommen
  


def resetSettings():
  pass

def loadSettings():
  pass
  





# Called after change of settings including once after script load
# TODO on modification or something hook
def script_update(settings):
  file_path = obs.obs_data_get_string(settings, "path_to_setting_file");
  contents = Path(file_path).read_text()
  # TODO load file from path
  obs.obs_data_set_string(settings, "fileInfo", contents);

# TODO on signal remove hook

# obs_data_create_from_json_file_safe
# https://docs.obsproject.com/reference-settings#c.obs_data_create_from_json
